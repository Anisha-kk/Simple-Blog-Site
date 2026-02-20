from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models, crud
from database import engine, SessionLocal
from schemas import PostCreate

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Static files (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Homepage - list posts
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    posts = crud.get_posts(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": posts
    })

# Single post page
@app.get("/posts/{post_id}", response_class=HTMLResponse)
def read_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    return templates.TemplateResponse("post.html", {
        "request": request,
        "post": post #Passed to Jinja2. This is seen in post.html
    })

# Create form page
@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    return templates.TemplateResponse("create.html", {
        "request": request
    })

# Handle form submission
@app.post("/create")
def create_post(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    post_data = PostCreate(title=title, content=content)
    #crud.create_post(db, post={"title": title, "content": content})
    crud.create_post(db, post_data)
    #save post and go to / - 303 See Other - “The request was processed. Now fetch another URL using GET
    return RedirectResponse("/", status_code=303) 

#Edit form
@app.get("/posts/{post_id}/edit", response_class=HTMLResponse)
def edit_page(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("edit.html", {
        "request": request,
        "post": post
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
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.delete_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return RedirectResponse("/", status_code=303)