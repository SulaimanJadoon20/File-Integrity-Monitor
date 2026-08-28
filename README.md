# File-Integrity-Monitor
A Python file integrity monitoring tool that detects file activity and changes using SHA-256 hashes, Watchdog, and SQLite.

# File Integrity & Activity Monitor

A Python-based file integrity monitoring tool that tracks activity within a targeted directory or file.

The program uses **SHA-256 hashing** to create file fingerprints, **Watchdog** to monitor filesystem events, and **SQLite** to store activity records and previous hashes.

## Features

* Monitor a specific file or directory.
* Recursively scan existing files in a targeted directory.
* Generate SHA-256 hashes for files.
* Store file activity and hashes in a SQLite database.
* Detect newly created files.
* Detect modified files.
* Detect moved files.
* Detect deleted files.
* Compare a modified file's current hash with its previous hash.
* Display activity and errors through the Rich console.
* Handle inaccessible files and database errors without immediately terminating the program.

## How It Works

The program follows a simple monitoring workflow:

```text
Target File/Directory
        │
        ▼
 Scan Existing Files
        │
        ▼
 Generate SHA-256 Hash
        │
        ▼
 Store Initial Record
        │
        ▼
 Start Watchdog Monitor
        │
        ├── File Created
        │
        ├── File Modified ──► Hash Comparison
        │
        ├── File Moved
        │
        └── File Deleted
        │
        ▼
 Store Activity in SQLite
```

### 1. Select the Target

The program asks for the path of the file or directory that should be monitored.

If a directory is selected, its files are scanned recursively using `os.walk()`.

### 2. Generate File Hashes

Files are opened in binary mode and processed in chunks before being hashed with SHA-256.

This allows the program to create a fingerprint representing the current contents of a file.

### 3. Store Records

The program creates a SQLite database containing a `file_recs` table with information such as:

* File address
* Activity
* Status
* SHA-256 hash

### 4. Monitor Filesystem Events

After the initial scan, `Watchdog` continuously monitors the selected directory.

The program handles four main events:

* **CREATED** — a new file appears.
* **MODIFIED** — an existing file changes.
* **MOVED** — a file is moved to another location.
* **DELETED** — a file is removed.

### 5. Detect Changes

When a file is modified, the program calculates its new SHA-256 hash and compares it with the most recent hash stored in the database.

If the hashes match:

```text
CONTEXT NOT CHANGED.
```

If the hashes differ:

```text
CONTEXT CHANGED.
```

This provides a basic method of detecting changes to file contents.

## Technologies Used

* **Python**
* **Watchdog** — filesystem event monitoring
* **SQLite** — local activity storage
* **Hashlib / SHA-256** — file integrity verification
* **OS module** — filesystem operations
* **Rich** — formatted terminal output

## Installation

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_DIRECTORY>
```

Install the required Python packages:

```bash
pip install watchdog rich
```

Then run the program:

```bash
python3 my_new_file_analyer.py
```

## Usage

When the program starts, it asks for:

1. The file or directory you want to monitor.
2. The directory where the SQLite database should be created.

For example:

```text
PLEASE ENTER THE TARGATED DIRECTORY/FILE PATH:
PLEASE ENTER THE DIRECTORY ADDRESS YOU WANT DATABASE IN:
```

After the initial scan, the program starts monitoring the selected directory.

You can stop the monitor with:

```text
Ctrl + C
```

## Database

The program creates a SQLite database named:

```text
my_db
```

The main table is:

```text
file_recs
```

The table stores:

```text
id
ADDRESS
ACTIVITY
STATUS
HASH
```

Each filesystem event can therefore be recorded as a separate entry.

## Example Activity

A modification may produce output similar to:

```text
/path/to/file.txt --> MODIFIED.
<sha256 hash>
CONTEXT CHANGED.
RECORDS ADDED IN DB SUCCESSFULLY.
```

A deletion is recorded with:

```text
/path/to/file.txt ---> DELETED.
```

and the status:

```text
GONE
```

## Project Purpose

This project was built as a practical Python and cybersecurity project to explore:

* File integrity monitoring
* Hash-based change detection
* Filesystem event monitoring
* SQLite databases
* Python exception handling
* Operating-system file operations
* Event-driven programming

The project is intentionally built from relatively simple components to understand how a basic file integrity monitoring system works internally.

## Limitations

This is an educational project and is **not intended to be a production-grade security monitoring system**.

Some areas that could be improved include:

* Database connection and path management
* More robust handling of filesystem race conditions
* Better logging architecture
* Configuration instead of hard-coded values
* Improved database schema and indexing
* Handling large numbers of filesystem events
* More detailed event metadata
* Better reporting and querying of historical activity
* Automated testing

## Future Improvements

Possible future development:

* Add a command-line interface with `argparse`.
* Add configurable hash algorithms.
* Add timestamps to every database record.
* Add a database query/reporting mode.
* Improve handling of moved files.
* Add file size and metadata tracking.
* Add configuration files.
* Add unit and integration tests.
* Improve performance for large directories.
* Add alerting when suspicious file changes are detected.
