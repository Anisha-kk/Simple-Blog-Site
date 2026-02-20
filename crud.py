from sqlalchemy.orm import Session
import models, schemas

def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts(db: Session):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).all()

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

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