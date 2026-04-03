from app import app, db, recommender
from models import Product

if __name__ == '__main__':
    print("Starting Recom...")
    print("Open: http://127.0.0.1:5000")
    
    with app.app_context():
        db.create_all()
        recommender.refresh()
        print(f"Products: {Product.query.count()}")
    
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
