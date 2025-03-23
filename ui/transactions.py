# ui/transactions.py - Finance Tracker App/ui/transactions.py

import sys
import flet as ft
from datetime import datetime, date, timedelta
from models import Transaction

class TransactionsView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.categories = ["Food", "Transport", "Housing", "Entertainment", "Utilities", "Healthcare", "Shopping", "Other"]
        # Initialize all UI components that need to be referenced later
        self.transactions_list = ft.ListView(
            expand=False,
            spacing=10,
            padding=20,
            height=400,  # Fixed height to allow parent scrolling
        )
        self.transactions_summary = ft.Text("Total: 0.00 CHF")
        self.view = self.build()
        self.load_transactions()
    
    def build(self):
        """Build the transactions management UI"""
        # Filters section
        self.filter_start_date = ft.TextField(
            label="Start Date",
            hint_text="YYYY-MM-DD",
            width=150,
        )
        
        self.filter_end_date = ft.TextField(
            label="End Date",
            hint_text="YYYY-MM-DD",
            width=150,
        )
        
        self.filter_account_dropdown = ft.Dropdown(
            label="Account",
            width=200,
            options=[
                ft.dropdown.Option("all", "All Accounts"),
            ],
        )
        
        self.filter_type_dropdown = ft.Dropdown(
            label="Transaction Type",
            width=200,
            options=[
                ft.dropdown.Option("all", "All Types"),
                ft.dropdown.Option("transfer", "Transfers"),
                ft.dropdown.Option("spending", "Spending"),
                ft.dropdown.Option("income", "Income"),
                ft.dropdown.Option("adjustment", "Adjustments"),
            ],
            value="all",
        )
        
        self.filter_category_dropdown = ft.Dropdown(
            label="Category",
            width=200,
            options=[
                ft.dropdown.Option("all", "All Categories"),
            ] + [ft.dropdown.Option(category.lower(), category) for category in self.categories],
            value="all",
        )
        
        # Quick date filters
        self.filter_this_month_button = ft.TextButton(
            "This Month",
            on_click=self.filter_this_month,
        )
        
        self.filter_last_month_button = ft.TextButton(
            "Last Month",
            on_click=self.filter_last_month,
        )
        
        self.filter_last_3_months_button = ft.TextButton(
            "Last 3 Months",
            on_click=self.filter_last_3_months,
        )
        
        # Apply filter button
        self.apply_filter_button = ft.ElevatedButton(
            "Apply Filters",
            icon=ft.Icons.FILTER_ALT,
            on_click=self.apply_filters,
        )
        
        self.clear_filter_button = ft.OutlinedButton(
            "Clear Filters",
            on_click=self.clear_filters,
        )
        
        # New transaction form
        self.transaction_type_dropdown = ft.Dropdown(
            label="Transaction Type",
            width=200,
            options=[
                ft.dropdown.Option("spending", "Spending"),
                ft.dropdown.Option("income", "Income"),
            ],
            value="spending",
        )
        
        self.transaction_date_picker = ft.TextField(
            label="Date",
            hint_text="YYYY-MM-DD",
            width=200,
            value=date.today().isoformat(),
        )
        
        self.transaction_amount_field = ft.TextField(
            label="Amount",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.transaction_description_field = ft.TextField(
            label="Description",
            width=400,
        )
        
        self.transaction_category_dropdown = ft.Dropdown(
            label="Category",
            width=200,
            options=[ft.dropdown.Option(category.lower(), category) for category in self.categories],
            value="other",
        )
        
        self.transaction_account_dropdown = ft.Dropdown(
            label="Account",
            width=200,
            options=[],
        )
        
        # Form actions
        self.add_transaction_button = ft.ElevatedButton(
            "Add Transaction",
            icon=ft.Icons.ADD,
            on_click=self.add_transaction,
        )
        
        # Create the transaction history header
        transaction_history_header = ft.Container(
            content=ft.Row([
                ft.Text("Transaction History", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                self.transactions_summary,
            ]),
            margin=ft.margin.only(left=20, right=20, bottom=10),
        )
        
        # Add transaction form
        self.transaction_form = ft.Container(
            content=ft.Column([
                ft.Text("New Transaction", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.transaction_type_dropdown,
                    self.transaction_date_picker,
                    self.transaction_amount_field,
                ]),
                ft.Row([
                    self.transaction_description_field,
                    self.transaction_category_dropdown,
                ]),
                ft.Row([
                    self.transaction_account_dropdown,
                    self.add_transaction_button,
                ]),
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # Set up event handler for transaction type change
        self.transaction_type_dropdown.on_change = self.on_transaction_type_change
        
        # Return the main container
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Transactions", size=32, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=20, top=10),
                ),
                self.transaction_form,
                ft.Container(
                    content=ft.Column([
                        ft.Text("Filters", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.filter_start_date,
                            self.filter_end_date,
                            self.filter_this_month_button,
                            self.filter_last_month_button,
                            self.filter_last_3_months_button,
                        ]),
                        ft.Row([
                            self.filter_account_dropdown,
                            self.filter_type_dropdown,
                            self.filter_category_dropdown,
                            self.apply_filter_button,
                            self.clear_filter_button,
                        ]),
                    ]),
                    padding=20,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20),
                ),
                transaction_history_header,
                self.transactions_list,
            ]),
            padding=20,
        )
    
    # The rest of the methods remain unchanged...
    def on_transaction_type_change(self, e):
        """Update account dropdown label based on transaction type"""
        if self.transaction_type_dropdown.value == "spending":
            self.transaction_account_dropdown.label = "From Account"
        else:
            self.transaction_account_dropdown.label = "To Account"
        self.page.update()
    
    def load_accounts_into_dropdowns(self):
        """Load accounts into filter and form dropdowns"""
        accounts = self.db.get_all_accounts()
        
        # Reset dropdowns
        self.filter_account_dropdown.options = [ft.dropdown.Option("all", "All Accounts")]
        self.transaction_account_dropdown.options = []
        
        for account in accounts:
            # Add to filter dropdown
            self.filter_account_dropdown.options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
            
            # Add to transaction form dropdown
            self.transaction_account_dropdown.options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        if self.transaction_account_dropdown.options:
            self.transaction_account_dropdown.value = self.transaction_account_dropdown.options[0].key
        
        if self.filter_account_dropdown.options:
            self.filter_account_dropdown.value = "all"
    
    def load_transactions(self, filters=None):
        """Load transactions from database with optional filters"""
        # Load accounts first for references
        self.load_accounts_into_dropdowns()
        
        # Default filters
        if not filters:
            filters = {}
        
        # Get transactions based on filters
        transactions = self.db.get_all_transactions(
            status=filters.get("status", "completed"),
            account_id=filters.get("account_id"),
            transaction_type=filters.get("transaction_type"),
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date"),
        )
        
        # Filter by category if needed
        if filters.get("category") and filters["category"] != "all":
            transactions = [t for t in transactions if t.category == filters["category"]]
        
        # Get accounts for reference
        accounts = {account.id: account for account in self.db.get_all_accounts()}
        
        # Clear list
        self.transactions_list.controls = []
        
        # Calculate total for displayed transactions
        total = 0
        currency = "CHF"  # Default currency
        
        for transaction in transactions:
            # Create transaction card
            card = self._create_transaction_card(transaction, accounts)
            self.transactions_list.controls.append(card)
            
            # Update total
            if transaction.transaction_type == "income":
                total += transaction.amount
                if transaction.to_account_id and transaction.to_account_id in accounts:
                    currency = accounts[transaction.to_account_id].currency
            elif transaction.transaction_type == "spending":
                total -= transaction.amount
                if transaction.from_account_id and transaction.from_account_id in accounts:
                    currency = accounts[transaction.from_account_id].currency
            elif transaction.transaction_type == "adjustment":
                if transaction.to_account_id:  # Positive adjustment
                    total += transaction.amount
                    if transaction.to_account_id in accounts:
                        currency = accounts[transaction.to_account_id].currency
                elif transaction.from_account_id:  # Negative adjustment
                    total -= transaction.amount
                    if transaction.from_account_id in accounts:
                        currency = accounts[transaction.from_account_id].currency
        
        # Update summary text
        self.transactions_summary.value = f"Total: {total:.2f} {currency} ({len(transactions)} transactions)"
        
        self.page.update()
    
    def _create_transaction_card(self, transaction, accounts):
        """Create a card UI for a transaction"""
        # Determine icon and color based on transaction type
        icon_name = ft.Icons.PAYMENT
        icon_color = ft.colors.BLUE
        amount_color = ft.colors.BLACK
        
        if transaction.transaction_type == "spending":
            icon_name = ft.Icons.SHOPPING_CART
            icon_color = ft.colors.RED
            amount_color = ft.colors.RED
        elif transaction.transaction_type == "income":
            icon_name = ft.Icons.MONETIZATION_ON
            icon_color = ft.colors.GREEN
            amount_color = ft.colors.GREEN
        elif transaction.transaction_type == "transfer":
            icon_name = ft.Icons.SYNC_ALT
            icon_color = ft.colors.PURPLE
        elif transaction.transaction_type == "adjustment":
            icon_name = ft.Icons.SETTINGS
            icon_color = ft.colors.AMBER
            if transaction.to_account_id:  # Positive adjustment
                amount_color = ft.colors.GREEN
            elif transaction.from_account_id:  # Negative adjustment
                amount_color = ft.colors.RED
        
        # Get account names
        from_account_name = "N/A"
        to_account_name = "N/A"
        currency = "CHF"  # Default
        
        if transaction.from_account_id and transaction.from_account_id in accounts:
            from_account = accounts[transaction.from_account_id]
            from_account_name = from_account.name
            currency = from_account.currency
        
        if transaction.to_account_id and transaction.to_account_id in accounts:
            to_account = accounts[transaction.to_account_id]
            to_account_name = to_account.name
            currency = to_account.currency
        
        # Format amount text
        if transaction.transaction_type == "spending" or (transaction.transaction_type == "adjustment" and transaction.from_account_id):
            amount_text = f"-{transaction.amount:.2f} {currency}"
        elif transaction.transaction_type == "income" or (transaction.transaction_type == "adjustment" and transaction.to_account_id):
            amount_text = f"+{transaction.amount:.2f} {currency}"
        else:
            amount_text = f"{transaction.amount:.2f} {currency}"
        
        # Format date
        date_str = transaction.date.strftime("%Y-%m-%d")
        
        # Create account info text
        account_info = ""
        if transaction.transaction_type == "transfer":
            account_info = f"From: {from_account_name} → To: {to_account_name}"
        elif transaction.transaction_type == "spending":
            account_info = f"From: {from_account_name}"
        elif transaction.transaction_type == "income":
            account_info = f"To: {to_account_name}"
        elif transaction.transaction_type == "adjustment":
            if transaction.from_account_id:
                account_info = f"Account: {from_account_name}"
            elif transaction.to_account_id:
                account_info = f"Account: {to_account_name}"
        
        # Delete button
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Delete transaction",
            data=transaction.id,  # Store the ID as data on the button
            on_click=lambda e: self.delete_transaction(e.control.data),
        )
        
        # Create transaction card
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(icon_name, color=icon_color),
                        title=ft.Text(
                            transaction.description or transaction.transaction_type.capitalize(),
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(f"{date_str} • {transaction.transaction_type.capitalize()}"),
                        trailing=ft.Text(
                            amount_text,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=amount_color,
                        ),
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(account_info),
                            ft.Text(f"Category: {transaction.category or 'Not categorized'}"),
                        ]),
                        padding=ft.padding.symmetric(horizontal=15),
                    ),
                    ft.Container(
                        content=ft.Row([
                            delete_button,
                        ], alignment=ft.MainAxisAlignment.END),
                        padding=ft.padding.only(right=10, bottom=5),
                    ),
                ]),
                padding=10,
            ),
        )
    
    def add_transaction(self, e):
        """Add a new transaction"""
        try:
            # Validate and parse inputs
            amount = float(self.transaction_amount_field.value)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            transaction_type = self.transaction_type_dropdown.value
            account_id = self.transaction_account_dropdown.value
            
            # Parse date
            try:
                transaction_date = datetime.strptime(self.transaction_date_picker.value, "%Y-%m-%d").date()
            except ValueError:
                transaction_date = date.today()
            
            # Create transaction
            if transaction_type == "spending":
                transaction = Transaction(
                    date=transaction_date,
                    amount=amount,
                    description=self.transaction_description_field.value,
                    transaction_type="spending",
                    from_account_id=account_id,
                    to_account_id=None,
                    status="pending",
                    category=self.transaction_category_dropdown.value
                )
            else:  # income
                transaction = Transaction(
                    date=transaction_date,
                    amount=amount,
                    description=self.transaction_description_field.value,
                    transaction_type="income",
                    from_account_id=None,
                    to_account_id=account_id,
                    status="pending",
                    category=self.transaction_category_dropdown.value
                )
            
            # Save transaction
            self.db.save_transaction(transaction)
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    "Transaction added as pending. Go to Pending Transactions to approve it."
                )
            )
            self.page.snack_bar.open = True
            
            # Reset form
            self.transaction_amount_field.value = ""
            self.transaction_description_field.value = ""
            
            self.page.update()
        except ValueError as e:
            # Show error
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(str(e) or "Please enter valid transaction details")
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction after confirmation"""
        # Create confirmation dialog
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this transaction? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Delete", on_click=lambda e: confirm_delete(e, dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        def confirm_delete(e, dialog):
            self.db.delete_transaction(transaction_id)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Transaction deleted"))
            self.page.snack_bar.open = True
            # Reload with current filters
            self.load_transactions()
            self.page.close(dialog)
        
        # Open the dialog using the correct method
        self.page.open(dlg)
    
    def filter_this_month(self, e):
        """Set date filters to current month"""
        today = date.today()
        first_day = date(today.year, today.month, 1)
        
        self.filter_start_date.value = first_day.isoformat()
        self.filter_end_date.value = today.isoformat()
        self.page.update()
    
    def filter_last_month(self, e):
        """Set date filters to last month"""
        today = date.today()
        first_day_this_month = date(today.year, today.month, 1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = date(last_day_last_month.year, last_day_last_month.month, 1)
        
        self.filter_start_date.value = first_day_last_month.isoformat()
        self.filter_end_date.value = last_day_last_month.isoformat()
        self.page.update()
    
    def filter_last_3_months(self, e):
        """Set date filters to last 3 months"""
        today = date.today()
        three_months_ago = date(today.year, today.month - 2, 1) if today.month > 2 else date(today.year - 1, today.month + 10, 1)
        
        self.filter_start_date.value = three_months_ago.isoformat()
        self.filter_end_date.value = today.isoformat()
        self.page.update()
    
    def apply_filters(self, e):
        """Apply selected filters to transaction list"""
        filters = {
            "status": "completed"  # Only show completed transactions
        }
        
        # Add date filters if provided
        if self.filter_start_date.value:
            try:
                filters["start_date"] = datetime.strptime(self.filter_start_date.value, "%Y-%m-%d").date()
            except ValueError:
                pass
        
        if self.filter_end_date.value:
            try:
                filters["end_date"] = datetime.strptime(self.filter_end_date.value, "%Y-%m-%d").date()
            except ValueError:
                pass
        
        # Add account filter if selected
        if self.filter_account_dropdown.value and self.filter_account_dropdown.value != "all":
            filters["account_id"] = self.filter_account_dropdown.value
        
        # Add transaction type filter if selected
        if self.filter_type_dropdown.value and self.filter_type_dropdown.value != "all":
            filters["transaction_type"] = self.filter_type_dropdown.value
        
        # Add category filter if selected
        if self.filter_category_dropdown.value and self.filter_category_dropdown.value != "all":
            filters["category"] = self.filter_category_dropdown.value
        
        # Load transactions with filters
        self.load_transactions(filters)
    
    def clear_filters(self, e):
        """Clear all filters"""
        self.filter_start_date.value = ""
        self.filter_end_date.value = ""
        self.filter_account_dropdown.value = "all"
        self.filter_type_dropdown.value = "all"
        self.filter_category_dropdown.value = "all"
        
        # Load all transactions
        self.load_transactions()