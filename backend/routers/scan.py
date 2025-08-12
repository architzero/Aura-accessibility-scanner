from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from bson import ObjectId
from datetime import datetime

import models
from database import projects_collection, scan_results_collection
from dependencies import get_current_active_user
from services.scanner import scan_website

router = APIRouter(prefix="/scan", tags=["Scanning"])

@router.post("/{project_id}", response_model=models.ScanResult, status_code=status.HTTP_201_CREATED) # <-- Corrected line
async def start_new_scan(project_id: str, current_user = Depends(get_current_active_user)):
    p_id = ObjectId(project_id)
    
    project = await projects_collection.find_one({"_id": p_id, "userId": ObjectId(current_user["_id"])})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        scan_data = await run_in_threadpool(scan_website, url=project["url"], project_id=project_id)
    except RuntimeError as e:
        print(f"--- SCANNER ERROR ---: {e}") 
        raise HTTPException(status_code=400, detail=str(e))

    score = max(0, 100 - (len(scan_data["issues"]) * 2))

    result_to_save = {
        "projectId": p_id,
        "scanType": "live",
        "accessibilityScore": score,
        "issues": scan_data["issues"],
        "genericSuggestions": scan_data["genericSuggestions"],
        "aiSuggestions": scan_data["aiSuggestions"],
        "screenshotUrl": scan_data["screenshot_url"],
        "createdAt": datetime.utcnow()
    }

    new_result = await scan_results_collection.insert_one(result_to_save)
    created_result = await scan_results_collection.find_one({"_id": new_result.inserted_id})
    
    return created_result

@router.get("/results/{result_id}", response_model=models.ScanResult)
async def get_scan_result(result_id: str, current_user = Depends(get_current_active_user)):
    scan_result = await scan_results_collection.find_one({"_id": ObjectId(result_id)})
    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan result not found")

    project = await projects_collection.find_one({
        "_id": scan_result["projectId"],
        "userId": ObjectId(current_user["_id"])
    })
    if not project:
        raise HTTPException(status_code=403, detail="Not authorized to view this scan result")

    return scan_result

@router.delete("/results/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan_result(result_id: str, current_user = Depends(get_current_active_user)):
    scan_result = await scan_results_collection.find_one({"_id": ObjectId(result_id)})
    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan result not found")

    # Security Check: Verify the user owns the project this scan belongs to
    project = await projects_collection.find_one({
        "_id": scan_result["projectId"],
        "userId": ObjectId(current_user["_id"])
    })
    if not project:
        raise HTTPException(status_code=403, detail="Not authorized to delete this scan result")

    # Delete the scan result
    await scan_results_collection.delete_one({"_id": ObjectId(result_id)})
    return