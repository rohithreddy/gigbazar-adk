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

import asyncio
import json
import logging
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

import backoff
import google.auth
import vertexai
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import logging as google_cloud_logging
from pydantic import BaseModel, Field
from websockets.exceptions import ConnectionClosedError

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the path to the frontend build directory
current_dir = Path(__file__).parent
frontend_build_dir = current_dir.parent.parent / "frontend" / "build"

# Mount static files if build directory exists
if frontend_build_dir.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(frontend_build_dir / "static")),
        name="static",
    )
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize default configuration
app.state.config = {
    "use_remote_agent": False,
    "remote_agent_engine_id": None,
    "project_id": None,
    "location": "us-central1",
    "local_agent_path": "..agent.root_agent",
    "agent_engine_object_path": "..agent_engine_app.agent_engine",
}


class WebSocketToQueueAdapter:
    """Adapter to convert WebSocket messages to an asyncio Queue for the agent engine."""

    def __init__(
        self,
        websocket: WebSocket,
        agent_engine: Any = None,
        remote_config: dict[str, Any] | None = None,
    ):
        """Initialize the adapter.

        Args:
            websocket: The client websocket connection
            agent_engine: The agent engine instance with bidi_stream_query method (None if using remote)
            remote_config: Remote agent engine configuration (project_id, location, remote_agent_engine_id)
        """
        self.websocket = websocket
        self.agent_engine = agent_engine
        self.remote_config = remote_config
        self.input_queue: asyncio.Queue[dict] = asyncio.Queue()
        self.first_message = True

    def _transform_remote_agent_engine_response(self, response: dict) -> dict:
        """Transform remote Agent Engine bidiStreamOutput to ADK Event format for frontend."""
        # Check if this is a remote Agent Engine bidiStreamOutput
        bidi_output = response.get("bidiStreamOutput")
        if not bidi_output:
            # Not a remote agent engine response, return as-is
            return response

        # Transform to ADK Event format that frontend already handles
        # Just unwrap the bidiStreamOutput wrapper - the content is already in ADK Event format
        return bidi_output

    async def receive_from_client(self) -> None:
        """Listen for messages from the client and put them in the queue."""
        while True:
            try:
                # Use receive() instead of receive_json() to handle both text and binary data
                message = await self.websocket.receive()

                # Handle different message types
                if "text" in message:
                    # Parse JSON text messages
                    data = json.loads(message["text"])

                    if isinstance(data, dict):
                        # Skip setup messages - they're for backend logging only, not valid LiveRequest format
                        if "setup" in data:
                            # Log setup information
                            logger.log_struct(
                                {**data["setup"], "type": "setup"}, severity="INFO"
                            )
                            logging.info(
                                "Received setup message (not forwarding to agent)"
                            )
                            continue

                        # Frontend handles message format for both modes
                        await self.input_queue.put(data)
                    else:
                        logging.warning(
                            f"Received unexpected JSON structure from client: {data}"
                        )

                elif "bytes" in message:
                    # Handle binary data
                    # Convert binary to appropriate format for agent engine
                    await self.input_queue.put({"binary_data": message["bytes"]})

                else:
                    logging.warning(
                        f"Received unexpected message type from client: {message}"
                    )

            except ConnectionClosedError as e:
                logging.warning(f"Client closed connection: {e}")
                break
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON from client: {e}")
                break
            except Exception as e:
                logging.error(f"Error receiving from client: {e!s}")
                break

    async def run_agent_engine(self) -> None:
        """Run the agent engine with the input queue."""
        try:
            if self.agent_engine is not None:
                # Local agent engine mode
                # Give the agent engine a moment to initialize before sending setupComplete
                await asyncio.sleep(1)

                # Send setupComplete after initialization delay
                setup_complete_response: dict = {"setupComplete": {}}
                await self.websocket.send_json(setup_complete_response)

                async for response in self.agent_engine.bidi_stream_query(
                    self.input_queue
                ):
                    # Send responses from agent engine to the websocket client
                    if response is not None:
                        await self.websocket.send_json(response)

                        # Check for error responses
                        if isinstance(response, dict) and "error" in response:
                            logging.error(f"Agent engine error: {response['error']}")
                            break
            else:
                # Remote agent engine mode
                # Don't send setupComplete until remote connection is established
                assert self.remote_config is not None, (
                    "remote_config must be set for remote mode"
                )
                await self.run_remote_agent_engine(
                    project_id=self.remote_config["project_id"],
                    location=self.remote_config["location"],
                    remote_agent_engine_id=self.remote_config["remote_agent_engine_id"],
                )
        except Exception as e:
            logging.error(f"Error in agent engine: {e}")
            await self.websocket.send_json({"error": str(e)})

    async def run_remote_agent_engine(
        self, project_id: str, location: str, remote_agent_engine_id: str
    ) -> None:
        """Run the remote agent engine connection."""
        client = vertexai.Client(
            project=project_id,
            location=location,
        )

        async with client.aio.live.agent_engines.connect(
            agent_engine=remote_agent_engine_id,
            config={"class_method": "bidi_stream_query"},
        ) as session:
            # Send setupComplete only after remote connection is established
            logging.info("Remote agent engine connection established")
            setup_complete_response: dict = {"setupComplete": {}}
            await self.websocket.send_json(setup_complete_response)

            # Create task to forward messages from queue to remote session
            async def forward_to_remote() -> None:
                while True:
                    try:
                        message = await self.input_queue.get()
                        await session.send(message)
                    except Exception as e:
                        logging.error(f"Error forwarding to remote: {e}")
                        break

            # Create task to receive from remote and send to websocket
            async def receive_from_remote() -> None:
                while True:
                    try:
                        response = await session.receive()
                        if response is not None:
                            # Transform remote Agent Engine bidiStreamOutput format to frontend format
                            transformed = self._transform_remote_agent_engine_response(
                                response
                            )
                            if transformed:
                                await self.websocket.send_json(transformed)

                            # Check for error responses
                            if isinstance(response, dict) and "error" in response:
                                logging.error(
                                    f"Remote agent engine error: {response['error']}"
                                )
                                break
                    except Exception as e:
                        logging.error(f"Error receiving from remote: {e}")
                        break

            await asyncio.gather(
                forward_to_remote(),
                receive_from_remote(),
            )


def _dynamic_import(path: str) -> Any:
    """Dynamically import an object from a given path.

    Args:
        path: Python import path (e.g., '..agent.root_agent')

    Returns:
        The imported object
    """
    import importlib

    module_path, object_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path, package=__package__)
    return getattr(module, object_name)


def get_connect_and_run_callable(
    websocket: WebSocket, config: dict[str, Any]
) -> Callable:
    """Create a callable that handles agent engine connection with retry logic.

    Args:
        websocket: The client websocket connection
        config: Configuration dict with agent engine settings

    Returns:
        Callable: An async function that establishes and manages the agent engine connection
    """

    async def on_backoff(details: backoff._typing.Details) -> None:
        await websocket.send_json(
            {
                "status": f"Model connection error, retrying in {details['wait']} seconds..."
            }
        )

    @backoff.on_exception(
        backoff.expo, ConnectionClosedError, max_tries=10, on_backoff=on_backoff
    )
    async def connect_and_run() -> None:
        if config["use_remote_agent"]:
            # Remote agent engine mode
            logging.info(
                f"Connecting to remote agent engine: {config['remote_agent_engine_id']}"
            )
            remote_config = {
                "project_id": config["project_id"],
                "location": config["location"],
                "remote_agent_engine_id": config["remote_agent_engine_id"],
            }
            adapter = WebSocketToQueueAdapter(
                websocket, agent_engine=None, remote_config=remote_config
            )
        else:
            # Local agent engine mode
            # Dynamically import the pre-configured agent_engine object
            agent_engine = _dynamic_import(config["agent_engine_object_path"])
            logging.info(
                f"Starting local agent engine with object: {type(agent_engine).__name__}"
            )

            adapter = WebSocketToQueueAdapter(websocket, agent_engine)

        logging.info("Starting bidirectional communication with agent engine")
        await asyncio.gather(
            adapter.receive_from_client(),
            adapter.run_agent_engine(),
        )

    return connect_and_run


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle new websocket connections."""
    await websocket.accept()
    connect_and_run = get_connect_and_run_callable(websocket, app.state.config)
    await connect_and_run()


class Feedback(BaseModel):
    """Represents feedback for a conversation."""

    score: int | float
    text: str | None = ""
    log_type: Literal["feedback"] = "feedback"
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# Global cache for the agent engine instance
_agent_engine_instance = None


def _get_agent_engine() -> Any:
    """Get or load the agent engine instance."""
    global _agent_engine_instance
    if _agent_engine_instance:
        return _agent_engine_instance

    config = app.state.config
    if config.get("use_remote_agent"):
        # For now, we don't support proxying arbitrary HTTP calls to remote engine easily
        # without client library wrapper.
        raise HTTPException(
            status_code=501,
            detail="HTTP operations not supported in remote mode in this proxy yet.",
        )

    try:
        _agent_engine_instance = _dynamic_import(config["agent_engine_object_path"])
        return _agent_engine_instance
    except Exception as e:
        logging.error(f"Failed to load agent engine: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load agent engine: {e}")


@app.post("/get_elevenlabs_signed_url")
async def get_elevenlabs_signed_url(request: dict[str, Any]) -> dict[str, str]:
    """Proxy for get_elevenlabs_signed_url."""
    agent_id = request.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="Missing agent_id")

    engine = _get_agent_engine()
    # Ensure method exists
    if not hasattr(engine, "get_elevenlabs_signed_url"):
        raise HTTPException(
            status_code=404,
            detail="Method get_elevenlabs_signed_url not found on agent engine",
        )

    return engine.get_elevenlabs_signed_url(agent_id=agent_id)


@app.post("/get_elevenlabs_signed_url_for_job")
async def get_elevenlabs_signed_url_for_job(request: dict[str, Any]) -> dict[str, str]:
    """Proxy for get_elevenlabs_signed_url_for_job - gets signed URL with job-specific agent."""
    job_id = request.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="Missing job_id")

    engine = _get_agent_engine()
    # Ensure method exists
    if not hasattr(engine, "get_elevenlabs_signed_url_for_job"):
        raise HTTPException(
            status_code=404,
            detail="Method get_elevenlabs_signed_url_for_job not found on agent engine",
        )

    return engine.get_elevenlabs_signed_url_for_job(job_id=job_id)


@app.post("/save_interview_data")
async def save_interview_data(data: dict[str, Any]) -> dict[str, Any]:
    """Proxy for save_interview_data."""
    engine = _get_agent_engine()
    if not hasattr(engine, "save_interview_data"):
        raise HTTPException(
            status_code=404,
            detail="Method save_interview_data not found on agent engine",
        )

    return engine.save_interview_data(data)


@app.get("/get_user_interviews")
async def get_user_interviews(user_id: str, limit: int = 50) -> dict[str, Any]:
    """Retrieve interview history for a specific user.

    Args:
        user_id: The user ID to query interviews for (required query parameter)
        limit: Maximum number of interviews to return (default 50)

    Returns:
        JSON with interviews list and count
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing required parameter: user_id")

    engine = _get_agent_engine()
    if not hasattr(engine, "get_user_interviews"):
        raise HTTPException(
            status_code=404,
            detail="Method get_user_interviews not found on agent engine",
        )

    result = engine.get_user_interviews(user_id=user_id, limit=limit)

    # Check if result contains an error
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# Job management endpoints
@app.post("/create_job")
async def create_job(request: dict[str, Any]) -> dict[str, Any]:
    """Create a new job posting."""
    user_id = request.get("user_id")
    job_data = request.get("job_data")

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing required parameter: user_id")
    if not job_data:
        raise HTTPException(status_code=400, detail="Missing required parameter: job_data")

    engine = _get_agent_engine()
    if not hasattr(engine, "create_job"):
        raise HTTPException(
            status_code=404,
            detail="Method create_job not found on agent engine",
        )

    result = engine.create_job(user_id=user_id, job_data=job_data)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/get_jobs")
async def get_jobs(request: dict[str, Any]) -> dict[str, Any]:
    """Retrieve all jobs for a user."""
    user_id = request.get("user_id")
    limit = request.get("limit", 50)

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing required parameter: user_id")

    engine = _get_agent_engine()
    if not hasattr(engine, "get_jobs"):
        raise HTTPException(
            status_code=404,
            detail="Method get_jobs not found on agent engine",
        )

    result = engine.get_jobs(user_id=user_id, limit=limit)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/get_job_by_token")
async def get_job_by_token(request: dict[str, Any]) -> dict[str, Any]:
    """Retrieve a job by its share token (public)."""
    share_token = request.get("share_token")

    if not share_token:
        raise HTTPException(status_code=400, detail="Missing required parameter: share_token")

    engine = _get_agent_engine()
    if not hasattr(engine, "get_job_by_token"):
        raise HTTPException(
            status_code=404,
            detail="Method get_job_by_token not found on agent engine",
        )

    result = engine.get_job_by_token(share_token=share_token)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/get_job_by_id")
async def get_job_by_id(request: dict[str, Any]) -> dict[str, Any]:
    """Retrieve a job by its ID."""
    job_id = request.get("job_id")

    if not job_id:
        raise HTTPException(status_code=400, detail="Missing required parameter: job_id")

    engine = _get_agent_engine()
    if not hasattr(engine, "get_job_by_id"):
        raise HTTPException(
            status_code=404,
            detail="Method get_job_by_id not found on agent engine",
        )

    result = engine.get_job_by_id(job_id=job_id)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# Interview management endpoints
@app.post("/create_interview")
async def create_interview(request: dict[str, Any]) -> dict[str, Any]:
    """Create a new interview record."""
    interview_data = request.get("interview_data")

    if not interview_data:
        raise HTTPException(status_code=400, detail="Missing required parameter: interview_data")

    engine = _get_agent_engine()
    if not hasattr(engine, "create_interview"):
        raise HTTPException(
            status_code=404,
            detail="Method create_interview not found on agent engine",
        )

    result = engine.create_interview(interview_data=interview_data)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/update_interview")
async def update_interview(request: dict[str, Any]) -> dict[str, Any]:
    """Update an existing interview."""
    interview_id = request.get("interview_id")
    updates = request.get("updates")

    if not interview_id:
        raise HTTPException(status_code=400, detail="Missing required parameter: interview_id")
    if not updates:
        raise HTTPException(status_code=400, detail="Missing required parameter: updates")

    engine = _get_agent_engine()
    if not hasattr(engine, "update_interview"):
        raise HTTPException(
            status_code=404,
            detail="Method update_interview not found on agent engine",
        )

    result = engine.update_interview(interview_id=interview_id, updates=updates)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/get_user_interviews_for_jobs")
async def get_user_interviews_for_jobs(request: dict[str, Any]) -> dict[str, Any]:
    """Retrieve all interviews for jobs created by user."""
    user_id = request.get("user_id")
    limit = request.get("limit", 100)

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing required parameter: user_id")

    engine = _get_agent_engine()
    if not hasattr(engine, "get_user_interviews_for_jobs"):
        raise HTTPException(
            status_code=404,
            detail="Method get_user_interviews_for_jobs not found on agent engine",
        )

    result = engine.get_user_interviews_for_jobs(user_id=user_id, limit=limit)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/get_interview_by_id")
async def get_interview_by_id(request: dict[str, Any]) -> dict[str, Any]:
    """Retrieve a single interview by ID."""
    interview_id = request.get("interview_id")

    if not interview_id:
        raise HTTPException(status_code=400, detail="Missing required parameter: interview_id")

    engine = _get_agent_engine()
    if not hasattr(engine, "get_interview_by_id"):
        raise HTTPException(
            status_code=404,
            detail="Method get_interview_by_id not found on agent engine",
        )

    result = engine.get_interview_by_id(interview_id=interview_id)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.get("/")
async def serve_frontend_root() -> FileResponse:
    """Serve the frontend index.html at the root path."""
    index_file = frontend_build_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(
        status_code=404,
        detail="Frontend not built. Run 'npm run build' in the frontend directory.",
    )


@app.get("/{full_path:path}")
async def serve_frontend_spa(full_path: str) -> FileResponse:
    """Catch-all route to serve the frontend for SPA routing.

    This ensures that client-side routes are handled by the React app.
    Excludes API routes (ws, feedback) and static assets.
    """
    # Don't intercept API routes
    if full_path.startswith(("ws", "feedback", "static", "api")):
        raise HTTPException(status_code=404, detail="Not found")

    # Serve index.html for all other routes (SPA routing)
    index_file = frontend_build_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(
        status_code=404,
        detail="Frontend not built. Run 'npm run build' in the frontend directory.",
    )


# Main execution
if __name__ == "__main__":
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Agent Engine Proxy Server")
    parser.add_argument(
        "--mode",
        choices=["local", "remote"],
        default="local",
        help="Agent engine mode: 'local' for local agent or 'remote' for deployed agent engine",
    )
    parser.add_argument(
        "--remote-id",
        type=str,
        help="Remote agent engine ID (required when mode=remote)",
    )
    parser.add_argument(
        "--project-id", type=str, help="GCP project ID (required when mode=remote)"
    )
    parser.add_argument(
        "--location",
        type=str,
        default="us-central1",
        help="GCP location (default: us-central1)",
    )
    parser.add_argument(
        "--local-agent",
        type=str,
        default="..agent.root_agent",
        help="Python path to local agent callable (e.g., 'app.agent.root_agent')",
    )
    parser.add_argument(
        "--agent-engine-object",
        type=str,
        default="..agent_engine_app.agent_engine",
        help="Python path to agent engine object instance",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to run the server on (default: localhost)",
    )

    args = parser.parse_args()

    # Initialize configuration
    config: dict[str, Any] = {
        "use_remote_agent": False,
        "remote_agent_engine_id": None,
        "project_id": None,
        "location": "us-central1",
        "local_agent_path": args.local_agent,
        "agent_engine_object_path": args.agent_engine_object,
    }

    if args.mode == "remote":
        config["use_remote_agent"] = True

        # Try to load from deployment_metadata.json if remote-id not provided
        if not args.remote_id:
            deployment_metadata_path = (
                Path(__file__).parent.parent.parent / "deployment_metadata.json"
            )
            if deployment_metadata_path.exists():
                with open(deployment_metadata_path) as f:
                    metadata = json.load(f)
                    config["remote_agent_engine_id"] = metadata.get(
                        "remote_agent_engine_id"
                    )
                    if not config["remote_agent_engine_id"]:
                        parser.error(
                            "No remote_agent_engine_id found in deployment_metadata.json"
                        )
                    print("Loaded remote agent engine ID from deployment_metadata.json")
            else:
                parser.error(
                    "--remote-id is required when deployment_metadata.json is not found"
                )
        else:
            config["remote_agent_engine_id"] = args.remote_id

        # Extract project ID from remote agent engine ID if not provided
        if not args.project_id:
            # Format: projects/PROJECT_ID/locations/LOCATION/reasoningEngines/ENGINE_ID
            import re

            match = re.match(
                r"projects/([^/]+)/locations/([^/]+)/reasoningEngines/",
                config["remote_agent_engine_id"],
            )
            if match:
                config["project_id"] = match.group(1)
                extracted_location = match.group(2)
                config["location"] = (
                    args.location
                    if args.location != "us-central1"
                    else extracted_location
                )
                print("Extracted project ID and location from remote agent engine ID")
            else:
                # Fall back to google.auth.default()
                try:
                    _, config["project_id"] = google.auth.default()
                    config["location"] = args.location
                    print(
                        f"Using default project ID from google.auth: {config['project_id']}"
                    )
                except Exception as e:
                    parser.error(f"Could not determine project ID: {e}")
        else:
            config["project_id"] = args.project_id
            config["location"] = args.location

        print("Starting server in REMOTE mode:")
        print(f"  Remote Agent Engine ID: {config['remote_agent_engine_id']}")
        print(f"  Project ID: {config['project_id']}")
        print(f"  Location: {config['location']}")
    else:
        print("Starting server in LOCAL mode")
        print(f"  Using agent: {config['local_agent_path']}")
        print(f"  Using agent engine object: {config['agent_engine_object_path']}")

    # Store configuration in app state
    app.state.config = config

    uvicorn.run(app, host=args.host, port=args.port)
