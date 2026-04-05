import os
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Product, UserAction, Review, init_db
from recommender import recommender

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
init_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ADMIN_EMAILS = ['bogdansilov@gmail.com', 'bogdansilov10@gmail.com']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/upload', methods=['POST'])
@login_required
def upload_image():
    if not current_user.is_admin and current_user.email not in ADMIN_EMAILS:
        return jsonify({'error': 'Access denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{secrets.token_hex(16)}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({
            'message': 'File uploaded',
            'url': f"/uploads/{filename}"
        })
    
    return jsonify({'error': 'Invalid file type'}), 400
login_manager.init_app(app)
login_manager.login_view = 'login'

ADMIN_EMAILS = ['bogdansilov@gmail.com', 'bogdansilov10@gmail.com']

def is_admin():
    return current_user.is_authenticated and current_user.email in ADMIN_EMAILS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    recommender.refresh()
    category = request.args.get('category')
    search = request.args.get('search', '').strip()
    
    query = Product.query
    
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%'),
                Product.category.ilike(f'%{search}%')
            )
        )
    
    if category:
        query = query.filter_by(category=category)
    
    products = query.order_by(Product.rating.desc()).all()
    recommendations = []
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]
    
    if current_user.is_authenticated:
        recommendations = recommender.get_recommendations(current_user.id, n=6)
    
    return render_template('index.html', products=products, recommendations=recommendations, categories=categories, current_category=category, search_query=search)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    recommender.refresh()
    similar = recommender.get_similar_products(product_id)
    
    if current_user.is_authenticated:
        action = UserAction.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id, 
            action_type='view'
        ).first()
        
        if not action:
            action = UserAction(
                user_id=current_user.id,
                product_id=product_id,
                action_type='view'
            )
            db.session.add(action)
            db.session.commit()
    
    return render_template('product.html', product=product, similar=similar)


@app.route('/api/products/<int:product_id>/action', methods=['POST'])
@login_required
def product_action(product_id):
    data = request.get_json()
    action_type = data.get('action_type')
    rating = data.get('rating')
    
    if action_type not in ['view', 'like', 'buy']:
        return jsonify({'error': 'Invalid action type'}), 400
    
    action = UserAction.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
        action_type=action_type
    ).first()
    
    if action:
        if action_type == 'like':
            db.session.delete(action)
            db.session.commit()
            return jsonify({'status': 'removed'})
        return jsonify({'status': 'already_exists'})
    
    action = UserAction(
        user_id=current_user.id,
        product_id=product_id,
        action_type=action_type,
        rating=rating
    )
    db.session.add(action)
    db.session.commit()
    
    if action_type in ['like', 'buy']:
        update_product_rating(product_id)
    
    return jsonify({'status': 'added'})


def update_product_rating(product_id):
    actions = UserAction.query.filter_by(
        product_id=product_id, 
        action_type='buy'
    ).all()
    
    if actions:
        avg_rating = sum(a.rating if a.rating else 5 for a in actions) / len(actions)
        product = Product.query.get(product_id)
        product.rating = round(avg_rating, 1)
        db.session.commit()


@app.route('/api/recommendations')
@login_required
def get_recommendations():
    recommendations = recommender.get_recommendations(current_user.id, n=10)
    return jsonify([p.to_dict() for p in recommendations])


@app.route('/profile')
@login_required
def profile():
    actions = UserAction.query.filter_by(user_id=current_user.id).order_by(
        UserAction.created_at.desc()
    ).all()
    
    stats = {
        'views': sum(1 for a in actions if a.action_type == 'view'),
        'likes': sum(1 for a in actions if a.action_type == 'like'),
        'buys': sum(1 for a in actions if a.action_type == 'buy')
    }
    
    return render_template('profile.html', actions=actions, stats=stats)


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    return jsonify({'message': 'Registration successful', 'user': {'id': user.id, 'username': user.username}})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('username')
    password = data.get('password')
    
    print(f"Login attempt: username={identifier}, password={password}")
    
    user = User.query.filter(
        db.or_(
            User.username == identifier,
            User.email == identifier
        )
    ).first()
    
    print(f"Found user: {user.username if user else None}, email: {user.email if user else None}")
    
    if not user:
        print("User not found")
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.check_password(password):
        print("Wrong password")
        return jsonify({'error': 'Invalid username or password'}), 401
    
    login_user(user)
    print("Login successful")
    return jsonify({'message': 'Login successful', 'user': {'id': user.id, 'username': user.username}})


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})


@app.route('/api/profile')
@login_required
def get_profile():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email
    })


@app.route('/api/profile/actions')
@login_required
def get_profile_actions():
    actions = UserAction.query.filter_by(user_id=current_user.id).order_by(
        UserAction.created_at.desc()
    ).all()
    
    return jsonify([{
        'id': a.id,
        'product_id': a.product_id,
        'product_name': a.product.name,
        'action_type': a.action_type,
        'rating': a.rating,
        'created_at': a.created_at.isoformat()
    } for a in actions])


@app.route('/api/products/<int:product_id>/reviews', methods=['GET'])
def get_reviews(product_id):
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reviews])


@app.route('/api/products/<int:product_id>/reviews', methods=['POST'])
@login_required
def create_review(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    rating = data.get('rating')
    text = data.get('text', '')
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    existing = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.rating = rating
        existing.text = text
        db.session.commit()
    else:
        review = Review(
            user_id=current_user.id,
            product_id=product_id,
            rating=rating,
            text=text
        )
        db.session.add(review)
        db.session.commit()
    
    update_product_rating(product_id)
    update_product_rating_from_reviews(product_id)
    product = Product.query.get(product_id)
    
    return jsonify({
        'message': 'Review saved',
        'product_rating': product.rating,
        'review': existing.to_dict() if existing else review.to_dict()
    }), 201


def update_product_rating_from_reviews(product_id):
    reviews = Review.query.filter_by(product_id=product_id).all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        product = Product.query.get(product_id)
        product.rating = round(avg_rating, 1)
        db.session.commit()


@app.route('/api/products/<int:product_id>/reviews/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(product_id, review_id):
    review = Review.query.filter_by(id=review_id, user_id=current_user.id).first_or_404()
    db.session.delete(review)
    db.session.commit()
    update_product_rating_from_reviews(product_id)
    product = Product.query.get(product_id)
    return jsonify({
        'message': 'Review deleted',
        'product_rating': product.rating if product else 0
    })


@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin and current_user.email not in ADMIN_EMAILS:
        return redirect(url_for('index'))
    
    users = User.query.all()
    products = Product.query.all()
    actions = UserAction.query.order_by(UserAction.created_at.desc()).limit(100).all()
    
    stats = {
        'total_users': len(users),
        'total_products': len(products),
        'total_actions': UserAction.query.count(),
        'total_views': UserAction.query.filter_by(action_type='view').count(),
        'total_likes': UserAction.query.filter_by(action_type='like').count(),
        'total_buys': UserAction.query.filter_by(action_type='buy').count(),
    }
    
    return render_template('admin.html', users=users, products=products, actions=actions, stats=stats)


@app.route('/admin/product/add', methods=['POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin and current_user.email not in ADMIN_EMAILS:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    category = data.get('category')
    image_url = data.get('image_url', '')
    
    if not all([name, description, price, category]):
        return jsonify({'error': 'All fields required'}), 400
    
    product = Product(
        name=name,
        description=description,
        price=float(price),
        category=category,
        image_url=image_url,
        rating=0.0
    )
    db.session.add(product)
    db.session.commit()
    
    return jsonify({'message': 'Product added', 'product': product.to_dict()})


@app.route('/admin/product/<int:product_id>', methods=['DELETE'])
@login_required
def admin_delete_product(product_id):
    if not current_user.is_admin and current_user.email not in ADMIN_EMAILS:
        return jsonify({'error': 'Access denied'}), 403
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted'})


@app.route('/admin/product/<int:product_id>', methods=['PUT'])
@login_required
def admin_update_product(product_id):
    if not current_user.is_admin and current_user.email not in ADMIN_EMAILS:
        return jsonify({'error': 'Access denied'}), 403
    
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if data.get('name'):
        product.name = data['name']
    if data.get('description'):
        product.description = data['description']
    if data.get('price') is not None:
        product.price = float(data['price'])
    if data.get('category'):
        product.category = data['category']
    if data.get('image_url') is not None:
        product.image_url = data['image_url']
    if data.get('rating') is not None:
        product.rating = float(data['rating'])
    
    db.session.commit()
    
    return jsonify({'message': 'Product updated', 'product': product.to_dict()})
    
    return jsonify({'message': 'Product updated', 'product': product.to_dict()})


@app.route('/admin/user/<int:user_id>', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin and current_user.email not in ADMIN_EMAILS:
        return jsonify({'error': 'Access denied'}), 403


@app.route('/api/ensure-admins', methods=['POST'])
def ensure_admins():
    ADMIN_USERS = {
        'bogdansilov@gmail.com': {'username': 'admin', 'password': 'admin123'},
        'bogdansilov10@gmail.com': {'username': 'bogdan', 'password': '1234'},
    }
    
    for email, data in ADMIN_USERS.items():
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=data['username'], email=email)
            user.set_password(data['password'])
            db.session.add(user)
        else:
            user.set_password(data['password'])
    
    db.session.commit()
    return jsonify({'message': 'Admins ready'})


@app.route('/debug-users')
def debug_users():
    users = User.query.all()
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'password_admin123': u.check_password('admin123'),
            'password_1234': u.check_password('1234'),
        })
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
