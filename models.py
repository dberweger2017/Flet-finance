# models.py - Finance Tracker App/models.py

import sqlite3
import uuid
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json
from decimal import Decimal


class Account:
    def __init__(self, id=None, name="", account_type="debit", currency="CHF", 
                 balance=0.0, credit_limit=0.0, is_savings=False):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.account_type = account_type  # "debit", "credit", "savings"
        self.currency = currency  # "CHF", "EUR"
        self.balance = float(balance)
        self.credit_limit = float(credit_limit)
        self.is_savings = is_savings
        
    def deposit(self, amount):
        """Add funds to the account"""
        self.balance += float(amount)
        
    def withdraw(self, amount):
        """Remove funds from the account if sufficient balance or credit limit"""
        amount = float(amount)
        if self.account_type == "credit":
            if self.balance - amount >= -self.credit_limit:
                self.balance -= amount
                return True
            return False
        elif self.account_type == "savings":
            # Savings accounts still require sufficient balance
            if self.balance >= amount:
                self.balance -= amount
                return True
            return False
        else:
            # Debit accounts can go negative (overdraft)
            self.balance -= amount
            return True
            
    def get_available_balance(self):
        """Return the available balance considering credit limits"""
        if self.account_type == "credit":
            return self.balance + self.credit_limit
        elif self.account_type == "debit" and self.balance < 0:
            # For debit accounts with negative balance, available balance is 0
            return 0
        return self.balance
        
    def reconcile_balance(self, reported_balance):
        """Creates an adjustment transaction to match reported balance"""
        reported_balance = float(reported_balance)
        adjustment = reported_balance - self.balance
        self.balance = reported_balance
        return adjustment  # Will be used to create an adjustment transaction

    def to_dict(self):
        """Convert account to dictionary for database storage"""
        return {
            "id": self.id,
            "name": self.name,
            "account_type": self.account_type,
            "currency": self.currency,
            "balance": self.balance,
            "credit_limit": self.credit_limit,
            "is_savings": 1 if self.is_savings else 0
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create account from dictionary data"""
        return cls(
            id=data["id"],
            name=data["name"],
            account_type=data["account_type"],
            currency=data["currency"],
            balance=data["balance"],
            credit_limit=data["credit_limit"],
            is_savings=bool(data["is_savings"])
        )


class Transaction:
    def __init__(self, id=None, date=None, amount=0.0, description="", transaction_type="", 
                 from_account_id=None, to_account_id=None, status="pending", category=None):
        self.id = id or str(uuid.uuid4())
        self.date = date or datetime.now().date()
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").date()
        self.amount = float(amount)
        self.description = description
        self.transaction_type = transaction_type  # "transfer", "spending", "income", "adjustment"
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.status = status  # "pending", "completed", "canceled"
        self.category = category  # Optional categorization
        
    def execute(self, accounts):
        """Execute transaction and update account balances"""
        if self.status != "pending":
            return False
            
        if self.transaction_type == "transfer" and self.from_account_id and self.to_account_id:
            from_account = accounts.get(self.from_account_id)
            to_account = accounts.get(self.to_account_id)
            
            if from_account and to_account and from_account.withdraw(self.amount):
                to_account.deposit(self.amount)
                self.status = "completed"
                return True
                
        elif self.transaction_type == "spending" and self.from_account_id:
            from_account = accounts.get(self.from_account_id)
            if from_account and from_account.withdraw(self.amount):
                self.status = "completed"
                return True
                
        elif self.transaction_type == "income" and self.to_account_id:
            to_account = accounts.get(self.to_account_id)
            if to_account:
                to_account.deposit(self.amount)
                self.status = "completed"
                return True
            
        elif self.transaction_type == "adjustment" and (self.from_account_id or self.to_account_id):
            # Adjustment transactions are already applied through reconcile_balance
            self.status = "completed"
            return True
            
        return False

    def to_dict(self):
        """Convert transaction to dictionary for database storage"""
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "amount": self.amount,
            "description": self.description,
            "transaction_type": self.transaction_type,
            "from_account_id": self.from_account_id,
            "to_account_id": self.to_account_id,
            "status": self.status,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create transaction from dictionary data"""
        return cls(
            id=data["id"],
            date=data["date"],
            amount=data["amount"],
            description=data["description"],
            transaction_type=data["transaction_type"],
            from_account_id=data["from_account_id"],
            to_account_id=data["to_account_id"],
            status=data["status"],
            category=data["category"]
        )


class Debt:
    def __init__(self, id=None, description="", amount=0.0, due_date=None, is_receivable=False, 
                 linked_account_id=None, status="pending", currency="CHF", payment_history=None):
        self.id = id or str(uuid.uuid4())
        self.description = description
        self.amount = float(amount)
        self.due_date = due_date or datetime.now().date()
        if isinstance(self.due_date, str):
            self.due_date = datetime.strptime(self.due_date, "%Y-%m-%d").date()
        self.is_receivable = is_receivable
        self.linked_account_id = linked_account_id
        self.status = status  # "pending", "partial", "paid", "overdue"
        self.currency = currency
        # Initialize payment history as an empty list if not provided
        self.payment_history = payment_history or []
        
    def get_paid_amount(self):
        """Return the total amount paid so far"""
        if not self.payment_history:
            return 0.0
        return sum(payment["amount"] for payment in self.payment_history)
    
    def get_remaining_amount(self):
        """Return the remaining amount to be paid"""
        return self.amount - self.get_paid_amount()
        
    def make_partial_payment(self, amount, transaction_date=None, notes=""):
        """Make a partial payment and create corresponding transaction"""
        if self.status == "paid":
            return None
            
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
            
        remaining = self.get_remaining_amount()
        if amount > remaining:
            raise ValueError(f"Payment amount ({amount}) exceeds remaining amount ({remaining})")
            
        transaction_date = transaction_date or datetime.now().date()
        
        # Create transaction for partial payment
        if self.is_receivable and self.linked_account_id:
            # Create income transaction for receiving partial payment
            transaction = Transaction(
                date=transaction_date,
                amount=amount,
                description=f"Received partial payment for: {self.description}",
                transaction_type="income",
                to_account_id=self.linked_account_id,
                status="pending"
            )
        elif not self.is_receivable and self.linked_account_id:
            # Create spending transaction for making partial payment
            transaction = Transaction(
                date=transaction_date,
                amount=amount,
                description=f"Made partial payment for: {self.description}",
                transaction_type="spending",
                from_account_id=self.linked_account_id,
                status="pending"
            )
        else:
            return None
            
        # Add to payment history
        payment_record = {
            "date": transaction_date.isoformat(),
            "amount": amount,
            "notes": notes
        }
        self.payment_history.append(payment_record)
        
        # Update debt status
        paid_amount = self.get_paid_amount()
        if abs(paid_amount - self.amount) < 0.01:  # Account for floating point precision
            self.status = "paid"
        else:
            self.status = "partial"
            
        return transaction

    def mark_as_paid(self, transaction_date=None):
        """Creates a transaction to record full debt payment"""
        if self.status == "paid":
            return None
            
        transaction_date = transaction_date or datetime.now().date()
        remaining = self.get_remaining_amount()
        
        if remaining <= 0:
            # Already fully paid through partial payments
            self.status = "paid"
            return None
            
        # Create transaction for remaining amount
        if self.is_receivable and self.linked_account_id:
            # Create income transaction
            transaction = Transaction(
                date=transaction_date,
                amount=remaining,
                description=f"Received final payment for: {self.description}",
                transaction_type="income",
                to_account_id=self.linked_account_id,
                status="pending"
            )
        elif not self.is_receivable and self.linked_account_id:
            # Create spending transaction
            transaction = Transaction(
                date=transaction_date,
                amount=remaining,
                description=f"Paid remaining balance for: {self.description}",
                transaction_type="spending",
                from_account_id=self.linked_account_id,
                status="pending"
            )
        else:
            return None
            
        # Add to payment history
        payment_record = {
            "date": transaction_date.isoformat(),
            "amount": remaining,
            "notes": "Final payment"
        }
        self.payment_history.append(payment_record)
        
        self.status = "paid"
        return transaction

    def to_dict(self):
        """Convert debt to dictionary for database storage"""
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "due_date": self.due_date.isoformat(),
            "is_receivable": 1 if self.is_receivable else 0,
            "linked_account_id": self.linked_account_id,
            "status": self.status,
            "currency": self.currency,
            "payment_history": json.dumps(self.payment_history)
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create debt from dictionary data"""
        payment_history = []
        if "payment_history" in data and data["payment_history"]:
            try:
                payment_history = json.loads(data["payment_history"])
            except (json.JSONDecodeError, TypeError):
                payment_history = []
                
        return cls(
            id=data["id"],
            description=data["description"],
            amount=data["amount"],
            due_date=data["due_date"],
            is_receivable=bool(data["is_receivable"]),
            linked_account_id=data["linked_account_id"],
            status=data["status"],
            currency=data["currency"],
            payment_history=payment_history
        )


class Subscription:
    def __init__(self, id=None, name="", amount=0.0, frequency="monthly", next_payment_date=None, 
                 linked_account_id=None, status="active", currency="CHF", category=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.amount = float(amount)
        self.frequency = frequency  # "monthly", "quarterly", "yearly"
        self.next_payment_date = next_payment_date or datetime.now().date()
        if isinstance(self.next_payment_date, str):
            self.next_payment_date = datetime.strptime(self.next_payment_date, "%Y-%m-%d").date()
        self.linked_account_id = linked_account_id
        self.status = status  # "active", "paused", "canceled"
        self.currency = currency
        self.category = category
        
    def generate_pending_transaction(self):
        """Creates a pending transaction for this subscription"""
        if self.status != "active" or not self.linked_account_id:
            return None
            
        transaction = Transaction(
            date=self.next_payment_date,
            amount=self.amount,
            description=f"Subscription: {self.name}",
            transaction_type="spending",
            from_account_id=self.linked_account_id,
            status="pending",
            category=self.category
        )
        
        return transaction
        
    def calculate_next_payment_date(self, after_payment=True):
        """Updates the next payment date based on frequency"""
        if not after_payment:
            return self.next_payment_date
            
        current_date = self.next_payment_date
        if self.frequency == "monthly":
            self.next_payment_date = current_date + relativedelta(months=1)
        elif self.frequency == "quarterly":
            self.next_payment_date = current_date + relativedelta(months=3)
        elif self.frequency == "yearly":
            self.next_payment_date = current_date + relativedelta(years=1)
        else:
            # Default to monthly
            self.next_payment_date = current_date + relativedelta(months=1)
            
        return self.next_payment_date

    def to_dict(self):
        """Convert subscription to dictionary for database storage"""
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "frequency": self.frequency,
            "next_payment_date": self.next_payment_date.isoformat(),
            "linked_account_id": self.linked_account_id,
            "status": self.status,
            "currency": self.currency,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create subscription from dictionary data"""
        return cls(
            id=data["id"],
            name=data["name"],
            amount=data["amount"],
            frequency=data["frequency"],
            next_payment_date=data["next_payment_date"],
            linked_account_id=data["linked_account_id"],
            status=data["status"],
            currency=data["currency"],
            category=data["category"]
        )