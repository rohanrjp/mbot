from fastapi import FastAPI,status
import uvicorn
from api.routes import functionality_router

api_version="v1"
app=FastAPI(title="MariaBot",description="A Github PR Code Reviewer",version=api_version)

@app.get("/",status_code=status.HTTP_200_OK,tags=["Root route"])
async def hello_world():
    return {"message":"hello world!"}

app.include_router(functionality_router)

if __name__ == "__main__":
    uvicorn.run(app)
