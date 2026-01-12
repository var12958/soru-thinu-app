import os
import sys
import shutil
from pathlib import Path

# Configuration
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
EXTRACT_PATH = Path(__file__).resolve().parent / "dataset"

# Possible local dataset path (provided in workspace)
LOCAL_INDIAN_FOLDER = Path(__file__).resolve().parent.parent / "Indian Food Images" / "Indian Food Images"

def prepare_dataset():
    """Prepare dataset for training.

    Behavior:
    - If a food-101 tarball is present at DOWNLOAD path, it will try to extract (legacy support).
    - If a local "Indian Food Images/Indian Food Images" folder exists in the repo, copy
      all class subfolders into `ml/dataset` and keep their structure.
    """
    os.makedirs(EXTRACT_PATH, exist_ok=True)

    # If local Indian dataset exists, prefer it and copy all classes
    if LOCAL_INDIAN_FOLDER.exists() and LOCAL_INDIAN_FOLDER.is_dir():
        print(f"Found local Indian dataset at {LOCAL_INDIAN_FOLDER}. Copying classes...")

        # Copy each subdirectory (each class) into ml/dataset/<class>
        for child in sorted(LOCAL_INDIAN_FOLDER.iterdir()):
            if child.is_dir():
                dest = EXTRACT_PATH / child.name
                if dest.exists():
                    print(f"Class already present, skipping: {child.name}")
                    continue
                print(f"Copying class {child.name} -> {dest}")
                try:
                    shutil.copytree(child, dest)
                except Exception as e:
                    print(f"Failed to copy {child}: {e}")
        print(f"All classes copied to {EXTRACT_PATH}")
        return

    # Legacy: check for a compressed food-101 tarball in Downloads
    TAR_PATH = Path.home() / "Downloads" / "food-101.tar.gz"
    if TAR_PATH.exists():
        import tarfile
        print(f"Found tarball at {TAR_PATH}, extracting selective content to {EXTRACT_PATH}...")
        try:
            with tarfile.open(str(TAR_PATH), "r:gz") as tar:
                print("Scanning archive headers and extracting all images directory...")
                members = [m for m in tar.getmembers() if m.name.startswith("food-101/images/")]
                tar.extractall(path=EXTRACT_PATH, members=members)
                print(f"Extraction complete to {EXTRACT_PATH}")
                return
        except Exception as e:
            print(f"Failed to extract tarball: {e}")

    print("No dataset found. Please place the Indian Food Images folder in the repository or put food-101.tar.gz in Downloads.")


if __name__ == "__main__":
    prepare_dataset()
