from pydantic import BaseModel
from typing import Literal, Any

class WalletData(BaseModel):
    wallet_id: str
    seed: str
    network_id: Literal["base-mainnet"] = "base-mainnet"
    default_address_id: str | None = None

class UserData(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    user_id: int|str
    wallet: WalletData
    agent: Any
    config: dict
