from sqlalchemy.orm import Session
from database import SessionLocal, engine
from database import FileMetadata, Finding

db = SessionLocal()
files = db.query(FileMetadata).all()
print("Total Files:", len(files))
deleted_files = [f for f in files if getattr(f, "file_path", "").startswith("[DELETED]")]
print("Deleted Files count:", len(deleted_files))
if deleted_files:
    print("Example deleted:", deleted_files[-1].file_path)

findings = db.query(Finding).filter(Finding.status == "deleted").all()
print("Deleted findings count:", len(findings))
