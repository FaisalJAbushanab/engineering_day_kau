from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.sql.expression import nullslast
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_marshmallow import Marshmallow

app = Flask(__name__)

ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SECRET_KEY'] = 'c9aafc85052059bcf8c42237bf291ae9295a294dcc707384b47d94b340bae26a'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['MAIL_SERVER'] = 'smtp.ionos.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True


else:
    app.debug = True
    app.config['SECRET_KEY'] = 'c9aafc85052059bcf8c42237bf291ae9295a294dcc707384b47d94b340bae26a'
#   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yilboziuuucmpj:f7c22115880b874cff646a60f4d81940159242a60c4e760defb193b123f24e93@ec2-50-17-255-120.compute-1.amazonaws.com:5432/dcjg9oq80q0h3v'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qkpbisijwohqrm:89247105548928c4ad710b14e92636b98207043586eec7363ff46ef179e1bbb3@ec2-34-194-14-176.compute-1.amazonaws.com:5432/d3k031h0jklro0'
    app.config['MAIL_SERVER'] = 'smtp.ionos.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_USERNAME'] = 'support@7alaqh.com'
app.config['MAIL_PASSWORD'] = '@Faisal00700'
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
from app import routes