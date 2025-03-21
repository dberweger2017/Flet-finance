# main.py - Finance Tracker App/main.py

import flet as ft
import os
from datetime import datetime
from db import Database

# Import UI views
from ui.dashboard import DashboardView
from ui.accounts import AccountsView
from ui.transactions import TransactionsView
from ui.pending import PendingView
from ui.debts import DebtsView
from ui.subscriptions import SubscriptionsView

class FinanceTrackerApp:
    def __init__(self):
        self.db = Database()
        self.current_view = None
        self.nav_rail = None
        self.page = None
        
    def initialize(self, page: ft.Page):
        """Initialize the app with the given page"""
        self.page = page
        
        # Configure page
        self.page.title = "Personal Finance Tracker"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # Create navigation rail
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            extended=True,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.DASHBOARD,
                    selected_icon=ft.icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.ACCOUNT_BALANCE,
                    selected_icon=ft.icons.ACCOUNT_BALANCE,
                    label="Accounts",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.RECEIPT_LONG,
                    selected_icon=ft.icons.RECEIPT_LONG,
                    label="Transactions",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PENDING_ACTIONS,
                    selected_icon=ft.icons.PENDING_ACTIONS,
                    label="Pending",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PAYMENTS,
                    selected_icon=ft.icons.PAYMENTS,
                    label="Debts",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SUBSCRIPTIONS,
                    selected_icon=ft.icons.SUBSCRIPTIONS,
                    label="Subscriptions",
                ),
            ],
            on_change=self.nav_change,
        )
        
        # Create main content area
        self.content_area = ft.Container(
            expand=True,
        )
        
        # Set up app layout
        self.page.add(
            ft.Row(
                [
                    ft.Card(
                        content=ft.Container(
                            content=self.nav_rail,
                            padding=ft.padding.only(top=30, bottom=30),
                        ),
                        elevation=1,
                    ),
                    ft.VerticalDivider(width=1),
                    self.content_area,
                ],
                expand=True,
            )
        )
        
        # Set up routes
        self.page.on_route_change = self.route_change
        
        # Set initial route
        self.page.go("/")
    
    def nav_change(self, e):
        """Handle navigation rail selection changes"""
        index = e.control.selected_index
        
        if index == 0:
            self.page.go("/")
        elif index == 1:
            self.page.go("/accounts")
        elif index == 2:
            self.page.go("/transactions")
        elif index == 3:
            self.page.go("/pending")
        elif index == 4:
            self.page.go("/debts")
        elif index == 5:
            self.page.go("/subscriptions")
    
    def route_change(self, route):
        """Handle route changes and update the UI"""
        self.content_area.content = None
        
        # Determine which view to show based on route
        if route.route == "/":
            self.nav_rail.selected_index = 0
            self.current_view = DashboardView(self.page, self.db)
            self.content_area.content = self.current_view.view
            
        elif route.route == "/accounts":
            self.nav_rail.selected_index = 1
            self.current_view = AccountsView(self.page, self.db)
            self.content_area.content = self.current_view.view
            
        elif route.route == "/transactions":
            self.nav_rail.selected_index = 2
            self.current_view = TransactionsView(self.page, self.db)
            self.content_area.content = self.current_view.view
            
        elif route.route == "/pending":
            self.nav_rail.selected_index = 3
            self.current_view = PendingView(self.page, self.db)
            self.content_area.content = self.current_view.view
            
        elif route.route == "/debts":
            self.nav_rail.selected_index = 4
            self.current_view = DebtsView(self.page, self.db)
            self.content_area.content = self.current_view.view
            
        elif route.route == "/subscriptions":
            self.nav_rail.selected_index = 5
            self.current_view = SubscriptionsView(self.page, self.db)
            self.content_area.content = self.current_view.view
        
        # Update the page
        self.page.update()

    def close_db(self):
        """Close the database connection when the app is closed"""
        if self.db:
            self.db.close()

def main(page: ft.Page):
    """Main entry point for the app"""
    app = FinanceTrackerApp()
    app.initialize(page)
    
    # Set up a handler for app closing to properly close the database
    page.on_close = lambda e: app.close_db()

if __name__ == "__main__":
    ft.app(target=main)