"""Service for managing ElevenLabs AI agents.

This implementation uses the ElevenLabs SDK v2.x for conversational AI.
Documentation: https://elevenlabs.io/docs/api-reference/conversational-ai
"""
import logging
import os
from typing import Any
from elevenlabs.client import ElevenLabs
from elevenlabs import (
    ConversationalConfig,
    AgentConfig,
    PromptAgentApiModelOutput,
    TtsConversationalConfigOutput,
)


def create_conversational_agent(
    name: str,
    first_message: str,
    system_prompt: str,
    language: str = "en"
) -> dict[str, Any]:
    """
    Creates a new ElevenLabs conversational AI agent.

    Args:
        name: Name of the agent
        first_message: The first message the agent will say
        system_prompt: The detailed instructions for the agent
        language: Language code (default: "en")

    Returns:
        Dictionary with agent_id or error
    """
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            logging.error("ELEVENLABS_API_KEY not found")
            return {"error": "Server configuration error: Missing API Key"}

        client = ElevenLabs(api_key=api_key)

        # Get default voice ID from environment or use a default
        voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel voice

        # Build the conversation configuration using SDK v2.x structure
        conversation_config = ConversationalConfig(
            agent=AgentConfig(
                first_message=first_message,
                language=language,
                prompt=PromptAgentApiModelOutput(
                    prompt=system_prompt
                )
            ),
            tts=TtsConversationalConfigOutput(
                voice_id=voice_id
            )
        )

        # Create the agent using the correct SDK v2.x method
        agent = client.conversational_ai.agents.create(
            name=name,
            conversation_config=conversation_config
        )

        # Get agent ID from response
        agent_id = agent.agent_id

        if not agent_id:
            logging.error(f"Agent created but no ID returned: {agent}")
            return {"error": "Agent created but ID not found in response"}

        logging.info(f"Created ElevenLabs agent: {agent_id}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "agent_name": name
        }

    except Exception as e:
        logging.error(f"Error creating ElevenLabs agent: {e}")
        return {"error": f"Failed to create agent: {str(e)}"}


def update_agent_prompt(agent_id: str, system_prompt: str) -> dict[str, Any]:
    """
    Updates an existing agent's system prompt.

    Args:
        agent_id: The agent's ID
        system_prompt: The new system prompt

    Returns:
        Dictionary with status or error
    """
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            logging.error("ELEVENLABS_API_KEY not found")
            return {"error": "Server configuration error: Missing API Key"}

        client = ElevenLabs(api_key=api_key)

        # Build updated configuration
        conversation_config = ConversationalConfig(
            agent=AgentConfig(
                prompt=PromptAgentApiModelOutput(
                    prompt=system_prompt
                )
            )
        )

        # Update the agent using SDK v2.x method
        client.conversational_ai.agents.update(
            agent_id=agent_id,
            conversation_config=conversation_config
        )

        logging.info(f"Updated agent {agent_id}")
        return {"status": "success"}

    except Exception as e:
        logging.error(f"Error updating agent: {e}")
        return {"error": f"Failed to update agent: {str(e)}"}


def get_signed_url_for_agent(agent_id: str) -> dict[str, Any]:
    """
    Generates a signed URL for agent authentication.

    Args:
        agent_id: The agent's ID

    Returns:
        Dictionary with signed_url or error
    """
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            logging.error("ELEVENLABS_API_KEY not found")
            return {"error": "Server configuration error: Missing API Key"}

        client = ElevenLabs(api_key=api_key)

        # Get signed URL using the correct SDK method
        response = client.conversational_ai.conversations.get_signed_url(agent_id=agent_id)

        return {"signed_url": response.signed_url}

    except Exception as e:
        logging.error(f"Error generating signed URL: {e}")
        return {"error": f"Failed to generate signed URL: {str(e)}"}


def delete_agent(agent_id: str) -> dict[str, Any]:
    """
    Deletes an ElevenLabs agent.

    Args:
        agent_id: The agent's ID

    Returns:
        Dictionary with status or error
    """
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            logging.error("ELEVENLABS_API_KEY not found")
            return {"error": "Server configuration error: Missing API Key"}

        client = ElevenLabs(api_key=api_key)

        # Delete using SDK v2.x method
        client.conversational_ai.agents.delete(agent_id=agent_id)

        logging.info(f"Deleted agent {agent_id}")
        return {"status": "success"}

    except Exception as e:
        logging.error(f"Error deleting agent: {e}")
        return {"error": f"Failed to delete agent: {str(e)}"}
