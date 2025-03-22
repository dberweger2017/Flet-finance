# db.py - Finance Tracker App/db.py

import sqlite3
import json
import os
from datetime import datetime, date, timedelta

class Database:
    def __init__(self, db_path="finance_tracker.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize()
        
    def initialize(self):
        """Initialize the database connection and tables"""
        create_new = not os.path.exists(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        if create_new:
            self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
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
            FOREIGN KEY (linked_account_id) REFERENCES accounts (id)
        )
        ''')
        
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
        
        self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
    
    # Account operations
    def save_account(self, account):
        """Save or update an account"""
        cursor = self.conn.cursor()
        data = account.to_dict()
        
        cursor.execute('''
        INSERT OR REPLACE INTO accounts (id, name, account_type, currency, balance, credit_limit, is_savings)
        VALUES (:id, :name, :account_type, :currency, :balance, :credit_limit, :is_savings)
        ''', data)
        
        self.conn.commit()
        return account.id
    
    def get_account(self, account_id):
        """Get account by ID"""
        from models import Account
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
        row = cursor.fetchone()
        
        if row:
            return Account.from_dict(dict(row))
        return None
    
    def get_all_accounts(self):
        """Get all accounts"""
        from models import Account
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts')
        rows = cursor.fetchall()
        
        return [Account.from_dict(dict(row)) for row in rows]
    
    def delete_account(self, account_id):
        """Delete an account by ID"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Transaction operations
    def save_transaction(self, transaction):
        """Save or update a transaction"""
        cursor = self.conn.cursor()
        data = transaction.to_dict()
        
        cursor.execute('''
        INSERT OR REPLACE INTO transactions 
        (id, date, amount, description, transaction_type, from_account_id, to_account_id, status, category)
        VALUES (:id, :date, :amount, :description, :transaction_type, :from_account_id, :to_account_id, :status, :category)
        ''', data)
        
        self.conn.commit()
        return transaction.id
    
    def get_transaction(self, transaction_id):
        """Get transaction by ID"""
        from models import Transaction
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        row = cursor.fetchone()
        
        if row:
            return Transaction.from_dict(dict(row))
        return None
    
    def get_all_transactions(self, status=None, account_id=None, transaction_type=None, start_date=None, end_date=None):
        """Get transactions with optional filtering"""
        from models import Transaction
        
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
        
        return [Transaction.from_dict(dict(row)) for row in rows]
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by ID"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Debt operations
    def save_debt(self, debt):
        """Save or update a debt"""
        cursor = self.conn.cursor()
        data = debt.to_dict()
        
        cursor.execute('''
        INSERT OR REPLACE INTO debts 
        (id, description, amount, due_date, is_receivable, linked_account_id, status, currency)
        VALUES (:id, :description, :amount, :due_date, :is_receivable, :linked_account_id, :status, :currency)
        ''', data)
        
        self.conn.commit()
        return debt.id
    
    def get_debt(self, debt_id):
        """Get debt by ID"""
        from models import Debt
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM debts WHERE id = ?', (debt_id,))
        row = cursor.fetchone()
        
        if row:
            return Debt.from_dict(dict(row))
        return None
    
    def get_all_debts(self, status=None, is_receivable=None):
        """Get debts with optional filtering"""
        from models import Debt
        
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
        
        return [Debt.from_dict(dict(row)) for row in rows]
    
    def delete_debt(self, debt_id):
        """Delete a debt by ID"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM debts WHERE id = ?', (debt_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Subscription operations
    def save_subscription(self, subscription):
        """Save or update a subscription"""
        cursor = self.conn.cursor()
        data = subscription.to_dict()
        
        cursor.execute('''
        INSERT OR REPLACE INTO subscriptions 
        (id, name, amount, frequency, next_payment_date, linked_account_id, status, currency, category)
        VALUES (:id, :name, :amount, :frequency, :next_payment_date, :linked_account_id, :status, :currency, :category)
        ''', data)
        
        self.conn.commit()
        return subscription.id
    
    def get_subscription(self, subscription_id):
        """Get subscription by ID"""
        from models import Subscription
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM subscriptions WHERE id = ?', (subscription_id,))
        row = cursor.fetchone()
        
        if row:
            return Subscription.from_dict(dict(row))
        return None
    
    def get_all_subscriptions(self, status=None):
        """Get subscriptions with optional filtering"""
        from models import Subscription
        
        cursor = self.conn.cursor()
        query = 'SELECT * FROM subscriptions'
        
        if status:
            query += ' WHERE status = ?'
            cursor.execute(query, (status,))
        else:
            cursor.execute(query)
            
        rows = cursor.fetchall()
        
        return [Subscription.from_dict(dict(row)) for row in rows]
    
    def delete_subscription(self, subscription_id):
        """Delete a subscription by ID"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM subscriptions WHERE id = ?', (subscription_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Utility methods
    def get_savings_stats(self, month=None, year=None):
        """Get savings statistics for current month or specified month/year"""
        current_date = datetime.now()
        month = month or current_date.month
        year = year or current_date.year
        
        # Get savings accounts
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM accounts WHERE is_savings = 1')
        savings_account_ids = [row[0] for row in cursor.fetchall()]
        
        if not savings_account_ids:
            return {"total_balance": 0, "month_contribution": 0}
        
        # Get total savings balance
        savings_accounts = []
        total_balance = 0
        for account_id in savings_account_ids:
            account = self.get_account(account_id)
            if account:
                savings_accounts.append(account)
                total_balance += account.balance
        
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
        
        return {
            "total_balance": total_balance,
            "month_contribution": month_contribution,
            "savings_accounts": savings_accounts
        }
    
    def get_liquidity(self):
        """Calculate current liquidity (sum of debit accounts and available credit)"""
        accounts = self.get_all_accounts()
        liquidity = 0
        
        for account in accounts:
            if account.account_type == "debit":
                # Add only non-negative balance for debit accounts
                liquidity += max(0, account.balance)
            elif account.account_type == "savings":
                liquidity += account.balance
            elif account.account_type == "credit":
                liquidity += account.get_available_balance()
        
        return liquidity
    
    def get_net_worth(self):
        """Calculate net worth considering accounts, debts, and subscriptions"""
        # Assets: All account balances + receivables
        assets = 0
        accounts = self.get_all_accounts()
        for account in accounts:
            assets += account.balance
        
        receivables = self.get_all_debts(status="pending", is_receivable=True)
        for debt in receivables:
            assets += debt.amount
        
        # Liabilities: Credit account negative balances + debts
        liabilities = 0
        for account in accounts:
            if account.account_type == "credit" and account.balance < 0:
                liabilities += abs(account.balance)
        
        payable_debts = self.get_all_debts(status="pending", is_receivable=False)
        for debt in payable_debts:
            liabilities += debt.amount
        
        # Upcoming subscription payments (next 30 days)
        today = date.today()
        thirty_days = today + timedelta(days=30)  # FIXED: Use timedelta for date arithmetic
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT SUM(amount) FROM subscriptions 
        WHERE status = 'active' AND next_payment_date <= ?
        ''', (thirty_days.isoformat(),))
        
        upcoming_subscriptions = cursor.fetchone()[0] or 0
        liabilities += upcoming_subscriptions
        
        return {
            "assets": assets,
            "liabilities": liabilities,
            "net_worth": assets - liabilities
        }
    
    def check_and_update_overdue_debts(self):
        """Update status of overdue debts"""
        today = date.today().isoformat()
        cursor = self.conn.cursor()
        
        cursor.execute('''
        UPDATE debts SET status = 'overdue'
        WHERE due_date < ? AND status = 'pending'
        ''', (today,))
        
        self.conn.commit()
        return cursor.rowcount
    
    def generate_pending_subscription_transactions(self):
        """Generate pending transactions for active subscriptions due today or in the past"""
        from models import Subscription
        
        today = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM subscriptions 
        WHERE status = 'active' AND next_payment_date <= ? 
        ''', (today,))
        
        rows = cursor.fetchall()
        subscriptions = [Subscription.from_dict(dict(row)) for row in rows]
        
        transactions_generated = []
        for subscription in subscriptions:
            transaction = subscription.generate_pending_transaction()
            if transaction:
                self.save_transaction(transaction)
                subscription.calculate_next_payment_date(True)
                self.save_subscription(subscription)
                transactions_generated.append(transaction)
        
        return transactions_generated