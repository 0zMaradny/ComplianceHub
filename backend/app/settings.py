import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Antigravity (Tier 0)
ANTIGRAVITY_CLIENT_ID: str = os.environ.get('ANTIGRAVITY_CLIENT_ID', '')
ANTIGRAVITY_CLIENT_SECRET: str = os.environ.get('ANTIGRAVITY_CLIENT_SECRET', '')
ANTIGRAVITY_REFRESH: str = os.environ.get('ANTIGRAVITY_REFRESH', '')

# OpenRouter (Tier 1+2)
OPENROUTER_API_KEY: str = os.environ.get('OPENROUTER_API_KEY', '')

# Groq (Tier 3)
GROQ_API_KEY: str = os.environ.get('GROQ_API_KEY', '')

# AI Router
AI_PROVIDER: str = os.environ.get('AI_PROVIDER', 'openrouter')
AI_DEGRADE_THRESHOLD: int = int(os.environ.get('AI_DEGRADE_THRESHOLD', '3'))
AI_CACHE_TTL: int = int(os.environ.get('AI_CACHE_TTL', '3600'))
AI_BATCH_SIZE: int = int(os.environ.get('AI_BATCH_SIZE', '2'))
AI_PEAK_START: int = int(os.environ.get('AI_PEAK_START', '12'))
AI_PEAK_END: int = int(os.environ.get('AI_PEAK_END', '18'))
AI_QUALITY_THRESHOLD: float = float(os.environ.get('AI_QUALITY_THRESHOLD', '6.0'))
AI_QUALITY_MAX_RETRIES: int = int(os.environ.get('AI_QUALITY_MAX_RETRIES', '1'))

# Local AI
LOCAL_AI_BASE: str = os.environ.get('LOCAL_AI_BASE', 'http://localhost:8080')
LOCAL_AI_TIMEOUT: int = int(os.environ.get('LOCAL_AI_TIMEOUT', '120'))
LOCAL_AI_MAX_RETRIES: int = int(os.environ.get('LOCAL_AI_MAX_RETRIES', '2'))

# General
DATABASE_URL: str = os.environ.get('DATABASE_URL', '')
CORS_ORIGINS: str = os.environ.get('CORS_ORIGINS', '*')
FRONTEND_STATIC_DIR: str = os.environ.get('FRONTEND_STATIC_DIR', '')
TUNNEL_MODE: str = os.environ.get('TUNNEL_MODE', 'auto')
