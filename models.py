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
    ]
    
    for p in products:
        db.session.add(p)
    db.session.commit()
