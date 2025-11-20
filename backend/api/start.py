"""
Start the Ether Clinic API server.

This script starts the FastAPI server on port 8000.
Make sure you've installed dependencies first: pip install -r requirements.txt
"""
import subprocess
import sys

def main():
    print("=" * 60)
    print("🚀 Starting Ether Clinic API Server")
    print("=" * 60)
    print()
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("🔌 API Endpoints: http://localhost:8000")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    # Run uvicorn
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

if __name__ == "__main__":
    main()
