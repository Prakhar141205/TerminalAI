import config
from clients import ask_openai, ask_gemini, ask_ollama



def model_name():
    """Return the name of the model based on the provider."""
    if config.PROVIDER == "openai":
        return config.OPENAI_MODEL
    elif config.PROVIDER == "gemini":
        return config.GEMINI_MODEL
    elif config.PROVIDER == "ollama":
        return config.OLLAMA_MODEL
    else:
        raise ValueError(f"Unknown provider: {config.PROVIDER}")


def check_setup():
    """Return a message if something is missing in .env or if the provider is unknown."""

    if config.PROVIDER not in ('openai', 'gemini', 'ollama'):
        return f"Unknown provider: {config.PROVIDER}. Please set PROVIDER in .env to one of: openai, gemini, ollama."

    if config.PROVIDER == "openai" and not config.OPENAI_API_KEY:
        return "Missing OPENAI_API_KEY in .env. Please set it to your OpenAI API key."

    if config.PROVIDER == "gemini" and not config.GEMINI_API_KEY:
        return "Missing GEMINI_API_KEY in .env. Please set it to your Gemini API key."
    if config.PROVIDER == "ollama" and not config.OLLAMA_BASE_URL:
        return "Missing OLLAMA_BASE_URL in .env. Please set it to your Ollama server URL."

    if not model_name():
        return f"Missing model name for provider {config.PROVIDER}. Please set the appropriate model in .env."


def ask_model(message):
    """Send a message to the selected provider and return the response."""
    if config.PROVIDER == "openai":
        return ask_openai(message)
    elif config.PROVIDER == "gemini":
        return ask_gemini(message)
    elif config.PROVIDER == "ollama":
        return ask_ollama(message)
    else:
        raise ValueError(f"Unknown provider: {config.PROVIDER}")


def main():
    """Main function to run the CLI chatbot."""

    setup_message = check_setup()

    if setup_message:
        print(f"\n{setup_message}\n")
        return

    print()
    print("╭──────────────────────────────────────╮")
    print("│              GenCLI                  │")
    print("│       Command-Line AI Chatbot        │")
    print("╰──────────────────────────────────────╯")
    print()
    print(f"  Provider : {config.PROVIDER}")
    print(f"  Model    : {model_name()}")
    print("  Type 'exit' to quit.")
    print()

    while True:
        try:
            user_input = input("You  › ")

            if user_input.lower().strip() == "exit":
                print("\nGoodbye! 👋\n")
                break

            if not user_input.strip():
                continue

            print("AI  › ", end="", flush=True)

            for chunk in ask_model(user_input):
                print(chunk, end="", flush=True)

            print()
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break

        except Exception as e:
            print(f"\n\nError: {e}\n")

if __name__ == "__main__":
    main()