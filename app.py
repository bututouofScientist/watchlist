from flask import Flask, url_for, render_template, flash, request, redirect
app = Flask(__name__)
app.config['SECRET_KEY'] = "qwer"

# 初始化flask_sqlalchemy
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

#  初始化flask-login
from flask_login import LoginManager,login_required,current_user

login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = 'login'

@login_manager.user_loader  # 实现用户加载回调函数
def load_user(user_id):  # 接收用户id作为参数
    user = User.query.get(int(user_id))
    return user


@app.route('/', methods=['GET', 'POST'])
def index():
    # 假设是get请求，直接重定向主页；
    # 假如是post请求且表单验证通过，写入数据库，重定向主页；假设验证不通过，提示错误，重定向主页
    if request.method == 'POST':  # 如果是post方法
        if not current_user.is_authenticated:
            return redirect(url_for("index"))
        title = request.form.get('title')  # 通过request表单获取title值
        year = request.form.get('year')  # 通过request表单获取year值
        if not title or not year or len(title) > 60 or len(year) > 4:  # 如果任一个变量输入有误
            flash('Invalid input')  # 提示错误信息
            return redirect(url_for("index"))  # 重定向主页
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加数据库会话
        db.session.commit()  # 提交数据库会话
        flash("Item created")  # 提示成功信息
        return redirect(url_for("index"))  # 重定向主页
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/user/<name>")
def user_page(name):
    return "User:%s" % name


@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html"), 404


@app.route("/movie/edit/<int:movie_id>", methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == "POST":  # 处理编辑表单的请求
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(title) > 60 or len(year) > 4:
            flash("Invalid input")
            return redirect(url_for("edit", movie_id=movie_id))
        movie.title = title    # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash("Item updated")
        return redirect(url_for("index"))
    return render_template("edit.html", movie=movie)


@app.route("/movie/delete/<int:movie_id>", methods=["POST"])  # 限定只接受post请求
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Item Deleted")
    return redirect(url_for("index"))


from flask_login import login_user


@app.route("/login",methods=["GET","POST"])
def login():  # 处理登录的视图函数
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash('Invalid input')
            return redirect(url_for("login"))
        user = User.query.first()
    #     验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 用user用户登录
            flash("Login success")  # 提示登录成功
            return redirect(url_for("index"))  # 重定向主页
        flash("Invalid username or password")
        return redirect(url_for("login"))
    return render_template("login.html")


from flask_login import logout_user


@app.route("/logout", methods=["GET"])
def logout():  # 处理注销的视图函数
    logout_user()
    flash("Logout success")  # 提示注销成功
    return redirect(url_for("index"))  # 重定向主页


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')





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


from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


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


@app.cli.command()
@click.option("--username", prompt=True, help='The username used to login in')
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login in')
def admin(username, password):
    """create user"""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo("Updating user...")
        user.username = username
        user.set_password(password)
    else:
        click.echo("Creating user...")
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo("Done")




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








