from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    print("Добавляем индексы для ускорения запросов...")

    # Индексы для товаров
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating)"))

    # Индексы для пользователей
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))

    # Индексы для действий
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_actions_product_id ON user_actions(product_id)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_actions_action_type ON user_actions(action_type)"))

    # Индексы для отзывов
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id)"))

    db.session.commit()
    print("✅ Индексы добавлены!")