from app import app
import os
from database import db
from flask_migrate import Migrate

if __name__ == '__main__':
    db.init_app(app)
    conexao = 'postgresql://meubanco.sql'

    app.config['SECRET_KEY'] = "palavra-secreta"
    app.config['SQLALCHEMY_DATABASE_URI'] = conexao
    app.config['SQLALCHEMY_TRACKMODIFICATIONS'] = False

    migrate = Migrate(app, db)

    port = int(os.getenv('PORT', default='5000'))
    app.run(host='0.0.0.0', port=port)