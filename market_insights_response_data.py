import pandas as pd
import numpy as np

# Current date and formatted datetime
current_date = pd.Timestamp.now().date()
combined_datetime = pd.Timestamp.combine(current_date, pd.Timestamp("22:00:00").time())
formatted_datetime = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")

# Load data from URLs
dynamic_url = "https://api.nationalgrideso.com/datastore/dump/596f29ac-0387-4ba4-a6d3-95c243140707"
dynamic = pd.read_csv(dynamic_url, index_col=4, parse_dates=True, storage_options={'User-Agent': 'Mozilla/5.0'})
dynamic.index = dynamic.index.strftime('%Y-%m-%d')
dynamic.index = pd.to_datetime(dynamic.index)
dynamic = dynamic[dynamic['auctionProduct'].isin(['DCH', 'DCL', 'DMH', 'DML', 'DRH', 'DRL'])]
dynamic['deliveryStart'] = pd.to_datetime(dynamic['deliveryStart'])
dynamic['Time'] = dynamic['deliveryStart'].dt.strftime('%H:%M')
dynamic['EFA'] = dynamic['Time'].map({'22:00': 1, '02:00': 2, '06:00': 3, '10:00': 4, '14:00': 5, '18:00': 6, '23:00': 1, '03:00': 2, '07:00': 3, '11:00': 4, '15:00': 5, '19:00': 6})

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

dynamic_pt_price.to_csv('C:/Users/krishna.mohinani/EAC data/dynamic_pt_price.csv', index = False)
dynamic_pt_volume.to_csv('C:/Users/krishna.mohinani/EAC data/dynamic_pt_volume.csv', index = False)
percentage_volume.to_csv('C:/Users/krishna.mohinani/EAC data/percentage_volume.csv', index = False)