import os
import sys

# Ensure chatbot package is importable in Vercel runtime
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
CHATBOT_DIR = os.path.join(ROOT_DIR, "chatbot")
if CHATBOT_DIR not in sys.path:
    sys.path.insert(0, CHATBOT_DIR)

from app import app  # noqa: E402

__all__ = ["app"]

