from email.policy import HTTP
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app = FastAPI()

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts): #iterates and grabs
        if p['id'] == id:
            return i
        
#* Standard conventions
    # http://127.0.0.1:8000/...
    # create    post        request with a /posts
    # read      get         request with a /posts/[{id}] for all [or one] post
    # update    put/patch   request with a /posts/{id}. put reqyures all parameters, patch for only 1 field
    # delete    delete      request with a /posts/{id}

#* Command line notes
    # make a Python package (folder) called app for all code and the empty__init__py file
    # make venv with $ py -3 -m venv [venv name] and change interpreter to this path
    # enable venv with [venv name]\Scripts\activate.bat
    # do once: pip install "fastapi[all]"
    # uvicorn app.main:app --reload to start server [and check reloads each time]
    # Use <Postman> for requests

#* Path operations
    # decorator @app.get("/") defines path operation so it is an API, get is the HTTP request method, and / is the root path (e.g. goes to example.com/[...])
        # does the first path for ties in matches
    # [async] def root()... [async] optional for tasks that take certain amount of time (e.g. talk with database)
    # any root name (e.g. login) works fine
    # returns as JSON
    
#* Schemas: rules to make sure inputs from front-end are correct
# pydantic library (separate from fastAPI)
class Post(BaseModel):
    title: str
    content: str
    isPublished: bool = True
    # typing library
    # rating: Optional[int] = None

#* Database: an array of dictionaries (posts). Need an uniqID. Stored in mem, will be cleared each reload
my_posts = [{"title": "eg title", "content": "content eg", "id": 1}, {"title": "fav foods", "content": "I love pizza", "id": 2}]


#* Path operations: get
@app.get("/") 
def root():
    return {"message": "welcome to my second test"}
# This will never run due to the first match rule:
# @app.get("/") 
# def root():
#     return {"never runs"} 

@app.get("/posts") 
def get_posts():
    return {"data": my_posts} #fastAPI serializes this array into JSON format automatically

#* Path operations: post (and default status code)
@app.post("/posts", status_code = status.HTTP_201_CREATED) 
# parameterName: type [= Body (from fastAPI lib)]
def create_posts(post: Post):
    # print(post)
    # print(post.dict())
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}
# old function with no schema: 
# def create_posts(payLoad: dict = Body(...)):
#     print(payLoad)
#     return {"new_post": f"title: {payLoad['title']} content: {payLoad['content']}"}

#* Path operations: get (with path parameter)
#! put more specific ones like posts/latest BEFORE the most generic path parameter
@app.get("/posts/{id}") 
def getOnePost(id: int, response: Response): #! Path parameter always returned as string, must convert
    post = find_post(id)
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
        # old hardcoded version:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id: {id} was not found"}
    print(post)
    return {"post_details": post}

#* Path operations: delete
@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT) #delete doesn't get anything
def delete_post(id: int):
    # Find post to delete, exception if not found
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
        
    my_posts.pop(index)
    return Response(status_code = status.HTTP_204_NO_CONTENT) #204 expects not data to be returned

#* Path operations: put
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    # Find post to delete, exception if not found
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    
    updated_post = post.dict()
    updated_post['id'] = id #copy the index
    my_posts[index] = updated_post
    return {"data": updated_post}

#* DBMS (database management system): 
    # NoSQL database: MongoDB, DynamoDB, ORACLE, SQL Server
    # Relational database: MYSQL, POSTGRESQL, ORACLE, SQL Server
        # SQL: Structured Query Language, used to communicate with DBMS
        # Table represents a subject or event
            # Related to one another
            # Has a unique primary key for each entry (row), NOT always the id. Anything unique (email, SSN)
                # Optional: add a UNIQUE, NOT NULL constraint for columns
        # POSTGRES: also has datatypes (varchar is basically a string)
            # <pgAdmin>: make [postgres] server with localhost admin
            # Make [fastapi] database, then make tables under schemas > public 
            # Datatypes: mkes incrementing integer ID through serial datatype (1, 2, ...), timestamp w/time zone with NOW() defaulted, char varying for text
            # Save data changes to push into database
            # [fastapi] database > query tool
                # ; at end of cmds, capitals ignored so use '' if camelCase, but conventionally capitalize SQL specific keywords
                #* Making queries
                    # SELECT [column name; all with *; or an ordered list col1, col2, col3] FROM [table name]
                        # renaming:     [column name] AS [new col name]
                        # filter rows:  WHERE [conditional col ...]
                        #   conditions: AND, OR, IN {set of num}: = num1 OR = num2 ...
                        #               string = 'str', string LIKE '%TV%' where % is any string
                        # sort:         ORDER BY [col name] [ACSdefault/DESC], [tiebreaker col] [DESC]         
                        # head:         LIMIT [n] [OFFSET n]
                #* Making entries
                    # INSERT INTO [table name] (col1, col2, opt col3, ...) VALUES ('val1', val2, opt val3), (...), ...  [RETURNING] [* or select cols];
                #* Deleting entries
                    # DELETE FROM [table name] WHERE [condition] [RETURNING]
                #* Updating entries
                    # UPDATE [table name] SET [col1 = val1 to update], [col2 = val2] WHERE [condition]                  [RETURNING] [* or select cols]
            # Psycopg 3:57
                    