"""
Image upload handling for chatbot
"""

from fastapi import UploadFile, HTTPException
from typing import Optional
import os
import uuid
from datetime import datetime, timezone
import aiofiles


class ImageUploadService:
    """Handle image uploads for chatbot (symptoms, rashes, etc.)"""
    
    def __init__(self, upload_dir: str = "uploads/chatbot_images"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        
        # Allowed file types
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        self.max_file_size = 5 * 1024 * 1024  # 5MB
    
    async def save_image(
        self,
        file: UploadFile,
        session_id: str
    ) -> dict:
        """
        Save uploaded image and return metadata
        
        Args:
            file: Uploaded file
            session_id: Chatbot session ID
        
        Returns:
            Dict with file info
        """
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(self.allowed_extensions)}"
            )
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{session_id}_{timestamp}_{unique_id}{file_ext}"
        filepath = os.path.join(self.upload_dir, filename)
        
        # Read and validate file size
        content = await file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {self.max_file_size / (1024*1024)}MB"
            )
        
        # Save file
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(content)
        
        return {
            "filename": filename,
            "filepath": filepath,
            "size": len(content),
            "content_type": file.content_type,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_image_analysis(self, filepath: str) -> dict:
        """
        Analyze image using OpenAI Vision API (GPT-4 Vision)
        
        This is a placeholder for future implementation
        Would use: openai.ChatCompletion.create with vision model
        """
        
        # TODO: Implement OpenAI Vision API
        # For now, return placeholder
        return {
            "analysis": "Image uploaded successfully. Visual analysis coming soon.",
            "observations": [],
            "medical_relevance": "pending"
        }
