# TerminalCLI

A Python command-line chatbot that sends each prompt to a selected OpenAI, Gemini, or Ollama model.

## Features

- Select OpenAI, Gemini, or Ollama using `LLM_PROVIDER`.
- Configure a model name and system prompt through environment variables.
- Receive streamed text chunks from Gemini and Ollama.
- Send requests to an Ollama server running locally or at a configured URL.
- Ignore blank input and continue the prompt loop after displaying request errors.


## Architecture

```text
Terminal input
	 |
	 v
chatbot.py: main() -> ask_model(message)
	 |
	 +---- LLM_PROVIDER=openai --> OpenAI Responses API --> complete text
	 |
	 +---- LLM_PROVIDER=gemini --> Gemini generate_content_stream --> text chunks
	 |
	 `---- LLM_PROVIDER=ollama --> Ollama /api/chat --> JSON lines
														|
														v
										   extracted text -> terminal
```


## Streaming

For Gemini and Ollama, the provider implementation yields text chunks and the CLI prints each chunk immediately, flushing standard output. After the provider finishes, the CLI prints a blank line before the next prompt.

```text
user input
	↓
ask_model(message)
	↓
selected provider function
	↓
provider response chunks
	↓
CLI prints each chunk and flushes output

```

## Ollama Setup

### 1. What is Ollama?

Ollama runs language models locally and exposes an HTTP API. This project sends prompts to that API when `LLM_PROVIDER=ollama` is selected.

### 2. Ollama Installation

The following installation instructions are for Linux, matching the available development environment for this project. Install Ollama using its official installer:

```sh
curl -fsSL https://ollama.com/install.sh | sh
```

Verify that the command is available:

```sh
ollama --version
```

### 3. Start the Ollama Server

Start the server in a terminal:

```sh
ollama serve
```

### 4. Download the Required Ollama Model

The model configured by default in `config.py` is `qwen3:0.6b`. Download it with:

```sh
ollama pull qwen3:0.6b
```

Confirm that it is installed:

```sh
ollama list
```

If you choose another model, set `OLLAMA_MODEL` to its exact installed name. The application does not pull models automatically.

### 5. Test the Model Manually

Run the configured model:

```sh
ollama run qwen3:0.6b
```


### 6. Test the Ollama HTTP API

The implementation sends a `POST` request to `http://localhost:11434/api/chat` when using the default base URL. This request mirrors its model, system message, user message, and streaming setting:

```sh
curl http://localhost:11434/api/chat \
  -d '{
	"model": "qwen3:0.6b",
	"messages": [
	  {"role": "system", "content": "You are a helpful assistant."},
	  {"role": "user", "content": "Reply with exactly: Ollama is working."}
	],
	"stream": true
  }'
```

With streaming enabled, the response is newline-delimited JSON rather than one combined JSON document. Each response line includes message data; this project reads `message.content` from each line. The code constructs the endpoint by appending `/api/chat` to `OLLAMA_BASE_URL`, so configure the base URL as the server root (for example, `http://localhost:11434`), not with `/api` already appended.

### 7. Ollama Environment Configuration

The Ollama-related variables read by `config.py` are:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base address to which the code appends `/api/chat`. |
| `OLLAMA_MODEL` | `qwen3:0.6b` | Model name included in each chat request. It must be available to the Ollama server. |

Select the provider with `LLM_PROVIDER=ollama`. A complete `.env` example appears in [Configuration](#configuration).

### 9. Ollama Streaming

The Ollama request uses two streaming controls for different layers:

- JSON body `"stream": true` asks Ollama's `/api/chat` endpoint to return incremental response data.
- `requests.post(..., stream=True)` tells the Python HTTP client not to wait for the complete response body before exposing it.

The code then iterates `response.iter_lines(decode_unicode=True)`. Each non-empty line is decoded as JSON, and its `message.content` value is yielded to the CLI. The CLI prints each yielded text chunk immediately. The implementation does not process separate completion metadata fields.

### 10. Connecting Ollama to the CLI

Set `LLM_PROVIDER=ollama` to make `ask_model()` dispatch each prompt to `ask_ollama()`:

```text
CLI input
	↓
ask_model()
	↓
ask_ollama()
	↓
Ollama POST /api/chat
	↓
streamed JSON lines
	↓
message.content chunks
	↓
CLI output
```

## Project Structure

```text
.
├── .env.example
├── .gitignore
|
├── README.md
├── chatbot.py
├── clients.py
├── config.py
└── requirements.txt
```

- `chatbot.py`: CLI entry point, setup checks, provider selection, and interactive input/output loop.
- `clients.py`: OpenAI, Gemini, and Ollama request implementations.
- `config.py`: loads `.env` and defines provider, system prompt, credentials, and model settings.
- `requirements.txt`: Python package dependencies.
- `__pycache__/`: checked-in compiled Python cache files; they are generated artifacts, not required source files.
- `.env.example`: sample environment file. Its variable names and values are not fully aligned with the current `config.py`; use the configuration names and example below when creating `.env`.
- `.gitignore`: excludes `.env`, `venv/`, and `__pycache__/` from Git.

## Requirements

- Python is required. The repository does not declare a minimum or pinned Python version.
- Install the packages listed in `requirements.txt`
- OpenAI use requires an OpenAI API key and network access to the OpenAI API.
- Gemini use requires a Gemini API key and network access to the Gemini API.
- Ollama use requires a reachable Ollama server and the configured model to be installed on that server. The server may be local or at a URL supplied with `OLLAMA_BASE_URL`.
- Only the selected provider's credentials or service are needed to run that provider. No API key is used by this project for Ollama.

## Installation

From a terminal, clone the repository using its actual Git URL, then enter the project directory. The repository URL is not specified in the project files, so replace the placeholder with the URL from the repository page:

```sh
git clone <repository-url>
cd TerminalAI
```

Create and activate a virtual environment on Linux:

```sh
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```sh
python -m pip install -r requirements.txt
```

Create a `.env` file in the project directory using the names and syntax in [Configuration](#configuration). Add credentials only for the provider you intend to use. For Ollama, install and start Ollama, then pull `qwen3:0.6b` as described in [Ollama Setup](#ollama-setup).

Start the CLI from the project directory:

```sh
python chatbot.py
```

## Configuration

`config.py` uses `python-dotenv` to load `.env`. These are all environment variables read by the project:

| Variable | Default | Notes |
| --- | --- | --- |
| `LLM_PROVIDER` | `openai` | Provider selector: `openai`, `gemini`, or `ollama`. |
| `SYSTEM_PROMPT` | `You are a helpful assistant.` | Instructions passed to the selected provider. |
| `OPENAI_API_KEY` | Empty string | Required when `LLM_PROVIDER=openai`. Use your own key; never commit it. |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model name. |
| `GEMINI_API_KEY` | Unset | Required when `LLM_PROVIDER=gemini`. Use your own key; never commit it. |
| `GEMINI_MODEL` | `gemini-1.5-turbo` | Gemini model name. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server base URL; `/api/chat` is appended by the client. |
| `OLLAMA_MODEL` | `qwen3:0.6b` | Ollama model name. |

Example `.env` for Ollama (the model and URL shown match the current defaults):

```env
LLM_PROVIDER=ollama
SYSTEM_PROMPT="You are a helpful assistant."
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:0.6b
```

## Author

**Prakhar Sharma**  
