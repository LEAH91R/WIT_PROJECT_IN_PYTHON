import os
import shutil
import uuid
import json
import filecmp
from datetime import datetime
from interface import IVersionControl

WIT_DIR = ".wit"
STAGING_DIR = os.path.join(WIT_DIR, "staging")
COMMITS_DIR = os.path.join(WIT_DIR, "commits")
METADATA_FILE = os.path.join(WIT_DIR, "metadata.json")


class WitManager(IVersionControl):
    def __init__(self):
        self.is_initialized = os.path.exists(WIT_DIR)

    def _get_ignored(self):
        protected_files = {
            WIT_DIR, ".wit","__pycache__", ".witignore", ".venv", "venv", "wit.py", "manager.py", "interface.py"
        }
        if os.path.exists(".witignore"):
            with open(".witignore", "r") as f:
                protected_files.update(line.strip() for line in f if line.strip())
        return protected_files

    def _are_dirs_identical(self, dir1, dir2):
        if not os.path.exists(dir1) or not os.path.exists(dir2): return False
        comparison = filecmp.dircmp(dir1, dir2)
        if comparison.left_only or comparison.right_only or comparison.diff_files:
            return False
        for sub_dir in comparison.common_dirs:
            if not self._are_dirs_identical(os.path.join(dir1, sub_dir), os.path.join(dir2, sub_dir)):
                return False
        return True

    def init(self):
        if not self.is_initialized:
            os.makedirs(STAGING_DIR)
            os.makedirs(COMMITS_DIR)
            with open(METADATA_FILE, "w") as f:
                json.dump({"last_commit": None, "history": []}, f)
            print("Initialized empty WIT repository.")
        else:
            print("Repository already exists.")

    def add(self, path):
        if path in self._get_ignored():
            print(f"Path {path} is protected or ignored.")
            return
        if os.path.exists(path):
            if os.path.isfile(path):
                shutil.copy2(path, STAGING_DIR)
            else:
                dest = os.path.join(STAGING_DIR, os.path.basename(path))
                if os.path.exists(dest): shutil.rmtree(dest)
                shutil.copytree(path, dest)
            print(f"Added {path} to staging.")

    def commit(self, message):
        if not os.listdir(STAGING_DIR):
            print("Nothing to commit (staging is empty).")
            return

        with open(METADATA_FILE, "r") as f:
            data = json.load(f)

        last_commit_id = data.get("last_commit")
        if last_commit_id:
            last_commit_path = os.path.join(COMMITS_DIR, last_commit_id)
            if self._are_dirs_identical(STAGING_DIR, last_commit_path):
                print("No changes detected since the last commit. Commit aborted.")
                return

        commit_id = str(uuid.uuid4())[:8]
        new_commit_path = os.path.join(COMMITS_DIR, commit_id)
        shutil.copytree(STAGING_DIR, new_commit_path)

        data["history"].append({"id": commit_id, "message": message, "timestamp": str(datetime.now())})
        data["last_commit"] = commit_id
        with open(METADATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Commit {commit_id} created.")

    def status(self):
        staged = os.listdir(STAGING_DIR)
        ignored = self._get_ignored()
        working = [f for f in os.listdir('.') if f not in ignored]
        untracked = [f for f in working if f not in staged]
        print(f"Staged files: {staged}")
        print(f"Untracked files: {untracked}")

    def checkout(self, commit_id):
        source = os.path.join(COMMITS_DIR, commit_id)
        if not os.path.exists(source):
            print(f"Error: Commit {commit_id} not found.")
            return

        ignored = self._get_ignored()


        for f in os.listdir('.'):
            if f not in ignored:
                try:
                    if os.path.isfile(f):
                        os.remove(f)
                    elif os.path.isdir(f):
                        shutil.rmtree(f)
                except Exception as e:
                    print(f"Could not delete {f}: {e}")


        for item in os.listdir(source):
            src_item = os.path.join(source, item)
            if os.path.isfile(src_item):
                shutil.copy2(src_item, '.')
            else:
                shutil.copytree(src_item, item)

        print(f"Successfully switched to commit {commit_id}")