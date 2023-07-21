import streamlit as st

# Add a title
st.title('My Streamlit Dashboard')
st.set_option('deprecation.showPyplotGlobalUse', False)

# Add text
st.write('Welcome to my dashboard!')

# Add a plot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

transactions = pd.read_excel('card_transactions.xlsx')

st.sidebar.header('Filter Transactions')
selected_categories = st.multiselect('Select Categories', transactions['category'].unique(), default=transactions['category'].unique())
transactions=transactions[transactions['category'].isin(selected_categories)]

start_month = st.sidebar.slider('Select Start Month', min_value=transactions['transaction_month'].min(), max_value=transactions['transaction_month'].max(), value=transactions['transaction_month'].min())
start_day = st.sidebar.slider('Select Start Day', min_value=1, max_value=31, value=1)
end_month = st.sidebar.slider('Select End Month', min_value=transactions['transaction_month'].min(), max_value=transactions['transaction_month'].max(), value=transactions['transaction_month'].max())
end_day = st.sidebar.slider('Select End Day', min_value=1, max_value=31, value=31)
filtered_transactions = transactions[((transactions['transaction_month'] > start_month) | ((transactions['transaction_month'] == start_month) & (transactions['transaction_day'] >= start_day))) &
                                        ((transactions['transaction_month'] < end_month) | ((transactions['transaction_month'] == end_month) & (transactions['transaction_day'] <= end_day)))]


sum_values = filtered_transactions['amount'].sum()

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

st.plotly_chart(fig)
#st.pyplot()
#fig_pie = px.pie(filtered_transactions, names='transaction_month', values='amount', title='Sum of amount by Month')
fig_stacked_bar = px.bar(filtered_transactions, x='category', y='amount', color='organization', barmode='stack', title='Spending by Category and Organization (Stacked)')

st.plotly_chart(fig_stacked_bar)

#fig_histogram = px.histogram(filtered_transactions, x='transaction_month',y='amount', nbins=12, title='Monthly Spending Distribution', labels={'Amount': 'Spending Amount'})
#st.plotly_chart(fig_histogram)

monthly_spending =filtered_transactions.groupby('transaction_month')['amount'].sum().reset_index()

# Create a histogram to show the amount by month
fig_histogram = px.bar(monthly_spending, x='transaction_month', y='amount', title='Monthly Spending Distribution',
                       labels={'transaction_month': 'month', 'amount': 'Spending Amount'})

# Add text on top of the histogram bars
fig_histogram.update_traces(text=round(monthly_spending['amount']), textposition='outside')
st.plotly_chart(fig_histogram)



fig_pie = px.pie(
    filtered_transactions,
    names='transaction_month',
    values='amount',
    title='Sum of Values by Month',
)

# Customizing the labels on the pie chart to include both percentages and actual values
fig_pie.update_traces(
    textinfo='label+percent',
    texttemplate=' %{value:0.f} (%{percent})',
)
st.subheader('Pie Chart: Sum of Values by Month')
st.plotly_chart(fig_pie)