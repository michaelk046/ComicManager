from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class ComicBase(BaseModel):
    title: str
    issue_number: str
    publisher: Optional[str] = None
    grade: Optional[str] = None
    cover_image_url: Optional[str] = None
    buy_price: Optional[float] = None
    current_value: Optional[float] = None
    sell_price: Optional[float] = None

class ComicCreate(BaseModel):
    title: str
    issue_number: str
    publisher: Optional[str] = None
    grade: Optional[str] = None
    cover_image_url: Optional[str] = None
    buy_price: Optional[float] = None
    current_value: Optional[float] = None
    sell_price: Optional[float] = None

class Comic(ComicBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True