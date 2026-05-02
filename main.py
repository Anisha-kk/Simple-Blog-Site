from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models, crud
from database import engine, SessionLocal
from schemas import PostCreate
from starlette.middleware.sessions import SessionMiddleware
from config import Config
from auth import verify_password
from fastapi import status
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Static files (CSS)
#app.mount("/static", StaticFiles(directory="static"), name="static")

#Enables login sessions in FastAPI app when doing server-rendered pages 
app.add_middleware(
    SessionMiddleware,
    secret_key=Config.SECRET_KEY
)

#templates = Jinja2Templates(directory="templates")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Get current user
def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == user_id).first()

#User registration APIs
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = crud.get_user_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = crud.create_user(db, username, password)
    request.session["user_id"] = user.id

    return RedirectResponse("/", status_code=303)

#User login
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)

# Homepage - list posts
@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db)
):
    limit = 5
    skip = (page - 1) * limit

    posts = crud.get_posts(db, skip=skip, limit=limit)
    user = get_current_user(request, db)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": posts,
        "user": user,
        "page": page
    })

# Single post page
@app.get("/posts/{post_id}", response_class=HTMLResponse)
def read_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    user = get_current_user(request, db)
    return templates.TemplateResponse("post.html", {
        "request": request,
        "post": post, #Passed to Jinja2. This is seen in post.html
        "user":user
    })

# Create form page
@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("create.html", {
        "request": request,
        "user": user
    })

# Handle form submission
@app.post("/create")
def create_post( request: Request,title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    post_data = PostCreate(title=title, content=content)

    crud.create_post(db, post_data, author_id=user.id)

    return RedirectResponse("/", status_code=303)

#Only display posts of the logged in user
@app.get("/my-posts", response_class=HTMLResponse)
def my_posts(request: Request, page: int = 1, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse("/login", status_code=303)

    limit = 5
    skip = (page - 1) * limit

    posts = db.query(models.Post)\
        .filter(models.Post.author_id == user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()

    return templates.TemplateResponse("my_posts.html", {
        "request": request,
        "posts": posts,
        "user": user,
        "page": page
    })

#Edit form
@app.get("/posts/{post_id}/edit", response_class=HTMLResponse)
def edit_page(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    user = get_current_user(request, db)

    if not post:
        raise HTTPException(status_code=404)

    if not user or post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return templates.TemplateResponse("edit.html", {
        "request": request,
        "post": post,
        "user":user
    })

#Handle Edit Submission
@app.post("/posts/{post_id}/edit")
def edit_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    post = crud.update_post(db, post_id, title, content)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return RedirectResponse(f"/posts/{post_id}", status_code=303)

#Delete post
@app.post("/posts/{post_id}/delete")
def delete_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    user = get_current_user(request, db)

    if not post:
        raise HTTPException(status_code=404)

    if not user or post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    crud.delete_post(db, post_id)

    return RedirectResponse("/", status_code=303)


#Logout
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)