import uvicorn

from fastapi import Depends, FastAPI

from .routers import webhook

app = FastAPI()


app.include_router(webhook.router)


@app.get("/")
async def root():
    return {"message": "Hello Webhook Server!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)