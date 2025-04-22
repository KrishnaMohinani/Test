import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Load DataFrames
dynamic_pt_price = pd.read_csv('C:/Users/krishna.mohinani/EAC data/dynamic_pt_price.csv')
dynamic_pt_volume = pd.read_csv('C:/Users/krishna.mohinani/EAC data/dynamic_pt_volume.csv')
percentage_volume = pd.read_csv('C:/Users/krishna.mohinani/EAC data/percentage_volume.csv')

# Convert 'deliveryEnd' to datetime
for df in [dynamic_pt_volume, dynamic_pt_price, percentage_volume]:
    df['deliveryEnd'] = pd.to_datetime(df['deliveryEnd'])

# Streamlit App
st.title("Dx Dashboard")

# Filters
efa_options = list(dynamic_pt_volume.columns[2:])
selected_efas = st.multiselect("Select EFA(s)", efa_options, default=efa_options)

auction_product_options = dynamic_pt_volume['auctionProduct'].unique()
selected_auction_product = st.multiselect("Select Auction Product", auction_product_options)

# Calculate default date range (last 7 days)
today = datetime.today()
seven_days_ago = today - timedelta(days=7)

# Ensure the default date range is within the available data range
min_date = dynamic_pt_volume['deliveryEnd'].min()
max_date = dynamic_pt_volume['deliveryEnd'].max()
default_start_date = max(min_date, seven_days_ago)
default_end_date = min(max_date, today)

start_date, end_date = st.date_input("Select Date Range", [default_start_date, default_end_date])

# Convert start_date and end_date to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Apply filters
filtered_volume = dynamic_pt_volume[
    (dynamic_pt_volume['auctionProduct'].isin(selected_auction_product)) &
    (dynamic_pt_volume['deliveryEnd'] >= start_date) &
    (dynamic_pt_volume['deliveryEnd'] <= end_date)
]

filtered_price = dynamic_pt_price[
    (dynamic_pt_price['auctionProduct'].isin(selected_auction_product)) &
    (dynamic_pt_price['deliveryEnd'] >= start_date) &
    (dynamic_pt_price['deliveryEnd'] <= end_date)
]

# Calculate summary statistics
summary_data = []

for efa in selected_efas:
    for product in selected_auction_product:
        efa_data = filtered_price[filtered_price['auctionProduct'] == product][efa]
        summary_data.append({
            'Product': product,
            'EFA': efa,
            'Mean': efa_data.mean(),
            'Median': efa_data.median(),
            '25th Percentile (Q1)': efa_data.quantile(0.25),
            '75th Percentile (Q3)': efa_data.quantile(0.75),
            'Standard Deviation': efa_data.std()
        })

summary_df = pd.DataFrame(summary_data)
summary_df = np.round(summary_df, 2)

# Display summary statistics table
st.subheader("Summary Statistics Table")
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Plotting with Plotly
st.subheader("Price Line Plot")
fig = go.Figure()
for efa in selected_efas:
    for product in selected_auction_product:
        filtered_data = filtered_price[filtered_price['auctionProduct'] == product]
        fig.add_trace(go.Scatter(x=filtered_data['deliveryEnd'], y=filtered_data[efa], mode='lines', name=f"{product} - EFA {efa}"))
fig.update_layout(title="Price Line Plot", xaxis_title="Delivery End", yaxis_title="Price")
st.plotly_chart(fig)

st.subheader("Volume Bar Plot")
fig = go.Figure()
for efa in selected_efas:
    for product in selected_auction_product:
        filtered_data = filtered_volume[filtered_volume['auctionProduct'] == product]
        fig.add_trace(go.Bar(x=filtered_data['deliveryEnd'], y=filtered_data[efa], name=f"{product} - EFA {efa}"))
fig.update_layout(barmode='stack', title="Volume Bar Plot", xaxis_title="Delivery End", yaxis_title="Volume")
st.plotly_chart(fig)

# Display DataFrames
st.subheader("Volume Procured")
st.dataframe(filtered_volume, use_container_width=True)

st.subheader("Clearing Price")

# Calculate median for each EFA
median_prices = filtered_price[selected_efas].median()

# Round prices to two decimal places
filtered_price[selected_efas] = filtered_price[selected_efas].round(2)

# Apply colour formatting based on median
def color_price(val, median):
    if val < median:
        return 'background-color: green'
    elif val > median:
        return 'background-color: darkred'
    else:
        return ''

# Apply style to the clearing price DataFrame
styled_price_df = filtered_price.style.apply(
    lambda x: [color_price(v, median_prices[i]) for i, v in enumerate(x)],
    subset=selected_efas, axis=1
).format("{:.2f}", subset=selected_efas)

st.dataframe(styled_price_df, use_container_width=True, hide_index=True)

st.subheader("Percentage Volume Procured")

# Apply colour formatting
def color_percentage(val):
    if val < 100:
        red_intensity = int((100 - val) * 2.55)
        return f'background-color: rgb({red_intensity}, 0, 0)'
    else:
        return 'background-color: green'

# Filter and style percentage_volume DataFrame
filtered_percentage_volume = percentage_volume[
    (percentage_volume['auctionProduct'].isin(selected_auction_product)) &
    (percentage_volume['deliveryEnd'] >= start_date) &
    (percentage_volume['deliveryEnd'] <= end_date)
]

# Round percentage values to integers and convert to integer type
filtered_percentage_volume[selected_efas] = filtered_percentage_volume[selected_efas].round().astype(int)

# Apply style to the percentage column(s)
styled_percentage_df = filtered_percentage_volume.style.applymap(color_percentage, subset=selected_efas)

st.dataframe(styled_percentage_df, use_container_width=True, hide_index=True)