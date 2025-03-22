# ui/pending.py - Finance Tracker App/ui/pending.py

import flet as ft
from datetime import datetime

class PendingView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.view = self.build()
        self.load_pending_transactions()
    
    def build(self):
        """Build the pending transactions UI"""
        # Pending transactions list
        self.pending_list = ft.ListView(
            expand=False,
            spacing=10,
            padding=20,
            height=400,  # Fixed height to allow parent scrolling
        )
        
        # Empty state message
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=64, color=ft.colors.GREY_400),
                ft.Text("No pending transactions", size=20, color=ft.colors.GREY_600),
                ft.Text("All your transactions have been processed.", color=ft.colors.GREY_600),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True,
        )
        
        # Return the main container
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("Pending Transactions", size=32, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Process Selected",
                            icon=ft.Icons.CHECK,
                            on_click=self.process_selected,
                            disabled=True,
                        ),
                        ft.OutlinedButton(
                            "Refresh",
                            icon=ft.Icons.REFRESH,
                            on_click=self.refresh_pending,
                        ),
                    ]),
                    margin=ft.margin.only(bottom=20, top=10),
                ),
                ft.Text(
                    "Review and process transactions that are waiting for your approval.",
                    size=16,
                ),
                ft.Container(height=20),
                self.pending_list,
                self.empty_state,
            ]),
            padding=20,
        )
    
    def load_pending_transactions(self):
        """Load pending transactions from database"""
        pending_transactions = self.db.get_all_transactions(status="pending")
        
        # Get accounts for reference
        accounts = {account.id: account for account in self.db.get_all_accounts()}
        
        # Clear list
        self.pending_list.controls = []
        self.selected_transactions = {}
        
        # Show empty state if no pending transactions
        if not pending_transactions:
            self.empty_state.visible = True
        else:
            self.empty_state.visible = False
            
            for transaction in pending_transactions:
                # Create transaction card
                card = self._create_pending_card(transaction, accounts)
                self.pending_list.controls.append(card)
        
        self.page.update()
    
    def _create_pending_card(self, transaction, accounts):
        """Create a card UI for a pending transaction with horizontal text layout"""
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
        if transaction.transaction_type == "spending":
            amount_text = f"-{transaction.amount:.2f} {currency}"
        elif transaction.transaction_type == "income":
            amount_text = f"+{transaction.amount:.2f} {currency}"
        else:
            amount_text = f"{transaction.amount:.2f} {currency}"
        
        # Format date
        date_str = transaction.date.strftime("%Y-%m-%d")
        
        # Create account info text - FIX THE LAYOUT HERE TO BE HORIZONTAL
        account_info = ""
        if transaction.transaction_type == "transfer":
            account_info = f"From: {from_account_name} → To: {to_account_name}"
        elif transaction.transaction_type == "spending":
            account_info = f"From: {from_account_name}"
        elif transaction.transaction_type == "income":
            account_info = f"To: {to_account_name}"
        
        # Create the checkbox for selecting transactions
        checkbox = ft.Checkbox(
            value=False,
            on_change=lambda e, tid=transaction.id: self.on_transaction_selected(e, tid),
        )
        
        # Action buttons
        approve_button = ft.ElevatedButton(
            "Approve",
            icon=ft.Icons.CHECK,
            on_click=lambda e, tid=transaction.id: self.approve_transaction(tid),
        )
        
        delete_button = ft.OutlinedButton(
            "Delete",
            icon=ft.Icons.DELETE,
            on_click=lambda e, tid=transaction.id: self.delete_transaction(tid),
        )
        
        edit_button = ft.TextButton(
            "Edit",
            icon=ft.Icons.EDIT,
            on_click=lambda e, tid=transaction.id: self.edit_transaction(tid),
        )
        
        # Create transaction card with fixed layout - WRAPPED IN PROPER CONTAINER TO ENSURE HORIZONTAL TEXT
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Row([checkbox, ft.Icon(icon_name, color=icon_color)]),
                        title=ft.Text(
                            transaction.description or transaction.transaction_type.capitalize(),
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(f"{date_str} • {transaction.transaction_type.capitalize()}"),
                        trailing=ft.Container(
                            content=ft.Text(
                                amount_text,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=amount_color,
                            ),
                            width=150,  # Fixed width to prevent vertical text
                        ),
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Text(account_info),
                                width=350,  # Ensure sufficient width for the text
                            ),
                            ft.Text(f"Category: {transaction.category or 'Not categorized'}"),
                        ]),
                        padding=ft.padding.symmetric(horizontal=15),
                    ),
                    ft.Container(
                        content=ft.Row([
                            approve_button,
                            edit_button,
                            delete_button,
                        ], alignment=ft.MainAxisAlignment.END),
                        padding=ft.padding.only(right=10, bottom=10, top=10),
                    ),
                ]),
                padding=10,
                width=600,  # Ensure the container has sufficient width
            ),
        )
    
    def on_transaction_selected(self, e, transaction_id):
        """Handle transaction selection"""
        if e.control.value:
            self.selected_transactions[transaction_id] = True
        else:
            if transaction_id in self.selected_transactions:
                del self.selected_transactions[transaction_id]
        
        # Enable/disable process selected button
        process_button = self.view.content.controls[0].content.controls[2]
        process_button.disabled = len(self.selected_transactions) == 0
        
        self.page.update()
    
    def process_selected(self, e):
        """Process all selected transactions"""
        if not self.selected_transactions:
            return
        
        success_count = 0
        fail_count = 0
        
        for transaction_id in self.selected_transactions:
            transaction = self.db.get_transaction(transaction_id)
            if transaction:
                # Get accounts
                accounts = {account.id: account for account in self.db.get_all_accounts()}
                
                # Execute transaction
                if transaction.execute(accounts):
                    # Update accounts
                    if transaction.from_account_id and transaction.from_account_id in accounts:
                        self.db.save_account(accounts[transaction.from_account_id])
                    
                    if transaction.to_account_id and transaction.to_account_id in accounts:
                        self.db.save_account(accounts[transaction.to_account_id])
                    
                    # Save transaction with updated status
                    self.db.save_transaction(transaction)
                    success_count += 1
                else:
                    fail_count += 1
        
        # Show results
        message = f"Processed {success_count} transactions successfully."
        if fail_count > 0:
            message += f" {fail_count} transactions failed (insufficient funds?)"
        
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        
        # Clear selected transactions
        self.selected_transactions = {}
        
        # Reload transactions
        self.load_pending_transactions()
    
    def approve_transaction(self, transaction_id):
        """Approve a single transaction"""
        transaction = self.db.get_transaction(transaction_id)
        if transaction:
            # Get accounts
            accounts = {account.id: account for account in self.db.get_all_accounts()}
            
            # Execute transaction
            if transaction.execute(accounts):
                # Update accounts
                if transaction.from_account_id and transaction.from_account_id in accounts:
                    self.db.save_account(accounts[transaction.from_account_id])
                
                if transaction.to_account_id and transaction.to_account_id in accounts:
                    self.db.save_account(accounts[transaction.to_account_id])
                
                # Save transaction with updated status
                self.db.save_transaction(transaction)
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Transaction approved successfully"))
                self.page.snack_bar.open = True
            else:
                # Show error message
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Failed to process transaction. Check account balance."))
                self.page.snack_bar.open = True
        
        # Reload transactions
        self.load_pending_transactions()
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction after confirmation"""
        def confirm_delete(e):
            self.db.delete_transaction(transaction_id)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Transaction deleted"))
            self.page.snack_bar.open = True
            self.load_pending_transactions()
            self.page.dialog.open = False
            self.page.update()
        
        def cancel_delete(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Show confirmation dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this transaction? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.TextButton("Delete", on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()
    
    def edit_transaction(self, transaction_id):
        """Edit a pending transaction"""
        transaction = self.db.get_transaction(transaction_id)
        if not transaction:
            return
        
        # Get accounts for dropdowns
        accounts = self.db.get_all_accounts()
        account_options = []
        
        for account in accounts:
            account_options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        # Create form fields
        description_field = ft.TextField(
            label="Description",
            value=transaction.description,
            width=400,
        )
        
        amount_field = ft.TextField(
            label="Amount",
            value=str(transaction.amount),
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        date_picker = ft.TextField(
            label="Date",
            value=transaction.date.isoformat(),
            width=200,
        )
        
        from_account_dropdown = ft.Dropdown(
            label="From Account",
            options=account_options,
            value=transaction.from_account_id,
            width=200,
        )
        
        to_account_dropdown = ft.Dropdown(
            label="To Account",
            options=account_options,
            value=transaction.to_account_id,
            width=200,
        )
        
        category_dropdown = ft.Dropdown(
            label="Category",
            options=[ft.dropdown.Option(category.lower(), category) for category in [
                "Food", "Transport", "Housing", "Entertainment", "Utilities", 
                "Healthcare", "Shopping", "Other"
            ]],
            value=transaction.category or "other",
            width=200,
        )
        
        # Handle different transaction types
        if transaction.transaction_type == "transfer":
            account_row = ft.Row([from_account_dropdown, to_account_dropdown])
        elif transaction.transaction_type == "spending":
            account_row = ft.Row([from_account_dropdown])
        elif transaction.transaction_type == "income":
            account_row = ft.Row([to_account_dropdown])
        else:
            account_row = ft.Row([])
        
        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit {transaction.transaction_type.capitalize()} Transaction"),
            content=ft.Column([
                description_field,
                ft.Row([
                    amount_field,
                    date_picker,
                ]),
                account_row,
                category_dropdown,
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog()),
                ft.TextButton("Save", on_click=lambda e: self.save_edit(
                    transaction_id,
                    description_field.value,
                    amount_field.value,
                    date_picker.value,
                    from_account_dropdown.value if transaction.transaction_type in ["transfer", "spending"] else None,
                    to_account_dropdown.value if transaction.transaction_type in ["transfer", "income"] else None,
                    category_dropdown.value
                )),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Show dialog
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        """Close the current dialog"""
        self.page.dialog.open = False
        self.page.update()
    
    def save_edit(self, transaction_id, description, amount, date_str, from_account_id, to_account_id, category):
        """Save edited transaction"""
        try:
            # Parse amount
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Parse date
            try:
                transaction_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                # If date format is invalid, keep the original date
                transaction = self.db.get_transaction(transaction_id)
                transaction_date = transaction.date
            
            # Update transaction
            transaction = self.db.get_transaction(transaction_id)
            if transaction:
                transaction.description = description
                transaction.amount = amount
                transaction.date = transaction_date
                transaction.from_account_id = from_account_id
                transaction.to_account_id = to_account_id
                transaction.category = category
                
                self.db.save_transaction(transaction)
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Transaction updated successfully"))
                self.page.snack_bar.open = True
                
                # Close dialog and reload
                self.close_dialog()
                self.load_pending_transactions()
            else:
                raise ValueError("Transaction not found")
        except ValueError as e:
            # Show error
            self.page.snack_bar = ft.SnackBar(content=ft.Text(str(e) or "Invalid input"))
            self.page.snack_bar.open = True
            self.page.update()
    
    def refresh_pending(self, e):
        """Refresh the pending transactions list"""
        self.load_pending_transactions()
        
        # Show confirmation
        self.page.snack_bar = ft.SnackBar(content=ft.Text("Pending transactions refreshed"))
        self.page.snack_bar.open = True
        self.page.update()