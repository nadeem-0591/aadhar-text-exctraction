from fastapi import FastAPI, HTTPException, Header
from pymongo import MongoClient
from datetime import datetime, timedelta
import secrets

app = FastAPI()

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['todolist']
users_collection = db['todocollection']

# API key expiration duration (1 year)
API_KEY_EXPIRATION = timedelta(days=365)

# Helper functions
def generate_api_key():
    return secrets.token_hex(10)

# Endpoints
@app.post("/register")
def register(username: str, email: str):
    if not username or not email:
        raise HTTPException(status_code=400, detail="Username and email are required.")

    api_key = generate_api_key()
    expiry_date = datetime.now() + API_KEY_EXPIRATION

    user = {
        'username': username,
        'email': email,
        'expiry_date': expiry_date,
        'api_key': api_key
    }

    users_collection.insert_one(user)

    return {"message": "User registered successfully."}

@app.post("/user/authenticate")
def authenticate(api_key: str = Header(...)):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is missing.")

    user = users_collection.find_one({'api_key': api_key})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key.")

    if user['expiry_date'] < datetime.now():
        raise HTTPException(status_code=402, detail="API key expired.")

    return {"username": user['username'], "email": user['email']}

@app.get("/getUserData")
def get_user_data(api_key: str = Header(...)):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is missing.")

    user = users_collection.find_one({'api_key': api_key})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key.")

    if user['expiry_date'] < datetime.now():
        raise HTTPException(status_code=402, detail="API key expired.")

    return {"username": user['username'], "email": user['email']}
