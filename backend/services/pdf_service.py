# backend/services/pdf_service.py
import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any, Tuple
import io
from PIL import Image
import base64

class PDFService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.logger = logging.getLogger(__name__)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_and_images(self, file_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
        """Extract high-quality text and images with metadata."""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        full_text = ""
        images = []
        
        for i, page in enumerate(doc):
            full_text += page.get_text() + "\n"
            
            # Extract images
            page_images = page.get_images(full=True)
            for img_index, img in enumerate(page_images):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Basic captioning logic: look for text blocks below the image
                    # For production, we'd use a more robust layout analyzer (e.g. LayoutParser)
                    caption = f"Figure on Page {i+1}" 
                    
                    images.append({
                        "page": i + 1,
                        "bytes": image_bytes,
                        "caption": caption,
                        "ext": base_image["ext"]
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to extract image on page {i+1}: {e}")
        
        doc.close()
        return full_text, images

    def recursive_split(self, text: str) -> List[str]:
        """Simple recursive-style character splitting for cleaner context blocks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            if end >= len(text):
                chunks.append(text[start:].strip())
                break
                
            # Try to find a good breaking point (newline or period)
            chunk = text[start:end]
            last_newline = chunk.rfind('\n')
            last_period = chunk.rfind('.')
            
            break_point = max(last_newline, last_period)
            if break_point == -1 or break_point < self.chunk_size // 2:
                # No good break point found in the last half of the chunk, break at space
                last_space = chunk.rfind(' ')
                if last_space != -1:
                    break_point = last_space
                else:
                    break_point = self.chunk_size # Hard break
            
            actual_end = start + break_point
            chunks.append(text[start:actual_end].strip())
            start = actual_end - self.chunk_overlap
            
        return [c for c in chunks if len(c) > 50] # Filter out noise
