from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    actions = db.relationship('UserAction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500), default='')
    rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    actions = db.relationship('UserAction', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'rating': self.rating
        }


class UserAction(db.Model):
    __tablename__ = 'user_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    action_type = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', 'action_type', name='unique_user_product_action'),
    )


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reviews', lazy=True)
    product = db.relationship('Product', backref='reviews', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_review'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'product_id': self.product_id,
            'rating': self.rating,
            'text': self.text,
            'created_at': self.created_at.isoformat()
        }


def init_db(app):
    with app.app_context():
        db.create_all()
        seed_products()


def seed_products():
    if Product.query.first():
        return
    
    products = [
        # Смартфоны
        Product(name='iPhone 15 Pro', description='Флагманский смартфон Apple с чипом A17 Pro, титановым корпусом и продвинутой камерой', price=149990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400', rating=4.8),
        Product(name='Samsung Galaxy S24 Ultra', description='Ультимативный смартфон с S Pen, AI-функциями и 200МП камерой', price=134990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400', rating=4.6),
        Product(name='Xiaomi 14 Pro', description='Флагман с Leica оптикой, Snapdragon 8 Gen 3 и 120W быстрой зарядкой', price=89990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400', rating=4.4),
        Product(name='Google Pixel 8 Pro', description='Смартфон с лучшей камерой на рынке, чистый Android и AI-функциями Google', price=99990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400', rating=4.5),
        Product(name='OnePlus 12', description='Флагман с Snapdragon 8 Gen 3, Hasselblad камерой и 100W зарядкой', price=79990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400', rating=4.3),
        
        # Ноутбуки
        Product(name='MacBook Pro 14', description='Профессиональный ноутбук с M3 Pro, Liquid Retina XDR дисплеем и до 22 часов автономности', price=249990, category='Ноутбуки', image_url='https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400', rating=4.9),
        Product(name='Dell XPS 15', description='Премиальный ноутбук с OLED дисплеем, Intel Core i9 и ультратонким корпусом', price=189990, category='Ноутбуки', image_url='https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400', rating=4.4),
        Product(name='ASUS ROG Zephyrus G16', description='Игровой ноутбук с RTX 4070, Intel Core i9 и 240Hz дисплеем', price=179990, category='Ноутбуки', image_url='https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400', rating=4.6),
        Product(name='Lenovo ThinkPad X1 Carbon', description='Бизнес-ноутбук с Intel Core i7, легким корпусом и долгой автономностью', price=149990, category='Ноутбуки', image_url='https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400', rating=4.5),
        
        # Наушники
        Product(name='Sony WH-1000XM5', description='Премиальные беспроводные наушники с активным шумоподавлением и 30 часами работы', price=34990, category='Наушники', image_url='https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400', rating=4.7),
        Product(name='AirPods Pro 2', description='Беспроводные наушники с адаптивным шумоподавлением и персонализированным звуком', price=24990, category='Наушники', image_url='https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400', rating=4.5),
        Product(name='Bose QuietComfort Ultra', description='Наушники с пространственным звуком, CustomTune и до 24 часов работы', price=42990, category='Наушники', image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400', rating=4.6),
        Product(name='Samsung Galaxy Buds2 Pro', description='Компактные наушники с ANC, 360 Audio и защитой от воды IPX7', price=19990, category='Наушники', image_url='https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400', rating=4.3),
        
        # Планшеты
        Product(name='iPad Pro 12.9', description='Профессиональный планшет с M2, Liquid Retina XDR и поддержкой Apple Pencil', price=119990, category='Планшеты', image_url='https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400', rating=4.8),
        Product(name='Samsung Galaxy Tab S9 Ultra', description='Планшет с 14.6" AMOLED дисплеем, S Pen и водозащитой IP68', price=99990, category='Планшеты', image_url='https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400', rating=4.4),
        
        # Умные часы
        Product(name='Apple Watch Ultra 2', description='Самые прочные смарт-часы Apple для экстремальных условий с GPS и дайвинг-функциями', price=89990, category='Умные часы', image_url='https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400', rating=4.7),
        Product(name='Samsung Galaxy Watch 6 Classic', description='Классические смарт-часы с вращающимся безелем, ECG и пульсоксиметром', price=34990, category='Умные часы', image_url='https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400', rating=4.5),
        Product(name='Garmin Fenix 7', description='Мультиспортивные часы с GPS, картами и до 22 дней автономной работы', price=59990, category='Умные часы', image_url='https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400', rating=4.8),
        
        # Игровые консоли
        Product(name='PlayStation 5', description='Игровая консоль нового поколения с 4K, Ray Tracing и обратной совместимостью', price=54990, category='Игровые консоли', image_url='https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400', rating=4.9),
        Product(name='Nintendo Switch OLED', description='Портативная консоль с 7" OLED экраном, улучшенной подставкой и Ethernet портом', price=34990, category='Игровые консоли', image_url='https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400', rating=4.7),
        Product(name='Xbox Series X', description='Самая мощная консоль с 12 TFLOPS, 4K 120fps и Game Pass', price=49990, category='Игровые консоли', image_url='https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=400', rating=4.6),
        
        # Аудио и техника
        Product(name='JBL Flip 6', description='Компактная портативная колонка с мощным звуком, водозащитой IPX7 и 12ч работы', price=7990, category='Аудио', image_url='https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400', rating=4.4),
        Product(name='Sonos Era 300', description='Премиальная колонка с Dolby Atmos, пространственным звуком и голосовым управлением', price=44990, category='Аудио', image_url='https://images.unsplash.com/photo-1589003077984-894e133dabab?w=400', rating=4.5),
        
        # Дроны
        Product(name='DJI Mini 4 Pro', description='Компактный дрон с 4K камерой, системой обхода препятствий и 34 мин полета', price=79990, category='Дроны', image_url='https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=400', rating=4.6),
        Product(name='DJI Air 3', description='Дрон с двумя камерами (широкоугольная и зум), 46 мин полета и 4K 100fps', price=119990, category='Дроны', image_url='https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=400', rating=4.7),
        
        # Фото и видео
        Product(name='Sony A7 IV', description='Полнокадровая беззеркалка с 33МП, 4K 60fps и продвинутым автофокусом', price=229990, category='Фото и видео', image_url='https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400', rating=4.9),
        Product(name='Canon EOS R6 Mark II', description='Профессиональная камера с 40МП, 8K видео и стабилизацией IBIS', price=299990, category='Фото и видео', image_url='https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400', rating=4.8),
        Product(name='GoPro Hero 12 Black', description='Экшн-камера с 5.3K видео, HDR и до 2ч работы от одного заряда', price=44990, category='Фото и видео', image_url='https://images.unsplash.com/photo-1564466021188-1e4aa5248a3d?w=400', rating=4.5),
        
        # Электронные книги
        Product(name='Kindle Paperwhite', description='Электронная книга с 6.8" экраном, теплой подсветкой и водозащитой', price=14990, category='Электронные книги', image_url='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400', rating=4.3),
        Product(name='Kobo Libra 2', description='电子书 reader с 7" E Ink экраном, Bluetooth и поддержкой аудиокниг', price=17990, category='Электронные книги', image_url='https://images.unsplash.com/photo-1553756513-4037891615cd?w=400', rating=4.2),
        
        # Аксессуары
        Product(name='Logitech MX Master 3S', description='Эргономичная беспроводная мышь с тихими кнопками и колесом прокрутки MagSpeed', price=8990, category='Аксессуары', image_url='https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400', rating=4.5),
        Product(name='Keychron Q1 Pro', description='Механическая клавиатура с горячими клавишами, QMK и алюминиевым корпусом', price=14990, category='Аксессуары', image_url='https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=400', rating=4.6),
        Product(name='Samsung T7 Shield', description='Внешний SSD на 2ТБ с IP65 защитой и скоростью до 1050МБ/с', price=19990, category='Аксессуары', image_url='https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=400', rating=4.7),
        
        # Спорт и фитнес
        Product(name='Apple AirPods Max', description='Премиальные накладные наушники с пространственным звуком и активным шумоподавлением', price=69990, category='Аудио', image_url='https://images.unsplash.com/photo-1623183848-1af7d4b2fe71?w=400', rating=4.6),
        Product(name='Xiaomi Mi Band 8 Pro', description='Фитнес-браслет с 1.74" AMOLED, GPS и мониторингом здоровья 24/7', price=4990, category='Умные часы', image_url='https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400', rating=4.2),
        Product(name='Theragun Elite', description='Массажный пистолет с QuietForce технологией и 5 насадками для глубокого массажа', price=34990, category='Спорт и фитнес', image_url='https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400', rating=4.5),
        Product(name='Hydro Flask 32oz', description='Термобутылка из нержавеющей стали, сохраняет холод 24ч, горячий 12ч', price=3990, category='Спорт и фитнес', image_url='https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400', rating=4.6),
        
        # Для дома
        Product(name='Dyson V15 Detect', description='Беспроводной пылесос с лазерным обнаружением пыли и LED-подсветкой', price=54990, category='Для дома', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.7),
        Product(name='iRobot Roomba j7+', description='Робот-пылесос с навигацией PrecisionVision, самоочисткой и AI-планированием', price=64990, category='Для дома', image_url='https://images.unsplash.com/photo-1603618090561-412154b4bd1b?w=400', rating=4.4),
        Product(name='Philips Hue Starter Kit', description='Умное освещение с 4 лампами E27, мостом и управлением через приложение', price=9990, category='Для дома', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        Product(name='Nest Hub 2', description='Умная колонка с 7" экраном, Google Assistant и мониторингом сна', price=8990, category='Для дома', image_url='https://images.unsplash.com/photo-1543512214-318c7553f230?w=400', rating=4.2),
        
        # Парфюмерия
        Product(name='Dior Sauvage EDP', description='Аромат с бергамотом, амброксаном и белым мускусом. Для мужчин.', price=8990, category='Парфюмерия', image_url='https://images.unsplash.com/photo-1541643600914-78b084683601?w=400', rating=4.6),
        Product(name='Chanel No. 5 EDP', description='Классический женский аромат с розой, ирисом и ванилью', price=12990, category='Парфюмерия', image_url='https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400', rating=4.8),
        Product(name='Tom Ford Black Orchid EDP', description='Роскошный аромат с черной орхидеей, трюфелем и ветивером', price=11990, category='Парфюмерия', image_url='https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=400', rating=4.5),
        
        # Косметика и уход
        Product(name='La Mer Crème de la Mer', description='Увлажняющий крем с Miracle Broth для сияния и омоложения кожи', price=24990, category='Косметика', image_url='https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400', rating=4.4),
        Product(name='Dyson Airwrap', description='Мультистайлер для волос с завивкой, выпрямлением и сушкой без перегрева', price=54990, category='Косметика', image_url='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400', rating=4.7),
        Product(name='Foreo Luna 3', description='Умная щетка для лица с вибрациями T-Sonic для глубокого очищения', price=12990, category='Косметика', image_url='https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=400', rating=4.3),
        
        # Одежда
        Product(name='North Face Thermoball Eco', description='Утепленная куртка из переработанных материалов, легкая и водонепроницаемая', price=24990, category='Одежда', image_url='https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400', rating=4.6),
        Product(name='Canada Goose Expedition', description='Экспедиционная парка с гусиным пухом и защитой от -30°C', price=79990, category='Одежда', image_url='https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400', rating=4.8),
        Product(name='Lululemon Align 25', description='Леггинсы из супермягкой ткани Nulu, идеальны для йоги и тренировок', price=8990, category='Одежда', image_url='https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=400', rating=4.5),
        
        # Обувь
        Product(name='Nike Air Max 90', description='Классические кроссовки с видимой Air-подушкой и кожаным верхом', price=12990, category='Обувь', image_url='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400', rating=4.7),
        Product(name='Adidas Ultraboost 23', description='Беговые кроссовки с Boost подошвой и Primeknit верхом для комфорта', price=14990, category='Обувь', image_url='https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400', rating=4.5),
        Product(name='Timberland Premium Yellow', description='Культовые ботинки из натуральной кожи с водонепроницаемостью', price=19990, category='Обувь', image_url='https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=400', rating=4.6),
        
        # Игрушки
        Product(name='LEGO Star Wars Millennium Falcon', description='Набор 7545 деталей с Ханом Соло, Чубаккой и минифигурками персонажей', price=24990, category='Игрушки', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.9),
        Product(name='Play-Doh Kitchen Creations', description='Набор для лепки с инструментами, формочками и яркими цветами для детей от 3 лет', price=2990, category='Игрушки', image_url='https://images.unsplash.com/photo-1563904092230-7ec217b65fe2?w=400', rating=4.4),
        Product(name='Funko Pop! Marvel Avengers', description='Коллекционная фигурка Железного человека из фильма Мстители', price=1990, category='Игрушки', image_url='https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400', rating=4.3),
        
        # Книги
        Product(name='1984 — Джордж Оруэлл', description='Антиутопический роман о тоталитарном обществе и контроле над мышлением', price=590, category='Книги', image_url='https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400', rating=4.8),
        Product(name='Мастер и Маргарита — М. Булгаков', description='Классика русской литературы о дьяволе в Москве 1930-х годов', price=690, category='Книги', image_url='https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400', rating=4.9),
        Product(name='Atomic Habits — James Clear', description='Практическое руководство по построению полезных привычек и личной эффективности', price=990, category='Книги', image_url='https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=400', rating=4.7),
        
        # Автотовары
        Product(name='Xiaomi Mi Electric Scooter 4 Pro', description='Электросамокат с максимальной скоростью 25 км/ч и запасом хода до 45 км', price=44990, category='Автотовары', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.5),
        Product(name='Playseat Evolution Pro', description='Гоночный симулятор с лицензией F1 для игровых рулей и педалей', price=54990, category='Автотовары', image_url='https://images.unsplash.com/photo-1563904092230-7ec217b65fe2?w=400', rating=4.4),
        Product(name='Nextbase 522GW', description='Видеорегистратор с 4K, GPS и функцией экстренной записи', price=14990, category='Автотовары', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        
        # Музыкальные инструменты
        Product(name='Yamaha P-225', description='Компактное цифровое пианино с 88 клавишами и встроенными динамиками', price=44990, category='Музыкальные инструменты', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.6),
        Product(name='Fender Player Stratocaster', description='Электрогитара с классическим звуком и удобным грифом', price=44990, category='Музыкальные инструменты', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.7),
        Product(name='Roland TD-17KVX', description='Электронная ударная установка для домашних занятий и выступлений', price=89990, category='Музыкальные инструменты', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.5),
        
        # Сад и огород
        Product(name='Einhell GE-CC 18 Li', description='Аккумуляторный триммер для газона с телескопической ручкой', price=8990, category='Сад и огород', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.2),
        Product(name='Karcher K5 Premium', description='Мойка высокого давления 145 бар для автомобилей и дома', price=29990, category='Сад и огород', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.6),
        
        # Здоровье
        Product(name='Omron M3 Intellisense', description='Автоматический тонометр с технологией Intellisense и памятью', price=3990, category='Здоровье', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.4),
        Product(name='Xiaomi Mi Smart Body Composition Scale', description='Умные весы с анализом состава тела и синхронизацией с приложением', price=2990, category='Здоровье', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        Product(name='Philips Sonicare DiamondClean', description='Электрическая зубная щетка с технологией Sonic и датчиком давления', price=8990, category='Здоровье', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.5),
        
        # Продукты питания
        Product(name='Шоколад Lindt Excellence 85%', description='Тёмный швейцарский шоколад с высоким содержанием какао', price=590, category='Продукты питания', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.6),
        Product(name='Кофе Lavazza Crema e Aroma 1кг', description='Итальянский кофе в зёрнах средней обжарки для эспрессо', price=1990, category='Продукты питания', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.5),
        
        # Бытовая техника
        Product(name='Dyson Air Purifier', description='Очиститель воздуха с фильтрацией HEPA и LCD дисплеем', price=54990, category='Бытовая техника', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.6),
        Product(name='Xiaomi Mi Air Purifier 4 Pro', description='Очиститель воздуха с HEPA фильтром и тихой работой', price=14990, category='Бытовая техника', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        Product(name='Xiaomi Mi Smart Roborock S7', description='Робот-пылесос с ультразвуковой системой мытья пола', price=29990, category='Бытовая техника', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.5),
        
        # Телевизоры
        Product(name='Samsung OLED 65" S95C', description='OLED телевизор 65" с 4K, Dolby Atmos и Gaming Hub', price=249990, category='Телевизоры', image_url='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400', rating=4.8),
        Product(name='LG C3 55" OLED', description='OLED телевизор 55" с webOS 23, Game Optimizer и Dolby Vision', price=119990, category='Телевизоры', image_url='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400', rating=4.7),
        Product(name='Sony A95K 65" QD-OLED', description='QD-OLED телевизор с Google TV и Acoustic Surface Audio+', price=199990, category='Телевизоры', image_url='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400', rating=4.9),
        
        # Компьютеры и комплектующие
        Product(name='NVIDIA GeForce RTX 4090', description='Игровая видеокарта с 24GB GDDR6X и Ada Lovelace архитектурой', price=159990, category='Компьютеры', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.9),
        Product(name='AMD Ryzen 9 7950X', description='Процессор 16 ядер, 32 потока, 5.7GHz максимальная частота', price=44990, category='Компьютеры', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.8),
        Product(name='Corsair Dominator Platinum 32GB', description='Оперативная память DDR5 6000MHz для игровых ПК', price=14990, category='Компьютеры', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.6),
        
        # Смарт-колонки
        Product(name='Amazon Echo Dot 5', description='Умная колонка с Alexa, LED часами и улучшенным звуком', price=5990, category='Умный дом', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.4),
        Product(name='Apple HomePod Mini', description='Компактная колонка с Siri, пространственным звуком и Thread', price=9990, category='Умный дом', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.5),
        Product(name='Sonos One SL', description='Премиальная колонка с AirPlay 2 и голосовым управлением', price=14990, category='Умный дом', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.7),
        
        # Категория "Другое"
        Product(name='Polaroid Now+', description='Мгновенная камера с Bluetooth и набором цветных фильтров', price=8990, category='Другое', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        Product(name='Instant Pot Duo 7-in-1', description='Мультиварка с функциями скороварки, йогуртницы иSous Vide', price=12990, category='Другое', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.5),
        
        # Дополнительные товары - Смартфоны
        Product(name='iPhone 15', description='Смартфон с Dynamic Island, A16 Bionic и улучшенной камерой', price=89990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400', rating=4.5),
        Product(name='Samsung Galaxy A54', description='Среднебюджетный смартфон с 6.5" AMOLED и 50МП камерой', price=34990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400', rating=4.2),
        Product(name='Xiaomi Redmi Note 12 Pro', description='Народный смартфон с 108МП камерой и 120W зарядкой', price=29990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400', rating=4.3),
        Product(name='Google Pixel 7a', description='Смартфон среднего класса с Tensor G2 и отличной камерой', price=39990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400', rating=4.4),
        Product(name='OPPO Find X6 Pro', description='Флагман с камерой Hasselblad и Snapdragon 8 Gen 2', price=79990, category='Смартфоны', image_url='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400', rating=4.5),
        
        # Дополнительные товары - Ноутбуки
        Product(name='MacBook Air 15', description='Тонкий ноутбук с M2, 15.3" Liquid Retina и до 18ч автономности', price=169990, category='Ноутбуки', image_url='https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400', rating=4.7),
        Product(name='HP Spectre x360', description='Трансформер с OLED дисплеем, Intel Core i7 и сенсорным экраном', price=129990, category='Ноутбуки', image_url='https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400', rating=4.4),
        Product(name='Acer Predator Helios 18', description='Игровой ноутбук с RTX 4090, Intel i9 и 240Hz Mini-LED', price=249990, category='Ноутбуки', image_url='https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=400', rating=4.6),
        Product(name='Microsoft Surface Laptop 5', description='Ультрабук с PixelSense дисплеем и Alcantara корпусом', price=119990, category='Ноутбуки', image_url='https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400', rating=4.4),
        
        # Дополнительные товары - Наушники
        Product(name='Sennheiser Momentum 4', description='Премиальные наушники с 60ч работы и адаптивным ANC', price=34990, category='Наушники', image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400', rating=4.6),
        Product(name='Beats Studio Pro', description='Наушники с пространственным звуком и 40ч работы', price=26990, category='Наушники', image_url='https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=400', rating=4.3),
        Product(name='Shure Aonic 50', description='Наушники студийного качества с ANC и 20ч работы', price=32990, category='Наушники', image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400', rating=4.5),
        
        # Дополнительные товары - Телевизоры
        Product(name='TCL C845 55" Mini LED', description='55" Mini LED 4K с Google TV и Dolby Vision IQ', price=79990, category='Телевизоры', image_url='https://images.unsplash.com/photo-1461151304267-38535e780c79?w=400', rating=4.4),
        Product(name='Hisense U8HQ 65" Mini LED', description='65" Mini LED 4K с 144Hz и Game Mode Pro', price=109990, category='Телевизоры', image_url='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400', rating=4.5),
        Product(name='Samsung The Frame 55"', description='Телевизор-картина с QLED и Art Mode', price=89990, category='Телевизоры', image_url='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400', rating=4.6),
        
        # Дополнительные товары - Игровые консоли
        Product(name='PlayStation 5 Slim', description='Уменьшенная версия PS5 с 1ТБ SSD и поддержкой 8K', price=44990, category='Игровые консоли', image_url='https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400', rating=4.7),
        Product(name='Nintendo Switch Lite', description='Компактная портативная консоль в 5 цветах', price=19990, category='Игровые консоли', image_url='https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400', rating=4.4),
        
        # Дополнительные товары - Фото и видео
        Product(name='Canon EOS R50', description='Беззеркалка начального уровня с 4K и Dual Pixel AF', price=59990, category='Фото и видео', image_url='https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400', rating=4.4),
        Product(name='Insta360 X4', description='Панорамная камера 8K с AI-редактором и компактным корпусом', price=44990, category='Фото и видео', image_url='https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400', rating=4.6),
        Product(name='Sony ZV-E1', description='Полнокадровая камера для блогеров с 4K 120fps', price=149990, category='Фото и видео', image_url='https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400', rating=4.7),
        
        # Дополнительные товары - Умные часы
        Product(name='Apple Watch Series 9', description='Смарт-часы с S9 SiP, Double Tap и 18ч автономности', price=34990, category='Умные часы', image_url='https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400', rating=4.6),
        Product(name='Huawei Watch GT 4', description='Смарт-часы с 14 днями автономности и GPS', price=19990, category='Умные часы', image_url='https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400', rating=4.3),
        Product(name='Amazfit GTR 4', description='Спортивные часы с 双频GPS и 14 дней автономности', price=8990, category='Умные часы', image_url='https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400', rating=4.2),
        
        # Дополнительные товары - Косметика
        Product(name='Shiseido Vital Perfection', description='Омолаживающий крем с технологией ReNeura', price=8990, category='Косметика', image_url='https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400', rating=4.4),
        Product(name='Charlotte Tilbury Pillow Talk', description='Помада с эффектом увеличения губ и увлажнением', price=2990, category='Косметика', image_url='https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400', rating=4.7),
        Product(name='The Ordinary Glycolic Acid', description='Пилинг с гликолевой кислотой 7% для обновления кожи', price=1290, category='Косметика', image_url='https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400', rating=4.3),
        
        # Дополнительные товары - Парфюмерия
        Product(name='Yves Saint Laurent Y EDP', description='Мужской аромат с бергамотом, имбирем и амброй', price=7990, category='Парфюмерия', image_url='https://images.unsplash.com/photo-1541643600914-78b084683601?w=400', rating=4.5),
        Product(name='Jo Malone English Pear', description='Аромат с грушей, фрезией и кедром', price=6990, category='Парфюмерия', image_url='https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400', rating=4.6),
        Product(name='Versace Crystal Noir', description='Женский аромат с нотами бергамота, имбиря и сандала', price=5990, category='Парфюмерия', image_url='https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400', rating=4.4),
        
        # Дополнительные товары - Одежда
        Product(name='Patagonia Nano Puff', description='Пуховый жилет из переработанных материалов', price=8990, category='Одежда', image_url='https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400', rating=4.5),
        Product(name='Carhartt WIP Chore', description='Рабочая куртка из плотного хлопка с подкладкой', price=12990, category='Одежда', image_url='https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400', rating=4.4),
        Product(name='Uniqlo Heattech', description='Термобелье с технологией Heattech для холодной погоды', price=2990, category='Одежда', image_url='https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400', rating=4.3),
        
        # Дополнительные товары - Обувь
        Product(name='New Balance 574', description='Классические кроссовки из замши и сетки', price=8990, category='Обувь', image_url='https://images.unsplash.com/photo-1539185441755-769473a23570?w=400', rating=4.5),
        Product(name='Converse Chuck Taylor', description='Классические конверсы с Canvas верхом', price=5990, category='Обувь', image_url='https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=400', rating=4.6),
        Product(name='Vans Old Skool', description='Скейтбордические кроссовки с замшевым верхом', price=6990, category='Обувь', image_url='https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400', rating=4.5),
        
        # Дополнительные товары - Игрушки
        Product(name='LEGO Batman Movie Batcave', description='Набор 3492 деталей с Бэтменом и Джокером', price=19990, category='Игрушки', image_url='https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400', rating=4.8),
        Product(name='Nintendo Switch Pro Controller', description='Проводной контроллер с Haptic Feedback', price=6990, category='Игрушки', image_url='https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400', rating=4.5),
        Product(name='NERF Elite 2.0', description='Бластер для детей с дальностью до 27 метров', price=2990, category='Игрушки', image_url='https://images.unsplash.com/photo-1563904092230-7ec217b65fe2?w=400', rating=4.2),
        
        # Дополнительные товары - Книги
        Product(name='Sapiens — Yuval Noah Harari', description='Краткая история человечества от возникновения до будущего', price=790, category='Книги', image_url='https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=400', rating=4.8),
        Product(name='Гарри Поттер — Дж.К. Роулинг', description='Полное издание серии из 7 книг', price=4990, category='Книги', image_url='https://images.unsplash.com/photo-1618666012174-83b441c0bc76?w=400', rating=4.9),
        Product(name='Метро 2033 — Д. Глуховский', description='Постапокалиптический роман о выживании в метро', price=590, category='Книги', image_url='https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400', rating=4.6),
        
        # Дополнительные товары - Спорт и фитнес
        Product(name='Peloton Bike+', description='Велотренажер с 23.8" HD экраном и Live классами', price=149990, category='Спорт и фитнес', image_url='https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400', rating=4.5),
        Product(name='Whoop 4.0', description='Фитнес-браслет с мониторингом восстановления и нагрузки', price=24990, category='Спорт и фитнес', image_url='https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400', rating=4.2),
        Product(name='Hyperice Hypervolt', description='Массажный пистолет с 3 скоростями и 5 насадками', price=29990, category='Спорт и фитнес', image_url='https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400', rating=4.5),
        
        # Дополнительные товары - Для дома
        Product(name='Ring Video Doorbell 4', description='Умный дверной звонок с 1080p и Pre-Roll', price=14990, category='Для дома', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        Product(name='eufy Security Video Doorbell', description='Дверной звонок 2K с локальным хранилищем', price=8990, category='Для дома', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.2),
        Product(name='Philips Hue Go', description='Портативная умная лампа с 24ч работы от батареи', price=5990, category='Для дома', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        
        # Дополнительные товары - Бытовая техника
        Product(name='Ninja Foodi 10-in-1', description='Мультиварка с функциями аэрогриля и йогуртницы', price=19990, category='Бытовая техника', image_url='https://images.unsplash.com/photo-1585515320310-2595e8c5b600?w=400', rating=4.5),
        Product(name='Beko SteamFresh', description='Паровой шкаф для освежения одежды без стирки', price=24990, category='Бытовая техника', image_url='https://images.unsplash.com/photo-1585515320310-2595e8c5b600?w=400', rating=4.1),
        Product(name='Dyson Hot+Cool', description='Обогреватель-вентилятор с очисткой воздуха', price=44990, category='Бытовая техника', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.4),
        
        # Дополнительные товары - Аксессуары
        Product(name='Anker 737 Power Bank', description='Пауэрбанк 24000mAh с 140W и Display', price=8990, category='Аксессуары', image_url='https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400', rating=4.6),
        Product(name='Sony WF-1000XM5', description='TWS наушники с ANC и 8ч работы', price=24990, category='Аксессуары', image_url='https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400', rating=4.5),
        Product(name='Apple Pencil Pro', description='Стилус для iPad с тактильной отдачей', price=9990, category='Аксессуары', image_url='https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400', rating=4.6),
        
        # Дополнительные товары - Здоровье
        Product(name='Withings Body Scan', description='Умные весы с ЭКГ и анализом артериальной stiffness', price=29990, category='Здоровье', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.4),
        Product(name='Oura Ring Gen 3', description='Умное кольцо с мониторингом сна и восстановления', price=29990, category='Здоровье', image_url='https://images.unsplash.com/photo-1617347454431-f49d7ff5c3b1?w=400', rating=4.5),
        Product(name='Medisana BU 540', description='Тонометр с Bluetooth и голосовым сопровождением', price=4990, category='Здоровье', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.2),
        
        # Дополнительные товары - Продукты питания
        Product(name='Вино Chateau Margaux 2015', description='Красное вино Bordeaux Premier Grand Cru', price=89990, category='Продукты питания', image_url='https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=400', rating=4.8),
        Product(name='Чай Mariage Freres', description='Французский чай с ароматом Мадагаскара', price=1290, category='Продукты питания', image_url='https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400', rating=4.5),
        Product(name='Оливковое масло extra virgin', description='Итальянское оливковое масло первого отжима 1л', price=1990, category='Продукты питания', image_url='https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', rating=4.4),
        
        # Дополнительные товары - Автотовары
        Product(name='Tesla Cyber Whistle', description='Сувенирный свисток в стиле Cybertruck', price=990, category='Автотовары', image_url='https://images.unsplash.com/photo-1563904092230-7ec217b65fe2?w=400', rating=4.1),
        Product(name='Garmin Dash Cam 67W', description='Видеорегистратор 4K с голосовым управлением', price=16990, category='Автотовары', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.4),
        Product(name='Anker Roav Dash Cam', description='Видеорегистратор 1080p с ночным режимом', price=5990, category='Автотовары', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.2),
        
        # Дополнительные товары - Умный дом
        Product(name='Google Nest Doorbell', description='Умный дверной звонок с HDR и Night Vision', price=12990, category='Умный дом', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        Product(name='Aqara Smart Home Kit', description='Набор датчиков для умного дома с хабом', price=9990, category='Умный дом', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.2),
        Product(name='Philips Hue Go White', description='Умная лампа с регулировкой яркости и цвета', price=4990, category='Умный дом', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        
        # Дополнительные товары - Дроны
        Product(name='DJI Mavic 3 Pro', description='Профессиональный дрон с тройной камерой Hasselblad', price=209990, category='Дроны', image_url='https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=400', rating=4.8),
        Product(name='Autel EVO Nano+', description='Компактный дрон 249g с 50МП и 3-осевой стабилизацией', price=69990, category='Дроны', image_url='https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=400', rating=4.5),
        Product(name='DJI Inspire 3', description='Профессиональный кинематографический дрон', price=299990, category='Дроны', image_url='https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=400', rating=4.9),
        
        # Дополнительные товары - Компьютеры
        Product(name='AMD Ryzen 7 7800X3D', description='Игровой процессор с 3D V-Cache, 8 ядер', price=33990, category='Компьютеры', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.8),
        Product(name='Samsung 990 Pro 2TB', description='NVMe SSD PCIe 4.0 со скоростью 7450МБ/с', price=19990, category='Компьютеры', image_url='https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=400', rating=4.7),
        Product(name='Intel Core i9-14900K', description='Процессор 24 ядра, 32 потока, 6.0GHz', price=54990, category='Компьютеры', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.7),
        
        # Дополнительные товары - Планшеты
        Product(name='iPad 10', description='Планшет с 10.9" дисплеем, A14 Bionic и Touch ID', price=59990, category='Планшеты', image_url='https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400', rating=4.5),
        Product(name='Samsung Galaxy Tab A9+', description='Планшет 11" с 4 динамиками и S Pen', price=34990, category='Планшеты', image_url='https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400', rating=4.2),
        Product(name='Xiaomi Pad 6', description='Планшет с 11" 2.8K дисплеем и Snapdragon 870', price=29990, category='Планшеты', image_url='https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400', rating=4.4),
        
        # Дополнительные товары - Электронные книги
        Product(name='Amazon Kindle Scribe', description='Электронная книга с 10.2" и стилусом для заметок', price=39990, category='Электронные книги', image_url='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400', rating=4.4),
        Product(name='PocketBook Era', description='Электронная книга с 7" и водозащитой IPX8', price=19990, category='Электронные книги', image_url='https://images.unsplash.com/photo-1553756513-4037891615cd?w=400', rating=4.3),
        Product(name='Amazon Kindle 2024', description='Обновленная базовая модель Kindle с подсветкой', price=9990, category='Электронные книги', image_url='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400', rating=4.3),
        
        # Дополнительные товары - Музыкальные инструменты
        Product(name='Yamaha HS8', description='Студийные мониторы 8" для профессионального звука', price=24990, category='Музыкальные инструменты', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.6),
        Product(name='Native Instruments Komplete 15', description='Музыкальный софт с 90+ инструментами и эффектами', price=29990, category='Музыкальные инструменты', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.7),
        Product(name='Arturia MiniLab 3', description='Компактный MIDI-контроллер с 25 клавишами', price=8990, category='Музыкальные инструменты', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.5),
        
        # Дополнительные товары - Сад и огород
        Product(name='Greenworks 60V', description='Аккумуляторная газонокосилка 60V без проводов', price=24990, category='Сад и огород', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        Product(name='Fiskars Smart Trim', description='Аккумуляторные ножницы для кустов с телескопической ручкой', price=6990, category='Сад и огород', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.1),
        Product(name='Gardena Smart System', description='Умная система полива с датчиками и таймером', price=12990, category='Сад и огород', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.3),
        
        # Дополнительные товары - Другое
        Product(name='Rimowa Original Cabin', description='Чемодан алюминиевый 55cm с TSA замком', price=69990, category='Другое', image_url='https://images.unsplash.com/photo-1565026057447-bc90a3dceb87?w=400', rating=4.7),
        Product(name='Peak Design Travel Tripod', description='Компактный штатив из углеродного волокна', price=24990, category='Другое', image_url='https://images.unsplash.com/photo-1519638831568-d9897f54ed69?w=400', rating=4.5),
        Product(name='Solo Stove Bonfire', description='Переносной костер без дыма для дачи', price=9990, category='Другое', image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', rating=4.4),
    ]
    
    for p in products:
        db.session.add(p)
    db.session.commit()
