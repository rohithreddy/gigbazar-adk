# ruff: noqa
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

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.models import Gemini
from google.genai import types

import os
import google.auth
import vertexai

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

vertexai.init(project=project_id, location="us-central1")


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-live-2.5-flash-native-audio",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are an expert Technical Interviewer and Career Coach.
    Your goal is to help the user prepare for their upcoming interviews.
    
    You can:
    1. Conduct mock interviews for Software Engineering roles.
    2. Review answers and provide constructive feedback.
    3. Help with behavioral questions (STAR method).
    
    Always be professional, encouraging, but rigorous.
    If the user asks to start an interview, ask them what topic they want to focus on (e.g., System Design, Coding, Behavioral).
    """,
    tools=[],  # Start with no tools, purely conversational for now, or add specific interview tools later
)

app = App(root_agent=root_agent, name="app")
