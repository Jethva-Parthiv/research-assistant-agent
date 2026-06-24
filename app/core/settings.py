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

MD_FILE_STORE_LOCATION = os.getenv(
    "DOCUMENT_STORE_PATH",
    "data"
)

