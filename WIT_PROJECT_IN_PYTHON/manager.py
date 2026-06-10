import os
import shutil
import uuid
import json
import filecmp
import requests
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
            WIT_DIR, ".wit", "__pycache__", ".witignore", ".venv", "venv", "wit.py", "manager.py", "interface.py",
            "server"
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

    def _get_current_commit_id(self) -> str:
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "r") as f:
                data = json.load(f)
                last_commit = data.get("last_commit")
                if last_commit:
                    return last_commit
        return "manual_run"

    def discover_python_files(self, target_dir: str = ".") -> list:
        py_files = []
        ignored = self._get_ignored()

        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in ignored]
            for file in files:
                if file.endswith(".py") and file not in ignored:
                    py_files.append(os.path.join(root, file))
        return py_files

    def push(self):
        server_url = "http://127.0.0.1:8000/analyze"
        commit_id = self._get_current_commit_id()

        print(f"[*] Dispatching CI Pipeline deployment for Commit ID: {commit_id}")

        file_paths = self.discover_python_files()
        if not file_paths:
            print("[!] Analysis aborted: No active Python files detected in workspace.")
            return

        print(f"[*] Packaging {len(file_paths)} project files for transmission...")

        opened_files = []
        multipart_files = []

        try:
            for path in file_paths:
                f = open(path, "rb")
                opened_files.append(f)
                multipart_files.append(("files", (os.path.basename(path), f)))

            data_payload = {"commit_id": commit_id}

            print("[*] Streaming repository files to CodeGuard compilation engine...")
            response = requests.post(server_url, data=data_payload, files=multipart_files)

            if response.status_code == 200:
                result = response.json()
                print("\n" + "=" * 40)
                print("🚀 WIT PUSH & CI COUPLING SUCCESSFUL")
                print("=" * 40)
                print(f"Remote Reference : {result['commit_id']}")
                print(f"Files Processed  : {result['summary']['total_files']}")
                print(f"Analysis Alerts  : {result['summary']['total_alerts']}")
                print("-" * 40)
                print("[*] Operational charts successfully rendered on remote server.")
                print("=" * 40 + "\n")
            else:
                print(f"\n[X] Pipeline Interrupted (Status {response.status_code}): {response.text}")

        except requests.exceptions.ConnectionError:
            print("\n[X] Linkage Fault: CodeGuard verification server is offline.")
            print("[*] Please boot up the analysis engine (uvicorn server.main:app).")
        finally:
            for f in opened_files:
                f.close()