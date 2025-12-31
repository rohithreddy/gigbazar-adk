"""
DEPRECATED: This module uses file-based storage and is kept for reference only.

The application now uses Firestore for interview data storage.
See app/app_utils/firestore_store.py for the current implementation.

This file is retained for potential data recovery from legacy JSON files.
"""
import json
import os
from typing import Any, Dict
import logging

# We will store data in a 'data' directory at the project root for now.
DATA_DIR = "data"
INTERVIEW_FILE = os.path.join(DATA_DIR, "interviews.json")


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def save_interview_session(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Appends the interview session data to a JSON file.

    Args:
        data: A dictionary containing interview session details.

    Returns:
        A dictionary with a status or error message.
    """
    _ensure_data_dir()

    interviews = []

    # Read existing data if file exists
    if os.path.exists(INTERVIEW_FILE):
        try:
            with open(INTERVIEW_FILE, "r") as f:
                content = f.read()
                if content:
                    interviews = json.loads(content)
        except json.JSONDecodeError:
            logging.warning(f"Could not decode {INTERVIEW_FILE}, starting fresh.")
        except Exception as e:
            logging.error(f"Error reading {INTERVIEW_FILE}: {e}")
            return {"error": f"Failed to read storage: {str(e)}"}

    # Append new session
    interviews.append(data)

    # Write back
    try:
        with open(INTERVIEW_FILE, "w") as f:
            json.dump(interviews, f, indent=2)
        return {"status": "success", "message": "Interview saved successfully"}
    except Exception as e:
        logging.error(f"Error writing to {INTERVIEW_FILE}: {e}")
        return {"error": f"Failed to save data: {str(e)}"}
