import numpy as np
import matplotlib.pyplot as plt

def menu():
    print("=== Weekly Expense Tracker ===")
    print("1. Add expanse")
    print("2. Add budget")
    print("3. Show weekly summary")
    print("4. Reset the week")
    print("5. Exit")

class InteractiveExpenseTracker:
    def __init__(self):
        self.weekly_totals = {} 
        self.weekly_budgets = {}  
        self.active = 1

    def start(self):
        """Main interactive loop"""
        menu()

        while self.active == 1:
            print()
            option = input("Please select an option: ")
            try:
                option = int(option)
            except ValueError:
                print()
                print("Please enter an integer between 1 and 5.")
                print()
                menu()
                print()
            else:
                if option == 1:
                    self._add_expense_flow()
                elif option == 2:
                    self._set_budget_flow()
                elif option == 3:
                    self._show_summary()
                elif option == 4:
                    self._reset_week()
                elif option == 5:
                    print("Thank you for using Student Daily Usage & Expense Tracker! Good bye!")
                    self.active = 0
                else:
                    print()
                    print("Invalid option. Please select from 1 to 5.")
                    print()
                    menu()
                    print()

    def _add_expense_flow(self):
        """Handle expense entry process"""
        valid_input = False
        while not valid_input:
            try:
                amount = float(input("Enter amount: $").strip())
                category = input("Category: ").strip()
                category = category.capitalize()

                # Auto-create category if not exists
                if category.capitalize() not in self.weekly_totals:
                    self._handle_new_category(category)

                self._add_expense(amount, category)
                print(f"✅ Added ${amount:.2f} to {category}")
                valid_input = True

            except ValueError:
                print("Invalid amount! Please enter a number.")
                print()

    def _handle_new_category(self, category):
        """Handle dynamic category creation"""
        category = category.capitalize()
        print(f"New category detected: {category}")
        while True:
            choice = input("Set weekly budget for this category? (y/n): ").lower()
            if choice == 'y':
                self._set_budget_flow(category)
                break
            elif choice == 'n':
                print(f"{category} will have no budget monitoring")
                self.weekly_budgets[category] = None
                break
            else:
                print("Please answer y/n")

    def _add_expense(self, amount, category):
        """Update totals and check budget"""
        category = category.capitalize()
        self.weekly_totals[category] = self.weekly_totals.get(category, 0) + amount
        self._check_budget(category)

    def _set_budget_flow(self, predefined_category=None):
        """Budget setting workflow"""
        category = predefined_category or input("Category: ").strip()
        category = category.capitalize()
        try:
            budget = float(input(f"Weekly budget for {category}: $").strip())
            if budget <= 0:
                raise ValueError
            self.weekly_budgets[category] = budget
            print(f"✅ Weekly budget for {category} set to ${budget:.2f}")
        except ValueError:
            print("Invalid budget! Must be a positive number.")

    def _check_budget(self, category):
        category = category.capitalize()
        budget = self.weekly_budgets.get(category)
        if budget is None:
            return
        spent = self.weekly_totals[category]

        if spent > budget:
            print(f"OVERBUDGET! {category}: ${spent:.2f} / ${budget:.2f}")
        elif spent >= 0.9 * budget:
            print(f"WARNING: {category} at {spent / budget:.0%} ({spent:.2f}/{budget:.2f})")

    def _show_summary(self):
        print("\n=== Weekly Summary ===")
        for category, spent in self.weekly_totals.items():
            budget = self.weekly_budgets.get(category)
            budget_info = f"Budget: ${budget:.2f}" if budget else "No budget set"
            progress = spent / budget if budget else 0
            progress_bar = self._create_progress_bar(progress) if budget else ""

            print(f"{category.upper():<15} ${spent:.2f}  {budget_info} {progress_bar}")

    def _create_progress_bar(self, progress, length=20):
        """Visualize budget progress"""
        filled = min(int(progress * length), length)
        return f"[{'█' * filled}{'░' * (length - filled)}] {min(progress * 100, 100):.0f}%"

    def _reset_week(self):
        """Reset all weekly totals"""
        if self.weekly_totals == {}:
            print("Weekly totals is already empty!")
        else:
            self.weekly_totals.clear()
            print("Weekly totals cleared. Ready for new week!")


if __name__ == "__main__":
    tracker = InteractiveExpenseTracker()
    tracker.start()
