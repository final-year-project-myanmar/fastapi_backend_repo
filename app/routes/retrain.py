import os

import requests

from fastapi import APIRouter, HTTPException, Request

router= APIRouter()



@router.post("/retrainmodel")
async def retrain_model(request:Request):

    body = await request.json()
    dataset_path = body.get('key')
    print(f">>>> dataset Path: {dataset_path}")

    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO_OWNER = os.getenv('GITHUB_REPO_OWNER')
    GITHUB_REPO_NAME = os.getenv('GITHUB_REPO_NAME')

    if not GITHUB_TOKEN:
        return { "error": "Github token is missing"},500
    if not GITHUB_REPO_OWNER or not GITHUB_REPO_NAME:
        return { "error": "Github repository is misconfigured"},500
    
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/actions/workflows/retrain_model.yml/dispatches"
    data = {
    "ref": "development",#Change the target branch to be work on
    "inputs": {
        "dataset_path": dataset_path
    }
     }
    
    headers = { 
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": f"{GITHUB_REPO_OWNER}",
            }
    
    try:
        response = requests.post(
            url,
            headers = headers,
            json = data,
            timeout = 10  # Set timeout to 10 seconds
        )
        response.raise_for_status()
        
        return {"message": "Model retraining started",
            "github_repo": f"{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}",
            "inputs":f"{dataset_path}",
            "status_code": response.status_code}
        
    except requests.exceptions.RequestException as e:
        print(f"Error dispatching GitHub workflow: {e}")
        raise HTTPException(status_code=response.status_code, detail=str(e))
