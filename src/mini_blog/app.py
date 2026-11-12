from fastapi import FastAPI, HTTPException, Depends, File, Form, UploadFile
from mini_blog.schema import PostCreate, PostReturn
from mini_blog.db import Post, create_db_and_table, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from mini_blog.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import os
import shutil
import uuid
import tempfile


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_table()
    yield


app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(""),
        session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splittext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backend-upload"]
            )
        )
        if upload_result.response.http_status_code == 200:

            post = Post(
                caption=caption,
                url="dummy_yrl",
                file_type="photo",
                file_name="dummy_name"
            )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally :
        if temp_file_path and os.path.exists(temp_file_path):

            os.unlink(temp_file_path)
        file.file.close()

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