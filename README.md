# PipesHub_OMS_Assignment
 A Python-based Order Management System implementing throttling, order queuing, and time-window validation. Built as part of a backend assignment for PipesHub.

# Order Management System – Python

This project simulates a backend order management system built for an assignment by PipesHub.

## Features
- Throttled order processing (X orders/second)
- Logon/Logout time-window enforcement
- Modify and Cancel support for queued orders
- Exchange response latency tracking (logged to CSV)

## How It Works
- Orders are accepted only between 22:00 and 23:00
- Orders beyond the limit are queued and sent later
- Modify updates queued order values
- Cancel removes queued orders by ID

## How to Run
```bash
python OrderManagement.py
