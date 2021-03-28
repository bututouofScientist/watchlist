from flask import Flask, url_for, render_template
app = Flask(__name__)


from flask_sqlalchemy import SQLAlchemy
import sys
import os
Win = sys.platform.startswith("win")
if Win:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/user/<name>")
def user_page(name):
    return "User:%s" % name


@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html"), 404


# 模板上下文处理函数
@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}


@app.route('/test')
def test_url_for():
    print(url_for("hello"))
    print(url_for("user_page", name="boyu"))
    print(url_for("user_page", name="zhouying"))
    print(url_for("test_url_for", num=2))
    return 'Test Page'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))



import click


# 自定义命令initdb,自动创建数据库表
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """initialize the database"""
    if drop:
        db.drop_all()
        click.echo("drop complete")
    db.create_all()
    click.echo('initialized database')


# 自定义命令forge，添加虚拟数据到数据库
@app.cli.command()
def forge():
    """Generate fake data"""
    db.create_all()

#  全局的两个变量移动到这个函数内
    name = 'Boyu'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m["title"], year=m["year"])
        db.session.add(movie)
    db.session.commit()
    click.echo("Done")








