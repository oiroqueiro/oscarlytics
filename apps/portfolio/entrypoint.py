import sys
import subprocess
import os

def main():
    print("Starting initialization process...", flush=True)
    try:
        subprocess.run([sys.executable, "/app/init_content.py"], check=True)
        subprocess.run([sys.executable, "/app/sync_projects.py"], check=True)
        print("Initialization complete.", flush=True)
    except Exception as e:
        print(f"Error during initialization: {e}", flush=True)

    print("Starting Gunicorn...", flush=True)
    # Replaces the current process with gunicorn
    os.execl(
        sys.executable, 
        "python", 
        "-m", "gunicorn", 
        "--worker-tmp-dir", "/dev/shm", 
        "--workers=2", 
        "--threads=4", 
        "--bind", "0.0.0.0:8080", 
        "portfolio:portfolio"
    )

if __name__ == "__main__":
    main()
