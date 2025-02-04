from pydantic import BaseModel
from typing import Literal

class StartTwitterArgs(BaseModel):
    prompt: str|Literal["default"] = "default"
    social_network: Literal['twitter'] = 'twitter'

class StopTwitterArgs(BaseModel):
    social_network: Literal['twitter'] = 'twitter'

class GetTwitterStatusArgs(BaseModel):
    social_network: Literal['twitter'] = 'twitter'