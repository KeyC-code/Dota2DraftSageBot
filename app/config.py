import os
from dotenv import load_dotenv

load_dotenv()

MONTH_PRICE = 100
THREE_MONTH_PRICE = 250
DRAFT_ORDER = [
   ("ban", "Radiant"),
   ("ban", "Dire"),
   ("ban", "Radiant"),
   ("ban", "Dire"),
   ("ban", "Radiant"),
   ("ban", "Dire"),
   ("pick", "Radiant"),
   ("pick", "Dire"),
   ("pick", "Dire"),
   ("pick", "Radiant"),
   ("ban", "Radiant"),
   ("ban", "Dire"),
   ("ban", "Radiant"),
   ("ban", "Dire"),
   ("pick", "Radiant"),
   ("pick", "Dire"),
   ("pick", "Dire"),
   ("pick", "Radiant"),
   ("ban", "Radiant"),
   ("ban", "Dire"),
   ("ban", "Radiant"),
   ("ban", "Dire"),
   ("pick", "Dire"),
   ("pick", "Radiant"),
   ("pick", "Radiant"),
   ("pick", "Dire"),
]
MAX_STEPS = len(DRAFT_ORDER)

CURRENT_PATCH = os.getenv("CURRENT_PATCH")

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")