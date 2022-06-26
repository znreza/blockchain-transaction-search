import streamlit as st
import pandas as pd
import json
import requests
from sklearn.preprocessing import LabelEncoder
from PIL import Image

image = Image.open('./files/master logo.png')
st.set_page_config(page_icon = image, page_title="Arbiter Tools Dashboard") 

st.sidebar.image(
    image,
    use_column_width=True
)

c1, c2 = st.columns([1, 8])

# with c1:
#     st.image(
#         "https://drive.google.com/drive/u/0/folders/1l5R0J9cX1LYbZ3suZKqhJ_nhy75JcUb",
#         width=90,
#     )

st.markdown(
    """# **Arbiter Tools Dashboard**
Tools to support Arbiters with dispute resolution cases.
"""
)

st.header("**Transaction Data for Selected NFT**")

def extract_txs_info(json_row):
    
    tx_time = json_row[0]['block_signed_at']
    tx_hash = json_row[0]['log_events'][0]["tx_hash"]
    
    tx_type = json_row[0]['log_events'][0]["decoded"]["name"]
    
    price = json_row[0]["fees_paid"]
    
    if price:
        price = float(json_row[0]["fees_paid"]) / (10 ** 18)
    
    if tx_type == "TransferSingle":
        tx_from_adr = json_row[0]['log_events'][0]["decoded"]["params"][1]["value"]
        tx_to_adr = json_row[0]['log_events'][0]["decoded"]["params"][2]["value"]
    elif tx_type == "Transfer":
        tx_from_adr = json_row[0]['log_events'][0]["decoded"]["params"][0]["value"]
        tx_to_adr = json_row[0]['log_events'][0]["decoded"]["params"][1]["value"]
    else:
        tx_from_adr = None
        tx_to_adr = None
    
    return tx_time, tx_hash, tx_from_adr, tx_to_adr, price

API_KEY = 'ckey_fb737220d44340f886805b9c011'
base_url = 'https://api.covalenthq.com/v1'

def get_nft_transactions(chain_id, address):
    endpoint = f'/{chain_id}/tokens/{nft_contract_address}/nft_transactions/{token_id}/?key={API_KEY}'
    url = base_url + endpoint
    result = requests.get(url).json()
    data = result["data"]
    return data


def fetch_nft_transfer_data(bc_id, con_addr, token_id):
    
    blockchain_id = bc_id
    nft_contract_address = con_addr
    token_id = token_id
    
    data = get_nft_transactions(blockchain_id, nft_contract_address)
    
    raw_df = pd.json_normalize(data, ['items'])

    txs = pd.json_normalize(raw_df['nft_transactions'])
    txs = txs.T
    
    txs['Transaction Time'], txs['Transaction Hash'], txs['From'], txs['To'], txs['Price (ETH)'] = zip(*txs.apply(extract_txs_info, axis=1))

    txs = txs.dropna(subset=['From', 'To'])
    txs = txs.drop(0, axis=1)
    
    return txs

def encode_addr(txs):
    
    txs_add_list = list(set(list(txs["From"]) + list(txs["To"])))

    le = LabelEncoder().fit(txs_add_list)

    txs['From (coded)'] = le.transform(txs["From"])
    txs['To (coded)'] = le.transform(txs["To"])

    txs['From (coded)'] = txs['From (coded)'].apply(lambda x: "address_"+str(x))
    txs['To (coded)'] = txs['To (coded)'].apply(lambda x: "address_"+str(x))
    
    return txs

# Custom function for rounding values
# def round_value(input_value):
#     if input_value.values > 1:
#         a = float(round(input_value, 2))
#     else:
#         a = float(round(input_value, 8))
#     return a

st.header("")

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


blockchain_name = st.text_input("Blockchain Name", value="Ethereum")
nft_contract_address = st.text_input("NFT Contract Address", value="0xe4605d46fd0b3f8329d936a8b258d69276cba264")
token_id = st.number_input("Token ID", value=134)

if st.button("Search"):
    if blockchain_name == "Ethereum":
        blockchain_id = '1'
    else: blockchain_id = '1'
        
    token_id = int(token_id) 
    
    df = fetch_nft_transfer_data(bc_id=blockchain_id, con_addr=nft_contract_address, token_id=token_id)
    df = encode_addr(df)

    csv = convert_df(df)
    
#     st.download_button(
#         label="Download data as CSV",
#         data=csv,
#         file_name="large_df.csv",
#         mime="text/csv",
#     )
    
    st.dataframe(df, height=2000)


# st.markdown(
#     """
# <style>
# .sidebar .sidebar-content {
#     background-image: linear-gradient(#0000,#0000);
#     color: white;
# }
# </style>
# """,
#     unsafe_allow_html=True,
# )

st.markdown(
    """
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
""",
    unsafe_allow_html=True,
)
