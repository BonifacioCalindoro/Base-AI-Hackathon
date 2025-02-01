from cdp import Wallet, Cdp 
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key_name = os.getenv("CDP_API_KEY_NAME")
api_key_private_key = os.getenv("CDP_API_KEY_PRIVATE_KEY").replace('\\n', '\n')

Cdp.configure(api_key_name, api_key_private_key)

wallet = Wallet.create(network_id="base-mainnet")
json.dump(wallet.export_data().to_dict(), open("wallet.json", "w"))

