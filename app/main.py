import uvicorn

from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .routers import item, webhook

#app = FastAPI(dependencies=[Depends(get_query_token)])
app = FastAPI()


app.include_router(item.router)
app.include_router(webhook.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)