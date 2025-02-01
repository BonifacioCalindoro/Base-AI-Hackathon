from pydantic import BaseModel

class SearchPoolsArgs(BaseModel):
    query: str 