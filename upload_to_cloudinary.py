"""
Запусти ОДИН РАЗ из папки проекта:
    python upload_to_cloudinary.py

Что делает:
- Берёт каждый товар из базы у которого image_url = локальный файл (например iphone_15_pro.jpg)
- Находит этот файл в папке static/images/
- Загружает на Cloudinary
- Сохраняет в базу постоянный URL вида https://res.cloudinary.com/...
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

import cloudinary
import cloudinary.uploader
from app import app, db
from models import Product

# Настройка Cloudinary из .env
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')


def is_local_file(url):
    """Проверяет что image_url — это локальный файл, а не внешний URL"""
    if not url:
        return False
    return not url.startswith(('http://', 'https://'))


def upload_product_image(filepath, filename):
    """Загружает файл на Cloudinary и возвращает постоянный URL"""
    public_id = os.path.splitext(filename)[0]  # iphone_15_pro.jpg → iphone_15_pro
    result = cloudinary.uploader.upload(
        filepath,
        public_id=public_id,
        folder='ado_marketplace',
        overwrite=True,
        resource_type='image'
    )
    return result['secure_url']


with app.app_context():
    products = Product.query.all()

    uploaded = 0
    skipped = 0
    not_found = 0
    errors = 0

    print(f"Всего товаров в базе: {len(products)}")
    print(f"Папка с картинками: {IMAGES_FOLDER}")
    print("=" * 60)

    for product in products:
        url = product.image_url

        # Уже внешний URL — пропускаем
        if not is_local_file(url):
            print(f"⏭  Пропускаем (уже URL): {product.name[:45]}")
            skipped += 1
            continue

        # Ищем файл в static/images/
        filepath = os.path.join(IMAGES_FOLDER, url)
        if not os.path.exists(filepath):
            print(f"❌ Файл не найден: {url}  ({product.name[:35]})")
            not_found += 1
            continue

        # Загружаем на Cloudinary
        try:
            new_url = upload_product_image(filepath, url)
            product.image_url = new_url
            db.session.commit()
            print(f"✅ {product.name[:45]}")
            uploaded += 1
        except Exception as e:
            print(f"⚠  Ошибка {product.name[:35]}: {e}")
            errors += 1

    print()
    print("=" * 60)
    print(f"✅ Загружено на Cloudinary:  {uploaded}")
    print(f"⏭  Уже были URL (пропущено): {skipped}")
    print(f"❌ Файл не найден:           {not_found}")
    print(f"⚠  Ошибки при загрузке:     {errors}")
    print()

    if not_found > 0:
        print("💡 Совет: файлы не найдены потому что их нет в static/images/")
        print("   Зайди в админку и вручную поставь картинку для этих товаров.")

    if uploaded > 0:
        print()
        print("🎉 Готово! Картинки теперь в облаке — работают на любом устройстве.")
