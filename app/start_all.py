import subprocess
import os

# Get absolute path to project root
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # K-Chat_Backend

# Start FastAPI in project root
subprocess.Popen(
    ["uvicorn", "app.main:app", "--reload"],
    cwd=root_dir  # K-Chat_Backend
)

# Start Worker in app/workers
subprocess.Popen(
    ["python", "document_worker.py"],
    cwd=os.path.join(root_dir, "app", "workers")  # K-Chat_Backend\app\workers
)