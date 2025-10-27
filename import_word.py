import sqlite3
import json
import csv

def import_from_json(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            words = json.load(f)
        
        conn = sqlite3.connect('translations.db')
        cursor = conn.cursor()
        
        imported_count = 0
        for word in words:
            try:
                cursor.execute(
                    'INSERT OR IGNORE INTO words (informal_text, formal_text, explanation) VALUES (?, ?, ?)',
                    (word['informal_text'], word['formal_text'], word['explanation'])
                )
                imported_count += 1
            except sqlite3.Error as e:
                print(f"❌ Ошибка при добавлении слова {word}: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ Импортировано {imported_count} слов из JSON")
        
    except Exception as e:
        print(f"❌ Ошибка при чтении JSON файла: {e}")


def check_existing_words():
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM words')
    count = cursor.fetchone()[0]
    
    cursor.execute('SELECT * FROM words LIMIT 5')
    sample_words = cursor.fetchall()
    
    conn.close()
    
    print(f"📊 Всего слов в базе: {count}")
    if sample_words:
        print("📝 Примеры слов:")
        for word in sample_words:
            print(f"  {word[0]} → {word[1]}: {word[2]}")

if __name__ == "__main__":
    print("🔄 Импорт слов в базу данных...")
    
    json_file = "slangify_words.json"  
    try:
        import_from_json(json_file)
    except FileNotFoundError:
        print(f"❌ JSON файл {json_file} не найден")
    
    check_existing_words()