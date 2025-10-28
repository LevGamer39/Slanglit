from typing import Tuple, Optional
import sqlite3
from database import FDataBase

def connect_db():
    return sqlite3.connect('translations.db')

class TranslationService:
    def __init__(self, db: FDataBase, profanity_service=None):
        self.db = db
        self.profanity_service = profanity_service

    def translate_to_formal(self, text: str, user_id: int = None) -> Tuple[str, Optional[str]]:
        # Проверка на маты
        if self.profanity_service and self.profanity_service.contains_profanity(text):
            return None, "profanity_detected"
        
        original_text = text
        result = self.db.get_formal_translation(text.lower())
        if result:
            formal_text, explanation = result
            explanation_text = f"{text} → {formal_text}: {explanation}" if explanation else None
            self.db.add_translation(text, formal_text, explanation_text, user_id, "to_formal")
            return formal_text, explanation_text
        
        words = text.split()
        formal_parts = []
        explanations = []
        
        i = 0
        while i < len(words):
            found = False
            for length in range(min(3, len(words) - i), 0, -1):
                phrase = ' '.join(words[i:i + length])
                result = self.db.get_formal_translation(phrase.lower())
                if result:
                    formal_phrase, explanation = result
                    formal_parts.append(formal_phrase)
                    if explanation:
                        explanations.append(f"{phrase} → {formal_phrase}: {explanation}")
                    i += length
                    found = True
                    break
            
            if not found:
                formal_parts.append(words[i])
                i += 1
        
        formal_text = ' '.join(formal_parts)
        explanation_text = '\n'.join(explanations) if explanations else None
        
        self.db.add_translation(text, formal_text, explanation_text, user_id, "to_formal")
        
        return formal_text, explanation_text

    def translate_to_informal(self, text: str, user_id: int = None) -> Tuple[str, Optional[str]]:
        # Проверка на маты
        if self.profanity_service and self.profanity_service.contains_profanity(text):
            return None, "profanity_detected"
            
        words = text.split()
        informal_parts = []
        explanations = []
        
        i = 0
        while i < len(words):
            found = False
            for length in range(min(3, len(words) - i), 0, -1):
                phrase = ' '.join(words[i:i + length])
                result = self.db.get_informal_translation(phrase.lower())
                if result:
                    informal_phrase, explanation = result
                    informal_parts.append(informal_phrase)
                    if explanation:
                        explanations.append(f"{phrase} → {informal_phrase}: {explanation}")
                    i += length
                    found = True
                    break
            
            if not found:
                informal_parts.append(words[i])
                i += 1
        
        informal_text = ' '.join(informal_parts)
        explanation_text = '\n'.join(explanations) if explanations else None
        
        self.db.add_translation(text, informal_text, explanation_text, user_id, "to_informal")
        
        return informal_text, explanation_text