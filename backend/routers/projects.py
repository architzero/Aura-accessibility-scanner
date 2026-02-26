from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime, timezone
import pymongo

import models
from database import projects_collection, scan_results_collection
from dependencies import get_current_active_user
from utils import validate_url, logger

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=models.Project, status_code=status.HTTP_201_CREATED)
async def create_project(project: models.ProjectCreate, current_user: models.User = Depends(get_current_active_user)):
    # Validate URL format and security
    if not validate_url(project.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format or unsafe URL detected"
        )
    
    # Check for unique project names
    existing_project = await projects_collection.find_one({
        "projectName": project.projectName,
        "userId": ObjectId(current_user["_id"])
    })
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A project with this name already exists."
        )

    project_data = project.dict()
    project_data["userId"] = ObjectId(current_user["_id"])
    project_data["createdAt"] = datetime.now(timezone.utc)

    new_project = await projects_collection.insert_one(project_data)
    created_project = await projects_collection.find_one({"_id": new_project.inserted_id})
    
    logger.info(f"Project created: {created_project['_id']} by user {current_user['email']}")
    return created_project

@router.get("/", response_model=List[models.Project])
async def get_projects(current_user: models.User = Depends(get_current_active_user)):
    # --- MODIFIED: Added sorting to show newest first ---
    projects = await projects_collection.find(
        {"userId": ObjectId(current_user["_id"])}
    ).sort("createdAt", pymongo.DESCENDING).to_list(100)
    return projects

@router.get("/{project_id}", response_model=models.Project)
async def get_project(project_id: str, current_user: models.User = Depends(get_current_active_user)):
    project = await projects_collection.find_one({"_id": ObjectId(project_id), "userId": ObjectId(current_user["_id"])})
    if project:
        return project
    raise HTTPException(status_code=404, detail="Project not found")

@router.get("/{project_id}/history", response_model=List[models.ScanResult])
async def get_scan_history(project_id: str, current_user: models.User = Depends(get_current_active_user)):
    project = await projects_collection.find_one({"_id": ObjectId(project_id), "userId": ObjectId(current_user["_id"])})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    history = await scan_results_collection.find(
        {"projectId": ObjectId(project_id)}
    ).sort("createdAt", pymongo.DESCENDING).to_list(100)

    return history

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, current_user: models.User = Depends(get_current_active_user)):
    # --- ADD THIS: Also delete associated scan results ---
    await scan_results_collection.delete_many({"projectId": ObjectId(project_id)})
    # ---------------------------------------------------
    
    delete_result = await projects_collection.delete_one({"_id": ObjectId(project_id), "userId": ObjectId(current_user["_id"])})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return