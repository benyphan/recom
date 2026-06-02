import sqlite3
import os

db_path = 'instance/recommendation.db'


def view_database():
    """Полный просмотр структуры и данных SQLite базы"""

    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return

    print(f"📁 База данных: {db_path}")
    print("=" * 80)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    if not tables:
        print("❌ В базе нет таблиц!")
        conn.close()
        return

    print(f"📋 Найдено таблиц: {len(tables)}\n")

    for table in tables:
        table_name = table[0]
        print("=" * 80)
        print(f"📊 ТАБЛИЦА: {table_name}")
        print("=" * 80)

        # Получаем информацию о колонках
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        print(f"\n🔧 Структура таблицы:")
        print(f"{'№':<3} {'Название колонки':<25} {'Тип данных':<15} {'NOT NULL':<10} {'По умолчанию'}")
        print("-" * 80)

        for i, col in enumerate(columns, 1):
            col_name = col[1]
            col_type = col[2]
            not_null = "Да" if col[3] else "Нет"
            default = col[4] if col[4] else "-"
            print(f"{i:<3} {col_name:<25} {col_type:<15} {not_null:<10} {default}")

        # Получаем количество записей
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\n📈 Записей в таблице: {count}")

        # Показываем первые 5 записей
        if count > 0:
            print(f"\n📝 Первые 5 записей:")
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()

            # Заголовки колонок
            col_names = [col[1] for col in columns]
            print(f"   {col_names}")

            # Данные
            for i, row in enumerate(rows, 1):
                # Обрезаем длинные значения для читаемости
                formatted_row = []
                for val in row:
                    if val is None:
                        formatted_row.append("NULL")
                    elif isinstance(val, str) and len(val) > 30:
                        formatted_row.append(f"{val[:30]}...")
                    else:
                        formatted_row.append(str(val))
                print(f"   {i}. {formatted_row}")

        print("\n")

    conn.close()
    print("=" * 80)
    print("✅ Просмотр завершён")


if __name__ == '__main__':
    view_database()