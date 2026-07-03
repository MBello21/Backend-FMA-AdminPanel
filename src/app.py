import os
from flask import Flask
from flask_migrate import Migrate
from api.models import db
from api.routes import api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta


ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../dist/')

app = Flask(__name__)
# cambiar "*" por dominio exacto del front
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')  # Change this!
jwt = JWTManager(app)

db_url = os.getenv("DATABASE_URL")

if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        'postgres://', 'postgresql://')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db, compare_type=True)
db.init_app(app)

app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
