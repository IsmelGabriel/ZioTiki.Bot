import logging

from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from config import OPENAI_API_KEY, OPENAI_MODEL
from utils.memory_db import save_message, get_history
from utils.prompt_db import get_prompt

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_response(server_id: int, user_id: int, prompt: str) -> str:
    """Generates an AI response based on the user's history in the server."""
    # Get the prompt for the server
    system_prompt = get_prompt(server_id, "default")

    # Save user message
    save_message(server_id, user_id, "user", prompt)

    # Get history
    history = get_history(server_id, user_id)

    # Build context
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
    except RateLimitError:
        logger.warning("OpenAI rate limit reached for server=%s user=%s", server_id, user_id)
        return "⚠️ El sistema de IA está recibiendo muchas solicitudes. Intenta de nuevo en unos segundos."
    except APITimeoutError:
        logger.warning("OpenAI timeout for server=%s user=%s", server_id, user_id)
        return "⚠️ La respuesta de IA tardó demasiado. Intenta de nuevo."
    except APIError as e:
        logger.error("OpenAI API error for server=%s user=%s: %s", server_id, user_id, e)
        raise

    content = response.choices[0].message.content.strip()

    # Save bot's response
    save_message(server_id, user_id, "assistant", content)

    return content
