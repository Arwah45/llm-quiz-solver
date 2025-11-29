import os
from dotenv import load_dotenv

load_dotenv()

STUDENT_EMAIL = os.getenv("STUDENT_EMAIL")
STUDENT_SECRET = os.getenv("STUDENT_SECRET")
BASE_SYSTEM_PROMPT = os.getenv("BASE_SYSTEM_PROMPT", "")
BASE_USER_PROMPT = os.getenv("BASE_USER_PROMPT", "")
