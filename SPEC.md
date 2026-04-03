# RecommendHub - Система рекомендаций товаров

## Концепция и Видение

Современная платформа рекомендаций товаров с персонализированным подходом. Интерфейс минималистичный, но функциональный — акцент на карточки товаров и умный движок рекомендаций, который учится на основе действий пользователя (просмотры, лайки, покупки).

## Дизайн-система

### Эстетика
Чистый e-commerce стиль с акцентом на продукты. Белый фон, яркие акценты, тени для глубины карточек.

### Цветовая палитра
- Primary: `#2563eb` (синий)
- Secondary: `#64748b` (серый)
- Accent: `#f59e0b` (оранжевый для рейтингов/избранного)
- Background: `#f8fafc`
- Surface: `#ffffff`
- Text: `#1e293b`
- Text muted: `#64748b`

### Типографика
- Заголовки: Inter, sans-serif
- Текст: Inter, sans-serif
- Моноширинный: JetBrains Mono (для цен)

### Анимации
- Hover на карточках: scale(1.02), transition 200ms
- Кнопки: opacity 0.9, transition 150ms
- Загрузка страниц: плавный fade-in

## Структура

### Страницы
1. **Главная** (`/`) — каталог товаров с рекомендациями для авторизованных
2. **Личный кабинет** (`/profile`) — история действий, профиль
3. **Авторизация** (`/login`, `/register`) — вход/регистрация
4. **Товар** (`/product/<id>`) — детальная страница товара

### Модели данных

```
User
├── id
├── username
├── email
├── password_hash
└── created_at

Product
├── id
├── name
├── description
├── price
├── category
├── image_url
├── rating
└── created_at

UserAction (для обучения)
├── id
├── user_id (FK)
├── product_id (FK)
├── action_type (view/like/buy)
├── rating (1-5, nullable)
└── created_at

Recommendation
├── id
├── user_id (FK)
├── product_id (FK)
├── score
└── created_at
```

## Функциональность

### Система рекомендаций (Content-Based)
1. TF-IDF векторизация описаний товаров
2. Косинусное сходство между товарами
3. Рекомендации на основе:
   - Просмотренных товаров (вес 1.0)
   - Лайкнутых товаров (вес 2.0)
   - Купленных товаров (вес 3.0)
4. Адаптивное обновление при новых действиях

### Личный кабинет
- Просмотр истории действий
- Статистика (количество просмотров, лайков, покупок)
- Избранное

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register` | POST | Регистрация |
| `/api/login` | POST | Вход |
| `/api/logout` | POST | Выход |
| `/api/products` | GET | Список товаров |
| `/api/products/<id>` | GET | Детали товара |
| `/api/products/<id>/action` | POST | Действие (view/like/buy) |
| `/api/recommendations` | GET | Персональные рекомендации |
| `/api/profile` | GET | Профиль пользователя |
| `/api/profile/actions` | GET | История действий |

## Технический стек

- **Backend**: Flask 3.x
- **Database**: SQLite (через SQLAlchemy)
- **Auth**: Flask-Login
- **ML**: scikit-learn (TF-IDF, cosine similarity)
- **Frontend**: Jinja2 templates + Tailwind CSS CDN
- **Password**: Werkzeug security
