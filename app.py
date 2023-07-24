import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px 
from datetime import datetime

# Add a title
st.title('My Streamlit Dashboard')
st.set_option('deprecation.showPyplotGlobalUse', False)

# Add text
st.write('Welcome to my dashboard!')



current_path = os.getcwd()
UPLOAD_FOLDER = os.path.join(current_path, 'data')

# Create the folder if it doesn't exist

# Add a file uploader button to the app
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Check if a file was uploaded
if uploaded_file is not None:
    # Save the uploaded file to the specified folder
    with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write(f"File '{uploaded_file.name}' uploaded successfully!")
# Add a plot

month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

transactions = pd.read_excel('card_transactions.xlsx')

st.header('Filter Transactions')
selected_categories = st.multiselect('Select Categories', transactions['category'].unique(), default=transactions['category'].unique())
transactions=transactions[transactions['category'].isin(selected_categories)]

start_month = st.selectbox('Select Start Month',list(month_names.values()), index=0)
start_day = st.slider('Select Start Day',  min_value=1, max_value=31, value=1)
end_month = st.selectbox('Select End Month',list(month_names.values()), index=len(month_names) - 1)
end_day = st.slider('Select End Day', min_value=1, max_value=31, value=31)

start_date = datetime.strptime(f'{start_month} {start_day}', '%B %d')
end_date = datetime.strptime(f'{end_month} {end_day}', '%B %d')


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

# Filter unique categories and organizations for the selectbox
unique_categories = df['category'].unique()
selected_category = st.selectbox('Select Category:', unique_categories)

unique_organizations = df[df['category'] == selected_category]['organization'].unique()
selected_organization = st.selectbox('Select Organization:', unique_organizations)

# Filter data based on the selected category and organization
filtered_df = df[(df['category'] == selected_category) & (df['organization'] == selected_organization)]


filtered_df['transaction_month'] = filtered_df['transaction_month'].map(month_names)
# Create a histogram of monthly spending for the selected category and organization
fig_filtered = px.bar(filtered_df, x='transaction_month', y='amount', title='Histogram of Filtered Transactions',
                             labels={'Transaction Month': 'Transaction Month', 'Amount': 'Monthly Spending'},
                            category_orders={'Transaction Month': list(month_names.values())})

# Display the histogram
st.plotly_chart(fig_filtered)



selected_month = st.selectbox('Select Month', transactions['transaction_month'].unique())

# Filter data for the selected month
filtered_df = transactions[transactions['transaction_month'] == selected_month]
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

