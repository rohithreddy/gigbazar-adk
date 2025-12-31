import firebase_admin
from firebase_admin import credentials, firestore
import logging
import os
from typing import Any

# Global client
db = None


def _get_db():
    global db
    if db:
        return db

    try:
        # Check if already initialized
        if not firebase_admin._apps:
            # Use default credentials (GOOGLE_APPLICATION_CREDENTIALS)
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(
                cred,
                {
                    "projectId": os.environ.get("GOOGLE_CLOUD_PROJECT"),
                },
            )

        db = firestore.client()
        return db
    except Exception as e:
        logging.error(f"Failed to initialize Firestore: {e}")
        return None


def save_interview_session(data: dict[str, Any]) -> dict[str, str]:
    """
    Saves the interview session data to Firestore using user subcollections.

    Args:
        data: A dictionary containing interview session details including userId.

    Returns:
        A dictionary with a status or error message.
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    # Extract and validate userId
    user_id = data.get("userId")
    if not user_id:
        logging.error("Missing userId in interview data")
        return {"error": "Missing userId in interview data"}

    try:
        # Save to users/{userId}/interviews/{auto-generated-id}
        _, doc_ref = (
            client.collection("users")
            .document(user_id)
            .collection("interviews")
            .add(data)
        )
        logging.info(f"Interview saved for user {user_id} with ID: {doc_ref.id}")
        return {"status": "success", "id": doc_ref.id}
    except Exception as e:
        logging.error(f"Error writing to Firestore: {e}")
        return {"error": f"Failed to save data: {str(e)}"}


def get_user_interviews(user_id: str, limit: int = 50) -> dict[str, Any]:
    """
    Retrieves all interviews for a specific user from Firestore.

    Args:
        user_id: The user ID to query interviews for.
        limit: Maximum number of interviews to return (default 50).

    Returns:
        A dictionary with interviews list and count, or error message.
    """
    client = _get_db()
    if not client:
        return {"error": "Database not initialized"}

    if not user_id:
        logging.error("Missing user_id parameter")
        return {"error": "Missing user_id parameter"}

    try:
        # Query users/{userId}/interviews collection
        interviews_ref = (
            client.collection("users")
            .document(user_id)
            .collection("interviews")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )

        # Execute query
        docs = interviews_ref.stream()

        # Convert to list of dictionaries
        interviews = []
        for doc in docs:
            interview_data = doc.to_dict()
            interview_data["id"] = doc.id  # Include document ID
            interviews.append(interview_data)

        logging.info(f"Retrieved {len(interviews)} interviews for user {user_id}")
        return {"interviews": interviews, "count": len(interviews)}
    except Exception as e:
        logging.error(f"Error reading from Firestore: {e}")
        return {"error": f"Failed to retrieve data: {str(e)}"}
