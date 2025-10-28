import sqlite3
import re

def get_table_names_from_sql(file_path='sq_db.sql'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        table_matches = re.findall(
            r'CREATE TABLE (?:IF NOT EXISTS )?(\w+)', 
            sql_content, 
            re.IGNORECASE
        )
        
        return table_matches
    except Exception as e:
        print(f"❌ Ошибка чтения SQL-файла: {e}")
        return []

def create_database():
    conn = sqlite3.connect('../basic_scripts/translations.db')
    cursor = conn.cursor()
    
    with open('sq_db.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    
    table_names = get_table_names_from_sql()
    
    print("✅ База данных создана успешно!")
    if table_names:
        print(f"✅ Таблицы: {', '.join(table_names)}")
    else:
        print("❌ Не удалось определить названия таблиц")

if __name__ == "__main__":
    create_database()
