# Finance Tracker App - README.md

## Overview

Finance Tracker is a personal finance management application built with Python and Flet. It helps you track your finances, including accounts, transactions, debts, and subscriptions, with a focus on liquidity monitoring and savings tracking.

## Features

- **Multi-currency support**: Track accounts in CHF and EUR
- **Multiple account types**: Manage debit, credit, and savings accounts
- **Transaction management**: Track income, spending, and transfers between accounts
- **Debt tracking**: Manage money you owe and money owed to you
- **Subscription management**: Track recurring payments with automatic pending transaction generation
- **Manual reconciliation**: Reconcile account balances with your bank statements
- **Dashboard**: View key financial metrics including liquidity, net worth, and savings progress
- **Pending transactions**: Review and approve transactions before they affect your accounts

## Project Structure

```
Finance Tracker App/
├── main.py               # Main application entry point
├── models.py             # Data models for accounts, transactions, etc.
├── db.py                 # Database operations and utility functions
├── finance_tracker.db    # SQLite database (created on first run)
├── ui/                   # User interface modules
│   ├── dashboard.py      # Dashboard view
│   ├── accounts.py       # Accounts management view
│   ├── transactions.py   # Transactions history view
│   ├── pending.py        # Pending transactions view
│   ├── debts.py          # Debts management view
│   └── subscriptions.py  # Subscriptions management view
└── README.md             # This file
```

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required packages:

```bash
pip install flet python-dateutil
```

3. Clone or download this repository
4. Run the application:

```bash
python main.py
```

## Usage

### Dashboard

The dashboard provides an overview of your financial situation, including:
- Current liquidity (immediately available funds)
- Net worth (assets - liabilities)
- Savings status
- Accounts overview
- Upcoming transactions

### Accounts

Manage your bank accounts, credit cards, and savings accounts:
- Add, edit, or delete accounts
- Reconcile account balances with bank statements
- Transfer money between accounts
- Track available balances including credit limits

### Transactions

View and manage your income and spending:
- Filter transactions by date, account, type, and category
- Add new transactions (pending approval)
- Analyze transaction history

### Pending Transactions

Review transactions before they affect your accounts:
- Approve or reject transactions
- Edit transaction details
- Process multiple transactions at once

### Debts

Track money you owe and money owed to you:
- Add debts with due dates
- Mark debts as paid (creates corresponding transactions)
- Monitor overdue debts

### Subscriptions

Manage recurring payments:
- Add subscriptions with different frequencies (monthly, quarterly, yearly)
- Automatically generate pending transactions for due payments
- Pause or resume subscriptions
- View total monthly subscription costs

## Workflow Example

1. Add your bank accounts, credit cards, and savings accounts
2. Enter initial balances
3. Add your regular subscriptions
4. Record debts and receivables
5. Add transactions as they occur
6. Review and approve pending transactions
7. Periodically reconcile account balances with bank statements

## License

This project is open source and available for personal use.

## Credits

Created with Flet - https://flet.dev/