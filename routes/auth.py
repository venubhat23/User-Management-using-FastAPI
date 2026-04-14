from fastapi import APIRouter,HTTPException, Depends
from pydantic import BaseModel
from database import get_db
from passlib.context import CryptContext
import hashlib
from jose import jwt
from datetime import datetime,timedelta
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from typing import Annotated
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY="mysecretkey"
ALGORITHM="HS256"

router = APIRouter()

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

security = HTTPBearer()
class users(BaseModel):
    name:str
    email:str
    password:str

class LoginRequest(BaseModel):
    email:str
    password:str


###################################

def hash_password(password):
    
    sha_password = hashlib.sha256(password.encode()).hexdigest()

    return pwd_context.hash(sha_password)
def verify_password(plain: str, hashed: str) -> bool:
    sha_password = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(sha_password, hashed)

def create_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    
# def verify_token(token: Annotated[str, Depends(oauth2_scheme)]):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

#################################################


@router.get("/")
def home():
    return "Namste Ganesha Ji!"

@router.post("/register")
def add_user(user:users):
    db=get_db()
    cursor=db.cursor()
    try:
        cursor.execute("select *  from users where email=%s",(user.email,));
        existing_user=cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered")
        hashed_password=hash_password(user.password)
        cursor.execute("insert into users (name,email,password,role) values (%s,%s,%s,%s)",(user.name,user.email,hashed_password,"user"))
        db.commit()
        return {"message":"User Created"}
    except Exception as e :
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()

@router.post("/login")
def login(user:LoginRequest):
    db=get_db()
    cursor=db.cursor(dictionary=True)
    try:
        cursor.execute("select * from users where email=%s",(user.email,))
        existing_user=cursor.fetchone()
        if not existing_user:
            raise HTTPException(status_code=401,detail="User not exist")
        if not verify_password(user.password,existing_user["password"]):
            raise HTTPException(status_code=401,detail="Invalid Password")
        token=create_token({"sub":user.email})
        return {"message":"Login Successful","access_token":token}

    except HTTPException:
        raise

    except Exception as e :
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/profile")
def profile(user=Depends(verify_token)):
    return {
        "message": "Protected route",
        "user": user
    }