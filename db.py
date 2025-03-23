# db.py - Finance Tracker App/db.py

import sqlite3
import json
import os
import threading
from datetime import datetime, date, timedelta
from models import CurrencyConverter

class Database:
    def __init__(self, db_path="finance_tracker.db"):
        print(f"[DEBUG] Initializing Database with path: {db_path}")
        self.db_path = db_path
        self.conn = None
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        self.initialize()
        
    def initialize(self):
        """Initialize the database connection and tables"""
        print("[DEBUG] Starting database initialization")
        create_new = not os.path.exists(self.db_path)
        print(f"[DEBUG] Database {'will be created' if create_new else 'already exists'}")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Always create tables if they don't exist, regardless of whether the DB file is new
        self._create_tables()
        print("[DEBUG] Database initialization complete")
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        print("[DEBUG] Creating database tables")
        with self.lock:
            cursor = self.conn.cursor()
            
            # Create exchange_rates table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_rates (
                id INTEGER PRIMARY KEY,
                data TEXT NOT NULL
            )
            ''')
            print("[DEBUG] Created exchange_rates table")
            
            # Create accounts table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                account_type TEXT NOT NULL,
                currency TEXT NOT NULL,
                balance REAL NOT NULL,
                credit_limit REAL NOT NULL,
                is_savings INTEGER NOT NULL
            )
            ''')
            print("[DEBUG] Created accounts table")
            
            # Create transactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                transaction_type TEXT NOT NULL,
                from_account_id TEXT,
                to_account_id TEXT,
                status TEXT NOT NULL,
                category TEXT,
                FOREIGN KEY (from_account_id) REFERENCES accounts (id),
                FOREIGN KEY (to_account_id) REFERENCES accounts (id)
            )
            ''')
            print("[DEBUG] Created transactions table")
            
            # Create debts table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS debts (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                is_receivable INTEGER NOT NULL,
                linked_account_id TEXT,
                status TEXT NOT NULL,
                currency TEXT NOT NULL,
                payment_history TEXT,
                FOREIGN KEY (linked_account_id) REFERENCES accounts (id)
            )
            ''')
            print("[DEBUG] Created debts table")
            
            # Create subscriptions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                frequency TEXT NOT NULL,
                next_payment_date TEXT NOT NULL,
                linked_account_id TEXT,
                status TEXT NOT NULL,
                currency TEXT NOT NULL,
                category TEXT,
                FOREIGN KEY (linked_account_id) REFERENCES accounts (id)
            )
            ''')
            print("[DEBUG] Created subscriptions table")
            
            self.conn.commit()
            print("[DEBUG] All tables created successfully")
    
    def close(self):
        """Close the database connection"""
        print("[DEBUG] Closing database connection")
        if self.conn:
            with self.lock:
                self.conn.close()
                print("[DEBUG] Database connection closed")
    
    # Account operations
    def save_account(self, account):
        """Save or update an account"""
        print(f"[DEBUG] Saving account: {account.id}")
        with self.lock:
            cursor = self.conn.cursor()
            data = account.to_dict()
            
            cursor.execute('''
            INSERT OR REPLACE INTO accounts (id, name, account_type, currency, balance, credit_limit, is_savings)
            VALUES (:id, :name, :account_type, :currency, :balance, :credit_limit, :is_savings)
            ''', data)
            
            self.conn.commit()
            print(f"[DEBUG] Account {account.id} saved successfully")
            return account.id
    
    def get_account(self, account_id):
        """Get account by ID"""
        print(f"[DEBUG] Fetching account: {account_id}")
        from models import Account
        
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
            row = cursor.fetchone()
            
            if row:
                print(f"[DEBUG] Found account: {account_id}")
                return Account.from_dict(dict(row))
            print(f"[DEBUG] Account not found: {account_id}")
            return None
    
    def get_all_accounts(self):
        """Get all accounts"""
        print("[DEBUG] Fetching all accounts")
        from models import Account
        
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM accounts')
            rows = cursor.fetchall()
            
            accounts = [Account.from_dict(dict(row)) for row in rows]
            print(f"[DEBUG] Found {len(accounts)} accounts")
            return accounts
    
    def delete_account(self, account_id):
        """Delete an account by ID"""
        print(f"[DEBUG] Attempting to delete account: {account_id}")
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
            self.conn.commit()
            success = cursor.rowcount > 0
            print(f"[DEBUG] Account deletion {'successful' if success else 'failed'}: {account_id}")
            return success
    
    # Transaction operations
    def save_transaction(self, transaction):
        """Save or update a transaction"""
        print(f"[DEBUG] Saving transaction: {transaction.id}")
        with self.lock:
            cursor = self.conn.cursor()
            data = transaction.to_dict()
            
            cursor.execute('''
            INSERT OR REPLACE INTO transactions 
            (id, date, amount, description, transaction_type, from_account_id, to_account_id, status, category)
            VALUES (:id, :date, :amount, :description, :transaction_type, :from_account_id, :to_account_id, :status, :category)
            ''', data)
            
            self.conn.commit()
            print(f"[DEBUG] Transaction {transaction.id} saved successfully")
            return transaction.id
    
    def get_transaction(self, transaction_id):
        """Get transaction by ID"""
        print(f"[DEBUG] Fetching transaction: {transaction_id}")
        from models import Transaction
        
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
            row = cursor.fetchone()
            
            if row:
                print(f"[DEBUG] Found transaction: {transaction_id}")
                return Transaction.from_dict(dict(row))
            print(f"[DEBUG] Transaction not found: {transaction_id}")
            return None
    
    def get_all_transactions(self, status=None, account_id=None, transaction_type=None, start_date=None, end_date=None):
        """Get transactions with optional filtering"""
        print("[DEBUG] Fetching transactions with filters:", {
            "status": status,
            "account_id": account_id,
            "transaction_type": transaction_type,
            "start_date": start_date,
            "end_date": end_date
        })
        from models import Transaction
        
        with self.lock:
            cursor = self.conn.cursor()
            query = 'SELECT * FROM transactions'
            conditions = []
            params = []
            
            if status:
                conditions.append('status = ?')
                params.append(status)
            
            if account_id:
                conditions.append('(from_account_id = ? OR to_account_id = ?)')
                params.extend([account_id, account_id])
            
            if transaction_type:
                conditions.append('transaction_type = ?')
                params.append(transaction_type)
            
            if start_date:
                conditions.append('date >= ?')
                if isinstance(start_date, date):
                    start_date = start_date.isoformat()
                params.append(start_date)
            
            if end_date:
                conditions.append('date <= ?')
                if isinstance(end_date, date):
                    end_date = end_date.isoformat()
                params.append(end_date)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY date DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            transactions = [Transaction.from_dict(dict(row)) for row in rows]
            print(f"[DEBUG] Found {len(transactions)} transactions")
            return transactions
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by ID"""
        print(f"[DEBUG] Attempting to delete transaction: {transaction_id}")
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            self.conn.commit()
            success = cursor.rowcount > 0
            print(f"[DEBUG] Transaction deletion {'successful' if success else 'failed'}: {transaction_id}")
            return success
    
    # Debt operations
    def save_debt(self, debt):
        """Save or update a debt"""
        print(f"[DEBUG] Saving debt: {debt.id}")
        with self.lock:
            cursor = self.conn.cursor()
            data = debt.to_dict()
            
            cursor.execute('''
            INSERT OR REPLACE INTO debts 
            (id, description, amount, due_date, is_receivable, linked_account_id, status, currency, payment_history)
            VALUES (:id, :description, :amount, :due_date, :is_receivable, :linked_account_id, :status, :currency, :payment_history)
            ''', data)
            
            self.conn.commit()
            print(f"[DEBUG] Debt {debt.id} saved successfully")
            return debt.id
    
    def get_debt(self, debt_id):
        """Get debt by ID"""
        print(f"[DEBUG] Fetching debt: {debt_id}")
        from models import Debt
        
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM debts WHERE id = ?', (debt_id,))
            row = cursor.fetchone()
            
            if row:
                print(f"[DEBUG] Found debt: {debt_id}")
                return Debt.from_dict(dict(row))
            print(f"[DEBUG] Debt not found: {debt_id}")
            return None
    
    def get_all_debts(self, status=None, is_receivable=None):
        """Get debts with optional filtering"""
        print("[DEBUG] Fetching debts with filters:", {
            "status": status,
            "is_receivable": is_receivable
        })
        from models import Debt
        
        with self.lock:
            cursor = self.conn.cursor()
            query = 'SELECT * FROM debts'
            conditions = []
            params = []
            
            if status:
                conditions.append('status = ?')
                params.append(status)
            
            if is_receivable is not None:
                conditions.append('is_receivable = ?')
                params.append(1 if is_receivable else 0)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY due_date ASC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            debts = [Debt.from_dict(dict(row)) for row in rows]
            print(f"[DEBUG] Found {len(debts)} debts")
            return debts
    
    def delete_debt(self, debt_id):
        """Delete a debt by ID"""
        print(f"[DEBUG] Attempting to delete debt: {debt_id}")
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM debts WHERE id = ?', (debt_id,))
            self.conn.commit()
            success = cursor.rowcount > 0
            print(f"[DEBUG] Debt deletion {'successful' if success else 'failed'}: {debt_id}")
            return success
    
    # Subscription operations
    def save_subscription(self, subscription):
        """Save or update a subscription"""
        print(f"[DEBUG] Saving subscription: {subscription.id}")
        with self.lock:
            cursor = self.conn.cursor()
            data = subscription.to_dict()
            
            cursor.execute('''
            INSERT OR REPLACE INTO subscriptions 
            (id, name, amount, frequency, next_payment_date, linked_account_id, status, currency, category)
            VALUES (:id, :name, :amount, :frequency, :next_payment_date, :linked_account_id, :status, :currency, :category)
            ''', data)
            
            self.conn.commit()
            print(f"[DEBUG] Subscription {subscription.id} saved successfully")
            return subscription.id
    
    def get_subscription(self, subscription_id):
        """Get subscription by ID"""
        print(f"[DEBUG] Fetching subscription: {subscription_id}")
        from models import Subscription
        
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM subscriptions WHERE id = ?', (subscription_id,))
            row = cursor.fetchone()
            
            if row:
                print(f"[DEBUG] Found subscription: {subscription_id}")
                return Subscription.from_dict(dict(row))
            print(f"[DEBUG] Subscription not found: {subscription_id}")
            return None
    
    def get_all_subscriptions(self, status=None):
        """Get subscriptions with optional filtering"""
        print("[DEBUG] Fetching subscriptions with status filter:", status)
        from models import Subscription
        
        with self.lock:
            cursor = self.conn.cursor()
            query = 'SELECT * FROM subscriptions'
            
            if status:
                query += ' WHERE status = ?'
                cursor.execute(query, (status,))
            else:
                cursor.execute(query)
                
            rows = cursor.fetchall()
            
            subscriptions = [Subscription.from_dict(dict(row)) for row in rows]
            print(f"[DEBUG] Found {len(subscriptions)} subscriptions")
            return subscriptions
    
    def delete_subscription(self, subscription_id):
        """Delete a subscription by ID"""
        print(f"[DEBUG] Attempting to delete subscription: {subscription_id}")
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM subscriptions WHERE id = ?', (subscription_id,))
            self.conn.commit()
            success = cursor.rowcount > 0
            print(f"[DEBUG] Subscription deletion {'successful' if success else 'failed'}: {subscription_id}")
            return success
    
    # Utility methods
    def get_savings_stats(self, month=None, year=None):
        """Get savings statistics for current month or specified month/year"""
        print(f"[DEBUG] Getting savings stats for month: {month}, year: {year}")
        current_date = datetime.now()
        month = month or current_date.month
        year = year or current_date.year
        
        with self.lock:
            # Get savings accounts
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM accounts WHERE is_savings = 1')
            savings_account_ids = [row[0] for row in cursor.fetchall()]
            print(f"[DEBUG] Found {len(savings_account_ids)} savings accounts")
            
            if not savings_account_ids:
                print("[DEBUG] No savings accounts found")
                return {"total_balance": 0, "month_contribution": 0}
            
            # Get total savings balance
            savings_accounts = []
            total_balance = 0
            for account_id in savings_account_ids:
                account = self.get_account(account_id)
                if account:
                    savings_accounts.append(account)
                    total_balance += account.balance
            
            print(f"[DEBUG] Total savings balance: {total_balance}")
            
            # Calculate contributions for the month
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year+1}-01-01"
            else:
                end_date = f"{year}-{month+1:02d}-01"
                
            month_contribution = 0
            
            for account_id in savings_account_ids:
                # Get deposits to this savings account
                cursor.execute('''
                SELECT SUM(amount) FROM transactions 
                WHERE to_account_id = ? AND date >= ? AND date < ? AND status = 'completed'
                ''', (account_id, start_date, end_date))
                
                deposits = cursor.fetchone()[0] or 0
                
                # Subtract withdrawals from this savings account
                cursor.execute('''
                SELECT SUM(amount) FROM transactions 
                WHERE from_account_id = ? AND date >= ? AND date < ? AND status = 'completed'
                ''', (account_id, start_date, end_date))
                
                withdrawals = cursor.fetchone()[0] or 0
                
                month_contribution += deposits - withdrawals
            
            print(f"[DEBUG] Month contribution: {month_contribution}")
            
            return {
                "total_balance": total_balance,
                "month_contribution": month_contribution,
                "savings_accounts": savings_accounts
            }
    
    def get_liquidity(self):
        """Get total liquidity in CHF (available funds across all accounts)"""
        accounts = self.get_all_accounts()
        if not accounts:
            return 0
        
        # Calculate total liquidity (available funds from debit and checking accounts)
        # only CHF equivalent values
        liquidity = 0
        for account in accounts:
            # Exclude credit accounts with negative balance
            if account.account_type == "credit" and account.balance < 0:
                continue
                
            # Exclude savings accounts (they're not considered liquid)
            if account.is_savings:
                continue
            
            # Convert to CHF if needed and add to total
            if account.currency == "CHF":
                account_value_in_chf = account.get_available_balance()
            else:
                account_value_in_chf = CurrencyConverter.convert_to_chf(account.get_available_balance(), account.currency, self)
            
            liquidity += account_value_in_chf if account_value_in_chf > 0 else 0
        
        return liquidity
    
    def get_net_worth(self):
        """Calculate net worth in CHF (assets - liabilities) with detailed breakdown"""
        # Get all accounts
        accounts = self.get_all_accounts()
        
        # Get all debts
        debts = self.get_all_debts()
        
        # Calculate assets (positive account balances + receivables)
        assets = 0
        for account in accounts:
            # Add positive balances as assets
            if account.balance > 0:
                # Convert to CHF if needed
                if account.currency == "CHF":
                    account_value_in_chf = account.balance
                else:
                    account_value_in_chf = CurrencyConverter.convert_to_chf(account.balance, account.currency, self)
                    
                assets += account_value_in_chf
        
        # Add receivables (money owed to you)
        for debt in debts:
            if debt.is_receivable and debt.status != "paid":
                # Convert to CHF if needed
                if debt.currency == "CHF":
                    debt_value_in_chf = debt.get_remaining_amount()
                else:
                    debt_value_in_chf = CurrencyConverter.convert_to_chf(debt.get_remaining_amount(), debt.currency, self)
                    
                assets += debt_value_in_chf
        
        # Calculate liabilities (negative balances + debts)
        liabilities = 0
        for account in accounts:
            # Add negative balances as liabilities
            if account.balance < 0:
                # Convert to CHF if needed
                if account.currency == "CHF":
                    credit_value_in_chf = abs(account.balance)
                else:
                    credit_value_in_chf = CurrencyConverter.convert_to_chf(abs(account.balance), account.currency, self)
                    
                liabilities += credit_value_in_chf
        
        # Add debts (money you owe)
        for debt in debts:
            if not debt.is_receivable and debt.status != "paid":
                # Convert to CHF if needed
                if debt.currency == "CHF":
                    debt_value_in_chf = debt.get_remaining_amount()
                else:
                    debt_value_in_chf = CurrencyConverter.convert_to_chf(debt.get_remaining_amount(), debt.currency, self)
                    
                liabilities += debt_value_in_chf
        
        # Also include upcoming subscription payments in liabilities (next 30 days)
        today = date.today()
        thirty_days = today + timedelta(days=30)
        
        # Get active subscriptions with payments due in the next 30 days
        subscriptions = self.get_all_subscriptions(status="active")
        upcoming_subs = [sub for sub in subscriptions if sub.next_payment_date <= thirty_days]
        
        # Add upcoming subscription payments to liabilities
        for sub in upcoming_subs:
            if sub.currency == "CHF":
                sub_value_in_chf = sub.amount
            else:
                sub_value_in_chf = CurrencyConverter.convert_to_chf(sub.amount, sub.currency, self)
                
            liabilities += sub_value_in_chf
        
        # Calculate net worth
        net_worth = assets - liabilities
        
        return {
            "assets": assets,
            "liabilities": liabilities,
            "net_worth": net_worth
        }
    
    def check_and_update_overdue_debts(self):
        """Update status of overdue debts"""
        print("[DEBUG] Checking for overdue debts")
        today = date.today().isoformat()
        
        with self.lock:
            cursor = self.conn.cursor()
            
            cursor.execute('''
            UPDATE debts SET status = 'overdue'
            WHERE due_date < ? AND status = 'pending'
            ''', (today,))
            
            updated_count = cursor.rowcount
            self.conn.commit()
            print(f"[DEBUG] Updated {updated_count} overdue debts")
            return updated_count
    
    def generate_pending_subscription_transactions(self):
        """Generate pending transactions for active subscriptions due today or in the past"""
        print("[DEBUG] Generating pending subscription transactions")
        from models import Subscription
        
        today = date.today().isoformat()
        
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT * FROM subscriptions 
            WHERE status = 'active' AND next_payment_date <= ? 
            ''', (today,))
            
            rows = cursor.fetchall()
            subscriptions = [Subscription.from_dict(dict(row)) for row in rows]
            print(f"[DEBUG] Found {len(subscriptions)} subscriptions due for payment")
            
            transactions_generated = []
            for subscription in subscriptions:
                transaction = subscription.generate_pending_transaction()
                if transaction:
                    self.save_transaction(transaction)
                    subscription.calculate_next_payment_date(True)
                    self.save_subscription(subscription)
                    transactions_generated.append(transaction)
            
            print(f"[DEBUG] Generated {len(transactions_generated)} pending transactions")
            return transactions_generated