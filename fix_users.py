from app import app, db
from models import User

with app.app_context():
    db.create_all()
    
    emails = [
        ('bogdansilov@gmail.com', 'admin', 'admin123'),
        ('bogdansilov10@gmail.com', 'bogdan', '1234')
    ]
    
    for email, username, password in emails:
        u = User.query.filter_by(email=email).first()
        if not u:
            u = User(username=username, email=email)
            u.set_password(password)
            db.session.add(u)
            print('Created: ' + email)
        else:
            u.set_password(password)
            print('Updated: ' + email)
    
    db.session.commit()
    
    for u in User.query.all():
        print('User: ' + u.username + ' ' + u.email)
        print('  admin123: ' + str(u.check_password('admin123')))
        print('  1234: ' + str(u.check_password('1234')))
