# ui/subscriptions.py - Finance Tracker App/ui/subscriptions.py

import flet as ft
from datetime import datetime, date
from models import Subscription

class SubscriptionsView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.categories = ["Entertainment", "Software", "Streaming", "Utilities", "Insurance", "Other"]
        self.view = self.build()
        self.load_subscriptions()
    
    def build(self):
        """Build the subscriptions management UI"""
        # Subscriptions list
        self.subscriptions_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
        )
        
        # Empty state message
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.SUBSCRIPTIONS_OUTLINED, size=64, color=ft.colors.GREY_400),
                ft.Text("No subscriptions found", size=20, color=ft.colors.GREY_600),
                ft.Text("Add a subscription to get started.", color=ft.colors.GREY_600),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True,
        )
        
        # Form for adding new subscriptions
        self.name_field = ft.TextField(
            label="Subscription Name", 
            hint_text="e.g. Netflix, Spotify, Gym...",
            width=300,
        )
        
        self.amount_field = ft.TextField(
            label="Amount",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.frequency_dropdown = ft.Dropdown(
            label="Frequency",
            width=150,
            options=[
                ft.dropdown.Option("monthly", "Monthly"),
                ft.dropdown.Option("quarterly", "Quarterly"),
                ft.dropdown.Option("yearly", "Yearly"),
            ],
            value="monthly",
        )
        
        self.next_payment_date_picker = ft.TextField(
            label="Next Payment Date",
            hint_text="YYYY-MM-DD",
            width=150,
            value=date.today().isoformat(),
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
        
        self.category_dropdown = ft.Dropdown(
            label="Category",
            width=150,
            options=[ft.dropdown.Option(category.lower(), category) for category in self.categories],
            value="other",
        )
        
        self.linked_account_dropdown = ft.Dropdown(
            label="Payment Account",
            width=300,
            options=[
                ft.dropdown.Option("none", "None"),
            ],
        )
        
        # Form actions
        self.add_subscription_button = ft.ElevatedButton(
            "Add Subscription",
            icon=ft.icons.ADD,
            on_click=self.add_subscription,
        )
        
        # Subscription form container
        self.subscription_form = ft.Container(
            content=ft.Column([
                ft.Text("Add New Subscription", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.name_field,
                    self.amount_field,
                ]),
                ft.Row([
                    self.frequency_dropdown,
                    self.next_payment_date_picker,
                    self.currency_dropdown,
                ]),
                ft.Row([
                    self.category_dropdown,
                    self.linked_account_dropdown,
                    self.add_subscription_button,
                ]),
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # Stats section
        self.monthly_total = ft.Text("Monthly total: 0.00 CHF", size=16, weight=ft.FontWeight.BOLD)
        
        # Stats container
        self.stats_container = ft.Container(
            content=ft.Column([
                ft.Text("Subscription Statistics", size=20, weight=ft.FontWeight.BOLD),
                self.monthly_total,
                ft.Text("Note: Quarterly and yearly subscriptions are pro-rated to monthly equivalent.", size=12, color=ft.colors.GREY_600),
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
                    content=ft.Text("Subscriptions", size=32, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=20, top=10),
                ),
                self.subscription_form,
                self.stats_container,
                ft.Text(
                    "Your subscriptions will generate pending transactions automatically on their due dates.",
                    size=16,
                ),
                ft.Container(height=20),
                self.subscriptions_list,
                self.empty_state,
            ]),
            padding=20,
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
    
    def load_subscriptions(self):
        """Load subscriptions from database"""
        self.load_accounts_dropdown()
        
        # Get accounts for reference
        accounts = {account.id: account for account in self.db.get_all_accounts()}
        
        # Get subscriptions
        subscriptions = self.db.get_all_subscriptions()
        
        # Clear list
        self.subscriptions_list.controls = []
        
        # Calculate monthly cost
        monthly_total_chf = 0
        monthly_total_eur = 0
        
        for subscription in subscriptions:
            if subscription.status != "active":
                continue
                
            # Convert to monthly equivalent
            monthly_equivalent = subscription.amount
            if subscription.frequency == "quarterly":
                monthly_equivalent = subscription.amount / 3
            elif subscription.frequency == "yearly":
                monthly_equivalent = subscription.amount / 12
            
            # Add to appropriate currency total
            if subscription.currency == "CHF":
                monthly_total_chf += monthly_equivalent
            elif subscription.currency == "EUR":
                monthly_total_eur += monthly_equivalent
            
            # Create subscription card
            card = self._create_subscription_card(subscription, accounts)
            self.subscriptions_list.controls.append(card)
        
        # Update stats
        self.monthly_total.value = f"Monthly total: {monthly_total_chf:.2f} CHF + {monthly_total_eur:.2f} EUR"
        
        # Show empty state if no subscriptions
        self.empty_state.visible = len(self.subscriptions_list.controls) == 0
        
        self.page.update()
    
    def _create_subscription_card(self, subscription, accounts):
        """Create a card UI for a subscription"""
        # Determine icon and color based on category
        icon_name = ft.icons.SUBSCRIPTIONS
        
        if subscription.category:
            if subscription.category.lower() == "entertainment":
                icon_name = ft.icons.MOVIE
            elif subscription.category.lower() == "software":
                icon_name = ft.icons.COMPUTER
            elif subscription.category.lower() == "streaming":
                icon_name = ft.icons.VIDEO_LIBRARY
            elif subscription.category.lower() == "utilities":
                icon_name = ft.icons.HOME
            elif subscription.category.lower() == "insurance":
                icon_name = ft.icons.SECURITY
        
        icon_color = ft.colors.BLUE
        
        # Status indicator
        status_color = ft.colors.GREEN
        status_text = "Active"
        if subscription.status == "paused":
            status_color = ft.colors.AMBER
            status_text = "Paused"
        elif subscription.status == "canceled":
            status_color = ft.colors.GREY
            status_text = "Canceled"
        
        # Format next payment date
        next_payment_date_str = subscription.next_payment_date.strftime("%Y-%m-%d")
        
        # Get linked account name
        linked_account_name = "Not linked to any account"
        if subscription.linked_account_id and subscription.linked_account_id in accounts:
            linked_account_name = f"Paid from: {accounts[subscription.linked_account_id].name}"
        
        # Format frequency text
        frequency_text = subscription.frequency.capitalize()
        
        # Action buttons based on status
        action_buttons = []
        
        if subscription.status == "active":
            pause_button = ft.OutlinedButton(
                "Pause",
                icon=ft.icons.PAUSE,
                on_click=lambda e, sid=subscription.id: self.toggle_subscription_status(sid, "paused"),
            )
            action_buttons.append(pause_button)
        elif subscription.status == "paused":
            resume_button = ft.OutlinedButton(
                "Resume",
                icon=ft.icons.PLAY_ARROW,
                on_click=lambda e, sid=subscription.id: self.toggle_subscription_status(sid, "active"),
            )
            action_buttons.append(resume_button)
        
        edit_button = ft.OutlinedButton(
            "Edit",
            icon=ft.icons.EDIT,
            on_click=lambda e, sid=subscription.id: self.edit_subscription(sid),
        )
        action_buttons.append(edit_button)
        
        delete_button = ft.TextButton(
            "Delete",
            icon=ft.icons.DELETE,
            on_click=lambda e, sid=subscription.id: self.delete_subscription(sid),
        )
        action_buttons.append(delete_button)
        
        # Create subscription card
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(icon_name, color=icon_color),
                        title=ft.Text(
                            subscription.name,
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(f"Next payment: {next_payment_date_str} • {frequency_text}"),
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
                                f"{subscription.amount:.2f} {subscription.currency}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]),
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(linked_account_name),
                            ft.Text(f"Category: {subscription.category or 'Not categorized'}"),
                        ]),
                        padding=ft.padding.symmetric(horizontal=15),
                    ),
                    ft.Container(
                        content=ft.Row(action_buttons, alignment=ft.MainAxisAlignment.END),
                        padding=ft.padding.only(right=10, bottom=10, top=10),
                    ),
                ]),
                padding=10,
            ),
        )
    
    def add_subscription(self, e):
        """Add a new subscription"""
        try:
            # Validate and parse inputs
            amount = float(self.amount_field.value)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            if not self.name_field.value:
                raise ValueError("Subscription name is required")
            
            # Parse next payment date
            try:
                next_payment_date = datetime.strptime(self.next_payment_date_picker.value, "%Y-%m-%d").date()
            except ValueError:
                next_payment_date = date.today()
            
            # Set linked account
            linked_account_id = None
            if self.linked_account_dropdown.value != "none":
                linked_account_id = self.linked_account_dropdown.value
            
            # Create subscription
            subscription = Subscription(
                name=self.name_field.value,
                amount=amount,
                frequency=self.frequency_dropdown.value,
                next_payment_date=next_payment_date,
                linked_account_id=linked_account_id,
                status="active",
                currency=self.currency_dropdown.value,
                category=self.category_dropdown.value
            )
            
            # Save subscription
            self.db.save_subscription(subscription)
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Subscription added successfully"))
            self.page.snack_bar.open = True
            
            # Reset form
            self.name_field.value = ""
            self.amount_field.value = ""
            self.next_payment_date_picker.value = date.today().isoformat()
            self.frequency_dropdown.value = "monthly"
            self.currency_dropdown.value = "CHF"
            self.category_dropdown.value = "other"
            self.linked_account_dropdown.value = "none"
            
            # Reload subscriptions
            self.load_subscriptions()
        except ValueError as e:
            # Show error
            self.page.snack_bar = ft.SnackBar(content=ft.Text(str(e) or "Please enter valid subscription details"))
            self.page.snack_bar.open = True
            self.page.update()
    
    def toggle_subscription_status(self, subscription_id, new_status):
        """Toggle a subscription between active and paused"""
        subscription = self.db.get_subscription(subscription_id)
        if not subscription:
            return
        
        # Update status
        subscription.status = new_status
        
        # Save subscription
        self.db.save_subscription(subscription)
        
        # Show success message
        status_text = "paused" if new_status == "paused" else "activated"
        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Subscription {status_text} successfully"))
        self.page.snack_bar.open = True
        
        # Reload subscriptions
        self.load_subscriptions()
    
    def edit_subscription(self, subscription_id):
        """Edit a subscription"""
        subscription = self.db.get_subscription(subscription_id)
        if not subscription:
            return
        
        # Create form fields
        name_field = ft.TextField(
            label="Subscription Name",
            value=subscription.name,
            width=300,
        )
        
        amount_field = ft.TextField(
            label="Amount",
            value=str(subscription.amount),
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        frequency_dropdown = ft.Dropdown(
            label="Frequency",
            width=150,
            options=[
                ft.dropdown.Option("monthly", "Monthly"),
                ft.dropdown.Option("quarterly", "Quarterly"),
                ft.dropdown.Option("yearly", "Yearly"),
            ],
            value=subscription.frequency,
        )
        
        next_payment_date_picker = ft.TextField(
            label="Next Payment Date",
            value=subscription.next_payment_date.isoformat(),
            width=150,
        )
        
        currency_dropdown = ft.Dropdown(
            label="Currency",
            width=150,
            options=[
                ft.dropdown.Option("CHF", "CHF"),
                ft.dropdown.Option("EUR", "EUR"),
            ],
            value=subscription.currency,
        )
        
        category_dropdown = ft.Dropdown(
            label="Category",
            width=150,
            options=[ft.dropdown.Option(category.lower(), category) for category in self.categories],
            value=subscription.category or "other",
        )
        
        # Load accounts for dropdown
        accounts = self.db.get_all_accounts()
        account_options = [ft.dropdown.Option("none", "None")]
        
        for account in accounts:
            account_options.append(
                ft.dropdown.Option(account.id, f"{account.name} ({account.currency})")
            )
        
        linked_account_dropdown = ft.Dropdown(
            label="Payment Account",
            width=300,
            options=account_options,
            value=subscription.linked_account_id or "none",
        )
        
        def save_edit(e):
            try:
                # Validate and parse inputs
                amount = float(amount_field.value)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                
                if not name_field.value:
                    raise ValueError("Subscription name is required")
                
                # Parse next payment date
                try:
                    next_payment_date = datetime.strptime(next_payment_date_picker.value, "%Y-%m-%d").date()
                except ValueError:
                    next_payment_date = subscription.next_payment_date
                
                # Set linked account
                linked_account_id = None
                if linked_account_dropdown.value != "none":
                    linked_account_id = linked_account_dropdown.value
                
                # Update subscription
                subscription.name = name_field.value
                subscription.amount = amount
                subscription.frequency = frequency_dropdown.value
                subscription.next_payment_date = next_payment_date
                subscription.linked_account_id = linked_account_id
                subscription.currency = currency_dropdown.value
                subscription.category = category_dropdown.value
                
                # Save subscription
                self.db.save_subscription(subscription)
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Subscription updated successfully"))
                self.page.snack_bar.open = True
                
                # Close dialog and reload
                self.page.dialog.open = False
                self.load_subscriptions()
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
            title=ft.Text("Edit Subscription"),
            content=ft.Column([
                name_field,
                ft.Row([
                    amount_field,
                    currency_dropdown,
                ]),
                ft.Row([
                    frequency_dropdown,
                    next_payment_date_picker,
                ]),
                ft.Row([
                    category_dropdown,
                    linked_account_dropdown,
                ]),
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_edit),
                ft.TextButton("Save", on_click=save_edit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()
    
    def delete_subscription(self, subscription_id):
        """Delete a subscription after confirmation"""
        def confirm_delete(e):
            self.db.delete_subscription(subscription_id)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Subscription deleted"))
            self.page.snack_bar.open = True
            self.load_subscriptions()
            self.page.dialog.open = False
            self.page.update()
        
        def cancel_delete(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Show confirmation dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this subscription? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.TextButton("Delete", on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog.open = True
        self.page.update()