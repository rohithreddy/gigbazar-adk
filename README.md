# my-agent

Real-time multimodal agent with ADK and Gemini Live API for low-latency voice and video interaction.
Agent generated with [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) version `0.29.3`

## Project Structure

This project is organized as follows:

```
my-agent/
├── app/                 # Core application code
│   ├── agent.py         # Main agent logic
│   ├── agent_engine_app.py # Agent Engine application logic
│   └── app_utils/       # App utilities and helpers
├── tests/               # Unit, integration, and load tests
├── Makefile             # Makefile for common commands
├── GEMINI.md            # AI-assisted development guide
└── pyproject.toml       # Project dependencies and configuration
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)


## Quick Start (Local Testing)

Install required packages and launch the local development environment:

```bash
make install && make playground
```
> **📊 Observability Note:** Agent telemetry (Cloud Trace) is always enabled. Prompt-response logging (GCS, BigQuery, Cloud Logging) is **disabled** locally, **enabled by default** in deployed environments (metadata only - no prompts/responses). See [Monitoring and Observability](#monitoring-and-observability) for details.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch local development environment for testing agent |
| `make deploy`        | Deploy agent to Agent Engine |
| `make local-backend` | Launch local development server with hot-reload |
| `make ui`            | Start the frontend UI separately for development (requires backend running separately) |
| `make playground-dev` | Launch dev playground with both frontend and backend hot-reload |
| `make playground-remote` | Connect to remote deployed agent with local frontend |
| `make build-frontend` | Build the frontend for production |
| `make register-gemini-enterprise` | Register deployed agent to Gemini Enterprise ([docs](https://googlecloudplatform.github.io/agent-starter-pack/cli/register_gemini_enterprise.html)) |
| `make test`          | Run unit and integration tests                                                              |
| `make lint`          | Run code quality checks (codespell, ruff, mypy)                                             |

For full command options and usage, refer to the [Makefile](Makefile).


## Usage

This template follows a "bring your own agent" approach - you focus on your business logic in `app/agent.py`, and the template handles the surrounding components (UI, infrastructure, deployment, monitoring).

Here’s the recommended workflow for local development:

1.  **Install Dependencies (if needed):**
    ```bash
    make install
    ```

2.  **Start the Full Stack Server:**
    The FastAPI server now serves both the backend API and frontend interface:
    ```bash
    make local-backend
    ```
    The server is ready when you see `INFO:     Application startup complete.` The frontend will be available at `http://localhost:8000`.

    <details>
    <summary><b>Optional: Use AI Studio / API Key instead of Vertex AI</b></summary>

    By default, the backend uses Vertex AI and Application Default Credentials. If you prefer to use Google AI Studio and an API key:

    ```bash
    export VERTEXAI=false
    export GOOGLE_API_KEY="your-google-api-key" # Replace with your actual key
    make local-backend
    ```
    Ensure `GOOGLE_API_KEY` is set correctly in your environment.
    </details>
    <br>

    <details>
    <summary><b>Alternative: Run Frontend Separately</b></summary>

    If you prefer to run the frontend separately (useful for frontend development), you can still use:
    ```bash
    make ui
    ```
    This launches the frontend application, which connects to the backend server at `http://localhost:8000`.
    </details>
    <br>

3.  **Interact and Iterate:**
    *   Open your browser and navigate to `http://localhost:8000` to access the integrated frontend.
    *   Click the play button in the UI to connect to the backend.
    *   Interact with the agent! Try prompts like: *"Using the tool you have, define Governance in the context MLOPs"*
    *   Modify the agent logic in `app/agent.py`. The backend server (FastAPI with `uvicorn --reload`) should automatically restart when you save changes. Refresh the frontend if needed to see behavioral changes.


</details>

## Deployment

You can deploy your agent to a Dev Environment using the following command:

```bash
gcloud config set project <your-dev-project-id>
make deploy
```

**Note:** For secure access to your deployed backend, consider using Identity-Aware Proxy (IAP) by running `make deploy IAP=true`.

When ready for production deployment with CI/CD pipelines and Terraform infrastructure, run `uvx agent-starter-pack enhance` to add these capabilities.

## Monitoring and Observability

The application provides two levels of observability:

**1. Agent Telemetry Events (Always Enabled)**
- OpenTelemetry traces and spans exported to **Cloud Trace**
- Tracks agent execution, latency, and system metrics

**2. Prompt-Response Logging (Configurable)**
- GenAI instrumentation captures LLM interactions (tokens, model, timing)
- Exported to **Google Cloud Storage** (JSONL), **BigQuery** (external tables), and **Cloud Logging** (dedicated bucket)

| Environment | Prompt-Response Logging |
|-------------|-------------------------|
| **Local Development** (`make playground`) | ❌ Disabled by default |

**To enable locally:** Set `LOGS_BUCKET_NAME` and `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`.

See the [observability guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability.html) for detailed instructions, example queries, and visualization options.
