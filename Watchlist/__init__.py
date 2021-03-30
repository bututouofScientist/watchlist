import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# SQLite URI compatible
Win = sys.platform.startswith("win")
if Win:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'qwer')
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE','data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader  # 实现用户加载回调函数
def load_user(user_id):  # 接收用户id作为参数
    from Watchlist.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'login'
# login_manager.login_message = 'Your custom message'


# 模板上下文处理函数
@app.context_processor
def inject_user():  # 函数名可以随意修改
    from Watchlist.models import User
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}


from Watchlist import views, errors, commands