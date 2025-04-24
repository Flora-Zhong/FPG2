import numpy as np
import matplotlib.pyplot as plt
import json

def menu():
    print("=== Weekly Expense Tracker ===")
    print("1. Add expanse")
    print("2. Add budget")
    print("3. Show weekly summary")
    print("4. Reset the week")
    print("5. Plot the data")
    print("6. Get weekly report PDF")
    print("0. Exit")

class InteractiveExpenseTracker:
    def __init__(self):
        username = input("Enter your username: ").strip()
        self.username = username.capitalize()
        self.data_file = f"data_{self.username}.json"
        self.history_file = f"history_{self.username}.json"

        self.weekly_totals = {}
        self.weekly_budgets = {}
        self.active = 1

        try:
            with open(self.data_file, "r") as f:
                print("Username detected, load previous data or create a new username?")
                choice = input("Press 1 for data loading, and press 2 for new username: ")
                valid_input = False
                while not valid_input:
                    try:
                        choice = int(choice)
                    except ValueError:
                        print("Please enter an integer.")
                        print()
                    else:
                        if choice == 1:
                            data = json.load(f)
                            self.weekly_totals = data.get("weekly_totals", {})
                            self.weekly_budgets = data.get("weekly_budgets", {})
                            print(f"Loaded data for user: {self.username}")
                            print()
                            f.close()
                            valid_input = True
                        elif choice == 2:
                            valid_input = True
                            f.close()
                            original_username = self.username
                            i = 2
                            while True:
                                new_username = f"{original_username}{i}"
                                new_data_file = f"data_{new_username}.json"
                                try:
                                    with open(new_data_file, "r") as file:
                                        file.close()
                                    i += 1
                                except FileNotFoundError:
                                    self.username = new_username
                                    print(f"Your username is now {self.username}!")
                                    print(f"New user: {self.username}")
                                    self.data_file = f"data_{self.username}.json"
                                    self.history_file = f"history_{self.username}.json"
                                    break
        except FileNotFoundError:
            print(f"New user: {self.username}")

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
                print("Please enter an integer between 0 and 6.")
                print()
                menu()
                print()
            else:
                if option == 1:
                    self.add_expense_flow()
                elif option == 2:
                    self.set_budget_flow()
                elif option == 3:
                    self.show_summary()
                elif option == 4:
                    self.reset_week()
                elif option == 5:
                    self.visualize_expenses()
                elif option == 6:
                    self.creating_report_pdf()
                elif option == 0:
                    print("Thank you for using Student Weekly Expense Tracker! Good bye!")
                    self.active = 0
                else:
                    print()
                    print("Invalid option. Please select from 0 to 6.")
                    print()
                    menu()
                    print()

    def add_expense_flow(self):
        """Handle expense entry process"""
        valid_input = False
        category = input("Category: ").strip()
        category = category.capitalize()

        # Auto-create category if not exists
        if category.capitalize() not in self.weekly_totals:
            self.handle_new_category(category = category)
        while not valid_input:
            try:
                amount = float(input("Enter amount: $").strip())
                self.add_expense(amount, category)
                print(f"Added ${amount:.2f} to {category}")
                valid_input = True

            except ValueError:
                print("Invalid amount! Please enter a number.")
                print()

    def handle_new_category(self, category: str):
        """Handle dynamic category creation"""
        category = category.capitalize()
        print(f"New category detected: {category}")
        while True:
            choice = input("Set weekly budget for this category? (yes/no): ").lower()
            if choice == 'yes':
                self.set_budget_flow(category)
                break
            elif choice == 'no':
                print(f"{category} will have no budget monitoring")
                self.weekly_budgets[category] = None
                break
            else:
                print("Please answer yes/no")

    def add_expense(self, amount: float, category: str):
        """Update totals and check budget"""
        category = category.capitalize()
        self.weekly_totals[category] = self.weekly_totals.get(category, 0) + amount
        self.check_budget(category)
        self.save_data()

    def set_budget_flow(self, predefined_category: str = None):
        """Budget setting workflow"""
        category = predefined_category or input("Category: ").strip()
        category = category.capitalize()
        valid_input = False
        while not valid_input:
            try:
                budget = float(input(f"Weekly budget for {category}: $").strip())
                if budget <= 0:
                    raise ValueError
                self.weekly_budgets[category] = budget
                print(f"Weekly budget for {category} set to ${budget:.2f}")
                valid_input = True
                self.save_data()
            except ValueError:
                print("Invalid budget! Must be a positive number.")

    def check_budget(self, category: str):
        category = category.capitalize()
        budget = self.weekly_budgets.get(category)
        if budget is None:
            return
        spent = self.weekly_totals[category]

        if spent > budget:
            print(f"OVERBUDGET! {category}: ${spent:.2f} / ${budget:.2f}")
        elif spent >= 0.9 * budget:
            print(f"WARNING: {category} at {spent / budget:.0%} ({spent:.2f}/{budget:.2f})")

    def show_summary(self):
        print("\n=== Weekly Summary ===")
        for category, spent in self.weekly_totals.items():
            budget = self.weekly_budgets.get(category)
            budget_info = f"Budget: ${budget:.2f}" if budget else "No budget set"
            progress = spent / budget if budget else 0
            progress_bar = self.create_progress_bar(progress) if budget else ""

            print(f"{category.upper():<15} ${spent:.2f}  {budget_info} {progress_bar}")

    @classmethod
    def create_progress_bar(cls, progress, length: int = 20):
        """Visualize budget progress"""
        filled = min(int(progress * length), length)
        return f"[{'█' * filled}{'░' * (length - filled)}] {min(progress * 100, 100):.0f}%"

    def reset_week(self):
        """Reset all weekly totals"""
        if self.weekly_totals == {}:
            print("Weekly totals is already empty!")
        else:
            self.weekly_totals.clear()
            print("Weekly totals cleared. History data has stored. Ready for new week!")
            self.save_data()

    def prepare_chart_data(self):
        """ Arrange data into a dictionary with the form of category: [expanse, budget]. """
        chart_data = {}
        all_categories = sorted(set(self.weekly_totals.keys()))

        for category in all_categories:
            expanse = self.weekly_totals.get(category)
            budget = self.weekly_budgets.get(category, 0)
            chart_data[category] = [expanse, budget]
            print(chart_data)
        return chart_data

    def plotting(self):
        """ Plot a grouped bar chart with organized data. """
        data = self.prepare_chart_data()
        categories = list(data.keys())
        expanses = [v[0] for v in data.values()]
        budgets = [v[1] for v in data.values()]

        fig, ax = plt.subplots(figsize = (12, 7))
        bar_width = 0.4
        x_indexes = np.arange(len(categories))
        bars_expanse = ax.bar(x_indexes - bar_width / 2, expanses, width = bar_width, color = "blue", label = "Expense")
        bars_budget = ax.bar(x_indexes + bar_width / 2, budgets, width = bar_width, color = "orange", label = "Budget")

        def add_labels(bars, color):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f'${height:.2f}', ha = "center", va = "bottom", color = color)

        add_labels(bars_expanse, "blue")
        add_labels(bars_budget, "orange")

        ax.set_title("Weekly Spending vs Budget Comparison", pad = 20)
        ax.set_xlabel("Categories", labelpad = 15)
        ax.set_ylabel("Amount ($)", labelpad = 15)
        ax.set_xticks(x_indexes)
        ax.set_xticklabels(categories, rotation = 45, ha = "right")
        ax.legend(framealpha = 0.9)

        ax.yaxis.grid(True, linestyle = "--", alpha = 0.6)
        ax.set_axisbelow(True)

        plt.tight_layout()
        return fig

    def visualize_expenses(self):
        fig = self.plotting()
        plt.show()
        plt.close(fig)

    def creating_report_pdf(self):
        fig = self.plotting()
        plt.savefig(f"weekly_report_{self.username}.pdf")
        plt.close(fig)

    def save_data(self):
        data = {
            "weekly_totals": self.weekly_totals,
            "weekly_budgets": self.weekly_budgets}
        with open(self.data_file, "w") as f:
            json.dump(data, f)

        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []

        snapshot = {
            "totals": self.weekly_totals.copy(),
            "budgets": self.weekly_budgets.copy()
        }
        history.append(snapshot)

        with open(self.history_file, "w") as f:
            json.dump(history, f)


if __name__ == "__main__":
    tracker = InteractiveExpenseTracker()
    tracker.start()
