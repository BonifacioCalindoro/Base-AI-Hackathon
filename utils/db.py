from models.db.users import UserData, WalletData
from user_agent import initialize_agent
import os
import pickle
import json
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("data/users"):
    os.makedirs("data/users")

if not os.path.exists("data/metrics"):
    os.makedirs("data/metrics")

def load_user_data(logfire):
    user_datas = {}
    for user_id in os.listdir("data/users"):
        agent, config = initialize_agent(user_id, logfire)
        wallet_data = pickle.load(open(f"data/users/{user_id}/wallet_data.pkl", "rb"))
        user_datas[int(user_id)] = UserData(
            user_id=int(user_id),
            wallet=WalletData.model_validate_json(json.loads(wallet_data)),
            agent=agent,
            config=config)
    return user_datas

def create_user_data(user_id: int, logfire):
    os.makedirs(f"data/users/{user_id}")
    agent, config = initialize_agent(user_id, logfire)
    wallet_data = pickle.load(open(f"data/users/{user_id}/wallet_data.pkl", "rb"))
    return UserData(
        user_id=int(user_id),
        wallet=WalletData.model_validate_json(json.loads(wallet_data)),
        agent=agent,
        config=config)

def save_metrics(metrics):
    pickle.dump(metrics, open("data/metrics/metrics.pkl", "wb"))

def load_metrics():
    try:
        return pickle.load(open("data/metrics/metrics.pkl", "rb"))
    except FileNotFoundError:
        return {}
