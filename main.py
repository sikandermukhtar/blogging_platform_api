from fastapi import FastAPI
from routes.test import router as test_router
from routes.user import router as user_login_router
from routes.role import router as role_router
from routes.blog import router as blog_router, comment_router
from routes.moderation import router as moderation_router
from routes.admin import router as admin_router
import models
from config.base import Base
from config.session import engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(test_router)
app.include_router(user_login_router)
app.include_router(role_router)
app.include_router(blog_router)
app.include_router(comment_router)
app.include_router(moderation_router)
app.include_router(admin_router)


@app.get("/")
def index():
    return {"message": "Hello world!"}
