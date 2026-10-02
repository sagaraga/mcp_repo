# import random
# from fastmcp import FastMCP

# mcp = FastMCP(name = "Local MCP Server Demo")

# @mcp.tool
# def roll_dice(n_dices:int = 1) -> list[int]:
#     """Roll 6 sided n dices and return the results as a list."""
#     return [random.randint(1, 6) for _ in range(n_dices)]

# @mcp.tool
# def add_numbers(a: int, b: int) -> int:
#     """Return the sum of two numbers."""
#     return a + b

# Creating a MCP server for tracking expenses with sqlite3 db as backend. 
# contains two tools - add_expense and list_expenses

from fastmcp import FastMCP
import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__),"expenses.db")

mcp = FastMCP("ExpenseTracker")

# def init_db():
#     with sqlite3.connect(DB_PATH) as c:
#         # c.execute("PRAGMA journal_mode=WAL")
#         c.execute("""
#             CREATE TABLE IF NOT EXISTS expenses(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 date TEXT NOT NULL,
#                 amount REAL NOT NULL,
#                 category TEXT NOT NULL,
#                 subcategory TEXT DEFAULT '',
#                 note TEXT DEFAULT ''
#             )
#         """)
#         # Test write access
#         # c.execute("INSERT OR IGNORE INTO expenses(date, amount, category) VALUES ('2000-01-01', 0, 'test')")
#         # c.execute("DELETE FROM expenses WHERE category = 'test'")
#         print("Database initialized successfully with write access")

# init_db()

def init_db():  # Keep as sync for initialization
    try:
        # Use synchronous sqlite3 just for initialization
        import sqlite3
        with sqlite3.connect(DB_PATH) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)
            # Test write access
            c.execute("INSERT OR IGNORE INTO expenses(date, amount, category) VALUES ('2000-01-01', 0, 'test')")
            c.execute("DELETE FROM expenses WHERE category = 'test'")
            print("Database initialized successfully with write access")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

# Initialize database synchronously at module load
init_db()

@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    '''Add a new expense entry to the database.'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "ok", "id": cur.lastrowid}
    
@mcp.tool()
def list_expenses(start_date, end_date):
    '''List expense entries within an inclusive date range.'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    
if __name__ == "__main__":
    # mcp.run()
    mcp.run(transport="http", host="0.0.0.0", port=8000)