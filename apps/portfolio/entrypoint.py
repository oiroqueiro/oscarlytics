import sys
import subprocess
import os
import time
import psycopg2

def wait_for_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set, skipping wait.", flush=True)
        return
    
    print("Waiting for database to be ready...", flush=True)
    start_time = time.time()
    while time.time() - start_time < 30:
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            print("Database is ready!", flush=True)
            return
        except psycopg2.OperationalError:
            time.sleep(1)
    print("Database wait timed out, proceeding anyway.", flush=True)

def main():
    print("Starting initialization process...", flush=True)
    wait_for_db()
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
