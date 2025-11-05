import subprocess
import os
import sys
from dotenv import load_dotenv
import shutil

def deploy_package():
    print("🚀 Loading .env file...")
    load_dotenv()
    
    pypi_token = os.getenv("PYPI_TOKEN")

    if not pypi_token:
        print("❌ ERROR: PYPI_TOKEN environment variable not found in the .env file.")
        print("Please check the contents of your .env file.")
        return

    print("🧹 Cleaning up previous 'dist' folder and '__pycache__' files...")
    for folder in ["dist", "build"]:
        shutil.rmtree(folder, ignore_errors=True)
    for egg in [f for f in os.listdir(".") if f.endswith(".egg-info")]:
        shutil.rmtree(egg, ignore_errors=True)

    python_exe = sys.executable  
    print(f"🐍 Using Python executable: {python_exe}")

    print("📦 Building distribution packages (python -m build)...")
    try:
        subprocess.run([python_exe, "-m", "build"], check=True)
        print("✅ Packages successfully built.")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Package build failed. Error: {e}")
        return

    print("📤 Uploading to PyPI (python -m twine upload dist/*)...")
    try:
        env = os.environ.copy()
        env["TWINE_USERNAME"] = "__token__"
        env["TWINE_PASSWORD"] = pypi_token

        subprocess.run(
            [python_exe, "-m", "twine", "upload", "dist/*"],
            env=env,
            check=True
        )
        print("🎉 Upload completed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Twine upload failed. Error: {e}")
    except FileNotFoundError:
        print("❌ ERROR: 'twine' module not found. Please install it with 'pip install twine'.")


if __name__ == "__main__":
    deploy_package()
