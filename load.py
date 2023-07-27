# database_utils.py

import mysql.connector
import pandas as pd

def load_data_from_db_and_drop_duplicates(host, user, password, port, database_name):
    try:
        # Connect to the local MySQL server
        connection = mysql.connector.connect(host=host, user=user, password=password, port=port, database=database_name)

        # Read data from the 'transactions' table into a pandas DataFrame
        query = "SELECT * FROM transactions;"
        transactions_df = pd.read_sql_query(query, connection)

        # Drop duplicates from the DataFrame
        transactions_df.drop_duplicates(inplace=True)

        # Close the connection
        connection.close()

        return transactions_df

    except mysql.connector.Error as error:
        print(f"Error while connecting to MySQL: {error}")
        return None
