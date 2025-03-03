import httpx
import logging
from fastapi import Request, HTTPException, status
import jwt
import time
from api.core.config import Config
import base64

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def get_raw_diff_changes(incoming_request: Request):
    
    response = await incoming_request.json()
    logger.info("Incoming Payload: %s", response)  

    if response.get("action") != "opened":
        logger.warning("PR event is not 'opened'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PR event is not 'opened'")

    pull_request = response.get("pull_request")
    repository = response.get("repository")

    if not pull_request or not repository:
        logger.error("Invalid payload structure: Missing pull_request or repository data")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid GitHub webhook payload")

    diff_url = pull_request.get("diff_url")
    repo_owner = repository.get("owner", {}).get("login")
    repo_name = repository.get("name")
    pr_number = pull_request.get("number")
    commit_sha = pull_request.get("head", {}).get("sha")  

    if not all([diff_url, repo_owner, repo_name, pr_number, commit_sha]):
        logger.error("Missing required PR metadata")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required PR metadata")

    logger.info(f"Fetching diff from {repo_owner}/{repo_name} PR #{pr_number}, Commit: {commit_sha}")
    headers = {"Accept": "application/vnd.github.v3.diff"}

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            diff_response = await client.get(diff_url, headers=headers)

        logger.info("GitHub API Response Status: %d", diff_response.status_code)

        if diff_response.status_code == 200:
            diff_changes = diff_response.text
            logger.info("Code review received (preview): %s", diff_changes[:500])  
            return diff_changes, repo_owner, repo_name, pr_number, commit_sha
        else:
            logger.error("Failed to fetch PR diff. Status: %d, Details: %s",
                         diff_response.status_code, diff_response.text)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Failed to fetch PR diff: {diff_response.status_code}")

    except httpx.RequestError as e:
        logger.exception("HTTP Request Failed: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error connecting to GitHub")

async def generate_github_jwt():
    
    app_id = Config.GITHUB_APP_ID
    raw_private_key=Config.GITHUB_PRIVATE_KEY
    private_key_bytes = base64.b64decode(raw_private_key)

    private_key = private_key_bytes.decode("utf-8", errors="replace")
    
    payload = {
        "iat": int(time.time()),  
        "exp": int(time.time()) + (10 * 60),  
        "iss": app_id,  
    }

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt

async def get_installation_access_token(installation_id):
    
    jwt_token = await generate_github_jwt()

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        response = await client.post(url, headers=headers)

        if response.status_code == 201:
            return response.json()["token"]
        else:
            logger.error(f"Failed to get installation token: {response.status_code}, {response.text}")
            raise HTTPException(status_code=401, detail="Failed to get installation token")

async def get_installation_id(repo_owner, repo_name):
   
    jwt_token = await generate_github_jwt()  

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/app/installations", headers=headers)

        if response.status_code != 200:
            logger.error(f"Failed to get installations: {response.status_code}, {response.text}")
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid GitHub App JWT")

        installations = response.json()
        
        for install in installations:
            install_id = install["id"]
            
            
            token = await get_installation_access_token(install_id)  
            repo_headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            repo_response = await client.get("https://api.github.com/installation/repositories", headers=repo_headers)

            if repo_response.status_code == 200:
                repos = [r["full_name"] for r in repo_response.json().get("repositories", [])]
                if f"{repo_owner}/{repo_name}" in repos:
                    return install_id

        raise HTTPException(status_code=404, detail=f"Installation ID not found for {repo_owner}/{repo_name}")
       
async def generate_pr_code_review_messages(code_review_changes, repo_owner, repo_name, pr_number, commit_sha):
    
    installation_id = await get_installation_id(repo_owner, repo_name)

    token = await get_installation_access_token(installation_id)

    GITHUB_API_URL = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }    
    
    async with httpx.AsyncClient() as client:
        for issue in code_review_changes.get("issues", []):
            file_path = issue["file"]
            line_number = issue["line"]


            comment_payload = {
                "body": issue["suggestion"], 
                "commit_id": commit_sha,
                "path": file_path,
                "line": line_number+2,
                "start_line":line_number+1,
                "start_side":"RIGHT",
                "side":"RIGHT"
            }

            response = await client.post(GITHUB_API_URL, json=comment_payload, headers=headers)

            if response.status_code == 201:
                logger.info(f" Successfully posted comment on {file_path}:{line_number}")
            else:
                logger.error(f" Failed to post comment on {file_path}:{line_number}: {response.text}")