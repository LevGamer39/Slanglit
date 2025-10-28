from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from services.gigachat_service import GigaChatService
from database import FDataBase
import os

app = Flask(__name__)
CORS(app)

# Конфигурация БД
DATABASE = 'translations.db'

def get_db():
    """Создает новое подключение к БД для каждого запроса"""
    if not hasattr(g, 'sqlite_db'):
        try:
            g.sqlite_db = sqlite3.connect(DATABASE)
            g.sqlite_db.row_factory = sqlite3.Row
            print(f"✅ Создано новое подключение к БД в потоке {os.getpid()}")
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return None
    return g.sqlite_db

def get_db_instance():
    """Создает новый экземпляр FDataBase для каждого запроса"""
    db_connection = get_db()
    if db_connection:
        return FDataBase(db_connection)
    return None

@app.teardown_appcontext
def close_db(error):
    """Закрывает подключение к БД после запроса"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        print("🔒 Подключение к БД закрыто")

# Инициализация GigaChat (можно использовать один экземпляр)
try:
    gigachat = GigaChatService()
    gigachat_available = True
    print("✅ GigaChat инициализирован")
except Exception as e:
    print(f"❌ Ошибка инициализации GigaChat: {e}")
    gigachat_available = False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работы API и БД"""
    try:
        db = get_db_instance()
        if db:
            # Проверяем что БД отвечает
            test_query = db.get_user_translations('test', 1)
            db_status = "connected"
            message = "API и БД работают"
        else:
            db_status = "disconnected"
            message = "БД недоступна"
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")
        db_status = "error"
        message = f"Ошибка БД: {str(e)}"
    
    status = {
        "status": "ok" if db_status == "connected" else "error",
        "database": db_status,
        "gigachat": "connected" if gigachat_available else "disconnected",
        "message": message
    }
    return jsonify(status)

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Перевод текста через GigaChat с сохранением в БД"""
    try:
        # Проверяем доступность GigaChat
        if not gigachat_available:
            return jsonify({
                "error": "Сервис переводов временно недоступен",
                "details": "Попробуйте позже"
            }), 503
        
        data = request.get_json()
        
        # Валидация входных данных
        if not data or 'text' not in data or 'direction' not in data or 'user_id' not in data:
            return jsonify({"error": "Необходимы параметры: text, direction, user_id"}), 400
        
        text = data['text'].strip()
        direction = data['direction']
        user_id = data['user_id']
        
        if not text:
            return jsonify({"error": "Текст не может быть пустым"}), 400
        
        if direction not in ['to_formal', 'to_informal']:
            return jsonify({"error": "Некорректное направление перевода"}), 400
        
        # Выполняем перевод через GigaChat
        if direction == 'to_formal':
            translation, explanation = gigachat.translate_text(text, "to_formal")
            # Для to_formal: исходный текст = неформальный, перевод = формальный
            informal_text = text
            formal_text = translation
        else:
            translation, explanation = gigachat.translate_text(text, "to_informal")
            # Для to_informal: исходный текст = формальный, перевод = неформальный
            informal_text = translation
            formal_text = text
        
        # Сохраняем в базу данных (создаем новое подключение)
        db = get_db_instance()
        if db:
            success = db.add_translation(informal_text, formal_text, explanation, user_id, direction)
            if not success:
                print("⚠️ Предупреждение: не удалось сохранить в БД, но перевод выполнен")
        else:
            print("⚠️ Предупреждение: БД недоступна, перевод не сохранен")
        
        # Формируем ответ
        response = {
            "success": True,
            "original_text": text,
            "translated_text": translation,
            "explanation": explanation,
            "direction": direction,
            "timestamp": datetime.now().isoformat(),
            "saved_to_db": bool(db)  # Сообщаем сохранилось ли в БД
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Ошибка в API перевода: {e}")
        return jsonify({"error": f"Ошибка сервера: {str(e)}"}), 500

@app.route('/api/history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    """Получение истории переводов пользователя"""
    try:
        # Создаем новое подключение к БД
        db = get_db_instance()
        if not db:
            return jsonify({"error": "База данных недоступна"}), 503
        
        # Параметры пагинации
        limit = request.args.get('limit', default=100, type=int)
        
        # Получаем историю из БД
        translations = db.get_user_translations(user_id, limit)
        
        # Форматируем ответ
        history = []
        for trans in translations:
            direction = trans.get('direction', 'to_formal')
            
            history.append({
                "id": trans['id'],
                "informal_text": trans['informal_text'],
                "formal_text": trans['formal_text'],
                "explanation": trans['explanation'],
                "direction": direction,
                "created_at": trans['created_at']
            })
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "translations": history,
            "total": len(history)
        })
        
    except Exception as e:
        print(f"❌ Ошибка получения истории: {e}")
        return jsonify({"error": f"Ошибка получения истории: {str(e)}"}), 500

@app.route('/api/stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Получение статистики пользователя"""
    try:
        db = get_db_instance()
        if not db:
            return jsonify({"error": "База данных недоступна"}), 503
        
        translations = db.get_user_translations(user_id, 1000)
        
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
        return jsonify({"error": f"Ошибка получения статистики: {str(e)}"}), 500

@app.route('/api/test-db', methods=['GET'])
def test_db():
    """Тестовый эндпоинт для проверки БД"""
    try:
        db = get_db_instance()
        if db:
            # Пробуем выполнить простой запрос
            test_result = db.get_user_translations('test_user', 1)
            return jsonify({
                "success": True,
                "message": "БД работает корректно",
                "test_query_result": len(test_result) if test_result else 0
            })
        else:
            return jsonify({"error": "Не удалось подключиться к БД"}), 503
    except Exception as e:
        return jsonify({"error": f"Ошибка теста БД: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Запуск API сервера с исправленной многопоточностью...")
    print("📊 Эндпоинты:")
    print("   POST /api/translate - перевод текста")
    print("   GET  /api/history/<user_id> - история пользователя") 
    print("   GET  /api/stats/<user_id> - статистика")
    print("   GET  /api/health - проверка статуса")
    print("   GET  /api/test-db - тест БД")
    print("🔧 Порт: 5000")
    print("⚡ Режим: многопоточный с изоляцией БД")
    
    # Запускаем в режиме без debug (чтобы не было многопоточных проблем)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)