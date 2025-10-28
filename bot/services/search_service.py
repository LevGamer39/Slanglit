from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict

class SearchService:
    @staticmethod
    def create_search_results_keyboard(results: List[Dict], offset: int, search_type: str):
        keyboard_buttons = []
        nav_buttons = []
        
        if offset > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"search_prev_{offset-10}"))
        
        if offset + 10 < len(results):
            nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_next_{offset+10}"))
        
        if nav_buttons:
            keyboard_buttons.append(nav_buttons)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    @staticmethod
    def format_search_results(results: List[Dict], offset: int, search_type: str, search_text: str):
        page_results = results[offset:offset + 10]
        total_pages = (len(results) + 9) // 10
        
        if search_type == "history":
            text = f"🔍 Найдено {len(results)} переводов по запросу '{search_text}'\n"
            text += f"Страница {offset//10 + 1} из {total_pages}:\n\n"
            
            for i, trans in enumerate(page_results, offset + 1):
                direction = trans.get('direction', 'to_formal')
                if direction == 'to_formal':
                    text += f"{i}. 💼 Неформальный → Формальный\n"
                    text += f"   🔥 `{trans['informal_text']}`\n"
                    text += f"   → 💼 `{trans['formal_text']}`\n"
                else:
                    text += f"{i}. 🔥 Формальный → Неформальный\n"
                    text += f"   💼 `{trans['informal_text']}`\n"
                    text += f"   → 🔥 `{trans['formal_text']}`\n"
                text += f"   📅 {trans['created_at']}\n\n"
        
        else:
            text = f"🔍 Найдено {len(results)} слов по запросу '{search_text}'\n"
            text += f"Страница {offset//10 + 1} из {total_pages}:\n\n"
            
            for i, word in enumerate(page_results, offset + 1):
                text += f"{i}. 🔥 `{word['informal_text']}` → 💼 `{word['formal_text']}`"
                if word.get('explanation'):
                    text += f"\n   📖 {word['explanation']}\n\n"
                else:
                    text += "\n\n"
        
        return text