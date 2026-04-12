from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from datetime import datetime

class UserCreate(BaseModel):
    name : str = Field(...)
    email : str = Field(...)
    password : str = Field(...)

class UserResponse(BaseModel):
    id : PydanticObjectId 
    name : str
    email : str
    created_at : datetime
    model_config = {
        "from_attributes": True
    }