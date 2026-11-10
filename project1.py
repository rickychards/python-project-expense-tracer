"""Expense Tracker - a simple command-line app using SQLite.

Run interactively:  python expense_tracker.py
Run the demo:       python expense_tracker.py --demo
"""
import sqlite3
import sys
from datetime import date

DB_FILE = "expenses.db"


class ExpenseTracker:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS expenses (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT NOT NULL,
                   category TEXT NOT NULL,
                   description TEXT,
                   amount REAL NOT NULL CHECK (amount > 0)
               )"""
        )
        self.conn.commit()

    def add(self, category, amount, description="", when=None):
        when = when or date.today().isoformat()
        cur = self.conn.execute(
            "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
            (when, category.title(), description, float(amount)),
        )
        self.conn.commit()
        return cur.lastrowid

    def delete(self, expense_id):
        cur = self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def list_all(self):
        return self.conn.execute(
            "SELECT id, date, category, description, amount FROM expenses ORDER BY date, id"
        ).fetchall()

    def totals_by_category(self):
        return self.conn.execute(
            "SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC"
        ).fetchall()

    def grand_total(self):
        return self.conn.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses").fetchone()[0]

    # ---- display helpers ----
    def print_all(self):
        rows = self.list_all()
        if not rows:
            print("No expenses yet.")
            return
        print(f"{'ID':<4}{'Date':<12}{'Category':<12}{'Description':<18}{'Amount':>10}")
        print("-" * 56)
        for i, d, c, desc, a in rows:
            print(f"{i:<4}{d:<12}{c:<12}{desc:<18}{a:>10,.2f}")

    def print_summary(self):
        print("\nTotals by category:")
        total = self.grand_total()
        for cat, amt in self.totals_by_category():
            pct = amt / total * 100 if total else 0
            bar = "#" * int(pct // 5)
            print(f"  {cat:<12}{amt:>10,.2f}  {pct:5.1f}%  {bar}")
        print(f"\n  {'TOTAL':<12}{total:>10,.2f}")


def demo():
    t = ExpenseTracker(":memory:")
    t.add("food", 350, "Lunch at campus", "2026-11-02")
    t.add("transport", 120, "Matatu fare", "2026-11-02")
    t.add("airtime", 100, "Data bundles", "2026-11-03")
    t.add("food", 500, "Groceries", "2026-11-05")
    t.add("books", 1200, "BCS311 textbook", "2026-11-06")
    t.add("transport", 150, "Matatu fare", "2026-11-09")
    print("=== All expenses ===")
    t.print_all()
    t.print_summary()
    t.delete(3)
    print("\n=== After deleting expense #3 ===")
    t.print_all()
    t.print_summary()


def menu():
    t = ExpenseTracker()
    while True:
        print("\n1) Add  2) List  3) Summary  4) Delete  5) Quit")
        choice = input("Choose: ").strip()
        if choice == "1":
            try:
                cat = input("Category: ")
                amt = float(input("Amount: "))
                desc = input("Description: ")
                t.add(cat, amt, desc)
                print("Saved.")
            except (ValueError, sqlite3.IntegrityError):
                print("Invalid input. Amount must be a positive number.")
        elif choice == "2":
            t.print_all()
        elif choice == "3":
            t.print_summary()
        elif choice == "4":
            try:
                ok = t.delete(int(input("ID to delete: ")))
                print("Deleted." if ok else "ID not found.")
            except ValueError:
                print("Enter a number.")
        elif choice == "5":
            break


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else menu()