from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, List
import uvicorn
app = FastAPI()

# In-memory database to store posts, likes, and dislikes
db = {
    "users": {},
    "posts": [],
    "likes": {},
    "dislikes": {}
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Models
class User(BaseModel):
    username: str
    password: str
    email: str

class Post(BaseModel):
    title: str
    content: str
    author: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Helper functions
def get_user(username: str):
    if username in db["users"]:
        return db["users"][username]
    return None

def verify_password(plain_password: str, hashed_password: str):
    # You would typically use a more secure method to hash and verify passwords
    return plain_password == hashed_password

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return user

# Routes
@app.post("/signup")
def signup(user: User):
    if user.username in db["users"]:
        raise HTTPException(status_code=400, detail="Username already exists")

    '''I Tried opening account at https://hunter.io but for some reason it is not getting activated, so I commented the email verification section, 
    with a working emailhunter account this code will work.'''
    
    # Verify email existence using emailhunter.co
    # Replace `YOUR_EMAILHUNTER_API_KEY` with your actual API key
    #import requests
    # response = requests.get(
    #     f"https://api.emailhunter.co/v2/email-verifier?email={user.email}",
    #     headers={"Authorization": "Bearer YOUR_EMAILHUNTER_API_KEY"}
    # )
    # if response.status_code != 200 or not response.json().get("exist"):
    #     raise HTTPException(status_code=400, detail="Invalid email")

    # Save the user in the database
    db["users"][user.username] = {
        "username": user.username,
        "password": user.password,
        "email": user.email
    }
    return {"message": "User created successfully"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Generate a simple access token (not a secure implementation)
    access_token = f"Bearer {user['username']}"
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/posts", response_model=List[Post])
def get_posts(token: str = Depends(oauth2_scheme)):
    return db["posts"]

@app.post("/posts")
def create_post(post: Post, token: str = Depends(oauth2_scheme)):
    # Get the username from the token (a simple implementation)
    username = token.split()[1]
    post.author = username
    db["posts"].append(post)
    return {"message": "Post created successfully"}

@app.put("/posts/{post_id}")
def edit_post(post_id: int, post: Post, token: str = Depends(oauth2_scheme)):
    # Get the username from the token (a simple implementation)
    username = token.split()[1]
    existing_post = db["posts"][post_id]
    if existing_post.author != username:
        raise HTTPException(status_code=403, detail="You are not authorized to edit this post")
    db["posts"][post_id] = post
    return {"message": "Post updated successfully"}

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, token: str = Depends(oauth2_scheme)):
    # Get the username from the token (a simple implementation)
    username = token.split()[1]
    existing_post = db["posts"][post_id]
    if existing_post.author != username:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this post")
    del db["posts"][post_id]
    return {"message": "Post deleted successfully"}

@app.post("/posts/{post_id}/like")
def like_post(post_id: int, token: str = Depends(oauth2_scheme)):
    # Get the username from the token (a simple implementation)
    username = token.split()[1]
    existing_post = db["posts"][post_id]
    if existing_post.author == username:
        raise HTTPException(status_code=400, detail="You cannot like your own post")
    if post_id in db["likes"]:
        db["likes"][post_id].append(username)
    else:
        db["likes"][post_id] = [username]
    return {"message": "Post liked successfully"}

@app.post("/posts/{post_id}/dislike")
def dislike_post(post_id: int, token: str = Depends(oauth2_scheme)):
    # Get the username from the token (a simple implementation)
    username = token.split()[1]
    existing_post = db["posts"][post_id]
    if existing_post.author == username:
        raise HTTPException(status_code=400, detail="You cannot dislike your own post")
    if post_id in db["dislikes"]:
        db["dislikes"][post_id].append(username)
    else:
        db["dislikes"][post_id] = [username]
    return {"message": "Post disliked successfully"}

@app.get("/docs")
async def get_documentation():
    from fastapi.openapi.utils import get_openapi
    from fastapi import responses
    response = responses.HTMLResponse(get_openapi(title="Social Networking API", version="1.0.0", routes=app.routes))
    response.headers["Content-Type"] = "text/html"
    return response
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)