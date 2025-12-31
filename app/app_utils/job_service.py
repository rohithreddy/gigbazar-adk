"""Service for managing job postings."""
import logging
import uuid
from datetime import datetime
from typing import Any
from firebase_admin import firestore
from app.app_utils.firestore_store import _get_db


def create_job(user_id: str, job_data: dict[str, Any]) -> dict[str, Any]:
    """
    Creates a new job posting.

    Args:
        user_id: The HR user creating the job
        job_data: Job details (title, description, skills, difficulty, etc.)

    Returns:
        Dictionary with job id and share token, or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        # Generate unique share token
        share_token = str(uuid.uuid4())

        # Build job document
        job = {
            "id": "",  # Will be set after creation
            "createdBy": user_id,
            "title": job_data.get("title", ""),
            "description": job_data.get("description", ""),
            "skills": job_data.get("skills", []),
            "difficulty": job_data.get("difficulty", "mid"),
            "interviewDuration": job_data.get("interviewDuration", 10),
            "customPrompt": job_data.get("customPrompt", ""),
            "shareToken": share_token,
            "createdAt": datetime.utcnow().isoformat(),
        }

        # Save to Firestore
        _, doc_ref = client.collection("jobs").add(job)

        # Update with document ID
        doc_ref.update({"id": doc_ref.id})

        logging.info(f"Job created with ID: {doc_ref.id}")
        return {
            "status": "success",
            "id": doc_ref.id,
            "shareToken": share_token,
        }
    except Exception as e:
        logging.error(f"Error creating job: {e}")
        return {"error": f"Failed to create job: {str(e)}"}


def get_jobs(user_id: str, limit: int = 50) -> dict[str, Any]:
    """
    Retrieves all jobs created by a specific user.

    Args:
        user_id: The HR user ID
        limit: Maximum number of jobs to return

    Returns:
        Dictionary with jobs list and count, or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        # Query jobs created by this user
        jobs_ref = (
            client.collection("jobs")
            .where(field_path="createdBy", op_string="==", value=user_id)
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )

        # Execute query
        docs = jobs_ref.stream()

        # Convert to list
        jobs = []
        for doc in docs:
            job_data = doc.to_dict()
            jobs.append(job_data)

        logging.info(f"Retrieved {len(jobs)} jobs for user {user_id}")
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        logging.error(f"Error retrieving jobs: {e}")
        return {"error": f"Failed to retrieve jobs: {str(e)}"}


def get_job_by_token(share_token: str) -> dict[str, Any]:
    """
    Retrieves a job by its share token (public endpoint).

    Args:
        share_token: The unique share token

    Returns:
        Dictionary with job details, or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        # Query by share token
        jobs_ref = (
            client.collection("jobs")
            .where(field_path="shareToken", op_string="==", value=share_token)
            .limit(1)
        )

        docs = list(jobs_ref.stream())

        if not docs:
            return {"error": "Job not found"}

        job_data = docs[0].to_dict()
        return {"job": job_data}
    except Exception as e:
        logging.error(f"Error retrieving job by token: {e}")
        return {"error": f"Failed to retrieve job: {str(e)}"}


def get_job_by_id(job_id: str) -> dict[str, Any]:
    """
    Retrieves a job by its ID.

    Args:
        job_id: The job document ID

    Returns:
        Dictionary with job details, or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        doc_ref = client.collection("jobs").document(job_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {"error": "Job not found"}

        job_data = doc.to_dict()
        return {"job": job_data}
    except Exception as e:
        logging.error(f"Error retrieving job: {e}")
        return {"error": f"Failed to retrieve job: {str(e)}"}


def update_job(job_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """
    Updates an existing job.

    Args:
        job_id: The job document ID
        updates: Fields to update (e.g., {"agentId": "agent-123"})

    Returns:
        Dictionary with status or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        doc_ref = client.collection("jobs").document(job_id)
        doc_ref.update(updates)

        logging.info(f"Job {job_id} updated")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error updating job: {e}")
        return {"error": f"Failed to update job: {str(e)}"}
