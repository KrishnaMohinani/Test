ggg
import streamlit as st import pandas as pd import numpy as np import plotly.graph_objects as go from datetime import datetime, timedelta

Define a fragment to fetch and save data

@st.fragment def fetch_and_save_data(): if st.button("Fetch Latest Data"): # API calls and data processing dynamic_url = "https://api.nationalgrideso.com/datastore/dump/596f29ac-0387-4ba4-a6d3-95c243140707" dynamic = pd.read_csv(dynamic_url, index_col=4, parse_dates=True, storage_options={'User-Agent': 'Mozilla/5.0'}) dynamic.index = dynamic.index.strftime('%Y-%m-%d') dynamic.index = pd.to_datetime(dynamic.index) dynamic = dynamic[dynamic['auctionProduct'].isin(['DCH', 'DCL', 'DMH', 'DML', 'DRH', 'DRL'])] dynamic['deliveryStart'] = pd.to_datetime(dynamic['deliveryStart']) dynamic['Time'] = dynamic['deliveryStart'].dt.strftime('%H:%M') dynamic['EFA'] = dynamic['Time'].map({'22:00': 1, '02:00': 2, '06:00': 3, '10:00': 4, '14:00': 5, '18:00': 6, '23:00': 1, '03:00': 2, '07:00': 3, '11:00': 4, '15:00': 5, '19:00': 6})

dynamic_pt_volume = pd.pivot_table(dynamic, index=[dynamic.index, 'auctionProduct'], columns='EFA', values='clearedVolume')
    dynamic_pt_volume.columns = [int(float(col)) for col in dynamic_pt_volume.columns]
    dynamic_pt_price = pd.pivot_table(dynamic, index=[dynamic.index, 'auctionProduct'], columns='EFA', values='clearingPrice')
    dynamic_pt_price.columns = [int(float(col)) for col in dynamic_pt_price.columns]

    req_url = 'https://api.nationalgrideso.com/datastore/dump/1cf68f59-8eb8-4f1d-bccf-11b5a47b24e5'
    dynamic_req = pd.read_csv(req_url, index_col=5, parse_dates=True, storage_options={'User-Agent': 'Mozilla/5.0'})
    dynamic_req = dynamic_req[dynamic_req['auctionProduct'].isin(['DCH', 'DCL', 'DMH', 'DML', 'DRH', 'DRL'])]
    dynamic_req.index = dynamic_req.index.strftime('%Y-%m-%d')
    dynamic_req.index = pd.to_datetime(dynamic_req.index)
    dynamic_req['deliveryStart'] = pd.to_datetime(dynamic_req['deliveryStart'])
    dynamic_req['Time'] = dynamic_req['deliveryStart'].dt.strftime('%H:%M')
    dynamic_req['EFA'] = dynamic_req['Time'].map({'22:00': 1, '02:00': 2, '06:00': 3, '10:00': 4, '14:00': 5, '18:00': 6, '23:00': 1, '03:00': 2, '07:00': 3, '11:00': 4, '15:00': 5, '19:00': 6})
    dynamic_req = dynamic_req[~((dynamic_req['quantity'] == 100) & (dynamic_req['price'] == 0)) & ~((dynamic_req['quantity'] == 20) & (dynamic_req['price'] == 0))]

    dynamic_req_pt = pd.pivot_table(dynamic_req, index=[dynamic_req.index, 'auctionProduct'], columns=['EFA'], values='quantity', aggfunc=np.sum)
    percentage_volume = np.round((dynamic_pt_volume / dynamic_req_pt) * 100, 2)
    percentage_volume.columns = [int(float(col)) for col in percentage_volume.columns]

    dynamic_pt_price = dynamic_pt_price.reset_index()
    dynamic_pt_volume = dynamic_pt_volume.reset_index()
    percentage_volume = percentage_volume.reset_index()

    dynamic_pt_price.to_csv('C:/Users/krishna.mohinani/EAC data/dynamic_pt_price.csv', index=False)
    dynamic_pt_volume.to_csv('C:/Users/krishna.mohinani/EAC data/dynamic_pt_volume.csv', index=False)
    percentage_volume.to_csv('C:/Users/krishna.mohinani/EAC data/percentage_volume.csv', index=False)

    st.success("Data fetched and saved successfully.")

Load the saved data

price_path = 'C:/Users/krishna.mohinani/EAC data/dynamic_pt_price.csv' volume_path = 'C:/Users/krishna.mohinani/EAC data/dynamic_pt_volume.csv' percentage_path = 'C:/Users/krishna.mohinani/EAC data/percentage_volume.csv'

try: dynamic_pt_price = pd.read_csv(price_path) dynamic_pt_volume = pd.read_csv(volume_path) percentage_volume = pd.read_csv(percentage_path) except FileNotFoundError: st.error("One or more data files are missing. Please fetch the latest data first.") st.stop()

Convert 'deliveryEnd' to datetime

for df in [dynamic_pt_volume, dynamic_pt_price, percentage_volume]: df['deliveryEnd'] = pd.to_datetime(df['deliveryEnd'])

Streamlit Dashboard

st.title("Dx Dashboard")

Filters

efa_options = list(dynamic_pt_volume.columns[2:]) selected_efas = st.multiselect("Select EFA(s)", efa_options, default=efa_options) auction_product_options = dynamic_pt_volume['auctionProduct'].unique() selected_auction_product = st.multiselect("Select Auction Product", auction_product_options)

Date Range

today = datetime.today() seven_days_ago = today - timedelta(days=7) min_date = dynamic_pt_volume['deliveryEnd'].min() max_date = dynamic_pt_volume['deliveryEnd'].max() default_start_date = max(min_date, seven_days_ago) default_end_date = min(max_date, today) start_date, end_date = st.date_input("Select Date Range", [default_start_date, default_end_date]) start_date = pd.to_datetime(start_date) end_date = pd.to_datetime(end_date)

Filter data

filtered_volume = dynamic_pt_volume[ (dynamic_pt_volume['auctionProduct'].isin(selected_auction_product)) & (dynamic_pt_volume['deliveryEnd'] >= start_date) & (dynamic_pt_volume['deliveryEnd'] <= end_date) ] filtered_price = dynamic_pt_price[ (dynamic_pt_price['auctionProduct'].isin(selected_auction_product)) & (dynamic_pt_price['deliveryEnd'] >= start_date) & (dynamic_pt_price['deliveryEnd'] <= end_date) ]

Summary Statistics

summary_data = [] for efa in selected_efas: for product in selected_auction_product: efa_data = filtered_price[filtered_price['auctionProduct'] == product][efa] summary_data.append({ 'Product': product, 'EFA': efa, 'Mean': efa_data.mean(), 'Median': efa_data.median(), '25th Percentile (Q1)': efa_data.quantile(0.25), '75th Percentile (Q3)': efa_data.quantile(0.75), 'Standard Deviation': efa_data.std() }) summary_df = pd.DataFrame(summary_data) summary_df = np.round(summary_df, 2) st.subheader("Summary Statistics Table") st.dataframe(summary_df, use_container_width=True, hide_index=True)

Line Plot - Price

st.subheader("Price Line Plot") fig = go.Figure() for efa in selected_efas: for product in selected_auction_product: filtered_data = filtered_price[filtered_price['auctionProduct'] == product] fig.add_trace(go.Scatter(x=filtered_data['deliveryEnd'], y=filtered_data[efa], mode='lines', name=f"{product} - EFA {efa}")) fig.update_layout(title="Price Line Plot", xaxis_title="Delivery End", yaxis_title="Price") st.plotly_chart(fig)

Bar Plot - Volume

st.subheader("Volume Bar Plot") fig = go.Figure() for efa in selected_efas: for product in selected_auction_product: filtered_data = filtered_volume[filtered_volume['auctionProduct'] == product] fig.add_trace(go.Bar(x=filtered_data['deliveryEnd'], y=filtered_data[efa], name=f"{product} - EFA {efa}")) fig.update_layout(barmode='stack', title="Volume Bar Plot", xaxis_title="Delivery End", yaxis_title="Volume") st.plotly_chart(fig)

Display DataFrames

st.subheader("Volume Procured") st.dataframe(filtered_volume, use_container_width=True)

st.subheader("Clearing Price") median_prices = filtered_price[selected_efas].median() filtered_price[selected_efas] = filtered_price[selected_efas].round(2)

def color_price(val, median): if val < median: return 'background-color: green' elif val > median: return 'background-color: darkred' return ''

styled_price_df = filtered_price.style.apply( lambda x: [color_price(v, median_prices[i]) for i, v in enumerate(x)], subset=selected_efas, axis=1 ).format("{:.2f}", subset=selected_efas) st.dataframe(styled_price_df, use_container_width=True, hide_index=True)

Percentage Volume

st.subheader("Percentage Volume Procured") filtered_percentage_volume = percentage_volume[ (percentage_volume['auctionProduct'].isin(selected_auction_product)) & (percentage_volume['deliveryEnd'] >= start_date) & (percentage_volume['deliveryEnd'] <= end_date) ] filtered_percentage_volume[selected_efas] = filtered_percentage_volume[selected_efas].round().astype(int)

def color_percentage(val): if val < 100: red_intensity = int((100 - val) * 2.55) return f'background-color: rgb({red_intensity}, 0, 0)' return 'background-color: green'

styled_percentage_df = filtered_percentage_volume.style.applymap(color_percentage, subset=selected_efas) st.dataframe(styled_percentage_df, use_container_width=True, hide_index=True)

