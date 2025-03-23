# ui/debts.py - Finance Tracker App/ui/debts.py

import sys
import flet as ft
from datetime import datetime, date
from models import Debt

class DebtsView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.view = self.build()
        self.load_debts()
    
    def build(self):
        """Build the debts management UI"""
        # Tabs for payable and receivable debts
        self.payable_list = ft.ListView(expand=1, spacing=10, padding=10)
        self.receivable_list = ft.ListView(expand=1, spacing=10, padding=10)
        
        self.tab_bar = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Money You Owe",
                    icon=ft.Icons.ARROW_UPWARD,
                    content=ft.Column([
                        ft.Container(height=20),
                        self.payable_list,
                    ])
                ),
                ft.Tab(
                    text="Money Owed to You",
                    icon=ft.Icons.ARROW_DOWNWARD,
                    content=ft.Column([
                        ft.Container(height=20),
                        self.receivable_list,
                    ])
                ),
            ],
            expand=1,
        )
        
        # Form for adding new debts
        self.description_field = ft.TextField(
            label="Description", 
            hint_text="e.g. Rent, Car Loan, Friend Borrowed...",
            width=300,
        )
        
        self.amount_field = ft.TextField(
            label="Amount",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.due_date_picker = ft.TextField(
            label="Due Date",
            hint_text="YYYY-MM-DD",
            width=200,
            value=date.today().isoformat(),
        )
        
        self.is_receivable_toggle = ft.Switch(
            label="Someone owes me this money",
            value=False,
        )
        
        self.currency_dropdown = ft.Dropdown(
            label="Currency",
            width=150,
            options=[
                ft.dropdown.Option("CHF", "CHF"),
                ft.dropdown.Option("EUR", "EUR"),
            ],
            value="CHF",
        )
        
        self.linked_account_dropdown = ft.Dropdown(
            label="Linked Account (for payment)",
            width=300,
            options=[
                ft.dropdown.Option("none", "None"),
            ],
        )
        
        # Form actions
        self.add_debt_button = ft.ElevatedButton(
            "Add Debt",
            icon=ft.Icons.ADD,
            on_click=self.add_debt,
        )
        
        # Debt form container
        self.debt_form = ft.Container(
            content=ft.Column([
                ft.Text("Add New Debt or Receivable", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.description_field,
                    self.amount_field,
                    self.due_date_picker,
                ]),
                ft.Row([
                    self.is_receivable_toggle,
                    self.currency_dropdown,
                    self.linked_account_dropdown,
                ]),
                ft.Row([
                    self.add_debt_button,
                ]),
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # Return the main container
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Debts & Receivables", size=32, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=20, top=10),
                ),
                self.debt_form,
                ft.Text(
                    "Track money you owe and money owed to you. Mark debts as paid when settled.",
                    size=16,
                ),
                ft.Container(height=10),
                self.tab_bar,
            ]),
            padding=20,
            expand=True,
        )
    
    def load_accounts_dropdown(self):
        """Load accounts into the linked account dropdown"""
        accounts = self.db.get_all_accounts()
        
        # Reset dropdown
        self.linked_account_dropdown.options = [ft.dropdown.Option("none", "None")]
        
        for account in accounts:
            self.linked_account_dropdown.options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        self.linked_account_dropdown.value = "none"
    
    def load_debts(self):
        """Load debts from database"""
        self.load_accounts_dropdown()
        
        # Get accounts for reference
        accounts = {account.id: account for account in self.db.get_all_accounts()}
        
        # Get payable and receivable debts
        payable_debts = self.db.get_all_debts(is_receivable=False)
        receivable_debts = self.db.get_all_debts(is_receivable=True)
        
        # Clear lists
        self.payable_list.controls = []
        self.receivable_list.controls = []
        
        # Create debt cards
        for debt in payable_debts:
            card = self._create_debt_card(debt, accounts, is_payable=True)
            self.payable_list.controls.append(card)
        
        for debt in receivable_debts:
            card = self._create_debt_card(debt, accounts, is_payable=False)
            self.receivable_list.controls.append(card)
        
        self.page.update()
    
    def _create_debt_card(self, debt, accounts, is_payable=True):
        """Create a card UI for a debt"""
        # Determine icon, color, and status
        icon_name = ft.Icons.ARROW_UPWARD if is_payable else ft.Icons.ARROW_DOWNWARD
        icon_color = ft.colors.RED if is_payable else ft.colors.GREEN
        amount_color = ft.colors.RED if is_payable else ft.colors.GREEN
        
        # Calculate paid and remaining amounts
        paid_amount = debt.get_paid_amount()
        remaining_amount = debt.get_remaining_amount()
        paid_percentage = (paid_amount / debt.amount) * 100 if debt.amount > 0 else 0
        
        # Status indicator
        status_color = ft.colors.GREEN
        status_text = "Paid"
        if debt.status == "pending":
            status_color = ft.colors.BLUE
            status_text = "Pending"
        elif debt.status == "partial":
            status_color = ft.colors.ORANGE
            status_text = "Partial"
        elif debt.status == "overdue":
            status_color = ft.colors.RED
            status_text = "Overdue"
        
        # Format date
        due_date_str = debt.due_date.strftime("%Y-%m-%d")
        
        # Get linked account name
        linked_account_name = "Not linked to any account"
        if debt.linked_account_id and debt.linked_account_id in accounts:
            linked_account_name = f"Linked to: {accounts[debt.linked_account_id].name}"
        
        # Action buttons
        mark_paid_button = ft.ElevatedButton(
            "Mark as Paid",
            icon=ft.Icons.CHECK,
            on_click=lambda e, did=debt.id: self.mark_debt_paid(did),
            disabled=debt.status == "paid",
        )
        
        partial_payment_button = ft.OutlinedButton(
            "Partial Payment",
            icon=ft.Icons.PAYMENTS,
            on_click=lambda e, did=debt.id: self.show_partial_payment_dialog(did),
            disabled=debt.status == "paid",
        )
        
        edit_button = ft.OutlinedButton(
            "Edit",
            icon=ft.Icons.EDIT,
            on_click=lambda e, did=debt.id: self.edit_debt(did),
            disabled=debt.status == "paid",
        )
        
        delete_button = ft.TextButton(
            "Delete",
            icon=ft.Icons.DELETE,
            data=debt.id,
            on_click=lambda e: self.delete_debt(e.control.data),
        )
        
        history_button = ft.TextButton(
            "History",
            icon=ft.Icons.HISTORY,
            on_click=lambda e, did=debt.id: self.view_payment_history(did),
        )
        
        # Create debt card
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(icon_name, color=icon_color),
                        title=ft.Text(
                            debt.description,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            no_wrap=True,
                        ),
                        subtitle=ft.Text(f"Due: {due_date_str}"),
                        trailing=ft.Row([
                            ft.Container(
                                ft.Text(
                                    status_text,
                                    color=ft.colors.WHITE,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=status_color,
                                border_radius=5,
                                padding=5,
                            ),
                            ft.Container(width=10),
                            ft.Text(
                                f"{debt.amount:.2f} {debt.currency}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=amount_color,
                            ),
                        ]),
                        content_padding=ft.padding.all(10),
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(linked_account_name, no_wrap=True),
                            ft.Text(f"Paid: {paid_amount:.2f} {debt.currency} ({paid_percentage:.1f}%)"),
                            ft.Text(f"Remaining: {remaining_amount:.2f} {debt.currency}"),
                            ft.ProgressBar(
                                value=paid_percentage / 100,
                                bgcolor=ft.colors.GREY_300,
                                color=ft.colors.GREEN if is_payable else ft.colors.BLUE,
                            ),
                        ]),
                        padding=ft.padding.symmetric(horizontal=15),
                    ),
                    ft.Container(
                        content=ft.Row([
                            mark_paid_button,
                            partial_payment_button,
                            edit_button,
                            delete_button,
                            history_button,
                        ], alignment=ft.MainAxisAlignment.END, wrap=True),
                        padding=ft.padding.only(right=10, bottom=10, top=10),
                    ),
                ]),
                padding=10,
                expand=True,
            ),
        )
    
    def add_debt(self, e):
        """Add a new debt"""
        try:
            # Validate and parse inputs
            amount = float(self.amount_field.value)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            if not self.description_field.value:
                raise ValueError("Description is required")
            
            # Parse due date
            try:
                due_date = datetime.strptime(self.due_date_picker.value, "%Y-%m-%d").date()
            except ValueError:
                due_date = date.today()
            
            # Set linked account
            linked_account_id = None
            if self.linked_account_dropdown.value != "none":
                linked_account_id = self.linked_account_dropdown.value
            
            # Create debt
            debt = Debt(
                description=self.description_field.value,
                amount=amount,
                due_date=due_date,
                is_receivable=self.is_receivable_toggle.value,
                linked_account_id=linked_account_id,
                status="pending",
                currency=self.currency_dropdown.value
            )
            
            # Save debt
            self.db.save_debt(debt)
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Debt added successfully"))
            self.page.snack_bar.open = True
            
            # Reset form
            self.description_field.value = ""
            self.amount_field.value = ""
            self.due_date_picker.value = date.today().isoformat()
            self.is_receivable_toggle.value = False
            self.currency_dropdown.value = "CHF"
            self.linked_account_dropdown.value = "none"
            
            # Reload debts
            self.load_debts()
        except ValueError as e:
            # Show error
            self.page.snack_bar = ft.SnackBar(content=ft.Text(str(e) or "Please enter valid debt details"))
            self.page.snack_bar.open = True
            self.page.update()
    
    def mark_debt_paid(self, debt_id):
        """Mark a debt as paid and create corresponding transaction"""
        debt = self.db.get_debt(debt_id)
        if not debt or debt.status == "paid":
            return
        
        if not debt.linked_account_id:
            # Show account selection dialog if no linked account
            self.show_account_selection_dialog(debt_id)
        else:
            # Otherwise, mark as paid directly
            self.perform_mark_as_paid(debt_id, debt.linked_account_id)
    
    def show_account_selection_dialog(self, debt_id):
        """Show dialog to select account for payment"""
        accounts = self.db.get_all_accounts()
        account_options = []
        
        for account in accounts:
            account_options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        if not account_options:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("No accounts available. Please create an account first."))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        account_dropdown = ft.Dropdown(
            label="Select Account",
            options=account_options,
            value=account_options[0].key,
            width=300,
        )
        
        def confirm_selection(e):
            self.perform_mark_as_paid(debt_id, account_dropdown.value)
            self.page.dialog.open = False
            self.page.update()
        
        def cancel_selection(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Show dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Select Account for Payment"),
            content=ft.Column([
                ft.Text("Select the account to use for this payment:"),
                account_dropdown,
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_selection),
                ft.TextButton("Confirm", on_click=confirm_selection),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()
    
    def perform_mark_as_paid(self, debt_id, account_id):
        """Actually mark the debt as paid and create transaction"""
        debt = self.db.get_debt(debt_id)
        if not debt or debt.status == "paid":
            return
        
        # Update linked account if necessary
        if debt.linked_account_id != account_id:
            debt.linked_account_id = account_id
            self.db.save_debt(debt)
        
        # Create transaction for the payment
        transaction = debt.mark_as_paid()
        
        if transaction:
            self.db.save_transaction(transaction)
            
            # Show success message with info about the pending transaction
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Debt marked as paid. A pending transaction has been created. Go to Pending Transactions to approve it.")
            )
            self.page.snack_bar.open = True
        else:
            # Show error
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Failed to create payment transaction"))
            self.page.snack_bar.open = True
        
        # Save updated debt status
        self.db.save_debt(debt)
        
        # Reload debts
        self.load_debts()
    
    def edit_debt(self, debt_id):
        """Edit a debt"""
        debt = self.db.get_debt(debt_id)
        if not debt:
            return
        
        # Create form fields
        description_field = ft.TextField(
            label="Description",
            value=debt.description,
            width=300,
        )
        
        amount_field = ft.TextField(
            label="Amount",
            value=str(debt.amount),
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        due_date_picker = ft.TextField(
            label="Due Date",
            value=debt.due_date.isoformat(),
            width=200,
        )
        
        currency_dropdown = ft.Dropdown(
            label="Currency",
            width=150,
            options=[
                ft.dropdown.Option("CHF", "CHF"),
                ft.dropdown.Option("EUR", "EUR"),
            ],
            value=debt.currency,
        )
        
        # Load accounts for dropdown
        accounts = self.db.get_all_accounts()
        account_options = [ft.dropdown.Option("none", "None")]
        
        for account in accounts:
            account_options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        linked_account_dropdown = ft.Dropdown(
            label="Linked Account",
            width=300,
            options=account_options,
            value=debt.linked_account_id or "none",
        )
        
        def save_edit(e):
            try:
                # Validate and parse inputs
                amount = float(amount_field.value)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                
                if not description_field.value:
                    raise ValueError("Description is required")
                
                # Parse due date
                try:
                    due_date = datetime.strptime(due_date_picker.value, "%Y-%m-%d").date()
                except ValueError:
                    due_date = debt.due_date
                
                # Set linked account
                linked_account_id = None
                if linked_account_dropdown.value != "none":
                    linked_account_id = linked_account_dropdown.value
                
                # Update debt
                debt.description = description_field.value
                debt.amount = amount
                debt.due_date = due_date
                debt.linked_account_id = linked_account_id
                debt.currency = currency_dropdown.value
                
                # Save debt
                self.db.save_debt(debt)
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Debt updated successfully"))
                self.page.snack_bar.open = True
                
                # Close dialog and reload
                self.page.dialog.open = False
                self.load_debts()
            except ValueError as e:
                # Show error
                self.page.snack_bar = ft.SnackBar(content=ft.Text(str(e) or "Invalid input"))
                self.page.snack_bar.open = True
                self.page.update()
        
        def cancel_edit(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Show dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Edit Debt"),
            content=ft.Column([
                description_field,
                ft.Row([
                    amount_field,
                    currency_dropdown,
                ]),
                due_date_picker,
                linked_account_dropdown,
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_edit),
                ft.TextButton("Save", on_click=save_edit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()
    
    def delete_debt(self, debt_id):
        """Delete a debt after confirmation"""
        def confirm_delete(e):
            self.db.delete_debt(debt_id)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Debt deleted"))
            self.page.snack_bar.open = True
            self.load_debts()
            self.page.dialog.open = False
            self.page.update()
        
        def cancel_delete(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Show confirmation dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this debt? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.TextButton("Delete", on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()

    def show_partial_payment_dialog(self, debt_id):
        """Show dialog to make a partial payment on a debt"""
        debt = self.db.get_debt(debt_id)
        if not debt:
            return
        
        if not debt.linked_account_id:
            # Show account selection dialog if no linked account
            self.show_account_selection_dialog_for_partial(debt_id)
        else:
            # Otherwise, show partial payment dialog directly
            self.show_partial_payment_amount_dialog(debt_id, debt.linked_account_id)

    def show_account_selection_dialog_for_partial(self, debt_id):
        """Show dialog to select account for partial payment"""
        accounts = self.db.get_all_accounts()
        account_options = []
        
        for account in accounts:
            account_options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        if not account_options:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("No accounts available. Please create an account first."))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        account_dropdown = ft.Dropdown(
            label="Select Account",
            options=account_options,
            value=account_options[0].key,
            width=300,
        )
        
        def confirm_selection(e):
            self.show_partial_payment_amount_dialog(debt_id, account_dropdown.value)
            self.page.dialog.open = False
            self.page.update()
        
        def cancel_selection(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Show dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Select Account for Payment"),
            content=ft.Column([
                ft.Text("Select the account to use for this payment:"),
                account_dropdown,
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_selection),
                ft.TextButton("Confirm", on_click=confirm_selection),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()

    def show_partial_payment_amount_dialog(self, debt_id, account_id):
        """Show dialog to enter partial payment amount"""
        debt = self.db.get_debt(debt_id)
        if not debt:
            return
        
        # Update linked account if necessary
        if debt.linked_account_id != account_id:
            debt.linked_account_id = account_id
            self.db.save_debt(debt)
        
        remaining = debt.get_remaining_amount()
        
        amount_field = ft.TextField(
            label=f"Payment Amount (Max: {remaining:.2f} {debt.currency})",
            value=str(remaining),
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        notes_field = ft.TextField(
            label="Notes (Optional)",
            width=300,
        )
        
        def make_payment(e):
            try:
                amount = float(amount_field.value)
                if amount <= 0:
                    raise ValueError("Payment amount must be positive")
                
                if amount > remaining:
                    raise ValueError(f"Payment amount exceeds remaining balance of {remaining:.2f} {debt.currency}")
                
                # Make the partial payment
                transaction = debt.make_partial_payment(amount, notes=notes_field.value)
                
                if transaction:
                    self.db.save_transaction(transaction)
                    
                    # Show success message
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Partial payment recorded. A pending transaction has been created. Go to Pending Transactions to approve it.")
                    )
                    self.page.snack_bar.open = True
                else:
                    # Show error
                    self.page.snack_bar = ft.SnackBar(content=ft.Text("Failed to create payment transaction"))
                    self.page.snack_bar.open = True
                
                # Save updated debt
                self.db.save_debt(debt)
                
                # Close dialog and reload
                self.page.dialog.open = False
                self.load_debts()
            except ValueError as e:
                # Show error
                self.page.snack_bar = ft.SnackBar(content=ft.Text(str(e)))
                self.page.snack_bar.open = True
                self.page.update()
        
        def cancel_payment(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Show dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Make Partial Payment"),
            content=ft.Column([
                ft.Text(f"Debt: {debt.description}"),
                ft.Text(f"Total Amount: {debt.amount:.2f} {debt.currency}"),
                ft.Text(f"Already Paid: {debt.get_paid_amount():.2f} {debt.currency}"),
                ft.Text(f"Remaining: {remaining:.2f} {debt.currency}"),
                amount_field,
                notes_field,
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_payment),
                ft.TextButton("Make Payment", on_click=make_payment),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()

    def view_payment_history(self, debt_id):
        """Show dialog with payment history for a debt"""
        debt = self.db.get_debt(debt_id)
        if not debt or not debt.payment_history:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("No payment history available"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Create a data table for payment history
        columns = [
            ft.DataColumn(ft.Text("Date")),
            ft.DataColumn(ft.Text("Amount")),
            ft.DataColumn(ft.Text("Notes")),
        ]
        
        rows = []
        for payment in debt.payment_history:
            rows.append(
                ft.DataRow([
                    ft.DataCell(ft.Text(payment["date"])),
                    ft.DataCell(ft.Text(f"{payment['amount']:.2f} {debt.currency}")),
                    ft.DataCell(ft.Text(payment.get("notes", ""))),
                ])
            )
        
        history_table = ft.DataTable(
            columns=columns,
            rows=rows,
        )
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Show dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"Payment History - {debt.description}"),
            content=history_table,
            actions=[
                ft.TextButton("Close", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()