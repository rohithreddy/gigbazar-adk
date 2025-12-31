# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# mypy: disable-error-code="attr-defined,arg-type"
import logging
import os
from typing import Any

import vertexai
from dotenv import load_dotenv
from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.cloud import logging as google_cloud_logging
from vertexai.agent_engines.templates.adk import AdkApp
from vertexai.preview.reasoning_engines import AdkApp as PreviewAdkApp

from app.agent import app as adk_app
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback
from app.app_utils.firestore_store import get_user_interviews, save_interview_session
from app.app_utils.job_service import (
    create_job,
    get_jobs,
    get_job_by_token,
    get_job_by_id,
)
from app.app_utils.interview_service import (
    create_interview,
    update_interview,
    get_interviews_by_user_jobs,
    get_interview_by_id,
)
from app.app_utils.prompt_builder import build_interview_prompt, build_first_message
from app.app_utils.elevenlabs_service import (
    create_conversational_agent,
    update_agent_prompt,
    get_signed_url_for_agent,
    delete_agent,
)

# Load environment variables from .env file at runtime
load_dotenv()


class AgentEngineApp(AdkApp):
    def set_up(self) -> None:
        """Initialize the agent engine app with logging and telemetry."""
        vertexai.init()
        setup_telemetry()
        super().set_up()
        logging.basicConfig(level=logging.INFO)
        logging_client = google_cloud_logging.Client()
        self.logger = logging_client.logger(__name__)
        if gemini_location:
            os.environ["GOOGLE_CLOUD_LOCATION"] = gemini_location

    def register_feedback(self, feedback: dict[str, Any]) -> None:
        """Collect and log feedback."""
        feedback_obj = Feedback.model_validate(feedback)
        self.logger.log_struct(feedback_obj.model_dump(), severity="INFO")

    def register_operations(self) -> dict[str, list[str]]:
        """Registers the operations of the Agent."""
        operations = super().register_operations()
        operations[""] = operations.get("", []) + [
            "register_feedback",
            "get_elevenlabs_signed_url",
            "get_elevenlabs_signed_url_for_job",
            "save_interview_data",
            "get_user_interviews",
            # Job management endpoints
            "create_job",
            "get_jobs",
            "get_job_by_token",
            "get_job_by_id",
            # Interview management endpoints
            "create_interview",
            "update_interview",
            "get_user_interviews_for_jobs",
            "get_interview_by_id",
            # ElevenLabs agent management
            "create_agent_for_job",
            "update_agent_for_job",
            "delete_agent_for_job",
        ]
        # Add bidi_stream_query for adk_live
        operations["bidi_stream"] = ["bidi_stream_query"]
        return operations

    def get_elevenlabs_signed_url(self, agent_id: str) -> dict[str, str]:
        """Generates a signed URL for the ElevenLabs agent authentication."""
        try:
            from elevenlabs.client import ElevenLabs

            api_key = os.environ.get("ELEVENLABS_API_KEY")
            if not api_key:
                logging.error("ELEVENLABS_API_KEY not found")
                return {"error": "Server configuration error: Missing API Key"}

            client = ElevenLabs(api_key=api_key)
            # Use the correct SDK method for getting signed URLs
            response = client.conversational_ai.conversations.get_signed_url(agent_id=agent_id)
            return {"signed_url": response.signed_url}
        except Exception as e:
            logging.error(f"Error generating signed URL: {str(e)}")
            return {"error": str(e)}

    def save_interview_data(self, data: dict[str, Any]) -> dict[str, str]:
        """Saves interview session data."""
        return save_interview_session(data)

    def get_user_interviews(self, user_id: str, limit: int = 50) -> dict[str, Any]:
        """Retrieves interview history for a specific user."""
        return get_user_interviews(user_id, limit)

    # Job management endpoints
    def create_job(self, user_id: str, job_data: dict[str, Any]) -> dict[str, Any]:
        """Creates a new job posting and automatically creates a dedicated agent."""
        # Create the job first
        result = create_job(user_id, job_data)

        if "error" in result:
            return result

        job_id = result.get("id")
        if not job_id:
            return result

        # Automatically create a dedicated ElevenLabs agent for this job
        try:
            # Get the newly created job
            job_result = get_job_by_id(job_id)
            if "error" not in job_result:
                job = job_result["job"]

                # Build prompt and first message
                system_prompt = build_interview_prompt(job)
                first_message = build_first_message(job)
                agent_name = f"Interview Agent - {job.get('title', 'Position')}"

                # Create the agent
                agent_result = create_conversational_agent(
                    name=agent_name,
                    first_message=first_message,
                    system_prompt=system_prompt,
                    language="en"
                )

                if "error" not in agent_result and "agent_id" in agent_result:
                    # Update the job with the agent details
                    from app.app_utils.job_service import update_job
                    from datetime import datetime

                    agent_metadata = {
                        "agentId": agent_result["agent_id"],
                        "agentName": agent_result.get("agent_name", agent_name),
                        "agentCreatedAt": datetime.utcnow().isoformat(),
                        "agentVoiceId": os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
                        "agentLanguage": "en"
                    }
                    update_job(job_id, agent_metadata)

                    # Add agent info to the result
                    result["agentId"] = agent_result["agent_id"]
                    result["agentName"] = agent_result.get("agent_name", agent_name)
                    result["agentCreatedAt"] = agent_metadata["agentCreatedAt"]

                    logging.info(f"Created agent {agent_result['agent_id']} for job {job_id}")
                else:
                    # Log the error but don't fail the job creation
                    logging.warning(
                        f"Failed to create agent for job {job_id}: {agent_result.get('error', 'Unknown error')}"
                    )
        except Exception as e:
            # Log the error but don't fail the job creation
            logging.warning(f"Error creating agent for job {job_id}: {str(e)}")

        return result

    def get_jobs(self, user_id: str, limit: int = 50) -> dict[str, Any]:
        """Retrieves all jobs for a user."""
        return get_jobs(user_id, limit)

    def get_job_by_token(self, share_token: str) -> dict[str, Any]:
        """Retrieves a job by its share token (public)."""
        return get_job_by_token(share_token)

    def get_job_by_id(self, job_id: str) -> dict[str, Any]:
        """Retrieves a job by its ID."""
        return get_job_by_id(job_id)

    # Interview management endpoints
    def create_interview(self, interview_data: dict[str, Any]) -> dict[str, Any]:
        """Creates a new interview record."""
        return create_interview(interview_data)

    def update_interview(
        self, interview_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Updates an existing interview."""
        return update_interview(interview_id, updates)

    def get_user_interviews_for_jobs(
        self, user_id: str, limit: int = 100
    ) -> dict[str, Any]:
        """Retrieves all interviews for jobs created by user."""
        return get_interviews_by_user_jobs(user_id, limit)

    def get_interview_by_id(self, interview_id: str) -> dict[str, Any]:
        """Retrieves a single interview by ID."""
        return get_interview_by_id(interview_id)

    def get_elevenlabs_signed_url_for_job(self, job_id: str) -> dict[str, str]:
        """Generates a signed URL with dynamic prompt based on job requirements."""
        try:
            from elevenlabs.client import ElevenLabs

            api_key = os.environ.get("ELEVENLABS_API_KEY")
            if not api_key:
                logging.error("ELEVENLABS_API_KEY not found")
                return {"error": "Server configuration error: Missing API Key"}

            # Get job details
            job_result = get_job_by_id(job_id)
            if "error" in job_result:
                return job_result

            job = job_result["job"]

            # Check if job has an agent_id, if not use default
            agent_id = job.get("agentId") or os.environ.get(
                "ELEVENLABS_AGENT_ID", "your-default-agent-id"
            )

            # Build dynamic prompt for display
            prompt = build_interview_prompt(job)

            client = ElevenLabs(api_key=api_key)
            # Use the correct SDK method for getting signed URLs
            response = client.conversational_ai.conversations.get_signed_url(agent_id=agent_id)

            # Return both signed URL and the prompt
            return {"signed_url": response.signed_url, "prompt": prompt}
        except Exception as e:
            logging.error(f"Error generating signed URL for job: {str(e)}")
            return {"error": str(e)}

    def create_agent_for_job(self, job_id: str) -> dict[str, Any]:
        """Creates a new ElevenLabs agent specifically for a job."""
        try:
            # Get job details
            job_result = get_job_by_id(job_id)
            if "error" in job_result:
                return job_result

            job = job_result["job"]

            # Build prompt and first message
            system_prompt = build_interview_prompt(job)
            first_message = build_first_message(job)
            agent_name = f"Interview Agent - {job.get('title', 'Position')}"

            # Create the agent
            result = create_conversational_agent(
                name=agent_name,
                first_message=first_message,
                system_prompt=system_prompt,
                language="en"
            )

            if "error" in result:
                return result

            # Update the job with the agent ID
            from app.app_utils.job_service import update_job
            update_job(job_id, {"agentId": result["agent_id"]})

            logging.info(f"Created agent {result['agent_id']} for job {job_id}")

            return result
        except Exception as e:
            logging.error(f"Error creating agent for job: {str(e)}")
            return {"error": str(e)}

    def update_agent_for_job(self, job_id: str) -> dict[str, Any]:
        """Updates an existing agent's prompt for a job."""
        try:
            # Get job details
            job_result = get_job_by_id(job_id)
            if "error" in job_result:
                return job_result

            job = job_result["job"]
            agent_id = job.get("agentId")

            if not agent_id:
                return {"error": "Job does not have an associated agent"}

            # Build updated prompt
            system_prompt = build_interview_prompt(job)

            # Update the agent
            result = update_agent_prompt(agent_id, system_prompt)

            if "error" in result:
                return result

            logging.info(f"Updated agent {agent_id} for job {job_id}")

            return result
        except Exception as e:
            logging.error(f"Error updating agent for job: {str(e)}")
            return {"error": str(e)}

    def delete_agent_for_job(self, job_id: str) -> dict[str, Any]:
        """Deletes an agent associated with a job."""
        try:
            # Get job details
            job_result = get_job_by_id(job_id)
            if "error" in job_result:
                return job_result

            job = job_result["job"]
            agent_id = job.get("agentId")

            if not agent_id:
                return {"error": "Job does not have an associated agent"}

            # Delete the agent
            result = delete_agent(agent_id)

            if "error" in result:
                return result

            # Remove agent ID from job
            from app.app_utils.job_service import update_job
            update_job(job_id, {"agentId": None})

            logging.info(f"Deleted agent {agent_id} for job {job_id}")

            return result
        except Exception as e:
            logging.error(f"Error deleting agent for job: {str(e)}")
            return {"error": str(e)}


# Add bidi_stream_query support from preview AdkApp for adk_live
AgentEngineApp.bidi_stream_query = PreviewAdkApp.bidi_stream_query


gemini_location = os.environ.get("GOOGLE_CLOUD_LOCATION")
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
agent_engine = AgentEngineApp(
    app=adk_app,
    artifact_service_builder=lambda: GcsArtifactService(bucket_name=logs_bucket_name)
    if logs_bucket_name
    else InMemoryArtifactService(),
)
