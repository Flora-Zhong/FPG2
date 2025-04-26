import numpy as np
import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
import json
import csv

def menu():
    """ Print out the options for our student expense tracker. """
    print("=== Weekly Expense Tracker ===")
    print("1. Add expense")
    print("2. Add budget")
    print("3. Show weekly summary")
    print("4. Reset the week")
    print("5. Plot the data")
    print("6. Get weekly report PDF")
    print("7. Make an expense prediction for the next week")
    print("0. Exit") # We choose to use 0 instead of 8 here because we wrote this first and were keep adding functions by then.

class InteractiveExpenseTracker:
    def __init__(self):
        """ Initialize the instance of the InteractiveExpenseTracker class. """
        username = input("Enter your username: ").strip() # To make sure only the string itself is get here.
        self.username = username.capitalize() # To prevent the new username creation with upper and lower case.
        self.data_file = f"data_{self.username}.json"
        self.history_file = f"history_{self.username}.csv"
        self.current_week = 1
        self.init_history()
        self.weekly_totals = {}
        self.weekly_budgets = {}
        self.active = 1
        try:
            with open(self.data_file, "r") as data_file:
                print("Username detected, load previous data or create a new username?")
                valid_input = False
                while not valid_input:
                    choice = input("Press 1 for data loading, and press 2 for new username: ")
                    try:
                        choice = int(choice)
                    except ValueError:
                        print("Please enter an integer between 1 and 2.")
                        print()
                    else:
                        if choice == 1:
                            data = json.load(data_file)
                            self.weekly_totals = data.get("weekly_totals", {})
                            self.weekly_budgets = data.get("weekly_budgets", {})
                            print(f"Loaded data for user: {self.username}")
                            print()
                            valid_input = True
                        elif choice == 2:
                            valid_input = True
                            original_username = self.username
                            i = 2
                            while True:
                                new_username = f"{original_username}{i}"
                                new_data_file = f"data_{new_username}.json"
                                try:
                                    file = open(new_data_file, "r")
                                    file.close()
                                    i += 1
                                except FileNotFoundError:
                                    self.username = new_username
                                    print(f"Your username is now {self.username}!")
                                    print(f"New user: {self.username}")
                                    self.data_file = f"data_{self.username}.json"
                                    self.history_file = f"history_{self.username}.json"
                                    break
                        else:
                            print("Please choose from 1 and 2.")
                            print()
        except FileNotFoundError:
            print(f"New user: {self.username}")

    def main(self):
        """ The main interactive loop of the main program. """
        menu()
        while self.active == 1:
            print()
            option = input("Please select an option: ")
            try:
                option = int(option)
            except ValueError:
                print()
                print("Please enter an integer between 0 and 7.")
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
                    print("The plot has been created.")
                    print()
                elif option == 6:
                    self.creating_report_pdf()
                    print("The report has been created.")
                    print()
                elif option == 7:
                    self.expense_prediction()
                elif option == 0:
                    print("Thank you for using Student Weekly Expense Tracker! Good bye!")
                    self.active = 0
                else:
                    print()
                    print("Invalid option. Please select from 0 to 7.")
                    print()
                    menu()
                    print()

    def add_expense_flow(self):
        """ Add the expense to the category. """
        valid_input = False
        category = input("Category: ").strip()
        category = category.capitalize() # To prevent the new category creation with upper and lower case.
        if category.capitalize() not in self.weekly_totals:
            self.handle_new_category(category = category)
        while not valid_input:
            try:
                amount = float(input("Enter amount: $").strip())
                if amount <= 0:
                    raise ValueError
                self.add_expense(amount, category)
                print(f"Added ${amount:.2f} to {category}")
                valid_input = True
            except ValueError:
                print("Invalid amount! Please enter a positive number.")
                print()

    def handle_new_category(self, category: str):
        """ To create a new category for the week. """
        category = category.capitalize()
        print(f"New category detected: {category}")
        print("Automatically set it as weekly budget category.")
        self.set_budget_flow(category)


    def add_expense(self, amount: float, category: str):
        """ Update totals and check budget. """
        category = category.capitalize()
        self.weekly_totals[category] = self.weekly_totals.get(category, 0) + amount
        self.check_budget(category)
        self.save_current_data()

    def set_budget_flow(self, predefined_category: str = None):
        """ Budget setting workflow. """
        category = predefined_category or input("Category: ").strip()
        category = category.capitalize()
        if category not in self.weekly_totals:
            self.weekly_totals[category] = 0
        valid_input = False
        while not valid_input:
            try:
                budget = float(input(f"Weekly budget for {category}: $").strip())
                if budget <= 0:
                    raise ValueError
                self.weekly_budgets[category] = budget
                print(f"Weekly budget for {category} set to ${budget:.2f}")
                valid_input = True
                self.save_current_data()
            except ValueError:
                print("Invalid budget! Budget must be a positive number.")
                print()

    def check_budget(self, category: str):
        """ To check whether expense is close or over the budget or not and gives out warnings. """
        category = category.capitalize()
        budget = self.weekly_budgets.get(category)
        if budget is not None:
            spent = self.weekly_totals[category]
            if spent > budget:
                print(f"WARNING: OVER BUDGET! {category}: ${spent:.2f} / ${budget:.2f}")
            elif spent >= 0.8 * budget:
                print(f"WARNING: {category} at {spent / budget:.0%} ({spent:.2f}/{budget:.2f})")

    def show_summary(self):
        """ To show a weekly expense summary. """
        print()
        print("=== Weekly Summary ===")
        for category, spent in self.weekly_totals.items():
            budget = self.weekly_budgets.get(category)
            if budget is not None:
                budget_info = f"Budget: ${budget:.2f}"
                progress = spent / budget
                progress_bar = self.create_progress_bar(progress)
            else:
                budget_info = "No budget set."
                progress_bar = ""
            print(f"{category.upper():<15} ${spent:.2f}  {budget_info} {progress_bar}")

    @classmethod
    def create_progress_bar(cls, progress: float, length: int = 20):
        """ Visualize budget progress. """
        filled = min(int(progress * length), length)
        return f"[{"█" * filled}{"░" * (length - filled)}] {min(progress * 100, 100):.0f}%"

    def reset_week(self):
        """ Reset all weekly totals and record history data. """
        if self.weekly_totals == {}:
            print("Weekly totals is already empty!")
        else:
            self.update_history()
            self.save_history()
            self.weekly_totals.clear()
            print(f"Weekly totals for week {self.current_week - 1} cleared. History data has stored. Ready for new week {self.current_week}!")
            self.save_current_data()

    def prepare_chart_data(self):
        """ Arrange data into a dictionary with the form of category: [expanse, budget]. """
        chart_data = {}
        all_categories = sorted(set(self.weekly_totals.keys()))
        for category in all_categories:
            expense = self.weekly_totals.get(category)
            budget = self.weekly_budgets.get(category, 0)
            chart_data[category] = [expense, budget]
        return chart_data

    def plotting(self):
        """ Create a grouped bar chart with organized data. """
        data = self.prepare_chart_data()
        categories = list(data.keys())
        expanses = [values[0] for values in data.values()]
        budgets = [values[1] for values in data.values()]
        fig, ax = plt.subplots()
        bar_width = 0.35
        x_indexes = np.arange(len(categories))
        bars_expanse = ax.bar(x_indexes - bar_width / 2, expanses, width = bar_width, color = "blue", label = "Expense")
        bars_budget = ax.bar(x_indexes + bar_width / 2, budgets, width = bar_width, color = "orange", label = "Budget")

        def add_labels(bars: BarContainer, color: str):
            """ Add value labels to the bars. """
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height, f"${height:.2f}", ha = "center", va = "bottom", color = color)

        add_labels(bars_expanse, "blue") # Blue is the color of UF! Since we do not know what the exact name of the UF blue, we will just use "blue" here.
        add_labels(bars_budget, "orange") # Orange is also the color of UF! Since we do not know what the exact name of the UF orange, we will just use "orange" here.
        ax.set_title(f"{self.username}'s Week {self.current_week} Expense vs. Budget Comparison")
        ax.set_xlabel("Categories")
        ax.set_ylabel("Amount ($)")
        ax.set_xticks(x_indexes)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.yaxis.grid(True, linestyle = "--")
        ax.set_axisbelow(True)
        plt.tight_layout()
        return fig

    def visualize_expenses(self):
        """ Plot the grouped bar chart created before. """
        fig = self.plotting()
        plt.show()
        plt.close(fig)

    def creating_report_pdf(self):
        """ Turn the grouped bar chart into a PDF file. """
        fig = self.plotting()
        plt.savefig(f"weekly_report_{self.username}.pdf")
        plt.close(fig)

    def save_current_data(self):
        """ Save current weekly data to files. """
        data = {
            "weekly_totals": self.weekly_totals,
            "weekly_budgets": self.weekly_budgets,
            "current_week": self.current_week
        }
        with open(self.data_file, "w") as data_file:
            json.dump(data, data_file)

    def init_history(self):
        """ Initialize or retrieve history data. """
        try:
            with open(self.history_file, "r") as history_data_file:
                reader = csv.reader(history_data_file)
                rows = [row for row in reader if row]
                if rows == []:
                    raise FileNotFoundError
                try:
                    self.current_week = int(rows[0][0])
                except (IndexError, ValueError):
                    self.current_week = 1
                self.history = {}
                for row in rows[1:]:
                    if len(row) < 1:
                        continue
                    category = row[0]
                    amounts = []
                    for amount in row[1:]:
                        try:
                            val = float(amount)
                            if not np.isnan(val):
                                amounts.append(val)
                        except ValueError:
                            amounts.append(np.nan) # To have differences between real 0 data and error data.
                    self.history[category] = amounts
        except FileNotFoundError:
            self.history = {}
            with open(self.history_file, "w", newline = "") as history_data_file:
                writer = csv.writer(history_data_file)
                writer.writerow([self.current_week])

    def update_history(self):
        """ Update history data when reset the week. """
        all_categories = set(self.history.keys()) | set(self.weekly_totals.keys())
        for category in all_categories:
            current_data = self.weekly_totals.get(category, 0)
            if category not in self.history:
                self.history[category] = [0] * (self.current_week - 1)
            while len(self.history[category]) < self.current_week - 1:
                self.history[category].append(0) # Add 0 means that no expense for this category for previous weeks, which will help future predictions.
            self.history[category].append(current_data)

    def save_history(self):
        """ Save the updated history data. """
        self.current_week += 1
        with open(self.history_file, "w") as history_data_file:
            writer = csv.writer(history_data_file)
            writer.writerow([self.current_week])
            for category in sorted(self.history.keys()):
                formatted_data = [f"{x:.2f}" for x in self.history[category]]
                writer.writerow([category] + formatted_data)

    def expense_prediction(self):
        """ Show expense prediction for the next week. """
        if self.history == {}:
            print("No historical data available for prediction.")
        else:
            print()
            print("=== Prediction Statistics ===")
            for category in sorted(self.history.keys()):
                print()
                data = self.history[category]
                if len(data) < 1:
                    continue
                arr = np.array(data)
                print(f"{category} expense prediction:")
                print(f"History weeks: {len(data)} weeks")
                print(f"Mean: ${arr.mean():.2f}")
                print(f"Median: ${np.median(arr):.2f}")
                print(f"Standard deviation: ${arr.std():.2f}")
                print(f"Predicted expense for the next week: ${max(0, arr.mean() - arr.std()):.2f} - ${arr.mean() + arr.std():.2f}") # max() is to prevent negative values, and the prediction is based on ± 1 sd, which is a common way of data prediction that we've learned in statistics classes.


if __name__ == "__main__":
    tracker = InteractiveExpenseTracker()
    tracker.main()