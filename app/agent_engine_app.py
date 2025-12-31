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
            "save_interview_data",
            "get_user_interviews",
        ]
        # Add bidi_stream_query for adk_live
        operations["bidi_stream"] = ["bidi_stream_query"]
        return operations

    def get_elevenlabs_signed_url(self, agent_id: str) -> dict[str, str]:
        """Generates a signed URL for the ElevenLabs agent."""
        try:
            from elevenlabs.client import ElevenLabs

            api_key = os.environ.get("ELEVENLABS_API_KEY")
            if not api_key:
                self.logger.log_text("ELEVENLABS_API_KEY not found", severity="ERROR")
                return {"error": "Server configuration error: Missing API Key"}

            client = ElevenLabs(api_key=api_key)
            # The SDK might return an object, we need it as string.
            # Assuming client.conversational_ai.get_signed_url returns a response object or string.
            # Based on docs, it returns a GetSignedUrlResponse which has a signed_url property.
            response = client.conversational_ai.get_signed_url(agent_id=agent_id)
            return {"signed_url": response.signed_url}
        except Exception as e:
            self.logger.log_text(
                f"Error generating signed URL: {str(e)}", severity="ERROR"
            )
            return {"error": str(e)}

    def save_interview_data(self, data: dict[str, Any]) -> dict[str, str]:
        """Saves interview session data."""
        return save_interview_session(data)

    def get_user_interviews(self, user_id: str, limit: int = 50) -> dict[str, Any]:
        """Retrieves interview history for a specific user."""
        return get_user_interviews(user_id, limit)


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
