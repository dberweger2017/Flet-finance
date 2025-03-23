# ui/accounts.py - Finance Tracker App/ui/accounts.py

import flet as ft
from datetime import datetime
from models import Account, Transaction
import sys

class AccountsView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.accounts = []
        self.view = self.build()
        self.load_accounts()
    
    def build(self):
        """Build the accounts management UI"""
        # Accounts list
        self.accounts_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
        )
        
        # Form for adding/editing accounts
        self.name_field = ft.TextField(
            label="Account Name", 
            hint_text="e.g. Checking Account, Credit Card",
            width=300,
        )
        
        self.account_type_dropdown = ft.Dropdown(
            label="Account Type",
            width=300,
            options=[
                ft.dropdown.Option("debit", "Debit"),
                ft.dropdown.Option("credit", "Credit"),
                ft.dropdown.Option("savings", "Savings"),
            ],
            value="debit",
        )
        
        self.currency_dropdown = ft.Dropdown(
            label="Currency",
            width=300,
            options=[
                ft.dropdown.Option("CHF", "Swiss Franc (CHF)"),
                ft.dropdown.Option("EUR", "Euro (EUR)"),
                ft.dropdown.Option("USD", "US Dollar (USD)"),
            ],
            value="CHF",
        )
        
        self.balance_field = ft.TextField(
            label="Initial Balance",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0.00",
        )
        
        self.credit_limit_field = ft.TextField(
            label="Credit Limit (for credit accounts)",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0.00",
            disabled=True,
        )
        
        self.is_savings_checkbox = ft.Checkbox(
            label="This is a savings account",
            value=False,
        )
        
        # Form actions
        self.save_button = ft.ElevatedButton(
            "Add Account",
            icon=ft.Icons.SAVE,
            on_click=self.save_account,
        )
        
        self.cancel_button = ft.OutlinedButton(
            "Cancel",
            on_click=self.cancel_edit,
        )
        
        # Account form container
        self.account_form = ft.Container(
            content=ft.Column([
                ft.Text("Add New Account", size=20, weight=ft.FontWeight.BOLD),
                self.name_field,
                self.account_type_dropdown,
                self.currency_dropdown,
                self.balance_field,
                self.credit_limit_field,
                self.is_savings_checkbox,
                ft.Row([
                    self.save_button,
                    self.cancel_button,
                ]),
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # Reconciliation dialog
        self.reconcile_account_id = None
        self.reconcile_field = ft.TextField(
            label="Current account balance from bank statement",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.reconcile_dialog = ft.AlertDialog(
            title=ft.Text("Reconcile Account Balance"),
            content=ft.Column([
                ft.Text("Enter the current balance from your bank statement to reconcile this account:"),
                self.reconcile_field,
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_reconcile_dialog),
                ft.TextButton("Reconcile", on_click=self.perform_reconciliation),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Transfer dialog
        self.transfer_amount_field = ft.TextField(
            label="Transfer Amount",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.from_account_dropdown = ft.Dropdown(
            label="From Account",
            options=[],
        )
        
        self.to_account_dropdown = ft.Dropdown(
            label="To Account",
            options=[],
        )
        
        self.transfer_description_field = ft.TextField(
            label="Description (optional)",
        )
        
        # Setup event handler for account type changes
        self.account_type_dropdown.on_change = self.on_account_type_change
        
        # Transfer button
        transfer_button = ft.ElevatedButton(
            "Transfer Money",
            icon=ft.Icons.SYNC_ALT,
            on_click=self.show_transfer_dialog,
        )
        
        # Return the main container
        container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("Accounts", size=32, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        transfer_button,
                    ]),
                    margin=ft.margin.only(bottom=20, top=10),
                ),
                self.account_form,
                ft.Text("Your Accounts", size=20, weight=ft.FontWeight.BOLD),
                self.accounts_list,
            ]),
            padding=20,
        )
        
        # Check dialog initialization
        self.check_dialog_initialization()
        
        return container
    
    def on_account_type_change(self, e):
        """Enable/disable credit limit field based on account type"""
        if self.account_type_dropdown.value == "credit":
            self.credit_limit_field.disabled = False
        else:
            self.credit_limit_field.disabled = True
            self.credit_limit_field.value = "0.00"
        self.page.update()
    
    def load_accounts(self):
        """Load accounts from database and update UI"""
        self.accounts = self.db.get_all_accounts()
        self.accounts_list.controls = []
        
        # Also update the transfer dialog dropdowns
        self.from_account_dropdown.options = []
        self.to_account_dropdown.options = []
        
        for account in self.accounts:
            # Create account card
            card = self._create_account_card(account)
            self.accounts_list.controls.append(card)
            
            # Add to dropdown options
            self.from_account_dropdown.options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
            self.to_account_dropdown.options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        self.page.update()
    
    def _create_account_card(self, account):
        """Create a card UI for an account"""
        # Determine icon and color based on account type
        icon_name = ft.Icons.ACCOUNT_BALANCE
        icon_color = ft.colors.BLUE
        
        if account.account_type == "credit":
            icon_name = ft.Icons.CREDIT_CARD
            icon_color = ft.colors.PURPLE
        elif account.account_type == "savings":
            icon_name = ft.Icons.SAVINGS
            icon_color = ft.colors.GREEN
        
        # Determine balance color
        balance_color = ft.colors.BLACK
        if account.balance < 0:
            balance_color = ft.colors.RED
        
        # Create action buttons
        edit_button = ft.IconButton(
            icon=ft.Icons.EDIT,
            tooltip="Edit account",
            on_click=lambda e, aid=account.id: self.edit_account(aid),
        )
        
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Delete account",
            on_click=lambda e, aid=account.id: self.delete_account(aid),
        )
        
        reconcile_button = ft.IconButton(
            icon=ft.Icons.BALANCE,
            tooltip="Reconcile balance",
            on_click=lambda e, aid=account.id: self.reconcile_account(aid),
        )
        
        # Create account card
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(icon_name, color=icon_color),
                        title=ft.Text(
                            account.name, 
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(
                            f"{account.account_type.capitalize()} • {account.currency}"
                        ),
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Current Balance:", weight=ft.FontWeight.BOLD),
                                ft.Container(width=10),
                                ft.Text(
                                    f"{account.balance:.2f} {account.currency}",
                                    color=balance_color,
                                    weight=ft.FontWeight.BOLD,
                                    size=16,
                                ),
                            ]),
                            ft.Row([
                                ft.Text("Available Balance:", weight=ft.FontWeight.BOLD),
                                ft.Container(width=10),
                                ft.Text(
                                    f"{account.get_available_balance():.2f} {account.currency}",
                                ),
                            ]) if account.account_type == "credit" else ft.Container(),
                            ft.Row([
                                ft.Text("Credit Limit:", weight=ft.FontWeight.BOLD),
                                ft.Container(width=10),
                                ft.Text(
                                    f"{account.credit_limit:.2f} {account.currency}",
                                ),
                            ]) if account.account_type == "credit" else ft.Container(),
                        ]),
                        padding=ft.padding.symmetric(horizontal=15),
                    ),
                    ft.Container(
                        content=ft.Row([
                            edit_button,
                            delete_button,
                            reconcile_button,
                        ], alignment=ft.MainAxisAlignment.END),
                        padding=ft.padding.only(right=10, bottom=5),
                    ),
                ]),
                padding=10,
            ),
        )
    
    def save_account(self, e):
        """Save new account or update existing one"""
        try:
            balance = float(self.balance_field.value)
            credit_limit = float(self.credit_limit_field.value) if not self.credit_limit_field.disabled else 0.0
            
            # Validate inputs
            if not self.name_field.value:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Please enter account name"))
                self.page.snack_bar.open = True
                self.page.update()
                return
        except ValueError:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Please enter valid numbers for balance and credit limit"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Create or update account
        if hasattr(self, 'editing_account_id') and self.editing_account_id:
            # Update existing account
            account = self.db.get_account(self.editing_account_id)
            old_balance = account.balance
            
            account.name = self.name_field.value
            account.account_type = self.account_type_dropdown.value
            account.currency = self.currency_dropdown.value
            account.credit_limit = credit_limit
            account.is_savings = self.is_savings_checkbox.value
            
            # If balance changed, create an adjustment transaction
            if balance != old_balance:
                adjustment = balance - old_balance
                account.balance = balance
                
                # Create adjustment transaction
                transaction = Transaction(
                    date=datetime.now().date(),
                    amount=abs(adjustment),
                    description="Account balance adjustment",
                    transaction_type="adjustment",
                    from_account_id=account.id if adjustment < 0 else None,
                    to_account_id=account.id if adjustment > 0 else None,
                    status="completed"
                )
                self.db.save_transaction(transaction)
            
            self.db.save_account(account)
            success_msg = "Account updated successfully"
            
            # Clear editing state
            delattr(self, 'editing_account_id')
            self.save_button.text = "Add Account"
        else:
            # Create new account
            account = Account(
                name=self.name_field.value,
                account_type=self.account_type_dropdown.value,
                currency=self.currency_dropdown.value,
                balance=balance,
                credit_limit=credit_limit,
                is_savings=self.is_savings_checkbox.value
            )
            
            self.db.save_account(account)
            success_msg = "Account added successfully"
        
        # Reset form
        self.name_field.value = ""
        self.balance_field.value = "0.00"
        self.credit_limit_field.value = "0.00"
        self.account_type_dropdown.value = "debit"
        self.currency_dropdown.value = "CHF"
        self.is_savings_checkbox.value = False
        self.credit_limit_field.disabled = True
        
        # Show success message
        self.page.snack_bar = ft.SnackBar(content=ft.Text(success_msg))
        self.page.snack_bar.open = True
        
        # Reload accounts list
        self.load_accounts()
    
    def edit_account(self, account_id):
        """Load account data into form for editing"""
        account = self.db.get_account(account_id)
        if not account:
            return
        
        self.editing_account_id = account_id
        self.name_field.value = account.name
        self.account_type_dropdown.value = account.account_type
        self.currency_dropdown.value = account.currency
        self.balance_field.value = str(account.balance)
        self.credit_limit_field.value = str(account.credit_limit)
        self.is_savings_checkbox.value = account.is_savings
        
        # Enable/disable credit limit field
        self.credit_limit_field.disabled = account.account_type != "credit"
        
        # Update button text
        self.save_button.text = "Update Account"
        
        self.page.update()
    
    def cancel_edit(self, e):
        """Cancel editing and reset form"""
        self.name_field.value = ""
        self.balance_field.value = "0.00"
        self.credit_limit_field.value = "0.00"
        self.account_type_dropdown.value = "debit"
        self.currency_dropdown.value = "CHF"
        self.is_savings_checkbox.value = False
        self.credit_limit_field.disabled = True
        
        # Clear editing state
        if hasattr(self, 'editing_account_id'):
            delattr(self, 'editing_account_id')
        
        self.save_button.text = "Add Account"
        self.page.update()
    
    def delete_account(self, account_id):
        """Delete an account after confirmation"""
        # Create confirmation dialog
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this account? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Delete", on_click=lambda e: confirm_delete(e, dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        def confirm_delete(e, dialog):
            self.db.delete_account(account_id)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Account deleted"))
            self.page.snack_bar.open = True
            self.load_accounts()
            self.page.close(dialog)
        
        # Open the dialog using the correct method
        self.page.open(dlg)
    
    def reconcile_account(self, account_id):
        """Show dialog to reconcile account balance"""
        account = self.db.get_account(account_id)
        if not account:
            return
        
        # Set the account ID and current balance
        self.reconcile_account_id = account_id
        self.reconcile_field.value = str(account.balance)
        
        # Show dialog
        self.page.dialog = self.reconcile_dialog
        self.page.dialog.open = True
        self.page.update()
    
    def close_reconcile_dialog(self, e):
        """Close the reconciliation dialog"""
        self.page.dialog.open = False
        self.page.update()
    
    def perform_reconciliation(self, e):
        """Perform account reconciliation"""
        if not self.reconcile_account_id:
            return
        
        try:
            reported_balance = float(self.reconcile_field.value)
            
            # Get account and perform reconciliation
            account = self.db.get_account(self.reconcile_account_id)
            if not account:
                return
            
            adjustment = account.reconcile_balance(reported_balance)
            
            # Create transaction for the adjustment
            if adjustment != 0:
                transaction = Transaction(
                    date=datetime.now().date(),
                    amount=abs(adjustment),
                    description="Balance reconciliation adjustment",
                    transaction_type="adjustment",
                    from_account_id=account.id if adjustment < 0 else None,
                    to_account_id=account.id if adjustment > 0 else None,
                    status="completed"
                )
                self.db.save_transaction(transaction)
            
            # Save updated account
            self.db.save_account(account)
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Account balance reconciled successfully"))
            self.page.snack_bar.open = True
            
            # Close dialog and reload accounts
            self.page.dialog.open = False
            self.load_accounts()
        except ValueError:
            # Show error for invalid input
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Please enter a valid balance amount"))
            self.page.snack_bar.open = True
            self.page.update()
    
    def show_transfer_dialog(self, e):
        """Show dialog to transfer money between accounts"""
        print("Transfer button clicked!", file=sys.stderr)
        
        # Reset fields
        self.transfer_amount_field.value = ""
        self.transfer_description_field.value = ""
        
        # Make sure we have populated the account dropdowns
        if not self.from_account_dropdown.options or not self.to_account_dropdown.options:
            print("Reloading accounts to populate dropdowns", file=sys.stderr)
            self.load_accounts()  # This will populate the dropdown options
        
        # Set default values for dropdowns if options exist
        if self.from_account_dropdown.options:
            self.from_account_dropdown.value = self.from_account_dropdown.options[0].key
            print(f"Set from_account_dropdown value to: {self.from_account_dropdown.value}", file=sys.stderr)
        
        if len(self.to_account_dropdown.options) > 1:
            # Set to second account if available (to avoid same account transfer)
            self.to_account_dropdown.value = self.to_account_dropdown.options[1].key
            print(f"Set to_account_dropdown value to second option: {self.to_account_dropdown.value}", file=sys.stderr)
        elif self.to_account_dropdown.options:
            self.to_account_dropdown.value = self.to_account_dropdown.options[0].key
            print(f"Set to_account_dropdown value to first option: {self.to_account_dropdown.value}", file=sys.stderr)
        
        # Create a new dialog each time
        transfer_dialog = ft.AlertDialog(
            title=ft.Text("Transfer Between Accounts"),
            content=ft.Column([
                self.transfer_amount_field,
                self.from_account_dropdown,
                self.to_account_dropdown,
                self.transfer_description_field,
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_transfer_dialog),
                ft.TextButton("Transfer", on_click=self.perform_transfer),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        print("About to open dialog", file=sys.stderr)
        self.page.dialog = transfer_dialog
        self.page.dialog.open = True
        self.page.update()
        print("Dialog should be visible now", file=sys.stderr)
    
    def close_transfer_dialog(self, e):
        """Close the transfer dialog"""
        self.page.dialog.open = False
        self.page.update()
    
    def perform_transfer(self, e):
        """Execute a transfer between accounts"""
        try:
            amount = float(self.transfer_amount_field.value)
            from_account_id = self.from_account_dropdown.value
            to_account_id = self.to_account_dropdown.value
            description = self.transfer_description_field.value or "Transfer between accounts"
            
            # Validate inputs
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            if from_account_id == to_account_id:
                raise ValueError("Cannot transfer to the same account")
            
            # Create transaction
            transaction = Transaction(
                date=datetime.now().date(),
                amount=amount,
                description=description,
                transaction_type="transfer",
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                status="pending"
            )
            
            # Save transaction
            self.db.save_transaction(transaction)
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Transfer created as a pending transaction. Go to Pending Transactions to approve it.")
            )
            self.page.snack_bar.open = True
            
            # Close dialog
            self.page.dialog.open = False
            self.page.update()
        except ValueError as e:
            # Show error
            self.page.snack_bar = ft.SnackBar(content=ft.Text(str(e) or "Please enter valid transfer details"))
            self.page.snack_bar.open = True
            self.page.update()

    def check_dialog_initialization(self):
        """Debug function to check if dialogs are properly initialized"""
        print("Checking dialog initialization:", file=sys.stderr)
        print(f"Has transfer_dialog attribute: {hasattr(self, 'transfer_dialog')}", file=sys.stderr)
        print(f"Has transfer_amount_field attribute: {hasattr(self, 'transfer_amount_field')}", file=sys.stderr)
        print(f"Has from_account_dropdown attribute: {hasattr(self, 'from_account_dropdown')}", file=sys.stderr)
        print(f"Has to_account_dropdown attribute: {hasattr(self, 'to_account_dropdown')}", file=sys.stderr)
        
        # Check if the button is correctly configured
        if hasattr(self, 'view') and isinstance(self.view, ft.Container):
            content = self.view.content
            if isinstance(content, ft.Column) and len(content.controls) > 0:
                header_container = content.controls[0]
                if isinstance(header_container, ft.Container) and isinstance(header_container.content, ft.Row):
                    row = header_container.content
                    for control in row.controls:
                        if isinstance(control, ft.ElevatedButton) and control.text == "Transfer Money":
                            print("Found Transfer Money button", file=sys.stderr)
                            print(f"Button on_click: {control.on_click}", file=sys.stderr)
        else:
            print("View structure not as expected", file=sys.stderr)