# services/translation_service.py
from typing import Tuple, Optional
from database import FDataBase
from services.gigachat_service import GigaChatService

class TranslationService:
    def __init__(self, db: FDataBase):
        self.db = db
        self.gigachat = GigaChatService()

    def translate_to_formal(self, text: str, user_id: int = None) -> Tuple[str, Optional[str]]:
        """Перевод в формальный стиль через GigaChat"""
        translation, explanation = self.gigachat.translate_text(text, "to_formal")
        
        # Сохраняем в историю
        self.db.add_translation(text, translation, explanation, user_id, "to_formal")
        
        return translation, explanation

    def translate_to_informal(self, text: str, user_id: int = None) -> Tuple[str, Optional[str]]:
        """Перевод в неформальный стиль через GigaChat"""
        translation, explanation = self.gigachat.translate_text(text, "to_informal")
        
        # Сохраняем в историю
        self.db.add_translation(text, translation, explanation, user_id, "to_informal")
        
        return translation, explanation