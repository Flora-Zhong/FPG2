import numpy as np
import matplotlib.pyplot as plt

def select_category(category_list： list):
    """
    Display the available expense categories and allow the user to either choose an existing category or add a new one.

    Parameters:
        category_list: A list containing the current expense category names.

    Returns:
        str: The selected expense category, either chosen from the list or added by the user.
    """
    while True:
        print("\nAvailable Categories:")
        for index, category in enumerate(category_list, start=1):
            print(f"{index}. {category}")
        print(f"{len(category_list) + 1}. Add a New Category")
        choice_input = input("Please select a category by number: ").strip()
        try:
            choice_number = int(choice_input)
            if choice_number == len(category_list) + 1:
                new_category = input("Enter the new category name: ").strip()
                if new_category:
                    category_list.append(new_category)
                    print(f"Category '{new_category}' added.")
                    return new_category
                else:
                    print("Category name cannot be empty. ")
            elif 1 <= choice_number <= len(category_list):
                selected_category = category_list[choice_number - 1]
                return selected_category
            else:
                print("Please enter a valid number from the list.")
        except ValueError:
            print("Please enter a numeric value.")

def add_expense(expenses: list, category_list: list):
    """
    Enable the user to enter details for a new expense record and append it to the expense records list with the following details: date, amount, category, and additional notations (optional).
    
    Parameters:
        expense_records: A list to which the new expense record will be appended.
        category_list: A list of available expense categories.
    
    Returns:
        None
    """
    date_str = input('Enter the date (YYYY-MM-DD): ').strip()
    while True:
        amount_str = input('Enter the amount: ').strip()
        try:
            amount_value = float(amount_str)
            break
        except ValueError:
            print('Please enter a valid numeric value.')
    selected_category = select_category(category_list)
    expense_notes = input('Enter any additional notes (optional): ').strip()
    expense_record = {
        'date': date_str,
        'amount': amount_value,
        'category': selected_category,
        'notes': expense_notes
    }
    expense_records.append(expense_record)
    print("Expense added!")

def view_expenses(expense_records: list):
    """
    Display all recorded expense entries along with computed statistics such as total and average expense amounts using NumPy.

    Parameters:
        expense_records: A list of expense records to display.

    Returns:
        None
    """
    if not expense_records:
        print("No expense records available.")
        return
    print("\nAll Recorded Expenses:")
    for index, record in enumerate(expense_records, start=1):
        print(f"{index}. Date: {record['date']}, Amount: {record['amount']}, "
              f"Category: {record['category']}, Notes: {record['notes']}")
    amount_list = np.array([record['amount'] for record in expense_records])
    total_expense = np.sum(amount_list)
    average_expense = np.mean(amount_list)
    print(f"\nTotal Expense Amount: {total_expense}")
    print(f"Average Expense Amount: {average_expense:.2f}")

def data_visualization(categorized_data: dict):
    """ Plot a bar chart of a dictionary of categorized expense data. """
    plt.bar(list(categorized_data.keys()), list(categorized_data.values()))
    plt.title("Expense in Each Categories")
    plt.xlabel("Categories")
    plt.ylabel("Expense")
    plt.show()
