from fastapi import APIRouter,status,Request
from api.services.functionality_services import get_raw_diff_changes,generate_pr_code_review_messages
from api.services.ai_services import generate_code_review_changes

functionality_router=APIRouter(prefix="/api",tags=["Functionality"])

@functionality_router.post("/pr_review", status_code=status.HTTP_200_OK)
async def get_pr_code_review(incoming_request: Request):
    
    raw_diff_changes,repo_owner,repo_name,pr_number,commit_sha= await get_raw_diff_changes(incoming_request)
    
    code_review_changes= await generate_code_review_changes(raw_diff_changes)
    print(code_review_changes)
    
    await generate_pr_code_review_messages(code_review_changes,repo_owner,repo_name,pr_number,commit_sha)
    
    return {"review": code_review_changes}
        
    