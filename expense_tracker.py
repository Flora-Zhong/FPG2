import matplotlib.pyplot as plt

def data_visualization(categorized_data: dict):
    """ Plot a bar chart of a dictionary of categorized expense data. """
    plt.bar(list(categorized_data.keys()), list(categorized_data.values()))
    plt.title("Expense in Each Categories")
    plt.xlabel("Categories")
    plt.ylabel("Expense")
    plt.show()