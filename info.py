import json
import os
from datetime import datetime

import anthropic
import google.generativeai as genai
import openai
import requests


def get_openai_models():
    """Fetch available models from OpenAI"""
    try:
        client = openai.OpenAI(api_key=os.getenv("KEY_OPENAI"))
        models = client.models.list()
        return [model.id for model in models]
    except Exception as e:
        return f"Error fetching OpenAI models: {str(e)}"


def get_anthropic_models():
    """Fetch available models from Anthropic"""
    try:
        client = anthropic.Anthropic(api_key=os.getenv("KEY_ANTHROPIC"))
        models = client.models.list(limit=20)
        return [model.id for model in models.data]
    except Exception as e:
        return f"Error fetching Anthropic models: {str(e)}"


def get_gemini_models():
    """Fetch available models from Google Gemini"""
    try:
        genai.configure(api_key=os.getenv("KEY_GEMINI"))
        models = genai.list_models()
        return [model.name for model in models]
    except Exception as e:
        return f"Error fetching Gemini models: {str(e)}"


def get_deepseek_models():
    """Fetch available models from DeepSeek"""
    try:
        headers = {
            "Authorization": f'Bearer {os.getenv("KEY_DEEPSEEK")}',
            "Content-Type": "application/json",
        }
        response = requests.get("https://api.deepseek.com/v1/models", headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            # Extract just the model IDs from the data array
            if "data" in response_json and isinstance(response_json["data"], list):
                return [model["id"] for model in response_json["data"]]
            return f"Error: Unexpected response format"
        return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error fetching DeepSeek models: {str(e)}"


def main():
    """Main function to fetch and display all available models"""
    print(
        f"\nFetching available AI models as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    # OpenAI
    print("\nOpenAI Models:")
    print("-" * 50)
    openai_models = get_openai_models()
    if isinstance(openai_models, list):
        for model in sorted(openai_models):
            print(f"• {model}")
    else:
        print(openai_models)

    # Anthropic
    print("\nAnthropic Models:")
    print("-" * 50)
    anthropic_models = get_anthropic_models()
    if isinstance(anthropic_models, list):
        for model in anthropic_models:
            print(f"• {model}")
    else:
        print(anthropic_models)

    # Gemini
    print("\nGoogle Gemini Models:")
    print("-" * 50)
    gemini_models = get_gemini_models()
    if isinstance(gemini_models, list):
        for model in gemini_models:
            print(f"• {model}")
    else:
        print(gemini_models)

    # DeepSeek
    print("\nDeepSeek Models:")
    print("-" * 50)
    deepseek_models = get_deepseek_models()
    if isinstance(deepseek_models, list):
        for model in deepseek_models:
            print(f"• {model}")
    else:
        print(deepseek_models)


if __name__ == "__main__":
    main()
