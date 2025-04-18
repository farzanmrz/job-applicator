import base64
import json
import logging
import os
from typing import Dict

import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get logger
logger = logging.getLogger("AuthCommon")


def haiku_valLogin(screenshot_path: str) -> Dict:
    """Validate login success/failure using Claude 3 Haiku's vision capabilities"""

    api_key = os.environ.get("KEY_ANTHROPIC")

    if not api_key:
        logger.error("Anthropic API key not found")
        return {"platform": "Error: API key not found"}

    # Read screenshot file into bytes
    with open(screenshot_path, "rb") as f:
        screenshot_bytes = f.read()

    # Base64 encode the image bytes
    encoded_image = base64.b64encode(screenshot_bytes).decode("utf-8")

    # Create Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Define the prompt
    prompt = """Analyze the attached screenshot. 
    Respond ONLY with a single-line JSON object containing the following keys:
    1. "platform": string - The name of the main website or platform shown (e.g., "LinkedIn", "Google", "GitHub"). Make your best guess at the platform name.
    2. "login_status": string - One of these exact values:
       - "init" if the page shows ONLY a clean login form with absolutely no error messages or warnings
       - "failed" if ANY of these are present:
          * Error messages about incorrect username/email
          * Error messages about wrong password
          * Red text or highlighted fields indicating errors
          * Warning icons or symbols
          * Any text mentioning "incorrect", "invalid", or "wrong"
       - "reset" if there's a password reset form or one-time link page
       - "unknown" only if you cannot determine the login state
    CRITICAL: Before returning "init", verify there are NO error messages or warnings of any kind on the login form.
    IMPORTANT: Use double quotes (") not single quotes (') in the JSON."""

    # Make API call
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=50,
        messages=[
            {
                "role": "user",
                "content": [
                    # First content item: Image
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": encoded_image,
                        },
                    },
                    # Second content item: Text
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    # Get response text
    response_text = message.content[0].text
    print(f"\nRaw response text: '{response_text}'")

    # Parse and return JSON response
    result_dict = json.loads(response_text)
    return result_dict


if __name__ == "__main__":
    # Configure logging to show on console
    logging.basicConfig(level=logging.INFO)

    # Test single image
    image_path = "tools/auth/test_scrshot.png"
    print(f"\nTesting image: {image_path}")
    print("-" * 50)
    try:
        result = haiku_valLogin(image_path)
        print(f"Result: {result}")
    except FileNotFoundError:
        print(f"Image not found: {image_path}")
