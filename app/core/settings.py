from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()



# -----------------------------------
# MODELS
# -----------------------------------

CHAT_MODEL_NAME = os.getenv(
    "CHAT_MODEL_NAME",
    "gemini-2.5-flash"
)


