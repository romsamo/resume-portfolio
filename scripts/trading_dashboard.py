import os
import streamlit as st
import pandas as pd
import yfinance as yf
from plots import create_scatter_plot

# Set paths to images
plot_dir = '/Users/romano/Desktop/twitterBot/data/plots'

# Load the calculated data
monthly_metrics = pd.read_csv('/Users/romano/Desktop/twitterBot/data/monthly_metrics.csv', index_col=0)
total_stats = pd.read_csv('/Users/romano/Desktop/twitterBot/data/total_stats.csv')

# Set up the Streamlit app layout
st.title('Trading Performance Dashboard')

# Create tabs for the different views
tab1, tab2, tab3, tab4 = st.tabs(["Total Trading Stats", "Monthly Stats", "Charts", "Market Breadth"])

# First tab: Total Trading Stats
with tab1:
    st.subheader('Total Trading Stats')
    st.table(total_stats)

# Second tab: Monthly Stats
with tab2:
    st.subheader('Monthly Stats')
    st.table(monthly_metrics)

# Third tab: Display the saved plots
with tab3:
    st.subheader("Scatter Plots by Month")

    # Since months are stored as columns, we iterate over the columns (months)
    for month in monthly_metrics.columns:
        image_path = os.path.join(plot_dir, f'scatter_{month}.png')
        st.image(image_path, caption=f'Stock Performance vs Duration for {month}')

    # Display bar charts
    st.subheader('Monthly Performance in $ and %')
    st.image(os.path.join(plot_dir, 'bar_charts.png'), caption='Monthly Gain/Loss ($ and %)')

    # Display the new stock gain/loss chart
    st.subheader('Stock Gain/Loss Chart')
    st.image(os.path.join(plot_dir, 'stock_gain_loss.png'), caption='Stock Performance: $ Gain / Loss')


# Function to add '52w Low' and '52w High' to the DataFrame
def add_52_week_columns(df, ticker_dict, category_name):
    for ticker in ticker_dict.keys():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")  # Fetch 1 year data

        # Calculate % gain from 52w low and % gain from 52w high
        df.loc[df[category_name] == ticker, '52w Low'] = (float(
            df.loc[df[category_name] == ticker, 'Last'].replace({'$': ''}, regex=True)) - hist['Close'].min()) / hist[
                                                             'Close'].min() * 100
        df.loc[df[category_name] == ticker, '52w High'] = (float(
            df.loc[df[category_name] == ticker, 'Last'].replace({'$': ''}, regex=True)) - hist['Close'].max()) / hist[
                                                              'Close'].max() * 100
    return df


# Function to fetch stock data and calculate Last Price, RS%, and % Chg Week/Month
def fetch_market_data(tickers):
    market_data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)

        # Fetch last price
        last_price = stock.history(period="1d")['Close'].iloc[-1]
        weekly_history = stock.history(period="5d")
        monthly_history = stock.history(period="1mo")

        # Calculate weekly and monthly changes
        if len(weekly_history) >= 2:
            week_ago_price = weekly_history['Close'].iloc[0]
            chg_week = ((last_price - week_ago_price) / week_ago_price) * 100 if week_ago_price != 0 else 0
        else:
            chg_week = 0  # Set to 0 if not enough data

        if len(monthly_history) >= 2:
            month_ago_price = monthly_history['Close'].iloc[0]
            chg_month = ((last_price - month_ago_price) / month_ago_price) * 100 if month_ago_price != 0 else 0
        else:
            chg_month = 0  # Set to 0 if not enough data

        # Add fetched data to market_data dictionary
        market_data[ticker] = {
            'Last Price': last_price,
            '% Chg Week': chg_week,
            '% Chg Month': chg_month
        }

    return market_data


# Function to calculate relative strength vs SPY
def calculate_relative_strength(market_data, spy_price):
    for ticker, data in market_data.items():
        relative_strength = ((data['Last Price'] - spy_price) / spy_price) * 100
        market_data[ticker]['RS%'] = 100 + relative_strength  # Showing as 100 + actual result
    return market_data


# Define tickers and descriptions
tickers_main = {
    'SPY': 'S&P 500', 'RSP': 'EW S&P 500', 'QQQ': 'Nasdaq 100', 'DIA': 'Dow Jones Ind', 'IWM': 'Russell 2000',
    'IWN': 'Russell 2000 Value', 'IWO': 'Russell 2000 Growth', 'GLD': 'Gold', 'USO': 'Oil', 'TLT': '20+ Bonds',
    'IBIT': 'Bitcoin'
}

tickers_sectors = {
    'XLC': 'Communication', 'XLK': 'Technology', 'XLY': 'Consumer Discretionary', 'XLP': 'Consumer Staples',
    'XLF': 'Financials', 'XLRE': 'Real Estate', 'XLU': 'Utilities', 'XLE': 'Energy', 'XLB': 'Materials',
    'XLI': 'Industrials', 'XLV': 'Healthcare', 'XBI': 'Biotech', 'XHB': 'Home Builders'
}

tickers_subsectors = {
    'CIBR': 'Cybersecurity', 'DRIV': 'Electric Cars', 'XSD': 'Semiconductors', 'ROBO': 'Robotics',
    'XAR': 'Aerospace & Defense', 'JETS': 'Airlines', 'BOAT': 'Shipping', 'COPX': 'Copper Mining'
}

tickers_core7 = {
    'NVDA': 'Semiconductors', 'TSLA': 'EVs', 'MSFT': 'Tech Services', 'AAPL': 'Electronic Tech',
    'GOOGL': 'Tech Services', 'AMZN': 'Retail Trade', 'META': 'Tech Services'
}

# Combine all tickers into one list
all_tickers = {**tickers_main, **tickers_sectors, **tickers_subsectors, **tickers_core7}

# Fetch stock data
market_data = fetch_market_data(all_tickers.keys())

# Calculate relative strength compared to SPY
spy_price = market_data['SPY']['Last Price']
market_data = calculate_relative_strength(market_data, spy_price)


# Helper function to create the data table
# Helper function to create the data table
def create_data_table(tickers_dict, category_name):
    table_data = []
    for ticker, description in tickers_dict.items():
        table_data.append([
            ticker, description,
            f"${market_data[ticker]['Last Price']:.2f}",
            f"{market_data[ticker]['RS%']:.2f}%",
            f"{market_data[ticker]['% Chg Week']:.2f}%",
            f"{market_data[ticker]['% Chg Month']:.2f}%"
        ])

    # Create DataFrame
    df = pd.DataFrame(table_data, columns=[category_name, 'Description', 'Last', 'RS%', '% Chg Week', '% Chg Month'])

    # Remove dollar sign from 'Last' and convert to float for calculations
    df['Last'] = df['Last'].replace({'\$': ''}, regex=True).astype(float)

    # Add 52-week columns after creating the table
    df = add_52_week_columns(df, tickers_dict, category_name)

    return df


# Creating Scatter Plots for Market Breadth
with tab4:
    st.subheader('Market Breadth')

    # Main Data
    st.subheader('Main')
    main_df = create_data_table(tickers_main, 'MAIN')
    st.table(main_df)

    # Scatter Plot for Main - % Chg Week
    st.subheader('Scatter Plot for Main (% Chg Week)')
    scatter_main_week = create_scatter_plot(main_df, 'Main: RS% vs % Chg Week', '% Chg Week', 'RS%', '% Change Week',
                                            'RS %')
    st.pyplot(scatter_main_week)

    # Scatter Plot for Main - % Chg Month
    st.subheader('Scatter Plot for Main (% Chg Month)')
    scatter_main_month = create_scatter_plot(main_df, 'Main: RS% vs % Chg Month', '% Chg Month', 'RS%',
                                             '% Change Month', 'RS %')
    st.pyplot(scatter_main_month)

    # Sectors Data
    st.subheader('Sectors')
    sectors_df = create_data_table(tickers_sectors, 'SECTORS')
    st.table(sectors_df)

    # Scatter Plot for Sectors - % Chg Week
    st.subheader('Scatter Plot for Sectors (% Chg Week)')
    scatter_sectors_week = create_scatter_plot(sectors_df, 'Sectors: RS% vs % Chg Week', '% Chg Week', 'RS%',
                                               '% Change Week', 'RS %')
    st.pyplot(scatter_sectors_week)

    # Scatter Plot for Sectors - % Chg Month
    st.subheader('Scatter Plot for Sectors (% Chg Month)')
    scatter_sectors_month = create_scatter_plot(sectors_df, 'Sectors: RS% vs % Chg Month', '% Chg Month', 'RS%', '% Change Month', 'RS %')
    st.pyplot(scatter_sectors_month)

    # Subsectors Data
    st.subheader('Subsectors')
    subsectors_df = create_data_table(tickers_subsectors, 'SUBSECTORS')
    st.table(subsectors_df)

    # Scatter Plot for Subsectors - % Chg Week
    st.subheader('Scatter Plot for Subsectors (% Chg Week)')
    scatter_subsectors_week = create_scatter_plot(subsectors_df, 'Subsectors: RS% vs % Chg Week', '% Chg Week', 'RS%', '% Change Week', 'RS %')
    st.pyplot(scatter_subsectors_week)

    # Scatter Plot for Subsectors - % Chg Month
    st.subheader('Scatter Plot for Subsectors (% Chg Month)')
    scatter_subsectors_month = create_scatter_plot(subsectors_df, 'Subsectors: RS% vs % Chg Month', '% Chg Month', 'RS%', '% Change Month', 'RS %')
    st.pyplot(scatter_subsectors_month)

    # Core 7 Data
    st.subheader('Core 7')
    core7_df = create_data_table(tickers_core7, 'CORE 7')
    st.table(core7_df)

    # Scatter Plot for Core 7 - % Chg Week
    st.subheader('Scatter Plot for Core 7 (% Chg Week)')
    scatter_core7_week = create_scatter_plot(core7_df, 'Core 7: RS% vs % Chg Week', '% Chg Week', 'RS%', '% Change Week', 'RS %')
    st.pyplot(scatter_core7_week)

    # Scatter Plot for Core 7 - % Chg Month
    st.subheader('Scatter Plot for Core 7 (% Chg Month)')
    scatter_core7_month = create_scatter_plot(core7_df, 'Core 7: RS% vs % Chg Month', '% Chg Month', 'RS%', '% Change Month', 'RS %')
    st.pyplot(scatter_core7_month)

    # Scatter Plot of 52-Week High vs % Gain of 52-Week Low for Main
    st.subheader('Scatter Plot for Main (52-Week High vs % Gain of 52-Week Low)')
    scatter_52w_main = create_scatter_plot(main_df, 'Main: % 52W High vs % Gain 52W Low', '52w Low', '52w High', '% Gain of 52-Week Low', '% of 52-Week High')
    st.pyplot(scatter_52w_main)

    # Scatter Plot of 52-Week High vs % Gain of 52-Week Low for Sectors
    st.subheader('Scatter Plot for Sectors (52-Week High vs % Gain of 52-Week Low)')
    scatter_52w_sectors = create_scatter_plot(sectors_df, 'Sectors: % 52W High vs % Gain 52W Low', '52w Low', '52w High', '% Gain of 52-Week Low', '% of 52-Week High')
    st.pyplot(scatter_52w_sectors)

    # Scatter Plot of 52-Week High vs % Gain of 52-Week Low for Subsectors
    st.subheader('Scatter Plot for Subsectors (52-Week High vs % Gain of 52-Week Low)')
    scatter_52w_subsectors = create_scatter_plot(subsectors_df, 'Subsectors: % 52W High vs % Gain 52W Low', '52w Low', '52w High', '% Gain of 52-Week Low', '% of 52-Week High')
    st.pyplot(scatter_52w_subsectors)

    # Scatter Plot of 52-Week High vs % Gain of 52-Week Low for Core 7
    st.subheader('Scatter Plot for Core 7 (52-Week High vs % Gain of 52-Week Low)')
    scatter_52w_core7 = create_scatter_plot(core7_df, 'Core 7: % 52W High vs % Gain 52W Low', '52w Low', '52w High', '% Gain of 52-Week Low', '% of 52-Week High')
    st.pyplot(scatter_52w_core7)

