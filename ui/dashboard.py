# ui/dashboard.py - Finance Tracker App/ui/dashboard.py

import flet as ft
from datetime import datetime, date, timedelta
import calendar
import json
from dashboard_data import DashboardDataProvider

class DashboardView:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        # Initialize dashboard data provider
        self.data_provider = DashboardDataProvider(db)
        self.view = self.build()
        self.update_data()
        
    def build(self):
        """Build the dashboard UI with chart visualizations"""
        # Create metrics cards (same as the original)
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
        
        # Create simple chart visualizations using Flet's built-in components
        
        # Liquidity Chart Container
        self.liquidity_chart_title = ft.Text(
            "Liquidity Trend (Last 90 Days)",
            size=18,
            weight=ft.FontWeight.BOLD
        )
        
        self.liquidity_chart_container = ft.Container(
            content=ft.Column([
                self.liquidity_chart_title,
                ft.Text("Daily amount available for immediate spending", size=12, color=ft.colors.GREY_600),
                # Placeholder for the chart - will be populated in update_data
                ft.Container(height=200)
            ]),
            margin=ft.margin.only(top=10, bottom=20),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            width=800,
            alignment=ft.alignment.center
        )
        
        # Net Worth Chart Container
        self.net_worth_chart_title = ft.Text(
            "Net Worth Progress (Last 90 Days)",
            size=18,
            weight=ft.FontWeight.BOLD
        )
        
        self.net_worth_chart_container = ft.Container(
            content=ft.Column([
                self.net_worth_chart_title,
                ft.Text("Daily assets minus liabilities over time", size=12, color=ft.colors.GREY_600),
                # Placeholder for the chart - will be populated in update_data
                ft.Container(height=200)
            ]),
            margin=ft.margin.only(top=10, bottom=20),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            width=800,
            alignment=ft.alignment.center
        )
        
        # Monthly Savings Chart Container
        self.savings_chart_title = ft.Text(
            "Monthly Savings",
            size=18,
            weight=ft.FontWeight.BOLD
        )
        
        self.savings_chart_container = ft.Container(
            content=ft.Column([
                self.savings_chart_title,
                ft.Text("Amount saved each month", size=12, color=ft.colors.GREY_600),
                # Placeholder for the chart - will be populated in update_data
                ft.Container(height=200)
            ]),
            margin=ft.margin.only(top=10, bottom=20),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            width=800,
            alignment=ft.alignment.center
        )
        
        # Accounts summary section (same as original)
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
        
        # Upcoming section (same as original)
        self.upcoming_transactions = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Description")),
                ft.DataColumn(ft.Text("Amount"), numeric=True),
                ft.DataColumn(ft.Text("Type")),
            ],
            rows=[],
        )
        
        # Card for pending transactions alert (same as original)
        self.pending_alert = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=ft.colors.AMBER),
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
        
        # Return the main container with charts
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Pending transactions alert (same as original)
                self.pending_alert,
                
                # Current Liquidity section
                ft.Container(
                    content=ft.Column([
                        # Liquidity title in the middle
                        ft.Container(
                            content=ft.Text("Current Liquidity", size=24, weight=ft.FontWeight.BOLD),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=10, bottom=10)
                        ),
                        # Liquidity metric value
                        ft.Container(
                            content=ft.Text(
                                f"{self.db.get_liquidity():.2f} CHF",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=20)
                        ),
                        # Liquidity chart
                        ft.Container(
                            content=self.liquidity_chart_container,
                            alignment=ft.alignment.center
                        )
                    ]),
                    margin=ft.margin.only(bottom=30)
                ),
                
                # Net Worth section
                ft.Container(
                    content=ft.Column([
                        # Net Worth title in the middle
                        ft.Container(
                            content=ft.Text("Net Worth", size=24, weight=ft.FontWeight.BOLD),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=10, bottom=10)
                        ),
                        # Net Worth metric value
                        ft.Container(
                            content=ft.Text(
                                f"{self.db.get_net_worth()['net_worth']:.2f} CHF",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.GREEN
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=20)
                        ),
                        # Net Worth chart
                        ft.Container(
                            content=self.net_worth_chart_container,
                            alignment=ft.alignment.center
                        )
                    ]),
                    margin=ft.margin.only(bottom=30)
                ),
                
                # Monthly Savings section
                ft.Container(
                    content=ft.Column([
                        # Monthly Savings title in the middle
                        ft.Container(
                            content=ft.Text("Monthly Savings", size=24, weight=ft.FontWeight.BOLD),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=10, bottom=10)
                        ),
                        # Monthly Savings metric value
                        ft.Container(
                            content=ft.Text(
                                f"{self.db.get_savings_stats()['month_contribution']:.2f} CHF",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.PURPLE
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=20)
                        ),
                        # Savings chart
                        ft.Container(
                            content=self.savings_chart_container,
                            alignment=ft.alignment.center
                        )
                    ]),
                    margin=ft.margin.only(bottom=30)
                ),
                
                # Accounts section (same as original)
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
                
                # Upcoming section (same as original)
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("Upcoming Transactions", size=20, weight=ft.FontWeight.BOLD),
                            margin=ft.margin.only(bottom=10, top=10)
                        ),
                        self.upcoming_transactions,
                    ]),
                ),
                
                # Refresh button (same as original)
                ft.Container(
                    content=ft.ElevatedButton(
                        "Refresh Dashboard",
                        icon=ft.Icons.REFRESH,
                        on_click=self._refresh_clicked
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=20)
                ),
            ]),
            padding=20,
        )
    
    def _create_metric_card(self, title, value, subtitle=None):
        """Create a metric card (same as original)"""
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
        """Navigate to pending transactions page (same as original)"""
        self.page.go("/pending")
    
    def _refresh_clicked(self, e):
        """Refresh the dashboard data (same as original)"""
        self.update_data()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Dashboard refreshed"),
            action="OK",
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _create_sparkline_chart(self, data, value_key="value", color=ft.colors.BLUE, height=200):
        """Create a simple visual representation of data trend using Flet components"""
        if not data:
            return ft.Container(
                content=ft.Text("No data available", color=ft.colors.GREY_400),
                alignment=ft.alignment.center,
                height=height
            )
        
        # Extract values for plotting
        values = [point[value_key] for point in data]
        min_value = min(values)
        max_value = max(values)
        
        # Normalize to chart height
        range_value = max_value - min_value
        if range_value == 0:
            range_value = 1  # Avoid division by zero
        
        # Create points for line chart
        chart_width = 700  # Fixed width
        point_spacing = chart_width / (len(values) - 1) if len(values) > 1 else chart_width
        chart_height = height - 40  # Leave space for labels
        
        # Create a list of points
        points = []
        for i, value in enumerate(values):
            # Normalize y value (invert because Flet's coordinate system has y growing downward)
            y = chart_height - ((value - min_value) / range_value * chart_height)
            x = i * point_spacing
            points.append(ft.Offset(x, y))
        
        # Create bars for bar chart (for savings)
        max_bar_height = chart_height
        bar_spacing = 5
        bar_width = (chart_width / len(values)) - bar_spacing
        
        bars = []
        for i, value in enumerate(values):
            # Normalize bar height
            bar_height = (value / max_value) * max_bar_height if max_value > 0 else 0
            
            bars.append(
                ft.Container(
                    width=bar_width,
                    height=bar_height,
                    bgcolor=color,
                    border_radius=ft.border_radius.only(top_left=5, top_right=5),
                    # Position at the bottom
                    margin=ft.margin.only(bottom=0, top=max_bar_height - bar_height)
                )
            )
        
        # Create the chart components
        title = data[0].get("month", "")
        last_title = data[-1].get("month", "")
        
        # Use different chart types based on data
        if "month" in data[0]:
            # Bar chart for monthly data
            chart = ft.Row(
                bars,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=chart_width
            )
        else:
            # Line chart for daily data
            chart = ft.Stack([
                # Create grid lines
                ft.Column([
                    ft.Container(
                        height=1,
                        width=chart_width,
                        bgcolor=ft.colors.GREY_300
                    ),
                    ft.Container(
                        height=chart_height/2 - 1,
                        width=chart_width
                    ),
                    ft.Container(
                        height=1,
                        width=chart_width,
                        bgcolor=ft.colors.GREY_300
                    ),
                    ft.Container(
                        height=chart_height/2 - 1,
                        width=chart_width
                    ),
                    ft.Container(
                        height=1,
                        width=chart_width,
                        bgcolor=ft.colors.GREY_300
                    ),
                ]),
                
                # Create line
                ft.ShaderMask(
                    content=ft.Container(width=chart_width, height=chart_height),
                    blend_mode=ft.BlendMode.SRC_IN,
                    shader=ft.LinearGradient(
                        begin=ft.Alignment(-0.5, 0),
                        end=ft.Alignment(1, 0),
                        colors=[color, color],
                        stops=[0.0, 1.0],
                    ),
                    child=ft.ClipPath(
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        clip_path=ft.Path([
                            # Move to the start point
                            ft.PathMoveTo(points[0].x, points[0].y),
                            # Draw lines to each point
                            *[ft.PathLineTo(p.x, p.y) for p in points[1:]],
                            # Complete the path by going to the bottom right, then bottom left, then back to start
                            ft.PathLineTo(points[-1].x, chart_height),
                            ft.PathLineTo(points[0].x, chart_height),
                            ft.PathLineTo(points[0].x, points[0].y),
                        ]),
                        content=ft.Container(
                            width=chart_width,
                            height=chart_height,
                            opacity=0.3
                        )
                    )
                )
            ])
        
        # Create the axis labels
        labels = ft.Row([
            ft.Text(title, size=12, color=ft.colors.GREY_700),
            ft.Container(expand=True),
            ft.Text(last_title, size=12, color=ft.colors.GREY_700),
        ], width=chart_width)
        
        # Create the chart with labels
        return ft.Column([
            chart,
            labels,
            ft.Row([
                ft.Text(f"Min: {min_value:.2f} CHF", size=12, color=ft.colors.GREY_700),
                ft.Container(expand=True),
                ft.Text(f"Max: {max_value:.2f} CHF", size=12, color=ft.colors.GREY_700),
            ], width=chart_width)
        ])
    
    def update_data(self):
        """Update dashboard with latest data from database"""
        # Original metrics update code
        net_worth_data = self.db.get_net_worth()
        liquidity = self.db.get_liquidity()
        savings_data = self.db.get_savings_stats()
        
        # Get chart data from data provider
        dashboard_data = self.data_provider.get_dashboard_data()
        
        # Update liquidity chart
        liquidity_chart = self._create_sparkline_chart(
            dashboard_data["liquidity_trend"], 
            color=ft.colors.BLUE
        )
        self.liquidity_chart_container.content.controls[2] = liquidity_chart
        
        # Update net worth chart
        net_worth_chart = self._create_sparkline_chart(
            dashboard_data["net_worth_trend"], 
            color=ft.colors.GREEN
        )
        self.net_worth_chart_container.content.controls[2] = net_worth_chart
        
        # Update savings chart
        savings_chart = self._create_sparkline_chart(
            dashboard_data["monthly_savings"], 
            color=ft.colors.PURPLE
        )
        self.savings_chart_container.content.controls[2] = savings_chart
        
        # Original code for updating accounts summary
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
        
        # Original code for updating upcoming transactions
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