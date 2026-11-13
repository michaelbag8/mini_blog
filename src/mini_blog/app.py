from fastapi import FastAPI, HTTPException, Depends, File, Form, UploadFile
from mini_blog.schema import PostCreate, PostReturn
from mini_blog.db import Post, create_db_and_table, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from mini_blog.images import imagekit
import logging
import imagekitio
import uuid
from mini_blog.users import auth_backend, current_active_user, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_table()
    yield

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session),
):
    file_bytes = await file.read()

    try:
        result = await imagekit.files.upload(
            file=file_bytes,
            file_name=file.filename,
            use_unique_file_name=True,
            tags=["backend-upload"],
        )
    except imagekitio.APIError:
        logger.exception("ImageKit upload failed")
        raise HTTPException(status_code=502, detail="Image upload failed")

    is_video = (file.content_type or "").startswith("video/")
    post = Post(
        caption=caption,
        url=result.url,
        file_type="video" if is_video else "image",
        file_name=result.name,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post
    

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    post_data = []
    for post in posts:
        post_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat()
            }
        )
        return {"posts": post_data}
    

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
