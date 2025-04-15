# ------ Импорт прочих библиотек
import datetime
from config import SECRET_KEY

# ------ Импорт flask инструментов
from flask import Flask, render_template, session, redirect

# ------ Импорт инструментов для регистрации
from flask_login import LoginManager, login_user, login_required, logout_user
from forms.login_form import LoginForm
from forms.register_form import RegisterForm

# ------ Импорт всего связанного с бд
from data import db_session
from data.users import User


# ------ Конфигурация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# ------ Все роуты приложения
@app.route('/')
def test():
    return render_template('start.html', username='truwsfff')


@app.route('/registration')
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        pass
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               errors=['Неправильный логин или пароль'],
                               form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    tests_list = [
    ]
    return render_template('profile.html', tests=tests_list)


if __name__ == '__main__':
    db_session.global_init("db/quizzy.db")
    app.run(port=8080, host='0.0.0.0')
