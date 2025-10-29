from flask import Flask, request, jsonify, send_file
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Конфигурация
DATABASE = 'translations.db'

# ========== СТАТИЧЕСКИЕ ФАЙЛЫ ==========

@app.route('/')
def index():
    """Главная страница - отдаем site.html"""
    return send_file('site.html')

@app.route('/style.css')
def serve_css():
    """Отдаем CSS файл"""
    return send_file('style.css')

@app.route('/script.js')
def serve_js():
    """Отдаем JavaScript файл"""
    return send_file('script.js')

# ========== API МАРШРУТЫ ==========

def get_db():
    """Подключение к базе данных"""
    try:
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        return db
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None

def init_database():
    """Инициализация базы данных"""
    try:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                informal_text TEXT NOT NULL,
                formal_text TEXT NOT NULL,
                explanation TEXT,
                user_id TEXT NOT NULL,
                direction TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id ON translations(user_id)
        ''')
        
        db.commit()
        db.close()
        print("✅ База данных инициализирована")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False

class DatabaseManager:
    @staticmethod
    def add_translation(informal_text, formal_text, explanation, user_id, direction):
        """Добавление перевода в БД"""
        try:
            db = sqlite3.connect(DATABASE)
            cursor = db.cursor()
            
            cursor.execute('''
                INSERT INTO translations (informal_text, formal_text, explanation, user_id, direction, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', (informal_text, formal_text, explanation, user_id, direction))
            
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения в БД: {e}")
            return False
    
    @staticmethod
    def get_user_translations(user_id, limit=100):
        """Получение истории переводов пользователя"""
        try:
            db = sqlite3.connect(DATABASE)
            cursor = db.cursor()
            
            cursor.execute('''
                SELECT * FROM translations 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            translations = cursor.fetchall()
            db.close()
            
            result = []
            for trans in translations:
                result.append({
                    'id': trans[0],
                    'informal_text': trans[1],
                    'formal_text': trans[2],
                    'explanation': trans[3],
                    'user_id': trans[4],
                    'direction': trans[5],
                    'created_at': trans[6]
                })
            
            return result
        except Exception as e:
            print(f"❌ Ошибка получения истории: {e}")
            return []

# Простой сервис GigaChat для тестирования
class SimpleGigaChatService:
    def __init__(self):
        print("✅ SimpleGigaChatService инициализирован (тестовый режим)")
    
    def translate_text(self, text, direction):
        """Тестовый перевод"""
        if direction == "to_formal":
            translation = f"📝 Формальный вариант: {text}"
            explanation = "Это тестовый перевод в формальном стиле. В рабочем режиме здесь будет настоящее объяснение от GigaChat."
        else:
            translation = f"💬 Неформальный вариант: {text}"
            explanation = "Это тестовый перевод в неформальном стиле. В рабочем режиме здесь будет настоящее объяснение от GigaChat."
        
        return translation, explanation

# Инициализация сервисов
try:
    gigachat = SimpleGigaChatService()
    gigachat_available = True
    print("✅ GigaChatService инициализирован в тестовом режиме")
except Exception as e:
    print(f"❌ Ошибка инициализации GigaChat: {e}")
    gigachat_available = False

# Инициализация БД при старте
db_initialized = init_database()

# ========== API ЭНДПОИНТЫ ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работы API и БД"""
    try:
        db = get_db()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM translations")
            count = cursor.fetchone()[0]
            db.close()
            
            db_status = "connected"
            message = f"API и БД работают. Записей в БД: {count}"
        else:
            db_status = "disconnected"
            message = "БД недоступна"
    except Exception as e:
        db_status = "error"
        message = f"Ошибка БД: {str(e)}"
    
    status = {
        "status": "ok" if db_status == "connected" else "error",
        "database": db_status,
        "gigachat": "connected" if gigachat_available else "disconnected",
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    return jsonify(status)

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Перевод текста с сохранением в БД"""
    try:
        if not gigachat_available:
            return jsonify({
                "error": "Сервис переводов временно недоступен",
                "details": "Попробуйте позже"
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Отсутствуют данные в запросе"}), 400
            
        if 'text' not in data:
            return jsonify({"error": "Отсутствует параметр: text"}), 400
            
        if 'direction' not in data:
            return jsonify({"error": "Отсутствует параметр: direction"}), 400
            
        if 'user_id' not in data:
            return jsonify({"error": "Отсутствует параметр: user_id"}), 400
        
        text = data['text'].strip()
        direction = data['direction']
        user_id = data['user_id']
        
        if not text:
            return jsonify({"error": "Текст не может быть пустым"}), 400
        
        if direction not in ['to_formal', 'to_informal']:
            return jsonify({"error": "Некорректное направление перевода. Допустимо: to_formal, to_informal"}), 400
        
        print(f"🔧 Перевод запроса: '{text}' -> {direction} для пользователя {user_id}")
        
        # Выполняем перевод
        translation, explanation = gigachat.translate_text(text, direction)
        
        # Определяем формальный и неформальный текст для сохранения
        if direction == 'to_formal':
            informal_text = text
            formal_text = translation
        else:
            informal_text = translation
            formal_text = text
        
        # Сохраняем в базу данных
        saved = DatabaseManager.add_translation(informal_text, formal_text, explanation, user_id, direction)
        
        # Формируем ответ
        response = {
            "success": True,
            "original_text": text,
            "translated_text": translation,
            "explanation": explanation,
            "direction": direction,
            "timestamp": datetime.now().isoformat(),
            "saved_to_db": saved
        }
        
        print(f"✅ Перевод выполнен: {text[:50]}... -> {translation[:50]}...")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Ошибка в API перевода: {e}")
        return jsonify({
            "error": f"Внутренняя ошибка сервера: {str(e)}",
            "success": False
        }), 500

@app.route('/api/history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    """Получение истории переводов пользователя"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        
        translations = DatabaseManager.get_user_translations(user_id, limit)
        
        history = []
        for trans in translations:
            history.append({
                "id": trans['id'],
                "informal_text": trans['informal_text'],
                "formal_text": trans['formal_text'],
                "explanation": trans['explanation'],
                "direction": trans['direction'],
                "created_at": trans['created_at']
            })
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "translations": history,
            "total": len(history),
            "limit": limit
        })
        
    except Exception as e:
        print(f"❌ Ошибка получения истории: {e}")
        return jsonify({
            "error": f"Ошибка получения истории: {str(e)}",
            "success": False
        }), 500

@app.route('/api/stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Получение статистики пользователя"""
    try:
        translations = DatabaseManager.get_user_translations(user_id, 1000)
        
        stats = {
            "total_translations": len(translations),
            "to_formal_count": len([t for t in translations if t.get('direction') == 'to_formal']),
            "to_informal_count": len([t for t in translations if t.get('direction') == 'to_informal']),
            "last_activity": translations[0]['created_at'] if translations else None
        }
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "stats": stats
        })
        
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
        return jsonify({
            "error": f"Ошибка получения статистики: {str(e)}",
            "success": False
        }), 500

if __name__ == '__main__':
    print("🚀 Запуск единого приложения Slanglit (Сайт + API)")
    print("📊 Доступные URL:")
    print("   GET  /                    - главная страница сайта")
    print("   GET  /api/health          - проверка статуса API")
    print("   POST /api/translate       - перевод текста")
    print("   GET  /api/history/<id>    - история пользователя")
    print("   GET  /api/stats/<id>      - статистика пользователя")
    print("🔧 Порт: 5000")
    print("⚡ CORS проблемы решены - сайт и API на одном домене!")
    
    app.run(host='0.0.0.0', port=5000, debug=False)