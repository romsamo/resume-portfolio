import matplotlib.pyplot as plt

# Function to create a scatter plot for a given category
def create_scatter_plot(dataframe, title, x_col, y_col, x_label, y_label):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Clean up the columns to remove '%' and convert to float
    dataframe[x_col] = dataframe[x_col].replace({'%': ''}, regex=True).astype(float)
    dataframe[y_col] = dataframe[y_col].replace({'%': ''}, regex=True).astype(float)

    # X-axis and Y-axis
    x = dataframe[x_col]
    y = dataframe[y_col]

    # Plot scatter points
    scatter = ax.scatter(x, y, s=100, alpha=0.6)

    # Add labels to each point (ticker symbols)
    for i, symbol in enumerate(dataframe.iloc[:, 0]):  # Assuming first column is ticker symbol
        ax.text(x[i] + 0.2, y[i] + 0.2, symbol, fontsize=9, ha='center')

    # Add quadrant lines (median)
    x_median = x.median()
    y_median = y.median()
    ax.axhline(y=y_median, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=x_median, color='gray', linestyle='--', alpha=0.5)

    # Determine plot limits
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    # Add quadrant labels
    ax.text(x_max * 0.9, y_max * 0.9, 'Strong RS% and Good % Advance', fontsize=10, color='green', ha='right')
    ax.text(x_max * 0.9, y_min * 1.1, 'Good % Advance, Weak RS%', fontsize=10, color='orange', ha='right')
    ax.text(x_min * 1.1, y_max * 0.9, 'Strong RS% but Bad % Advance', fontsize=10, color='blue', ha='left')
    ax.text(x_min * 1.1, y_min * 1.1, 'Weak RS% and Weak % Advance', fontsize=10, color='red', ha='left')

    # Customize plot
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True)

    fig.tight_layout()  # Adjust layout

    return fig
