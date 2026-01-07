import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["OPENAI_API_KEY"] = "test"
os.environ["DATA_ENCRYPTION_KEY"] = "g2CDXwdc6VKAElQ5QWqFBCsmXL_dQAs3e44_Gl1oJaU="

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
