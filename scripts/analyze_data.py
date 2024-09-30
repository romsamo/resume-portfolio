import pandas as pd
import matplotlib.pyplot as plt
import os

# Load your cleaned trades data
cleaned_file_path = '/Users/romano/Desktop/twitterBot/data/cleaned_data.csv'
cleaned_data = pd.read_csv(cleaned_file_path)

# Convert 'Date Sold' to datetime
cleaned_data['Date Sold'] = pd.to_datetime(cleaned_data['Date Sold'], errors='coerce')

# Add a 'Month' column to group by month and year
cleaned_data['Month'] = cleaned_data['Date Sold'].dt.to_period('M')

# Group the data by month
monthly_groups = cleaned_data.groupby('Month')

# Initialize a DataFrame to store the metrics
monthly_metrics = pd.DataFrame()

# 1. ($ Gain / Loss)
monthly_metrics['$ Gain / Loss'] = monthly_groups['Profit(Loss) $'].sum()

# 2. (% Gain / Loss): Sum the percentage profit/loss for each month
monthly_metrics['% Gain / Loss'] = monthly_groups['Profit(Loss) %'].sum()

# 3. Win %: Ratio of winning trades (profit > 0) to total trades
monthly_metrics['Win %'] = (monthly_groups.apply(lambda x: (x['Profit(Loss) $'] > 0).mean())) * 100

# 4. Average Winner %: Average percentage gain of winning trades
monthly_metrics['Average Winner %'] = monthly_groups.apply(lambda x: x.loc[x['Profit(Loss) $'] > 0, 'Profit(Loss) %'].mean())

# 5. Average Loser %: Average percentage loss of losing trades
monthly_metrics['Average Loser %'] = monthly_groups.apply(lambda x: x.loc[x['Profit(Loss) $'] < 0, 'Profit(Loss) %'].mean())

# 6. Best Win: Largest gain in a single trade in a month
monthly_metrics['Best Win $'] = monthly_groups['Profit(Loss) $'].max()
monthly_metrics['Best Win %'] = monthly_groups['Profit(Loss) %'].max()

# 7. Worst Loss: Largest loss in a single trade in a month
monthly_metrics['Worst Loss $'] = monthly_groups['Profit(Loss) $'].min()
monthly_metrics['Worst Loss %'] = monthly_groups['Profit(Loss) %'].min()

# 8. Profit / Loss Ratio: Average profit divided by average loss
monthly_metrics['Profit / Loss Ratio'] = monthly_groups.apply(lambda x: (
    x.loc[x['Profit(Loss) $'] > 0, 'Profit(Loss) $'].mean() /
    -x.loc[x['Profit(Loss) $'] < 0, 'Profit(Loss) $'].mean() if not x.loc[x['Profit(Loss) $'] < 0].empty else 0))

# 9. Trades Closed: Total number of trades closed in the month
monthly_metrics['Trades Closed'] = monthly_groups.size()

# 10. Average R Gain: Average R gain for winning trades
monthly_metrics['Average R Gain'] = monthly_groups.apply(lambda x: x.loc[x['Profit(Loss) $'] > 0, 'risk/Reward ratio'].mean())

# 11. Average R Loss: Average R loss for losing trades
monthly_metrics['Average R Loss'] = monthly_groups.apply(lambda x: x.loc[x['Profit(Loss) $'] < 0, 'risk/Reward ratio'].mean())

# 12. Average R Gain/Loss Ratio: Ratio of R gain to R loss
monthly_metrics['Average R Gain/Loss Ratio'] = monthly_metrics['Average R Gain'] / -monthly_metrics['Average R Loss']

# 13. Account Return $ per Month (Total Gain/Loss for the month)
monthly_metrics['Account Return $'] = monthly_metrics['$ Gain / Loss']
monthly_metrics['Account Return %'] = monthly_groups['Profit(Loss) %'].sum()

# Save the DataFrame
transposed_metrics = monthly_metrics.T
transposed_metrics.to_csv('/Users/romano/Desktop/twitterBot/data/monthly_metrics.csv', index=True)

# Create a directory to save the plots if it doesn't exist
plot_dir = '/Users/romano/Desktop/twitterBot/data/plots'
os.makedirs(plot_dir, exist_ok=True)

# Load monthly_metrics.csv for scatter plots
monthly_metrics = pd.read_csv('/Users/romano/Desktop/twitterBot/data/monthly_metrics.csv', index_col=0)

# Loop over each month's column and generate scatter plots
for month in monthly_metrics.columns:
    plt.figure(figsize=(10, 6))

    # Scatter plot for each month's data
    data = cleaned_data[cleaned_data['Month'] == month]
    plt.scatter(data['Duration'], data['Profit(Loss) %'], c=data['Profit(Loss) %'], cmap='coolwarm', s=150, alpha=0.75)

    # Add text annotations for each stock
    for i, ticker in enumerate(data['Ticker']):
        plt.text(data['Duration'].iloc[i], data['Profit(Loss) %'].iloc[i] + 0.5, ticker, fontsize=9, ha='center')

    # Customize the plot
    plt.title(f'Stock Performance vs Duration for {month}', fontsize=16)
    plt.xlabel('Duration (Days)', fontsize=14)
    plt.ylabel('Performance (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.colorbar(label='Performance (%)')

    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, f'scatter_{month}.png'))
    plt.close()

# Create bar charts
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

colors_dollars = ['green' if val > 0 else 'red' for val in monthly_metrics.loc['$ Gain / Loss']]
ax1.bar(monthly_metrics.columns, monthly_metrics.loc['$ Gain / Loss'], color=colors_dollars, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Month', fontsize=14, labelpad=10)
ax1.set_ylabel('$ Gain / Loss', fontsize=14, labelpad=10)
ax1.set_title('Monthly Performance in $', fontsize=18, pad=15)
ax1.grid(True, which='both', axis='both', linestyle='--', alpha=0.7)

colors_percent = ['green' if val > 0 else 'red' for val in monthly_metrics.loc['% Gain / Loss']]
ax2.bar(monthly_metrics.columns, monthly_metrics.loc['% Gain / Loss'], color=colors_percent, edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Month', fontsize=14, labelpad=10)
ax2.set_ylabel('% Gain / Loss', fontsize=14, labelpad=10)
ax2.set_title('Monthly Performance in %', fontsize=18, pad=15)
ax2.grid(True, which='both', axis='both', linestyle='--', alpha=0.7)

ax1.tick_params(axis='x', rotation=45)
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(plot_dir, 'bar_charts.png'))
plt.close()

# Final trading stats calculation and saving
total_trades = len(cleaned_data)
winning_trades = cleaned_data[cleaned_data['Profit(Loss) $'] > 0]
losing_trades = cleaned_data[cleaned_data['Profit(Loss) $'] < 0]

hit_ratio = (len(winning_trades) / total_trades) * 100
avg_win = winning_trades['Profit(Loss) $'].mean()
avg_loss = -losing_trades['Profit(Loss) $'].mean()  # Use negative of loss
profit_loss_ratio = avg_win / avg_loss if avg_loss != 0 else None

realized_avg_win_percent = winning_trades['Profit(Loss) %'].mean()
realized_avg_loss_percent = losing_trades['Profit(Loss) %'].mean()

avg_hold_period_win = winning_trades['Duration'].mean()
avg_hold_period_loss = losing_trades['Duration'].mean()

hit_ratio_decimal = len(winning_trades) / total_trades
expected_value = (hit_ratio_decimal * realized_avg_win_percent) + ((1 - hit_ratio_decimal) * realized_avg_loss_percent)

# Save the total trading stats
total_stats = pd.DataFrame({
    'Hit Ratio (%)': [hit_ratio],
    'Profit / Loss Ratio': [profit_loss_ratio],
    'Realized Average Win % Per Trade': [realized_avg_win_percent],
    'Realized Average Loss % Per Trade': [realized_avg_loss_percent],
    'Average Hold Period For Winning Trades (Days)': [avg_hold_period_win],
    'Average Hold Period For Losing Trades (Days)': [avg_hold_period_loss],
    'Expected Value (EV)': [expected_value]
})


transposed_total_stats = total_stats.T
transposed_total_stats.to_csv('/Users/romano/Desktop/twitterBot/data/total_stats.csv', index=True)

# Create a directory to save the plots if it doesn't exist
plot_dir = '/Users/romano/Desktop/twitterBot/data/plots'
os.makedirs(plot_dir, exist_ok=True)


# Create a bar chart with stock names on Y-axis and $ Gain/Loss on X-axis
def plot_gain_loss_by_stock(data, plot_dir):
    # Sorting data by gain/loss
    sorted_data = data[['Ticker', 'Profit(Loss) $']].groupby('Ticker').sum().sort_values('Profit(Loss) $')

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(sorted_data.index, sorted_data['Profit(Loss) $'],
             color=['green' if x > 0 else 'red' for x in sorted_data['Profit(Loss) $']])

    # Customize the plot
    plt.xlabel('$ Gain / Loss', fontsize=14)
    plt.ylabel('Stock', fontsize=14)
    plt.title('Stock Performance: $ Gain / Loss', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'stock_gain_loss.png'))
    plt.close()


# Generate the chart
plot_gain_loss_by_stock(cleaned_data, plot_dir)
