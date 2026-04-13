from pydantic import BaseModel, Field
from .user_schemas import UserResponse
from datetime import datetime

class ReviewCreateModel(BaseModel):
    movie_name : str
    release_date : str
    review_content : str
    rating : float= Field(...,ge=0,le=5,description="Rating must be between 0 and 5")

class ReviewEditModel(BaseModel):
    review_content:str
    rating: float = Field(..., ge=0, le=5, description="Rating must be between 0 and 5")


class ReviewItemResposnseModel( BaseModel):
    review_content : str
    rating : float
    created_by : UserResponse
    created_at : datetime

class ReviewResponseModel(BaseModel):
    movie_name : str
    release_date : str
    overall_rating : float
    reviews : list[ReviewItemResposnseModel]