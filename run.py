import requests

from app import app, db, recommender
from models import Product, User

ADMIN_USERS = {
    'bogdansilov@gmail.com': {'username': 'admin', 'password': 'admin123'},
    'bogdansilov10@gmail.com': {'username': 'bogdan', 'password': '1234'},
}

if __name__ == '__main__':
    print("Starting Recom...")
    print("Open: http://127.0.0.1:5000")
    
    with app.app_context():
        db.create_all()
        
        for email, data in ADMIN_USERS.items():
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(username=data['username'], email=email)
                user.set_password(data['password'])
                db.session.add(user)
                print(f"Admin created: {email} / {data['password']}")
        
        db.session.commit()
        recommender.refresh()
        print(f"Products: {Product.query.count()}")
    
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
