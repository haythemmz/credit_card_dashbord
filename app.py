import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px 
from datetime import datetime
import os
import json
import shutil
import subprocess
from load import load_data_from_db_and_drop_duplicates
transactions_df=pd.read_excel('card_transactions.xlsx')
def creat_name(x,l):
    for i in l : 
        if i.upper() in str(x).upper():
            return i.upper()
    return None

def creat_cat(x,l):
    for i in l : 
        if i.upper() in str(x).upper():
            return True
    return False
def get_category(text,original_dict):

    # Destination dictionary
    new_dict = {}

    # Key to move
    key_to_move = 'PLACE'

# Check if the key exists in the original dictionary
    if key_to_move in original_dict:
    # Extract the key-value pair and move it to the new dictionary
        new_dict[key_to_move] = original_dict.pop(key_to_move)
    cat='OTHER'
    name='OTHER'
    for k in original_dict.keys():
        if creat_cat(text,original_dict[k])==True:
            cat=k
            name=creat_name(text,original_dict[k])
    return cat,name

# Add a title
st.title('My Streamlit Dashboard')
st.set_option('deprecation.showPyplotGlobalUse', False)

# Add text
st.write('Welcome to my dashboard!')
with open('categories.json', 'r') as file:
    json_data = file.read()

categories=json.loads(json_data)


current_path = os.getcwd()
UPLOAD_FOLDER = os.path.join(current_path, 'data')


# Define the target directory where the PDF files will be moved to
TARGET_DIRECTORY = UPLOAD_FOLDER

col1, col2 = st.columns(2)
# Create the folder if it doesn't exist
credit_card_ending = col2.number_input('Enter the last four digits of the credit card', min_value=1000, max_value=9999)

# Add a file uploader button to the app
uploaded_file = col1.file_uploader("Upload a PDF file", type=["pdf"])

# Check if a file was uploaded
if uploaded_file is not None:
    # Check if the file with the same name already exists in the target directory
    target_file_path = os.path.join(TARGET_DIRECTORY, uploaded_file.name)
    if os.path.exists(target_file_path):
        col1.write(f"File '{uploaded_file.name}' already exists in '{TARGET_DIRECTORY}'.")
    else:
        # Save the uploaded file to the specified folder
        with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        col1.write(f"File '{uploaded_file.name}' uploaded successfully!")

        # Move the file to the target directory
        if os.path.exists(TARGET_DIRECTORY):
            shutil.move(os.path.join(UPLOAD_FOLDER, uploaded_file.name), target_file_path)
            col1.write(f"File '{uploaded_file.name}' moved to '{TARGET_DIRECTORY}' successfully!")
        else:
            col1.write(f"Target directory '{TARGET_DIRECTORY}' does not exist!")


col1,col2,col3=st.columns(3)

if col1.button("Run ETL"):
    # Run the etl.py script using the subprocess module
    subprocess.run(['python', 'etl.py', str(credit_card_ending)])
    st.write("ETL process completed.")
if col2.button("update database"):
    subprocess.run(["python", "database.py"])
    st.write("update process completed.")
if col3.button("Load Data"):
    st.write("Loading data and dropping duplicates...")

    # Replace these variables with your MySQL server credentials
    host = '127.0.0.1'
    user = 'root'
    password = '1234'
    port = 3306
    database_name = 'credit_card'

    transactions_df = load_data_from_db_and_drop_duplicates(host, user, password, port, database_name)
    transactions_df[['category', 'organization']] = transactions_df['description'].apply(lambda x: pd.Series(get_category(x,categories)))
    transactions_df=transactions_df.drop_duplicates()

    if transactions_df is not None:
        st.write("Data loaded successfully:")
        st.dataframe(transactions_df)
        st.write(transactions_df.shape)
    else:
        st.write("Error occurred while loading data. Please check the connection.")
month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

transactions = pd.read_excel('card_transactions.xlsx')
transactions=transactions_df
st.header('Filter Transactions')

#selected_categories = st.multiselect('Select Categories', transactions['category'].unique(), default=transactions['category'].unique())
#transactions=transactions[transactions['category'].isin(selected_categories)]

#start_month = st.selectbox('Select Start Month',list(month_names.values()), index=0)
#start_day = st.slider('Select Start Day',  min_value=1, max_value=31, value=1)
#end_month = st.selectbox('Select End Month',list(month_names.values()), index=len(month_names) - 1)
#end_day = st.slider('Select End Day', min_value=1, max_value=31, value=31)
#start_date = datetime.strptime(f'{start_month} {start_day}', '%B %d')
#end_date = datetime.strptime(f'{end_month} {end_day}', '%B %d')
col1, col2 = st.columns(2)

start_date = datetime(datetime.today().year, 1, 1)
start_date = col1.date_input('Select Start Date', start_date)
end_date = col2.date_input('Select End Date', datetime.today())

filtered_transactions = transactions[((transactions['transaction_month'] > start_date.month) | ((transactions['transaction_month'] == start_date.month) & (transactions['transaction_day'] >= start_date.day))) &
                                        ((transactions['transaction_month'] < end_date.month) | ((transactions['transaction_month'] == end_date.month) & (transactions['transaction_day'] <= end_date.day)))]



    


sum_values = filtered_transactions['amount'].sum()

# Set the path to the folder where you want to save the uploaded PDF files


# Display the sum of values in the same Streamlit page
st.subheader('Sum of amount')
#st.write(f"The sum of values for the filtered DataFrame is: {round(sum_values)}")
st.markdown(
    f'<div style="width: 200px; height: 80px; background-color: lightblue; padding: 5px; text-align: center;">'
    f'<h3>{str(round(sum_values))+" $"}</h3>'
    f'</div>',
    unsafe_allow_html=True
)


fig = px.treemap(filtered_transactions, path=['category','organization'], values='amount',labels='category', 
                 color='amount', color_continuous_scale='Blues', 
                 hover_name='category', hover_data=['amount']
                 )
#fig.update_traces(textinfo='label+text')
col1, col2 = st.columns(2)
st.plotly_chart(fig)
#st.pyplot()
#fig_pie = px.pie(filtered_transactions, names='transaction_month', values='amount', title='Sum of amount by Month')
fig_stacked_bar = px.bar(filtered_transactions, x='category', y='amount', color='organization', barmode='stack', title='Spending by Category and Organization (Stacked)')

st.plotly_chart(fig_stacked_bar)
#col1.plotly_chart(fig)
#col2.plotly_chart(fig_stacked_bar)
#fig_histogram = px.histogram(filtered_transactions, x='transaction_month',y='amount', nbins=12, title='Monthly Spending Distribution', labels={'Amount': 'Spending Amount'})
#st.plotly_chart(fig_histogram)

monthly_spending =filtered_transactions.groupby('transaction_month')['amount'].sum().reset_index()

# Create a histogram to show the amount by month
fig_histogram = px.bar(monthly_spending, x='transaction_month', y='amount', title='Monthly Spending Distribution',
                       labels={'transaction_month': 'month', 'amount': 'Spending Amount'})

# Add text on top of the histogram bars
fig_histogram.update_traces(text=round(monthly_spending['amount']), textposition='outside')
st.plotly_chart(fig_histogram)

df = transactions
col1, col2 = st.columns(2)
# Filter unique categories and organizations for the selectbox
#unique_categories = df['category'].unique()
#selected_category = col1.selectbox('Select Category:', unique_categories)

unique_categories = df['category'].unique()
unique_organizations = df['organization'].unique()
# Option to select all categories
all_categories_option = 'All Categories'
all_organizations_option = 'All Organizations'
unique_categories_with_all = [all_categories_option] + list(unique_categories)
unique_organizations_with_all = [all_organizations_option] + list(unique_organizations)

# Selectbox for category selection with default as 'All Categories'
selected_category = col1.selectbox('Select Category:', unique_categories_with_all, index=0)
unique_organizations = df[df['category'] == selected_category]['organization'].unique()
unique_organizations_with_all = [all_organizations_option] + list(unique_organizations)

# Selectbox for organization selection with default as 'All Organizations'
selected_organization = col2.selectbox('Select Organization:', unique_organizations_with_all, index=0)

# If 'All Categories' is selected, use all categories in the filter
if selected_category == all_categories_option:
    unique_categories = df['category'].unique()
    selected_categories = unique_categories
else:
    selected_categories = [selected_category]

if selected_organization == all_organizations_option:
    unique_organizations = df['organization'].unique()
    selected_organizations = unique_organizations
else:
    selected_organizations = [selected_organization]


filtered_df = df[df['category'].isin(selected_categories) & df['organization'].isin(selected_organizations)]


# Filter data based on the selected category and organization
#filtered_df = df[(df['category'] == selected_category) & (df['organization'] == selected_organization)]


#filtered_df['transaction_month'] = filtered_df['transaction_month'].map(month_names)
monthly_spending =filtered_df.groupby('transaction_month')['amount'].sum().reset_index()
monthly_spending['transaction_month'] = monthly_spending['transaction_month'].map(month_names)

# Create a histogram of monthly spending for the selected category and organization
fig_filtered = px.bar(monthly_spending, x='transaction_month', y='amount', title='Histogram of Filtered Transactions',
                             labels={'Transaction Month': 'Transaction Month', 'Amount': 'Monthly Spending'},
                            category_orders={'Transaction Month': list(month_names.values())})

fig_filtered.update_traces(text=round(monthly_spending['amount']), textposition='outside')

# Display the histogram
st.plotly_chart(fig_filtered)

col1, col2, col3 = st.columns(3)

transactions['transaction_month'] = transactions['transaction_month'].map(month_names)

selected_month = col1.selectbox('Select Month', transactions['transaction_month'].unique())

# Filter data for the selected month
filtered_df = transactions[transactions['transaction_month'] == selected_month]
df = filtered_df
unique_categories = df['category'].unique()

# Option to select all categories
all_categories_option = 'All Categories'
all_organizations_option = 'All Organizations'
unique_categories_with_all = [all_categories_option] + list(unique_categories)

# Selectbox for category selection with default as 'All Categories'
selected_category = col2.selectbox('Select Category:', unique_categories_with_all, index=0)

# Filter unique organizations based on the selected category
if selected_category == all_categories_option:
    unique_organizations = df['organization'].unique()
else:
    unique_organizations = df[df['category'] == selected_category]['organization'].unique()

unique_organizations_with_all = [all_organizations_option] + list(unique_organizations)

# Selectbox for organization selection with default as 'All Organizations'
selected_organization = col3.selectbox('Select Organization:', unique_organizations_with_all, index=0)

# If 'All Categories' is selected, use all categories in the filter
if selected_category == all_categories_option:
    selected_categories = unique_categories
else:
    selected_categories = [selected_category]

# If 'All Organizations' is selected, use all organizations in the filter
if selected_organization == all_organizations_option:
    selected_organizations = unique_organizations
else:
    selected_organizations = [selected_organization]


filtered_df = df[df['category'].isin(selected_categories) & df['organization'].isin(selected_organizations)]
# Create a histogram to show the daily spending with stacked categories
fig_histogram = px.bar(filtered_df, x='transaction_day', y='amount', color='category',
                       title=f'Daily Spending with Stacked Categories for Month {selected_month}',
                       labels={'Transaction Day': 'Day', 'Amount': 'Spending Amount'},
                       #histfunc='sum', # To sum the spending amounts for each day
                       barmode='stack', # To create stacked bars
                       opacity=0.8, # To adjust the opacity of bars for better visibility
                       hover_data=['organization']) # To show the organization on hover

# Display the histogram in Streamlit
st.plotly_chart(fig_histogram)
daily_mean = filtered_df.groupby('transaction_day')['amount'].sum().mean()
st.markdown(
    f'<div style="width: 200px; height: 80px; background-color: lightblue; padding: 5px; text-align: center;">'
    f'<h3>{str(round(daily_mean,2))+" $"}</h3>'
    f'</div>',
    unsafe_allow_html=True
)
st.write(daily_mean)

daily_sum = filtered_df['amount'].sum()
st.markdown(
    f'<div style="width: 200px; height: 80px; background-color: lightblue; padding: 5px; text-align: center;">'
    f'<h3>{str(round(daily_sum,2))+" $"}</h3>'
    f'</div>',
    unsafe_allow_html=True
)
