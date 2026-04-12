from beanie import Document, Link
from pydantic import BaseModel, Field,EmailStr
from typing import List, Optional
from datetime import datetime,timezone

class User(Document):
    name : str
    email : EmailStr
    password :str
    created_at : datetime = Field(default_factory=lambda : datetime.now(timezone.utc))

    class Settings:
        collection = "users"


class ReviewItem(BaseModel):
    review_content : str =Field(default_factory=str)
    rating : float =Field(default_factory=0.0)
    created_by : Link[User]
    created_at : datetime = Field(default_factory=lambda : datetime.now(timezone.utc))

class Review(Document):
    movie_name:str = Field(...)
    release_date :str = Field(...)
    overall_rating : float = Field(default_factory=0.0)
    reviews : List[ReviewItem] = Field(default_factory=list)
    class Settings:
        collection = "reviews"