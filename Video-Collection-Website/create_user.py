from werkzeug.security import generate_password_hash
from app import app, db, User
import argparse

parser = argparse.ArgumentParser(description='Criar um novo usuário')
parser.add_argument('--name', help='Name', required=True)
parser.add_argument('--username', help='Username', required=True)
parser.add_argument('--password', help='Password', required=True)

args = parser.parse_args()
user_name = args.name
user_username = args.username
user_password = args.password

pw_hash = generate_password_hash(user_password)

with app.app_context():
    new_user = User(name=user_name, username=user_username, password_hash=pw_hash)
    db.session.add(new_user)
    db.session.commit()
    print(f'Usuário {user_username} criado com sucesso')
