from fastapi import APIRouter, HTTPException
import os
import requests

router= APIRouter()



@router.post("/retrainmodel")
async def retrain_model():
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO_OWNER = os.getenv('GITHUB_REPO_OWNER')
    GITHUB_REPO_NAME = os.getenv('GITHUB_REPO_NAME')

    if not GITHUB_TOKEN:
        return { "error": "Github token is missing"},500
    if not GITHUB_REPO_OWNER or not GITHUB_REPO_NAME:
        return { "error": "Github repository is misconfigured"},500
    
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/actions/workflows/retrain_model.yml/dispatches"
    
    headers = { 
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": f"{GITHUB_REPO_OWNER}",
            }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"ref": "main"}
        )
        response.raise_for_status()
        
        return {"message": "Model retraining started",
            "github_repo": f"{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}",
            "status_code": response.status_code}
        
    except requests.exceptions.RequestException as e:
        print(f"Error dispatching GitHub workflow: {e}")
        raise HTTPException(status_code=response.status_code, detail=str(e))
