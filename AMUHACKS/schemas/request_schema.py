from pydantic import BaseModel

class CrisisRequest(BaseModel):
    user_text: str
