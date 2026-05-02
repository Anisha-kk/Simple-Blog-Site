from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, password: str):
    user = models.User(
        username=username,
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_post(db: Session, post, author_id: int):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        author_id=author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts(db: Session,skip: int = 0, limit: int = 5):
    return db.query(models.Post)\
        .order_by(models.Post.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_posts_by_user(db: Session, user_id: int):
    return db.query(models.Post).filter(models.Post.author_id == user_id).all()

def update_post(db: Session, post_id: int, title: str, content: str):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        post.title = title
        post.content = content
        db.commit()
        db.refresh(post)
    return post

def delete_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()
    return post

