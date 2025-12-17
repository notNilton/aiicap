
import os
from dotenv import load_dotenv

print(f"CWD: {os.getcwd()}")
print(f"Before load_dotenv: DATABASE_URL={os.getenv('DATABASE_URL')}")

load_dotenv()

print(f"After load_dotenv: DATABASE_URL={os.getenv('DATABASE_URL')}")
print(f"DB_USER={os.getenv('DB_USER')}")
