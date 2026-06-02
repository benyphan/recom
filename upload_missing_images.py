from app import app
from models import db, Product
import cloudinary.uploader
import os


def upload_to_cloudinary():
    """Загрузить локальные картинки в Cloudinary"""

    with app.app_context():
        # Товары которые нужно исправить
        products_to_fix = [
            {'name': 'iPhone 15 Pro', 'file': 'iphone_15_pro.jpg'},
            {'name': 'Samsung Galaxy S24 Ultra', 'file': 'samsung_s24.jpg'}
        ]

        uploaded = 0

        for item in products_to_fix:
            product = Product.query.filter_by(name=item['name']).first()
            if not product:
                print(f"❌ Товар '{item['name']}' не найден")
                continue

            local_path = os.path.join('static', 'images', item['file'])

            if not os.path.exists(local_path):
                print(f"❌ Файл не найден: {local_path}")
                continue

            print(f"📤 Загружаем: {item['name']}...")

            try:
                # Загружаем в Cloudinary
                result = cloudinary.uploader.upload(
                    local_path,
                    folder="ado_marketplace",
                    transformation={'width': 800, 'height': 600, 'crop': 'limit'}
                )

                # Обновляем URL в базе
                product.image_url = result['secure_url']
                uploaded += 1

                print(f"  ✅ Загружено: {result['secure_url'][:60]}...")

            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
                # Устанавливаем дефолтную картинку
                product.image_url = 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400'

        db.session.commit()
        print(f"\n🎉 Загружено {uploaded} из {len(products_to_fix)} изображений")


if __name__ == '__main__':
    upload_to_cloudinary()