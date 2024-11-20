from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

### USING POSTMAN HERE
### uvicorn app.main:app --reload to start server

class Post(BaseModel):
    title: str
    content: str
    published: bool = True          # Providing a default value
    rating: Optional[int] = None    # Optional field

# Contains all the posts (dummy database)
my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favorite foods", "content": "I like pizza", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts", status_code = status.HTTP_201_CREATED)      # 201 status code for successful creation
def create_posts(post: Post):           # FastAPI will automatically validate the input as per Post class
    post_dict = post.model_dump()
    post_dict["id"] = randrange(0, 10000000)        # Inefficient way of choosing a random id each time
    my_posts.append(post_dict)
    return {"data": my_posts}

### This has to be over the get_post() method as otherwise the url /posts/{id} will be treated as /posts/latest and throw an error
@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return {"detail": post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"message": f"post with id {id} was not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist.")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update
@app.put("/posts/{id}")
def update_post(id: int, post: Post):       # FastAPI will automatically validate the input as per Post class
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist.")
    post_dict = post.model_dump()
    post_dict["id"] = id        # Retain the same id
    my_posts[index] = post_dict
    return {"data": post_dict}

### Type in http://127.0.0.1:8000/docs to see the documentation