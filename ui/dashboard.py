# ui/dashboard.py - Finance Tracker App/ui/dashboard.py

import flet as ft
from datetime import datetime, date
import calendar

class DashboardView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.view = self.build()
        self.update_data()
        
    def build(self):
        """Build the dashboard UI"""
        # Main metrics cards
        self.liquidity_card = self._create_metric_card(
            "Current Liquidity",
            "0.00 CHF",
            "Amount available for immediate spending"
        )
        
        self.net_worth_card = self._create_metric_card(
            "Net Worth",
            "0.00 CHF",
            "Assets - Liabilities"
        )
        
        self.savings_card = self._create_metric_card(
            "Savings",
            "0.00 CHF",
            "Total savings accounts balance"
        )
        
        self.monthly_savings_card = self._create_metric_card(
            "Monthly Savings",
            "0.00 CHF",
            f"Savings in {calendar.month_name[datetime.now().month]}"
        )
        
        # Accounts summary section
        self.accounts_summary = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Account")),
                ft.DataColumn(ft.Text("Type")),
                ft.DataColumn(ft.Text("Currency")),
                ft.DataColumn(ft.Text("Balance"), numeric=True),
                ft.DataColumn(ft.Text("Available"), numeric=True),
            ],
            rows=[],
        )
        
        # Upcoming section
        self.upcoming_transactions = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Description")),
                ft.DataColumn(ft.Text("Amount"), numeric=True),
                ft.DataColumn(ft.Text("Type")),
            ],
            rows=[],
        )
        
        # Card for pending transactions alert
        self.pending_alert = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color=ft.colors.AMBER),
                        ft.Text("Pending Transactions", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Text("You have 0 pending transactions that need attention.", size=14),
                    ft.ElevatedButton(
                        "View Pending Transactions",
                        on_click=self._go_to_pending
                    ),
                ]),
                padding=10,
            ),
            visible=False
        )
        
        # Return the main container
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Metrics row
                ft.Container(
                    content=ft.Row([
                        self.liquidity_card,
                        self.net_worth_card,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    margin=ft.margin.only(bottom=10)
                ),
                
                ft.Container(
                    content=ft.Row([
                        self.savings_card,
                        self.monthly_savings_card,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Pending transactions alert
                self.pending_alert,
                
                # Accounts section
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("Accounts Overview", size=20, weight=ft.FontWeight.BOLD),
                            margin=ft.margin.only(bottom=10, top=20)
                        ),
                        self.accounts_summary,
                    ]),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Upcoming section
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("Upcoming Transactions", size=20, weight=ft.FontWeight.BOLD),
                            margin=ft.margin.only(bottom=10, top=10)
                        ),
                        self.upcoming_transactions,
                    ]),
                ),
                
                # Refresh button
                ft.Container(
                    content=ft.ElevatedButton(
                        "Refresh Dashboard",
                        icon=ft.icons.REFRESH,
                        on_click=self._refresh_clicked
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=20)
                ),
            ]),
            padding=20,
        )
    
    def _create_metric_card(self, title, value, subtitle=None):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(subtitle, size=12, color=ft.colors.GREY_600) if subtitle else ft.Container(),
                ]),
                width=220,
                padding=15,
            ),
        )
    
    def _go_to_pending(self, e):
        """Navigate to pending transactions page"""
        self.page.go("/pending")
    
    def _refresh_clicked(self, e):
        """Refresh the dashboard data"""
        self.update_data()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Dashboard refreshed"),
            action="OK",
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def update_data(self):
        """Update dashboard with latest data from database"""
        # Update metrics
        net_worth_data = self.db.get_net_worth()
        liquidity = self.db.get_liquidity()
        savings_data = self.db.get_savings_stats()
        
        self.liquidity_card.content.content.controls[1].value = f"{liquidity:.2f} CHF"
        self.net_worth_card.content.content.controls[1].value = f"{net_worth_data['net_worth']:.2f} CHF"
        self.savings_card.content.content.controls[1].value = f"{savings_data['total_balance']:.2f} CHF"
        self.monthly_savings_card.content.content.controls[1].value = f"{savings_data['month_contribution']:.2f} CHF"
        
        # Generate color based on value
        if net_worth_data['net_worth'] >= 0:
            self.net_worth_card.content.content.controls[1].color = ft.colors.GREEN
        else:
            self.net_worth_card.content.content.controls[1].color = ft.colors.RED
            
        if savings_data['month_contribution'] >= 0:
            self.monthly_savings_card.content.content.controls[1].color = ft.colors.GREEN
        else:
            self.monthly_savings_card.content.content.controls[1].color = ft.colors.RED
        
        # Update accounts summary
        accounts = self.db.get_all_accounts()
        rows = []
        
        for account in accounts:
            icon = ft.Icon(
                name=ft.icons.ACCOUNT_BALANCE if account.account_type != "credit" else ft.icons.CREDIT_CARD,
                color=ft.colors.BLUE if account.account_type != "credit" else ft.colors.PURPLE
            )
            
            balance_color = ft.colors.BLACK
            if account.balance < 0:
                balance_color = ft.colors.RED
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row([icon, ft.Text(account.name)])),
                        ft.DataCell(ft.Text(account.account_type.capitalize())),
                        ft.DataCell(ft.Text(account.currency)),
                        ft.DataCell(ft.Text(f"{account.balance:.2f}", color=balance_color)),
                        ft.DataCell(ft.Text(f"{account.get_available_balance():.2f}")),
                    ]
                )
            )
        
        self.accounts_summary.rows = rows
        
        # Update upcoming transactions (next 7 days)
        today = date.today()
        seven_days = today.replace(day=today.day + 7)
        
        # Get upcoming subscription payments
        subscriptions = self.db.get_all_subscriptions(status="active")
        upcoming_subs = [sub for sub in subscriptions if sub.next_payment_date <= seven_days]
        
        # Get upcoming debt payments
        debts = self.db.get_all_debts(status="pending")
        upcoming_debts = [debt for debt in debts if debt.due_date <= seven_days]
        
        # Combine into upcoming transactions
        upcoming_rows = []
        
        for sub in upcoming_subs:
            upcoming_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(sub.next_payment_date.strftime("%Y-%m-%d"))),
                        ft.DataCell(ft.Text(f"Subscription: {sub.name}")),
                        ft.DataCell(ft.Text(f"-{sub.amount:.2f} {sub.currency}", color=ft.colors.RED)),
                        ft.DataCell(ft.Text("Subscription")),
                    ]
                )
            )
        
        for debt in upcoming_debts:
            amount_text = f"-{debt.amount:.2f} {debt.currency}" if not debt.is_receivable else f"+{debt.amount:.2f} {debt.currency}"
            amount_color = ft.colors.RED if not debt.is_receivable else ft.colors.GREEN
            debt_type = "Payment Due" if not debt.is_receivable else "Payment Expected"
            
            upcoming_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(debt.due_date.strftime("%Y-%m-%d"))),
                        ft.DataCell(ft.Text(debt.description)),
                        ft.DataCell(ft.Text(amount_text, color=amount_color)),
                        ft.DataCell(ft.Text(debt_type)),
                    ]
                )
            )
        
        # Sort by date
        upcoming_rows.sort(key=lambda row: row.cells[0].content.value)
        self.upcoming_transactions.rows = upcoming_rows
        
        # Update pending transactions alert
        pending_transactions = self.db.get_all_transactions(status="pending")
        if pending_transactions:
            self.pending_alert.content.content.controls[1].value = f"You have {len(pending_transactions)} pending transactions that need attention."
            self.pending_alert.visible = True
        else:
            self.pending_alert.visible = False
        
        # Check and update overdue debts
        self.db.check_and_update_overdue_debts()
        
        # Generate subscription transactions
        self.db.generate_pending_subscription_transactions()