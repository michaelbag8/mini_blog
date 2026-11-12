from fastapi import FastAPI, HTTPException
from mini_blog.schema import PostCreate, PostReturn

app = FastAPI()

text_posts = {
    1: {"title": "New Post", "content": "cool test post"},
    2: {"title": "second new Post", "content": "second cool test post"},
    3: {"title": "Getting Started with FastAPI", "content": "FastAPI makes building APIs quick and fun."},
    4: {"title": "Why Type Hints Matter", "content": "Type hints help catch bugs early and power validation."},
    5: {"title": "Understanding Path Parameters", "content": "Path parameters let you capture values from the URL."},
    6: {"title": "Query Parameters 101", "content": "Query parameters are optional filters added after the question mark."},
    7: {"title": "Pydantic Models Explained", "content": "Pydantic validates request bodies and shapes your responses."},
    8: {"title": "Handling Errors Gracefully", "content": "Use HTTPException to return clear status codes and messages."},
    9: {"title": "Async vs Sync Endpoints", "content": "Async endpoints shine when you wait on I/O like databases or APIs."},
    10: {"title": "Dependency Injection Basics", "content": "Depends lets you share logic like auth and database sessions."},
    11: {"title": "Writing Your First Test", "content": "TestClient lets you call your endpoints without running a server."},
    12: {"title": "Deploying to Production", "content": "Run uvicorn behind a process manager or a reverse proxy."},
}


@app.get("/")
def hello_World():
    return {"message": "Hello World"}

@app.get("/post")
def get_all_post(limit: int = None)-> dict:
    if limit:
        return list(text_posts.values())[:limit]
    return text_posts

@app.get("/post/{id}")
def get_post_by_id(id: int) -> PostReturn:
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="post not found")
    
    return text_posts.get(id)

@app.post("/posts")
def create_post(post: PostCreate)-> PostReturn:
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys()) + 1] = new_post
    return new_post
