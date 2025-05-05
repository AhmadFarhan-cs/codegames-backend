from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password_hash: str

class Lessons(SQLModel,table = True):
    pkey: Optional[int]=Field(default=None,primary_key=True)
    id: int
    title:str
    content:str
    module:str
class LessonXuser(SQLModel,table = True):
    u_id:  Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    l_id:  Optional[int] = Field(default=None, foreign_key="lessons.pkey", primary_key=True)

