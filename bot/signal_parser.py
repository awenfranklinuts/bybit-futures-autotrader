import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv(dotenv_path="config/.env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are a crypto futures trading assistant.\n"
    "Your task is to read WhatsApp messages from a professional trader, and identify whether the message is one of the following modes:\n"
    "1. 'open' - New futures trade signal.\n"
    "2. 'adjust' - Modify an existing position (e.g., move SL to entry).\n"
    "3. 'close' - Exit or close a position.\n"
    "4. 'commentary' - Just a market update or message with no actionable trade.\n\n"
    "If mode is 'open', extract the following fields if available: symbol, side, leverage, entry (can be range), targets (list), stop_loss, dca_point (if any), and risk_percent.\n"
    "If mode is 'adjust' or 'close', extract relevant action and symbol.\n"
    "Return a valid JSON object only."
)

def parse_signal(message: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=0.2
        )

        reply = response.choices[0].message.content.strip()
        parsed = json.loads(reply)
        return parsed

    except json.JSONDecodeError:
        print("⚠️ Failed to parse GPT response as JSON:", reply)
        return {"mode": "commentary", "note": "GPT response could not be parsed"}

    except Exception as e:
        print("❌ Error during signal parsing:", e)
        return {"mode": "commentary", "note": str(e)}
