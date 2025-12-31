"""Service for managing interviews at root collection level."""
import logging
from datetime import datetime
from typing import Any
from firebase_admin import firestore
from app.app_utils.firestore_store import _get_db


def create_interview(interview_data: dict[str, Any]) -> dict[str, Any]:
    """
    Creates a new interview record in root collection.

    Args:
        interview_data: Interview details (jobId, candidateName, candidateEmail, shareToken)

    Returns:
        Dictionary with interview id, or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        # Build interview document
        interview = {
            "id": "",  # Will be set after creation
            "jobId": interview_data.get("jobId", ""),
            "candidateName": interview_data.get("candidateName", ""),
            "candidateEmail": interview_data.get("candidateEmail", ""),
            "status": "in_progress",
            "startedAt": datetime.utcnow().isoformat(),
            "transcript": "",
        }

        # Save to root interviews collection
        _, doc_ref = client.collection("interviews").add(interview)

        # Update with document ID
        doc_ref.update({"id": doc_ref.id})

        logging.info(f"Interview created with ID: {doc_ref.id}")
        return {"status": "success", "id": doc_ref.id}
    except Exception as e:
        logging.error(f"Error creating interview: {e}")
        return {"error": f"Failed to create interview: {str(e)}"}


def update_interview(
    interview_id: str, updates: dict[str, Any]
) -> dict[str, Any]:
    """
    Updates an existing interview.

    Args:
        interview_id: The interview document ID
        updates: Fields to update

    Returns:
        Dictionary with status or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        doc_ref = client.collection("interviews").document(interview_id)

        # Add timestamp for completedAt if marking as completed
        if updates.get("status") == "completed" and "completedAt" not in updates:
            updates["completedAt"] = datetime.utcnow().isoformat()

        doc_ref.update(updates)

        logging.info(f"Interview {interview_id} updated")
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error updating interview: {e}")
        return {"error": f"Failed to update interview: {str(e)}"}


def get_interviews_by_job(job_id: str, limit: int = 100) -> dict[str, Any]:
    """
    Retrieves all interviews for a specific job.

    Args:
        job_id: The job ID
        limit: Maximum number of interviews to return

    Returns:
        Dictionary with interviews list and count, or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        interviews_ref = (
            client.collection("interviews")
            .where(field_path="jobId", op_string="==", value=job_id)
            .order_by("startedAt", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )

        docs = interviews_ref.stream()

        interviews = []
        for doc in docs:
            interview_data = doc.to_dict()
            interviews.append(interview_data)

        logging.info(f"Retrieved {len(interviews)} interviews for job {job_id}")
        return {"interviews": interviews, "count": len(interviews)}
    except Exception as e:
        logging.error(f"Error retrieving interviews: {e}")
        return {"error": f"Failed to retrieve interviews: {str(e)}"}


def get_interviews_by_user_jobs(user_id: str, limit: int = 100) -> dict[str, Any]:
    """
    Retrieves all interviews for jobs created by a specific user.

    Args:
        user_id: The HR user ID
        limit: Maximum number of interviews to return

    Returns:
        Dictionary with interviews list and count, or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        # First, get all job IDs created by this user
        jobs_ref = client.collection("jobs").where(
            field_path="createdBy", op_string="==", value=user_id
        )
        job_docs = jobs_ref.stream()
        job_ids = [doc.id for doc in job_docs]

        if not job_ids:
            return {"interviews": [], "count": 0}

        # Query interviews for these jobs
        # Note: Firestore 'in' operator supports up to 10 values
        # For hackathon MVP, we'll assume < 10 jobs per user
        interviews_ref = (
            client.collection("interviews")
            .where(field_path="jobId", op_string="in", value=job_ids[:10])
            .order_by("startedAt", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )

        docs = interviews_ref.stream()

        interviews = []
        for doc in docs:
            interview_data = doc.to_dict()
            interviews.append(interview_data)

        logging.info(f"Retrieved {len(interviews)} interviews for user {user_id}")
        return {"interviews": interviews, "count": len(interviews)}
    except Exception as e:
        logging.error(f"Error retrieving user interviews: {e}")
        return {"error": f"Failed to retrieve interviews: {str(e)}"}


def get_interview_by_id(interview_id: str) -> dict[str, Any]:
    """
    Retrieves a single interview by ID.

    Args:
        interview_id: The interview document ID

    Returns:
        Dictionary with interview details, or error
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    try:
        doc_ref = client.collection("interviews").document(interview_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {"error": "Interview not found"}

        interview_data = doc.to_dict()
        return {"interview": interview_data}
    except Exception as e:
        logging.error(f"Error retrieving interview: {e}")
        return {"error": f"Failed to retrieve interview: {str(e)}"}
