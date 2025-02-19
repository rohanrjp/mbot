from fastapi import APIRouter,status

functionality_router=APIRouter(prefix="/api",tags=["Functionality"])

@functionality_router.get("/pr_reveiw",status_code=status.HTTP_200_OK)
async def get_pr_code_review():
    return {"message":"Code review"}