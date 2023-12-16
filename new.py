import pandas as pd
import numpy as np
from datetime import datetime

# Specify the path to your CSV file
csv_file_path = r'C:\Users\hp\Desktop\hackathon\your_dataset.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path, parse_dates=['Transaction Time'])

# Function to calculate label and perform fraud detection checks
def calculate_label_and_fraud_detection(abnormal_flag, flag3, flag2, flag4):
    # Calculate label based on the specified expression
    x = 0.75 * abnormal_flag + 0.25 * flag3 + 0.75 * flag2 + 0.45 * flag4
    label = 1 / (1 + np.exp(-x))

    print(f'Calculated Label: {label}')

    # Check if the calculated label is greater than 0.65
    if label > 0.75:
        # Delete the newly entered row from the DataFrame
        df.drop(len(df) - 1, inplace=True)
        
        # Save the updated DataFrame to the CSV file
        df.to_csv(csv_file_path, index=False)

        # Display fraud detection warning message
        print('Fraud Detected! The newly entered row has been deleted.')
    else :
        label=1
        df.to_csv(csv_file_path, index=False)

# Function to add a new row to the DataFrame
def add_new_row():
    try:
        # Get user input for a new row
        new_row = {
            'Transaction Amount': float(input('Enter Transaction Amount: ')),
            'Transaction Time': datetime.now(),
            'Transaction Type': input('Enter Transaction Type: '),
            'Merchant Info': input('Enter Merchant Info: '),
            'User Account Info': input('Enter User Account Info: '),
            'Location Info': input('Enter Location Info: '),
            'Device Info': input('Enter Device Info: '),
            'User Behavior': input('Enter User Behavior: ')
        }

        # Check if 'Transaction Date' column exists in the DataFrame
        if 'Transaction Date' not in df.columns:
            df['Transaction Date'] = pd.to_datetime('today').date()

        # Check if the entered transaction amount is 1.75 times greater than the highest transaction amount
        max_transaction_amount = df['Transaction Amount'].max()
        flag3 = 1 if new_row['Transaction Amount'] > 1.75 * max_transaction_amount else 0

        # Add the new row to the DataFrame
        df.loc[len(df)] = new_row

        # Access values column by column and store in variables
        transaction_times = pd.to_datetime(df['Transaction Time'])
        transaction_types = df['Transaction Type'].tolist()
        merchant_infos = df['Merchant Info'].tolist()
        user_account_infos = df['User Account Info'].tolist()
        location_infos = df['Location Info'].tolist()

        # Sort DataFrame by 'User Account Info', 'Transaction Date', and 'Transaction Time'
        df.sort_values(by=['User Account Info', 'Transaction Date', 'Transaction Time'], inplace=True)
        df['Transaction Time'] = pd.to_datetime(df['Transaction Time'])  # Convert to datetime

        # Calculate the time difference between consecutive rows within each user group
        df['TimeDifference'] = (df.groupby('User Account Info')['Transaction Time'].shift() - df['Transaction Time']).dt.total_seconds()

        # Set abnormal_flag to 1 if the time difference is less than 0.5 milliseconds
        abnormal_flag = 1 if (df['TimeDifference'] < 500 / 1000).any() else 0

        # Check for time differences between consecutive rows
        #df['TimeDifference'] = (df['Transaction Time'].diff() < pd.Timedelta(seconds=.5)).astype(int)
        #flag1 = 1 if (df['TimeDifference'] == 1).any() else 0

        # Check for maximum number of rows within a transaction_time difference of 1 hour on the same transaction_date
        max_rows_same_date_hour_diff = df.groupby(['Transaction Date']).apply(lambda group: group['Transaction Time'].diff().lt(pd.Timedelta(hours=1)).sum()).max()
        flag2 = 1 if max_rows_same_date_hour_diff > len(df) / 2 else 0

       # ... (previous code remains the same)

        # Check if the string of 'Location Info' is not in any row of the column 'Location Info' (case-insensitive)
        flag4 = 0
        if new_row['Location Info'].lower() not in df['Location Info'].str.lower().tolist():
            flag4 = 1

# ... (rest of the code remains the same)

        #print(flag1);
        print(flag2)
        print(flag3)
        print(flag4)
        print(abnormal_flag)
        # Calculate label and perform fraud detection checks
        calculate_label_and_fraud_detection(abnormal_flag, flag3, flag2, flag4)

    except ValueError as e:
        print(f"Error: {e}. Please enter valid values.")

# Example: Continuously add new rows and perform checks
while True:
    add_new_row()
    continue_entry = input('Do you want to continue? (yes/no): ')
    if continue_entry.lower() != 'yes':
        break
