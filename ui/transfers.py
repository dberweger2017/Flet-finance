# ui/transfers.py - Finance Tracker App/ui/transfers.py

import flet as ft
from datetime import datetime
from models import Transaction

class TransfersView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.view = self.build()
        self.load_accounts()
    
    def build(self):
        """Build the transfers management UI"""
        # Transfer form
        self.amount_field = ft.TextField(
            label="Transfer Amount",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.from_account_dropdown = ft.Dropdown(
            label="From Account",
            width=300,
            options=[],
        )
        
        self.to_account_dropdown = ft.Dropdown(
            label="To Account",
            width=300,
            options=[],
        )
        
        self.description_field = ft.TextField(
            label="Description (optional)",
            width=300,
        )
        
        self.transfer_button = ft.ElevatedButton(
            "Create Transfer",
            icon=ft.Icons.SEND,
            on_click=self.perform_transfer,
        )
        
        # Transfer form container
        self.transfer_form = ft.Container(
            content=ft.Column([
                ft.Text("Transfer Between Accounts", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Create a transfer transaction between your accounts.", size=14),
                ft.Container(height=20),
                ft.Row([
                    self.amount_field,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    self.from_account_dropdown,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    self.to_account_dropdown,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    self.description_field,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    self.transfer_button,
                ], alignment=ft.MainAxisAlignment.CENTER),
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20, top=20),
            width=500,
            alignment=ft.alignment.center,
        )
        
        # Recent transfers list
        self.recent_transfers_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
        )
        
        # Return the main container
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Account Transfers", size=32, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=20, top=10),
                ),
                ft.Container(
                    content=self.transfer_form,
                    alignment=ft.alignment.center,
                ),
                ft.Text("Recent Transfers", size=20, weight=ft.FontWeight.BOLD),
                self.recent_transfers_list,
            ]),
            padding=20,
        )
    
    def load_accounts(self):
        """Load accounts into dropdowns and refresh recent transfers"""
        # Get accounts
        accounts = self.db.get_all_accounts()
        
        # Reset dropdowns
        self.from_account_dropdown.options = []
        self.to_account_dropdown.options = []
        
        # Add accounts to dropdowns
        for account in accounts:
            self.from_account_dropdown.options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
            self.to_account_dropdown.options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        # Set default selections if accounts exist
        if self.from_account_dropdown.options:
            self.from_account_dropdown.value = self.from_account_dropdown.options[0].key
            
            # Set to_account to second account if possible
            if len(self.to_account_dropdown.options) > 1:
                self.to_account_dropdown.value = self.to_account_dropdown.options[1].key
            else:
                self.to_account_dropdown.value = self.to_account_dropdown.options[0].key
        
        # Load recent transfers
        self.load_recent_transfers()
        
        self.page.update()
    
    def load_recent_transfers(self):
        """Load recent transfer transactions"""
        # Get recent transfers (up to 10)
        transfers = self.db.get_all_transactions(transaction_type="transfer")
        transfers = transfers[:10]  # Limit to 10 most recent
        
        # Get accounts for reference
        accounts = {account.id: account for account in self.db.get_all_accounts()}
        
        # Clear list
        self.recent_transfers_list.controls = []
        
        # Add transfers to list
        for transfer in transfers:
            card = self._create_transfer_card(transfer, accounts)
            self.recent_transfers_list.controls.append(card)
        
        self.page.update()
    
    def _create_transfer_card(self, transfer, accounts):
        """Create a card UI for a transfer"""
        # Get account names and currency
        from_account_name = "Unknown"
        to_account_name = "Unknown"
        currency = "CHF"  # Default
        
        if transfer.from_account_id and transfer.from_account_id in accounts:
            from_account = accounts[transfer.from_account_id]
            from_account_name = from_account.name
            currency = from_account.currency
        
        if transfer.to_account_id and transfer.to_account_id in accounts:
            to_account = accounts[transfer.to_account_id]
            to_account_name = to_account.name
        
        # Format date
        date_str = transfer.date.strftime("%Y-%m-%d")
        
        # Status color and text
        status_color = ft.colors.GREEN
        status_text = "Completed"
        
        if transfer.status == "pending":
            status_color = ft.colors.ORANGE
            status_text = "Pending"
        elif transfer.status == "canceled":
            status_color = ft.colors.RED
            status_text = "Canceled"
        
        # Create transfer card
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.SYNC_ALT, color=ft.colors.BLUE),
                        title=ft.Text(
                            transfer.description or "Transfer between accounts",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        subtitle=ft.Text(f"Date: {date_str}"),
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
                                f"{transfer.amount:.2f} {currency}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]),
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"From: {from_account_name} → To: {to_account_name}"),
                        ]),
                        padding=ft.padding.symmetric(horizontal=15),
                    ),
                ]),
                padding=10,
            ),
        )
    
    def perform_transfer(self, e):
        """Create a transfer transaction"""
        try:
            # Validate inputs
            if not self.amount_field.value:
                raise ValueError("Amount is required")
            
            amount = float(self.amount_field.value)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            from_account_id = self.from_account_dropdown.value
            to_account_id = self.to_account_dropdown.value
            description = self.description_field.value or "Transfer between accounts"
            
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
            
            # Reset form
            self.amount_field.value = ""
            self.description_field.value = ""
            
            # Reload transfers
            self.load_recent_transfers()
            
            self.page.update()
        except ValueError as e:
            # Show error
            self.page.snack_bar = ft.SnackBar(content=ft.Text(str(e)))
            self.page.snack_bar.open = True
            self.page.update()