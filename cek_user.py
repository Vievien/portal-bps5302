from app import app, db, User

with app.app_context():
    users = User.query.all()

    for u in users:
        print(u.id, u.username, u.password, u.role)