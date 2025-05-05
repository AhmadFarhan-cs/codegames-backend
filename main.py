from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy import or_,and_
from sqlmodel import Session, create_engine, SQLModel,select
from dotenv import load_dotenv
from models import User,Lessons,LessonXuser
import os


load_dotenv()

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# 🔧 App setup
engine = create_engine(DATABASE_URL)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Auth settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/")
def read_root():
    return {"message": "Connected to Supabase!"}

@app.post("/login")
def login(username: str = Form(), password: str = Form()):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username== username)).first()
       
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}
@app.post("/signup")
def signup(username: str = Form(),email:str = Form(),password: str = Form()):
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.exec(select(User).where(or_(User.username == username, User.email == email))).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists or email has been already been used")
        
    hashed_pass = pwd_context.hash(password)
    new_user = User(username=username,email=email,password_hash=hashed_pass)
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
@app.get("/datatype/lessons/{id}")
def getdatatypelesson(id:int):
    with Session(engine) as session:
     lesson = session.exec(select(Lessons).where(and_(Lessons.id == id,Lessons.module=="datatype"))).first()
    if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
    
    return lesson
@app.post("/datatype/lessons")
def complete_datatype_lesson(username:str= Form(),lessonid :int = Form()):
    
    with Session(engine) as session:
        pkey = session.exec(select(Lessons.pkey).where(and_(Lessons.id == lessonid,Lessons.module=="datatype"))).first()
        uid = session.exec(select(User.id).where(User.username==username)).first()
        exists = session.exec(select(LessonXuser).where(and_(LessonXuser.l_id == pkey,LessonXuser.u_id ==uid))).first()
        if exists:
            return
    newlink =  LessonXuser(u_id=uid,l_id=pkey)
    with Session(engine) as session:
        session.add(newlink)
        session.commit()
@app.get("/datatype/hasread")
def hasread(username: str):
    read_status = {}
    with Session(engine) as session:
        uid = session.exec(select(User.id).where(User.username == username)).first()
        if uid is None:
            return {}

        for lessonid in range(1, 6):  # lessons 1 to 5
            pkey = session.exec(
                select(Lessons.pkey).where(
                    and_(Lessons.id == lessonid, Lessons.module == "datatype")
                )
            ).first()

            if not pkey:
                read_status[lessonid] = False
                continue

            has_read = session.exec(
                select(LessonXuser).where(
                    and_(LessonXuser.l_id == pkey, LessonXuser.u_id == uid)
                )
            ).first()

            read_status[lessonid] = bool(has_read)
    return read_status

    