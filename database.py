import mysql.connector
import pandas as pd

# Replace these variables with your MySQL server credentials
host = '127.0.0.1'
user = 'root'
password = '1234'
port = 3306
database_name = 'credit_card'

# Initialize the connection variable
connection = None

try:
    # Connect to the local MySQL server
    connection = mysql.connector.connect(host=host, user=user, password=password, port=port)

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Create the database if it does not exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name};")

    # Switch to the created database
    cursor.execute(f"USE {database_name};")

    # Read your transactions DataFrame (assuming it's named 'transactions')
    # Replace 'transactions.csv' with the actual path to your CSV file if needed
    transactions = pd.read_csv('card_transactions.csv')
    transactions = transactions.drop(columns=transactions.columns[transactions.columns.str.contains('Unnamed')])

    # Fill NaN values in the DataFrame with None before insertion
    transactions = transactions.where(pd.notna(transactions), None)


    # Strip whitespaces from the 'organization' column

    # Replace comma with period in the 'amount' column

    # Create a table for transactions in the database
    create_table_query = """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_day INT,
            transaction_month INT,
            inscription_day INT,
            inscription_month INT,
            description VARCHAR(255),
            place VARCHAR(255),
            disc VARCHAR(255),
            amount FLOAT,
            category VARCHAR(255),
            organization VARCHAR(255)
        );
    """
    cursor.execute(create_table_query)

    # Insert the transactions data into the table
    try:
        for index, row in transactions.iterrows():
            if pd.isna(row['category']) or pd.isna(row['organization']):
            # Print the transaction with missing category or organization
                print(f"Transaction with index {index} has missing category or organization:\n{row}\n")
            else:
                insert_query = f"""
                INSERT INTO transactions (transaction_day, transaction_month, inscription_day, inscription_month, description, place, disc, amount, category, organization)
                VALUES ({row['transaction_day']}, {row['transaction_month']}, {row['inscription_day']}, {row['inscription_month']}, '{row['description']}', '{row['place']}', '{row['disc']}', {row['amount']}, '{row['category']}', '{row['organization']}');
                """
                try:
                    cursor.execute(insert_query)
                except Exception as e:
                    print(f"Error occurred while inserting data at index {index}: {e}")
                    print(f"Query causing the error: {insert_query}")
    except:
        print('error')

    # ... (remaining code) ...

    # Commit the changes to the database
    connection.commit()

    print(f"Transactions data imported to database '{database_name}' successfully.")

except mysql.connector.Error as error:
    print(f"Error while connecting to MySQL: {error}")

finally:
    # Close the cursor and connection
    if connection is not None and connection.is_connected():
        cursor.close()
        connection.close()
