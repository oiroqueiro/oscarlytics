from portfolio import portfolio, db
from portfolio.models import Users


def create_user():
    u = Users(username='name', email='email@email.com')
    u.set_password('password')
    db.session.add(u)
    db.session.commit()


if __name__ == '__main__':
    portfolio.app_context().push()
    create_user()
