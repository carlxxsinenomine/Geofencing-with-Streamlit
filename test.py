# diagnose_database.py
import os
import sys
from pathlib import Path


def find_chroma_databases():
    """Find all ChromaDB databases in the project"""
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}")

    chroma_dbs = []

    # Search for chroma_db directories
    for path in project_root.rglob("chroma_db"):
        if path.is_dir():
            # Check if it has ChromaDB files
            db_files = list(path.glob("*.parquet")) + list(path.glob("chroma.sqlite3"))
            if db_files:
                chroma_dbs.append({
                    'path': path,
                    'files': len(db_files),
                    'size_mb': sum(f.stat().st_size for f in path.rglob('*') if f.is_file()) / (1024 * 1024)
                })

    return chroma_dbs


def check_data_ingestion_output():
    """Check what the data ingestion script actually produces"""
    project_root = Path(__file__).parent

    # Expected locations
    expected_db = project_root / "chroma_db"
    data_dir = project_root / "data"

    print("=== DATABASE DIAGNOSIS ===")
    print(f"Expected DB path: {expected_db}")
    print(f"DB exists: {expected_db.exists()}")

    if expected_db.exists():
        files = list(expected_db.rglob("*"))
        print(f"Files in DB: {len(files)}")
        for file in files:
            print(f"  - {file.relative_to(project_root)} ({file.stat().st_size} bytes)")

    print(f"\nData directory: {data_dir}")
    print(f"Data exists: {data_dir.exists()}")
    if data_dir.exists():
        pdf_files = list(data_dir.glob("*.pdf"))
        print(f"PDF files: {len(pdf_files)}")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")

    # Find all ChromaDB databases
    print(f"\n=== SEARCHING FOR ALL CHROMA DATABASES ===")
    all_dbs = find_chroma_databases()
    if all_dbs:
        for db in all_dbs:
            print(f"Found DB: {db['path']}")
            print(f"  Files: {db['files']}, Size: {db['size_mb']:.2f} MB")
    else:
        print("No ChromaDB databases found!")


if __name__ == "__main__":
    check_data_ingestion_output()