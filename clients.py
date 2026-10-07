import config
import requests
import json
from google import genai
from openai import OpenAI


from google.genai import types # types to disable the warning for automatic function calling in Gemini API

def ask_openai(message):
    "Send a message to the OpenAI API and return the response in the text format."
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.responses.create(
        model=config.OPENAI_MODEL,
        instructions=config.SYSTEM_PROMPT,
        input = message
    )
    return  response.output_text



def ask_ollama(message):
    """Send a message to Ollama and stream text chunks."""

    try:
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": config.SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                "stream": True,
            },
            stream=True,
        )

        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if line:
                data = json.loads(line)
                yield data["message"]["content"]

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error connecting to Ollama API: {e}")


def ask_gemini(message):
    """Send a message to Gemini and stream the response."""

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    response = client.models.generate_content_stream(
        model=config.GEMINI_MODEL,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=config.SYSTEM_PROMPT,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text