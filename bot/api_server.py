from flask import Flask, request, jsonify, g
from flask_cors import CORS, cross_origin
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)

# РАСШИРЕННЫЕ НАСТРОЙКИ CORS ДЛЯ ГАРАНТИРОВАННОЙ РАБОТЫ
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_SUPPORTS_CREDENTIALS'] = False

# Инициализация CORS с максимально широкими настройками
CORS(app, 
     origins="*",
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     allow_headers=["*"],
     expose_headers=["*"],
     supports_credentials=False,
     max_age=600)

# Конфигурация БД
DATABASE = 'translations.db'

# ГЛОБАЛЬНАЯ ОБРАБОТКА CORS ДЛЯ ВСЕХ ЗАПРОСОВ
@app.after_request
def after_request(response):
    """Добавляем CORS заголовки к КАЖДОМУ ответу"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Length,Content-Range')
    response.headers.add('Access-Control-Max-Age', '600')
    return response

@app.before_request
def handle_preflight():
    """Обработка OPTIONS запросов для CORS"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

def get_db():
    """Создает новое подключение к БД для каждого запроса"""
    try:
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        return db
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None

def init_database():
    """Инициализация базы данных если её нет"""
    try:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        
        # Создаем таблицу если её нет
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
        
        # Создаем индекс для быстрого поиска по user_id
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

# Простой класс для работы с БД
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
    
    @staticmethod
    def get_stats():
        """Получение общей статистики"""
        try:
            db = sqlite3.connect(DATABASE)
            cursor = db.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM translations")
            total_translations = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM translations")
            unique_users = cursor.fetchone()[0]
            
            db.close()
            
            return {
                'total_translations': total_translations,
                'unique_users': unique_users
            }
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {'total_translations': 0, 'unique_users': 0}

# Простой сервис GigaChat для тестирования
class SimpleGigaChatService:
    def __init__(self):
        print("✅ SimpleGigaChatService инициализирован (тестовый режим)")
    
    def translate_text(self, text, direction):
        """Тестовый перевод без реального GigaChat"""
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

# API МАРШРУТЫ С ГАРАНТИРОВАННЫМ CORS

@app.route('/api/health', methods=['GET', 'OPTIONS'])
@cross_origin()
def health_check():
    """Проверка работы API и БД"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        # Проверяем подключение к БД
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

@app.route('/api/translate', methods=['POST', 'OPTIONS'])
@cross_origin()
def translate_text():
    """Перевод текста с сохранением в БД"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        # Проверяем доступность сервиса перевода
        if not gigachat_available:
            return jsonify({
                "error": "Сервис переводов временно недоступен",
                "details": "Попробуйте позже"
            }), 503
        
        data = request.get_json()
        
        # Валидация входных данных
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

@app.route('/api/history/<user_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_user_history(user_id):
    """Получение истории переводов пользователя"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        # Параметры пагинации
        limit = request.args.get('limit', default=100, type=int)
        
        # Получаем историю из БД
        translations = DatabaseManager.get_user_translations(user_id, limit)
        
        # Форматируем ответ
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

@app.route('/api/stats/<user_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_user_stats(user_id):
    """Получение статистики пользователя"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
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

@app.route('/api/stats', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_global_stats():
    """Получение глобальной статистики"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        stats = DatabaseManager.get_stats()
        
        return jsonify({
            "success": True,
            "stats": stats,
            "gigachat_status": "connected" if gigachat_available else "disconnected"
        })
        
    except Exception as e:
        print(f"❌ Ошибка получения глобальной статистики: {e}")
        return jsonify({
            "error": f"Ошибка получения статистики: {str(e)}",
            "success": False
        }), 500

@app.route('/api/test-db', methods=['GET', 'OPTIONS'])
@cross_origin()
def test_db():
    """Тестовый эндпоинт для проверки БД"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        # Проверяем подключение к БД
        db = get_db()
        if db:
            cursor = db.cursor()
            
            # Проверяем существование таблицы
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='translations'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.execute("SELECT COUNT(*) FROM translations")
                count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM translations")
                users_count = cursor.fetchone()[0]
                
                db.close()
                
                return jsonify({
                    "success": True,
                    "message": "БД работает корректно",
                    "table_exists": True,
                    "records_count": count,
                    "unique_users": users_count
                })
            else:
                db.close()
                return jsonify({
                    "success": False,
                    "message": "Таблица translations не существует",
                    "table_exists": False
                })
        else:
            return jsonify({
                "success": False,
                "message": "Не удалось подключиться к БД"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка теста БД: {str(e)}"
        }), 500

# Дополнительные тестовые маршруты
@app.route('/api/test-cors', methods=['GET', 'OPTIONS'])
@cross_origin()
def test_cors():
    """Тестовый эндпоинт для проверки CORS"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight'}), 200
        
    return jsonify({
        "success": True,
        "message": "CORS работает корректно",
        "timestamp": datetime.now().isoformat(),
        "cors_headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization"
        }
    })

@app.route('/api/echo', methods=['POST', 'OPTIONS'])
@cross_origin()
def echo():
    """Эхо-эндпоинт для тестирования"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    data = request.get_json() or {}
    return jsonify({
        "success": True,
        "echo": data,
        "timestamp": datetime.now().isoformat(),
        "headers": dict(request.headers)
    })

# Обработка ошибок
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Эндпоинт не найден",
        "path": request.path
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Внутренняя ошибка сервера"
    }), 500

if __name__ == '__main__':
    print("🚀 Запуск API сервера с гарантированным CORS...")
    print("📊 Доступные эндпоинты:")
    print("   GET  /api/health          - проверка статуса API")
    print("   POST /api/translate       - перевод текста")
    print("   GET  /api/history/<id>    - история пользователя")
    print("   GET  /api/stats/<id>      - статистика пользователя")
    print("   GET  /api/stats           - глобальная статистика")
    print("   GET  /api/test-db         - тест базы данных")
    print("   GET  /api/test-cors       - тест CORS")
    print("   POST /api/echo            - эхо-тест")
    print("🔧 Настройки:")
    print("   Порт: 5000")
    print("   Хост: 0.0.0.0 (все интерфейсы)")
    print("   CORS: разрешены все домены")
    print("   Режим: тестовый (SimpleGigaChatService)")
    print("⚡ Сервер запущен и готов к работе!")
    
    # Запускаем сервер
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=False, 
        threaded=True
    )