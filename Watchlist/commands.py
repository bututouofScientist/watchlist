from Watchlist import app, db
from Watchlist.models import User, Movie
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
