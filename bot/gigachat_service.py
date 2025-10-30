# services/gigachat_service.py
import gigachat
from gigachat.models import Chat, Messages, MessagesRole
import json
import re
from config import GIGACHAT_API_KEY

class GigaChatService:
    def __init__(self):
        self.api_key = GIGACHAT_API_KEY
        self.client = None
        self._connect()
        
    def _connect(self):
        """Подключение к GigaChat"""
        try:
            self.client = gigachat.GigaChat(
                credentials=self.api_key,
                verify_ssl_certs=False
            )
            # Получаем токен
            self.client.get_models()
            print("✅ Успешное подключение к GigaChat")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к GigaChat: {e}")
            return False
    
    def translate_text(self, text: str, direction: str = "to_formal") -> tuple[str, str]:
        """Перевод текста с помощью GigaChat"""
        if not self.client:
            if not self._connect():
                return text, "Ошибка подключения к нейросети"
        
        try:
            # Формируем промпт в зависимости от направления
            if direction == "to_formal":
                system_prompt = """Ты эксперт по русскому языку и сленгу. Твоя задача:
1. Перевести неформальный текст в формальный деловой стиль
2. Объяснить значение неформальных слов и выражений
3. Предложить несколько вариантов перевода если возможно

ВАЖНО: Ответь ТОЛЬКО в формате JSON без каких-либо дополнительных текстов:
{
  "translation": "переведенный текст",
  "explanation": "объяснение неформальных слов"
}

Пример для "Это кринж бро":
{
  "translation": "Это вызывает неловкость, друг / Это стыдно выглядит, приятель",
  "explanation": "• 'кринж' - чувство неловкости, стыда за чьи-то действий\\n• 'бро' - неформальное обращение к другу, приятелю"
}"""
            else:
                system_prompt = """Ты эксперт по русскому языку. Твоя задача:
1. Перевести формальный текст в неформальный разговорный стиль
2. Объяснить формальные выражения и предложить сленговые аналоги
3. Предложить несколько вариантов перевода если возможно

ВАЖНО: Ответь ТОЛЬКО в формате JSON без каких-либо дополнительных текстов:
{
  "translation": "переведенный текст",
  "explanation": "объяснение формальных выражений"
}

Пример для "Данная ситуация вызывает чувство дискомфорта":
{
  "translation": "Это неловко / Это стремно",
  "explanation": "• 'вызывает чувство дискомфорта' - формальное выражение, означает неловкость, стыд\\n• Можно заменить на сленг: 'кринж', 'стремно', 'неловка'"
}"""
            
            messages = [
                Messages(role=MessagesRole.SYSTEM, content=system_prompt),
                Messages(role=MessagesRole.USER, content=text)
            ]
            
            response = self.client.chat(Chat(messages=messages))
            content = response.choices[0].message.content
            
            print(f"🔍 Ответ от GigaChat: {content}")  # Для отладки
            
            # Парсим JSON ответ
            try:
                # Исправляем JSON - заменяем неэкранированные символы
                fixed_json = content
                
                # Экранируем обратные слеши в строках
                fixed_json = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', fixed_json)
                
                # Экранируем кавычки внутри строк
                def escape_quotes(match):
                    text = match.group(1)
                    # Экранируем кавычки, которые не экранированы
                    text = re.sub(r'(?<!\\)"', r'\\"', text)
                    return f'"{text}"'
                
                # Обрабатываем строки в JSON
                fixed_json = re.sub(r'"([^"]*)"', escape_quotes, fixed_json)
                
                # Парсим исправленный JSON
                parsed = json.loads(fixed_json)
                translation = parsed.get("translation", text)
                explanation = parsed.get("explanation", "Объяснение не предоставлено")
                
                # Заменяем \n на настоящие переносы строк
                explanation = explanation.replace('\\n', '\n')
                
            except Exception as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                # Альтернативный метод парсинга через регулярные выражения
                try:
                    translation_match = re.search(r'"translation"\s*:\s*"([^"]*)"', content, re.DOTALL)
                    explanation_match = re.search(r'"explanation"\s*:\s*"([^"]*)"', content, re.DOTALL)
                    
                    if translation_match and explanation_match:
                        translation = translation_match.group(1)
                        explanation = explanation_match.group(1)
                        # Заменяем \n на настоящие переносы строк
                        explanation = explanation.replace('\\n', '\n')
                    else:
                        # Если не нашли в кавычках, ищем без них
                        translation_match = re.search(r'"translation"\s*:\s*([^,\n}]*)', content)
                        explanation_match = re.search(r'"explanation"\s*:\s*([^,\n}]*)', content)
                        
                        if translation_match and explanation_match:
                            translation = translation_match.group(1).strip().strip('"')
                            explanation = explanation_match.group(1).strip().strip('"')
                        else:
                            translation = content
                            explanation = "Перевод выполнен нейросетью GigaChat"
                            
                except Exception as e2:
                    print(f"❌ Ошибка альтернативного парсинга: {e2}")
                    translation = content
                    explanation = "Перевод выполнен нейросетью GigaChat"
            
            return translation, explanation
            
        except Exception as e:
            print(f"❌ Ошибка перевода: {e}")
            return text, f"Ошибка перевода: {str(e)}"