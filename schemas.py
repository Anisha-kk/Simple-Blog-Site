from pydantic import BaseModel
from datetime import datetime

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    '''
    “Allow reading object attributes like post.title instead of only dictionary keys like post['title'].”Without it, FastAPI expects a dict.
    But SQLAlchemy returns a model instance, not a dict.
    '''
    model_config = {
    "from_attributes": True
    }