from typing import Optional, Dict
import os
import uuid
import shutil
from datetime import datetime, timedelta
from fastapi import UploadFile
import aiofiles
from pathlib import Path

class FileStorageError(Exception):
    """Custom exception for file storage operations"""
    pass

# In db_manager.py > save_temp_file()
async def save_temp_file(file: UploadFile) -> str:
    try:
        os.makedirs("temp", exist_ok=True)
        file_id = str(uuid.uuid4())
        temp_path = Path("temp") / f"{file_id}.pdf"
        
        # Validate PDF content
        content = await file.read()
        if not content.startswith(b'%PDF'):
            raise ValueError("Invalid PDF content")
            
        # Write with proper validation
        async with aiofiles.open(temp_path, 'wb') as out_file:
            await out_file.write(content)
            
        return file_id
    except Exception as e:
        raise FileStorageError(f"File validation failed: {str(e)}")

# async def save_temp_file(file: UploadFile) -> str:
#     """
#     Save an uploaded resume file to temporary storage
    
#     Args:
#         file (UploadFile): The uploaded PDF file
    
#     Returns:
#         str: Unique identifier for the saved file
    
#     Raises:
#         FileStorageError: If file saving fails
#     """
#     try:
#         # Ensure temp directory exists
#         os.makedirs("temp", exist_ok=True)
        
#         # Generate unique file ID
#         file_id = str(uuid.uuid4())
#         temp_path = Path("temp") / f"{file_id}.pdf"
        
#         # Save file asynchronously
#         async with aiofiles.open(temp_path, 'wb') as out_file:
#             content = await file.read()
#             await out_file.write(content)
        
#         return file_id
        
#     except Exception as e:
#         raise FileStorageError(f"Failed to save file: {str(e)}")

def get_temp_file(file_id: str) -> str:
    """
    Get the path to a temporary file
    
    Args:
        file_id (str): Unique identifier for the file
    
    Returns:
        str: Full path to the temporary file
    
    Raises:
        FileStorageError: If file is not found
    """
    file_path = Path("temp") / f"{file_id}.pdf"
    if not file_path.exists():
        raise FileStorageError(f"File not found: {file_id}")
    return str(file_path)

def get_temp_text_file(file_id: str) -> str:
    """
    Get the path to a temporary text file containing extracted resume content
    
    Args:
        file_id (str): Unique identifier for the file
    
    Returns:
        str: Full path to the temporary text file
    
    Raises:
        FileStorageError: If file is not found
    """
    file_path = Path("temp") / f"{file_id}.txt"
    if not file_path.exists():
        raise FileStorageError(f"Extracted text file not found: {file_id}")
    return str(file_path)

def cleanup_temp_files() -> None:
    """
    Remove temporary files older than 24 hours
    """
    try:
        temp_dir = Path("temp")
        if not temp_dir.exists():
            return
            
        current_time = datetime.now()
        retention_period = timedelta(hours=24)
        
        for file_path in temp_dir.glob("*.*"):
            file_time = datetime.fromtimestamp(file_path.stat().st_ctime)
            if current_time - file_time > retention_period:
                file_path.unlink()
                
    except Exception as e:
        # Log error but don't raise - cleanup failures shouldn't stop the application
        print(f"Error during cleanup: {str(e)}")

def get_storage_info() -> Dict:
    """
    Get information about temporary storage usage
    
    Returns:
        Dict containing storage statistics
    """
    try:
        temp_dir = Path("temp")
        if not temp_dir.exists():
            return {
                "total_files": 0,
                "total_size_mb": 0,
                "pdf_files": 0,
                "text_files": 0
            }
        
        pdf_count = len(list(temp_dir.glob("*.pdf")))
        txt_count = len(list(temp_dir.glob("*.txt")))
        total_size = sum(f.stat().st_size for f in temp_dir.glob("*.*"))
        
        return {
            "total_files": pdf_count + txt_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "pdf_files": pdf_count,
            "text_files": txt_count
        }
        
    except Exception as e:
        return {"error": str(e)}

def remove_processed_files(file_id: str) -> None:
    """
    Remove all temporary files associated with a processed resume
    
    Args:
        file_id (str): Unique identifier for the files to remove
    """
    try:
        temp_dir = Path("temp")
        for extension in [".pdf", ".txt"]:
            file_path = temp_dir / f"{file_id}{extension}"
            if file_path.exists():
                file_path.unlink()
                
    except Exception as e:
        # Log error but don't raise - cleanup failures shouldn't stop the application
        print(f"Error removing processed files: {str(e)}")