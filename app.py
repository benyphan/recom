from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Product, UserAction, Review, init_db
from recommender import recommender
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
init_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    login_user(user)
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
    product = Product.query.get(product_id)
    
    return jsonify({
        'message': 'Review saved',
        'product_rating': product.rating,
        'review': existing.to_dict() if existing else review.to_dict()
    }), 201


@app.route('/api/products/<int:product_id>/reviews/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(product_id, review_id):
    review = Review.query.filter_by(id=review_id, user_id=current_user.id).first_or_404()
    db.session.delete(review)
    db.session.commit()
    update_product_rating(product_id)
    product = Product.query.get(product_id)
    return jsonify({
        'message': 'Review deleted',
        'product_rating': product.rating if product else 0
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
