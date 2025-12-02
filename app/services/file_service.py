import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
from app.core.config import settings


class FileUploadService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.max_size = settings.MAX_UPLOAD_SIZE
        
        # Criar diretório de upload se não existir
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "checklist"), exist_ok=True)

    async def save_checklist_photo(self, file: UploadFile) -> str:
        """Salva uma foto do checklist e retorna o caminho"""
        # Validar tipo de arquivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validar tamanho
        contents = await file.read()
        if len(contents) > self.max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Max size: {self.max_size / (1024*1024)}MB"
            )
        
        # Gerar nome único
        ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(self.upload_dir, "checklist", filename)
        
        # Salvar arquivo
        with open(filepath, "wb") as f:
            f.write(contents)
        
        # Opcional: comprimir/redimensionar imagem
        try:
            self._optimize_image(filepath)
        except Exception as e:
            print(f"Error optimizing image: {e}")
        
        # Retornar path relativo
        return f"checklist/{filename}"

    def _optimize_image(self, filepath: str, max_width: int = 1920, max_height: int = 1920):
        """Otimiza e redimensiona a imagem"""
        with Image.open(filepath) as img:
            # Converter para RGB se necessário
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Redimensionar se necessário
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Salvar com qualidade otimizada
            img.save(filepath, "JPEG", quality=85, optimize=True)

    def delete_file(self, filepath: str) -> bool:
        """Deleta um arquivo"""
        full_path = os.path.join(self.upload_dir, filepath)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def get_file_url(self, filepath: str) -> str:
        """Retorna a URL completa do arquivo"""
        # Em produção, você pode retornar uma URL do CDN ou storage
        return f"/uploads/{filepath}"


file_service = FileUploadService()
