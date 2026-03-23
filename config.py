import os
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration (optional)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

# WhatsApp configuration
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "5511999999999")  # Include country code without '+'