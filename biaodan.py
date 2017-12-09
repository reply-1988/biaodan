from datetime import datetime

import os
from flask import Flask, render_template, session, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message

basedir = os.path.abspath(os.path.dirname(__file__))
# app的相关配置
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'date.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 1271997525
app.config['MAIL_PASSWORD'] = 'sodvdrykulkeiggg'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = 'Flasky'
app.config['FLASKY_MAIL_SENDER']='1271997525@qq.com'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')


# 数据库处理
db = SQLAlchemy(app)
# 模板处理
bootstrap = Bootstrap(app)
# 时间处理
moment = Moment(app)
# shell工具处理
manager = Manager(app)
# 邮箱处理
mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email( 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        # 两次输入数据的提醒
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash("你似乎改变了你的名字啊=。=")
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form = form, name = session.get('name'), known = session.get('known', False),
                           current_time = datetime.utcnow())

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

def send_email(subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=['jingjingdexue@outlook.com'])
    msg.body = render_template(template + 'txt', **kwargs)
    msg.html = render_template(template + 'html', **kwargs)
    mail.send(msg)

if __name__ == '__main__':
    app.run()

