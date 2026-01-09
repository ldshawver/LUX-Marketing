import pytest
from werkzeug.security import generate_password_hash

from app import app, db
from models import User


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_login_accepts_email_identifier(client):
    user = User(
        username='luke',
        email='liuke@adiken.com',
        password_hash=generate_password_hash('supersecret')
    )
    db.session.add(user)
    db.session.commit()

    response = client.post(
        '/auth/login',
        data={'username': 'LiUkE@Adiken.com', 'password': 'supersecret'},
        follow_redirects=False
    )

    assert response.status_code == 302


def test_passwordless_account_shows_clear_message(client):
    user = User(username='sso-user', email='sso@example.com', password_hash=None)
    db.session.add(user)
    db.session.commit()

    response = client.post(
        '/auth/login',
        data={'username': 'sso@example.com', 'password': 'anything'},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"doesn&#39;t have a password set" in response.data


def test_login_form_copy_mentions_email():
    with open('templates/login.html', 'r', encoding='utf-8') as handle:
        content = handle.read()

    assert 'Username or Email' in content
    assert 'Enter your username or email' in content
