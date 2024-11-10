from fastapi import FastAPI, Depends, HTTPException, Form
from backend.database.postgres_connection import insert_user, get_user, verify_email
from backend.authenticator.verify_mail import send_email
from backend.config.secrets import JWT_SECRET, BASE_URL
import uvicorn
from passlib.context import CryptContext
import jwt
from pydantic import BaseModel
from backend.database.mongo_connection import add_customer
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add `null` here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Token(BaseModel):
    access_token: str
    token_type: str
    dbid: str

class Register(BaseModel):
    fname: str
    lname: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

def create_token(dbid: int):
    payload = {"dbid": dbid}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except:
        return None

@app.post("/register/")
def register(register: Register):
    fname = register.fname
    lname = register.lname
    email = register.email
    password = register.password

    password = pwd_context.hash(password) 
    result = insert_user(fname, lname, email, password)
    if result >= 0:
        verification_link = f"{BASE_URL}/verify?dbid={str(result).encode().hex()}"
        if send_email(email, verification_link) == 0:
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Error sending email"}
    elif result == -1:
        return {"status": "error", "message": "User already exists"}
    elif result == -2:
        return {"status": "error", "message": "Error inserting user"}

@app.post("/login")
def login(login: Login):
    email = login.email
    password = login.password
    user_data = get_user(email)
    if user_data == None:
        return HTTPException(status_code=401, detail="Invalid credentials")
    dbid, db_password, email_verified = user_data
    if email_verified and pwd_context.verify(password, db_password):
        token = create_token(dbid)
        return Token(access_token=token, token_type="bearer", dbid=str(dbid))
    else:
        return HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/verify")
def verify(dbid: str):
    dbid = bytes.fromhex(dbid).decode()
    result = verify_email(dbid)
    if result == 0:
        add_customer(dbid)
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Error verifying email"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8101)