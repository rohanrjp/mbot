import httpx
import logging
from fastapi import Request, HTTPException, status

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def get_raw_diff_changes(incoming_request: Request):
    response = await incoming_request.json()
    logger.info("Incoming Payload: %s", response)  

    if response.get("action") != "opened":
        logger.warning("PR event is not 'opened'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PR event is not 'opened'")

    pull_request = response.get("pull_request")
    diff_url = pull_request.get("diff_url") if pull_request else None

    if not diff_url:
        logger.error("No diff_url found in the payload")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No diff_url found in the payload")

    logger.info("Fetching diff from URL: %s", diff_url)
    headers = {"Accept": "application/vnd.github.v3.diff"}

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            diff_response = await client.get(diff_url, headers=headers)

        logger.info("GitHub API Response Status: %d", diff_response.status_code)

        if diff_response.status_code == 200:
            diff_changes = diff_response.text
            logger.info("Code review received (preview): %s", diff_changes[:500])  
            return diff_changes
        else:
            logger.error("Failed to fetch PR diff. Status: %d, Details: %s",
                         diff_response.status_code, diff_response.text)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Failed to fetch PR diff: {diff_response.status_code}")

    except httpx.RequestError as e:
        logger.exception("HTTP Request Failed: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error connecting to GitHub")