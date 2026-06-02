import sqlite3
from app import app
from models import db, User, Product, UserAction, Review


def transfer_data():
    """Перенос данных из SQLite в PostgreSQL"""

    # Подключаемся к старой SQLite базе
    sqlite_conn = sqlite3.connect('instance/recommendation.db')
    sqlite_cursor = sqlite_conn.cursor()

    with app.app_context():
        # 1. Переносим товары
        sqlite_cursor.execute("SELECT * FROM products")
        products = sqlite_cursor.fetchall()

        for p in products:
            if not Product.query.filter_by(name=p[1]).first():
                product = Product(
                    id=p[0],
                    name=p[1],
                    description=p[2] if len(p) > 2 else '',
                    price=p[3] if len(p) > 3 else 0.0,
                    category=p[4] if len(p) > 4 else '',
                    image_url=p[5] if len(p) > 5 else '',
                    rating=p[6] if len(p) > 6 else 0.0
                )
                db.session.add(product)

        db.session.commit()
        print(f"✅ Перенесено {len(products)} товаров")

        # 2. Переносим пользователей
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()

        for u in users:
            if not User.query.filter_by(username=u[1]).first():
                user = User(
                    id=u[0],
                    username=u[1],
                    email=u[2] if len(u) > 2 else '',
                    password_hash=u[3] if len(u) > 3 else '',
                    is_admin=u[4] if len(u) > 4 else False
                )
                db.session.add(user)

        db.session.commit()
        print(f"✅ Перенесено {len(users)} пользователей")

        # 3. Переносим действия (история, избранное, корзина)
        sqlite_cursor.execute("SELECT * FROM user_actions")
        actions = sqlite_cursor.fetchall()

        for a in actions:
            # Убираем timestamp - его нет в модели, есть created_at
            action = UserAction(
                id=a[0],
                user_id=a[1],
                product_id=a[2],
                action_type=a[3],
                rating=a[4] if len(a) > 4 else None
            )
            db.session.add(action)

        db.session.commit()
        print(f"✅ Перенесено {len(actions)} действий")

        # 4. Переносим отзывы
        sqlite_cursor.execute("SELECT * FROM reviews")
        reviews = sqlite_cursor.fetchall()

        for r in reviews:
            existing = Review.query.filter_by(
                user_id=r[1],
                product_id=r[2]
            ).first()

            if not existing:
                review = Review(
                    id=r[0],
                    user_id=r[1],
                    product_id=r[2],
                    rating=r[3],
                    text=r[4] if len(r) > 4 else ''
                )
                db.session.add(review)

        db.session.commit()
        print(f"✅ Перенесено {len(reviews)} отзывов")

    sqlite_conn.close()
    print("🎉 Все данные перенесены!")


if __name__ == '__main__':
    transfer_data()