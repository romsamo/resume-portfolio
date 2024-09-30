import pandas as pd

# Load the cleaned data
file_path = '/Users/romano/Desktop/twitterBot/data/raw_google_sheets_data.csv'
raw_data = pd.read_csv(file_path)


# Cleaning steps:
# 1. Drop the first row which contains invalid data
cleaned_data = raw_data.drop(0)

# 2. Strip any leading/trailing spaces from column names
cleaned_data.columns = cleaned_data.columns.str.strip()
cleaned_data = cleaned_data.drop(11)

# 3. Remove dollar signs and convert to numeric where appropriate
columns_with_dollars = ['Price p.share', 'Position size', 'Market Cap', 'Stoploss', 'risk', 'Price Sold p.share', 'Sold Value', 'Profit(Loss) $']
for col in columns_with_dollars:
    cleaned_data[col] = cleaned_data[col].replace({'\$': '', 'B': '', 'M': '', ',': ''}, regex=True)
    cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')

# 4. Convert date columns to datetime format
cleaned_data['Date Bought'] = pd.to_datetime(cleaned_data['Date Bought'], errors='coerce')
cleaned_data['Date Sold'] = pd.to_datetime(cleaned_data['Date Sold'], errors='coerce')

# 5. Convert other numerical columns
cleaned_data['Shares'] = pd.to_numeric(cleaned_data['Shares'], errors='coerce')
cleaned_data['Duration'] = pd.to_numeric(cleaned_data['Duration'], errors='coerce')

# Clean percentage columns by removing the '%' symbol and converting to float
percentage_columns = ['Stop-loss %', 'Profit(Loss) %', 'Profit(Loss) as % of acc', '% of account', 'Risk of account']

for col in percentage_columns:
    cleaned_data[col] = cleaned_data[col].replace({'%': '', ',': ''}, regex=True).astype(float)

cleaned_data.to_csv("/Users/romano/Desktop/twitterBot/data/cleaned_data.csv", index=False)
























