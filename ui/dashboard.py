# ui/dashboard.py - Finance Tracker App/ui/dashboard.py

import flet as ft
from datetime import datetime, date, timedelta
import calendar
import json
from dashboard_data import DashboardDataProvider
from models import CurrencyConverter

class DashboardView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        # Initialize dashboard data provider
        self.data_provider = DashboardDataProvider(db)
        self.view = self.build()
        self.update_data()
        
    def build(self):
        """Build the dashboard UI"""
        # Pending transactions alert
        self.pending_alert = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER, color=ft.colors.AMBER),
                ft.Text("You have pending transactions that need your approval."),
                ft.Container(expand=True),
                ft.TextButton("View Pending", on_click=self._go_to_pending),
            ]),
            border=ft.border.all(1, ft.colors.AMBER),
            border_radius=5,
            padding=10,
            margin=ft.margin.only(bottom=20),
            visible=False,  # Will be made visible if pending transactions exist
        )
        
        # Dashboard metrics
        self.metrics_row = ft.Row([
            self._create_metric_card("Liquidity", "0.00 CHF", "Available funds"),
            self._create_metric_card("Net Worth", "0.00 CHF", "Assets - Liabilities"),
            self._create_metric_card("Savings Rate", "0.00 CHF/month", "Current month"),
        ])
        
        # Currency conversion info
        self.currency_info = ft.Container(
            content=ft.Column([
                ft.Text("Currency Exchange Rates (Base: CHF)", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("1 CHF = 1.13 USD", size=12),
                ft.Text("1 CHF = 1.04 EUR", size=12),
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # Liquidity trend chart
        self.liquidity_chart_container = ft.Container(
            content=ft.Column([
                ft.Text("Liquidity Trend (CHF)", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Available funds over the last 90 days", size=14),
                # Chart will be added here
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # Net worth trend chart
        self.net_worth_chart_container = ft.Container(
            content=ft.Column([
                ft.Text("Net Worth Trend (CHF)", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Net worth over the last 90 days", size=14),
                # Chart will be added here
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # Monthly savings chart
        self.savings_chart_container = ft.Container(
            content=ft.Column([
                ft.Text("Monthly Savings (CHF)", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Savings contribution by month", size=14),
                # Chart will be added here
            ]),
            padding=20,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # Accounts table
        self.accounts_summary = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Account")),
                ft.DataColumn(ft.Text("Type")),
                ft.DataColumn(ft.Text("Currency")),
                ft.DataColumn(ft.Text("Balance")),
                ft.DataColumn(ft.Text("Available")),
            ],
            rows=[],
        )
        
        # Upcoming transactions table
        self.upcoming_transactions = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Description")),
                ft.DataColumn(ft.Text("Amount")),
                ft.DataColumn(ft.Text("Type")),
            ],
            rows=[],
        )
        
        # Return the main container
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("Financial Dashboard", size=32, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Refresh",
                            icon=ft.Icons.REFRESH,
                            on_click=self._refresh_clicked,
                        ),
                    ]),
                    margin=ft.margin.only(bottom=20, top=10),
                ),
                self.pending_alert,
                self.metrics_row,
                self.currency_info,
                self.liquidity_chart_container,
                self.net_worth_chart_container,
                self.savings_chart_container,
                ft.Text("Accounts Summary", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.accounts_summary,
                    height=300,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Text("Upcoming Transactions", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.upcoming_transactions,
                    height=200,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                ),
            ]),
            padding=20,
        )
    
    def _create_metric_card(self, title, value, subtitle=None):
        """Create a card displaying a financial metric"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(subtitle, size=12, color=ft.colors.GREY_600) if subtitle else ft.Container(),
                ]),
                width=200,
                padding=15,
            ),
        )
    
    def _go_to_pending(self, e):
        """Navigate to pending transactions view"""
        self.page.go("/pending")
    
    def _refresh_clicked(self, e):
        """Refresh dashboard data"""
        self.update_data()
        self.page.snack_bar = ft.SnackBar(content=ft.Text("Dashboard refreshed"))
        self.page.snack_bar.open = True
        self.page.update()
    
    def _create_liquidity_chart(self, data):
        """Create a line chart for liquidity trend using Flet's built-in LineChart"""
        if not data:
            return ft.Container(
                content=ft.Text("No data available", color=ft.colors.GREY_400),
                alignment=ft.alignment.center,
                height=200
            )
        
        # Sort data by date to ensure chronological order
        sorted_data = sorted(data, key=lambda x: x["date"])
        
        # Modify the data to have zeros for days before the last 3 days
        today = date.today()
        three_days_ago = today - timedelta(days=3)
        
        # Format as ISO string for comparison
        three_days_ago_str = three_days_ago.isoformat()
        
        # Set all values before the last 3 days to zero
        for point in sorted_data:
            if point["date"] < three_days_ago_str:
                point["value"] = 0
        
        # Extract values for plotting
        values = [point["value"] for point in sorted_data]
        min_value = min(values) if values else 0  # Avoid empty list error
        max_value = max(values) if max(values) > 0 else 1  # Avoid division by zero
        
        # Create data points for the chart
        data_points = [
            ft.LineChartDataPoint(i, point["value"]) 
            for i, point in enumerate(sorted_data)
        ]
        
        # Create line chart for liquidity
        return ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    color=ft.colors.BLUE,
                    curved=True,
                    stroke_width=3,
                    stroke_cap_round=True,
                )
            ],
            border=ft.border.all(1, ft.colors.GREY_300),
            left_axis=ft.ChartAxis(
                # Add some Y-axis labels
                labels=[
                    ft.ChartAxisLabel(value=min_value, label=ft.Text(f"{min_value:.0f}")),
                    ft.ChartAxisLabel(value=(min_value + max_value) / 2, label=ft.Text(f"{(min_value + max_value) / 2:.0f}")),
                    ft.ChartAxisLabel(value=max_value, label=ft.Text(f"{max_value:.0f}")),
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                # Add some X-axis labels (dates)
                labels=[
                    ft.ChartAxisLabel(
                        value=i, 
                        label=ft.Container(ft.Text(sorted_data[i]["day"]), padding=5)
                    )
                    for i in range(0, len(sorted_data), max(1, len(sorted_data) // 5))  # Show ~5 labels evenly distributed
                ],
                labels_size=40,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.colors.GREY_300, 
                width=1,
                dash_pattern=[3, 3]
            ),
            min_y=min_value * 0.9,  # Add some padding
            max_y=max_value * 1.1,
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            interactive=True,
            expand=True,
            height=250,
        )

    def _create_net_worth_chart(self, data):
        """Create a line chart for net worth trend using Flet's built-in LineChart"""
        if not data:
            return ft.Container(
                content=ft.Text("No data available", color=ft.colors.GREY_400),
                alignment=ft.alignment.center,
                height=200
            )
        
        # Extract values for plotting
        values = [point["value"] for point in data]
        min_value = min(values)
        max_value = max(values)
        
        # Create data points for the chart
        data_points = [
            ft.LineChartDataPoint(i, point["value"]) 
            for i, point in enumerate(data)
        ]
        
        # Create line chart for net worth
        return ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    color=ft.colors.GREEN,
                    curved=True,
                    stroke_width=3,
                    stroke_cap_round=True,
                )
            ],
            border=ft.border.all(1, ft.colors.GREY_300),
            left_axis=ft.ChartAxis(
                # Add some Y-axis labels
                labels=[
                    ft.ChartAxisLabel(value=min_value, label=ft.Text(f"{min_value:.0f}")),
                    ft.ChartAxisLabel(value=(min_value + max_value) / 2, label=ft.Text(f"{(min_value + max_value) / 2:.0f}")),
                    ft.ChartAxisLabel(value=max_value, label=ft.Text(f"{max_value:.0f}")),
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                # Add some X-axis labels (dates)
                labels=[
                    ft.ChartAxisLabel(
                        value=i, 
                        label=ft.Container(ft.Text(data[i]["day"]), padding=5)
                    )
                    for i in range(0, len(data), max(1, len(data) // 5))  # Show ~5 labels evenly distributed
                ],
                labels_size=40,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.colors.GREY_300, 
                width=1,
                dash_pattern=[3, 3]
            ),
            min_y=min_value * 0.9,  # Add some padding
            max_y=max_value * 1.1,
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            interactive=True,
            expand=True,
            height=250,
        )

    def _create_savings_chart(self, data):
        """Create a bar chart for monthly savings using Flet's built-in BarChart"""
        if not data:
            return ft.Container(
                content=ft.Text("No data available", color=ft.colors.GREY_400),
                alignment=ft.alignment.center,
                height=200
            )
        
        # Extract values for plotting and find the max for scaling
        values = [point["value"] for point in data]
        max_value = max(values) if values else 0
        
        # Create the bar chart for monthly savings
        return ft.BarChart(
            bar_groups=[
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=point["value"],
                            width=30,
                            color=ft.colors.PURPLE,
                            tooltip=f"{point['value']:.2f} CHF",
                            border_radius=3,
                        ),
                    ],
                )
                for i, point in enumerate(data)
            ],
            border=ft.border.all(1, ft.colors.GREY_300),
            left_axis=ft.ChartAxis(
                title=ft.Text("Amount (CHF)"),
                title_size=30,
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i, 
                        label=ft.Container(ft.Text(point["month"]), padding=10)
                    )
                    for i, point in enumerate(data)
                ],
                labels_size=40,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.colors.GREY_300, 
                width=1, 
                dash_pattern=[3, 3]
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.5, ft.colors.GREY_300),
            max_y=max_value * 1.1 if max_value > 0 else 100,  # Add 10% padding
            interactive=True,
            expand=True,
            height=250,
        )
    
    def update_data(self):
        """Update dashboard with latest data from database"""
        # Show or hide pending transactions alert
        pending_transactions = self.db.get_all_transactions(status="pending")
        if pending_transactions:
            self.pending_alert.visible = True
        else:
            self.pending_alert.visible = False
        
        # Update metrics
        net_worth_data = self.db.get_net_worth()
        liquidity = self.db.get_liquidity()
        savings_data = self.db.get_savings_stats()
        
        # Update the metrics row with current values (all in CHF)
        self.metrics_row.controls = [
            self._create_metric_card("Liquidity", f"{liquidity:.2f} CHF", "Available funds (all currencies converted to CHF)"),
            self._create_metric_card("Net Worth", f"{net_worth_data['net_worth']:.2f} CHF", "Assets - Liabilities (all currencies converted to CHF)"),
            self._create_metric_card("Savings Rate", f"{savings_data['month_contribution']:.2f} CHF/month", "Current month"),
        ]
        
        # Get chart data from data provider
        dashboard_data = self.data_provider.get_dashboard_data()
        
        # Update liquidity chart
        liquidity_chart = self._create_liquidity_chart(dashboard_data["liquidity_trend"])
        self.liquidity_chart_container.content.controls[2] = liquidity_chart
        
        # Update net worth chart
        net_worth_chart = self._create_net_worth_chart(dashboard_data["net_worth_trend"])
        self.net_worth_chart_container.content.controls[2] = net_worth_chart
        
        # Update savings chart
        savings_chart = self._create_savings_chart(dashboard_data["monthly_savings"])
        self.savings_chart_container.content.controls[2] = savings_chart
        
        # Update accounts summary
        accounts = self.db.get_all_accounts()
        rows = []
        
        for account in accounts:
            icon = ft.Icon(
                name=ft.Icons.ACCOUNT_BALANCE if account.account_type != "credit" else ft.Icons.CREDIT_CARD,
                color=ft.colors.BLUE if account.account_type != "credit" else ft.colors.PURPLE
            )
            
            balance_color = ft.colors.BLACK
            if account.balance < 0:
                balance_color = ft.colors.RED
            
            # Include the native currency and the CHF equivalent in parentheses
            balance_in_chf = CurrencyConverter.convert_to_chf(account.balance, account.currency)
            available_in_chf = CurrencyConverter.convert_to_chf(account.get_available_balance(), account.currency)
            
            balance_text = f"{account.balance:.2f} {account.currency}"
            if account.currency != "CHF":
                balance_text += f" ({balance_in_chf:.2f} CHF)"
            
            available_text = f"{account.get_available_balance():.2f} {account.currency}"
            if account.currency != "CHF":
                available_text += f" ({available_in_chf:.2f} CHF)"
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row([icon, ft.Text(account.name)])),
                        ft.DataCell(ft.Text(account.account_type.capitalize())),
                        ft.DataCell(ft.Text(account.currency)),
                        ft.DataCell(ft.Text(balance_text, color=balance_color)),
                        ft.DataCell(ft.Text(available_text)),
                    ]
                )
            )
        
        self.accounts_summary.rows = rows
        
        # Update upcoming transactions
        today = date.today()
        seven_days = today + timedelta(days=7)
        
        # Get upcoming subscription payments
        subscriptions = self.db.get_all_subscriptions(status="active")
        upcoming_subs = [sub for sub in subscriptions if sub.next_payment_date <= seven_days]
        
        # Get upcoming debt payments
        debts = self.db.get_all_debts(status="pending")
        upcoming_debts = [debt for debt in debts if debt.due_date <= seven_days]
        
        # Combine into upcoming transactions
        upcoming_rows = []
        
        for sub in upcoming_subs:
            # Include the CHF equivalent for non-CHF currencies
            amount_text = f"-{sub.amount:.2f} {sub.currency}"
            if sub.currency != "CHF":
                amount_in_chf = CurrencyConverter.convert_to_chf(sub.amount, sub.currency)
                amount_text += f" ({amount_in_chf:.2f} CHF)"
            
            upcoming_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(sub.next_payment_date.strftime("%Y-%m-%d"))),
                        ft.DataCell(ft.Text(f"Subscription: {sub.name}")),
                        ft.DataCell(ft.Text(amount_text, color=ft.colors.RED)),
                        ft.DataCell(ft.Text("Subscription")),
                    ]
                )
            )
        
        for debt in upcoming_debts:
            # Include the CHF equivalent for non-CHF currencies
            amount_in_chf = CurrencyConverter.convert_to_chf(debt.amount, debt.currency)
            
            if not debt.is_receivable:
                amount_text = f"-{debt.amount:.2f} {debt.currency}"
                if debt.currency != "CHF":
                    amount_text += f" (-{amount_in_chf:.2f} CHF)"
                amount_color = ft.colors.RED
            else:
                amount_text = f"+{debt.amount:.2f} {debt.currency}"
                if debt.currency != "CHF":
                    amount_text += f" (+{amount_in_chf:.2f} CHF)"
                amount_color = ft.colors.GREEN
            
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
        
        # Limit to 5 most recent
        upcoming_rows = upcoming_rows[:5]
        
        self.upcoming_transactions.rows = upcoming_rows
        
        # Update the page
        self.page.update()