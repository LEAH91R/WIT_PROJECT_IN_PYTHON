# 🛠️ WIT: The Smart Versioning Engine

WIT is a lightweight, Python-based Version Control System (VCS). It is designed to help users track file modifications, capture project snapshots, and navigate through the project's history with simple commands.

---

## 🚀 Quick Navigation: Command Reference

Below is a summary of how to interact with the WIT system:

| Action | Command Syntax | Purpose |
| :--- | :--- | :--- |
| **Start** | `python wit.py init` | Creates a new repository in your current directory. |
| **Track** | `python wit.py add <path>` | Moves files to the Staging area for the next save. |
| **Exclude** | `python wit.py ignore <file>` | Tells WIT to skip specific files or folders. |
| **Save** | `python wit.py commit -m "msg"` | Records a permanent snapshot of staged files. |
| **Inspect** | `python wit.py status` | Displays differences between current files and the last save. |
| **Restore** | `python wit.py checkout <id>` | Switches the project back to a previous commit state. |
| **History** | `python wit.py log` | Lists all past commits and their unique IDs. |

---

## 💎 Core Highlights

* **Snapshot Recovery:** Save and restore the entire project state instantly.
* **Custom Filtering:** Use `.witignore` to keep your repository clean from unwanted files.
* **Visual Updates:** Clear status reports showing what has changed.
* **Safe Execution:** Core system files are protected during restore operations.

---

## 📂 Internal Architecture

WIT organizes your data within the hidden `.wit` directory:

1.  **Staging Zone:** A temporary storage area for files marked for saving.
2.  **Commit Archive:** A library where every version is stored under its unique ID.
3.  **Reference Point:** The `references.txt` file tracks the current active version (HEAD).

---

## 📝 Walkthrough Example

Ready to try it? Follow this workflow to manage your first file:

### Step 1: Initialize
```bash
python wit.py init

