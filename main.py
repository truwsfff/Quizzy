# ------ Импорт прочих библиотек
import datetime
from config import SECRET_KEY

# ------ Импорт flask инструментов
from flask import Flask, render_template, session, redirect

# ------ Импорт инструментов для регистрации
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
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
def start_window():
    return render_template('start.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        # Валидатор никнеймов
        if len(form.nickname.data) < 5 or len(form.nickname.data) > 15:
            return render_template('register.html',
                                   error_message='\
Никнейм не должен превышать 15 символов и быть меньше 5 символов.',
                                   form=form)

        for i in r"""!"#$%&'()*+,-./:;<=>?@[\]^`{|}~ абвгдеёжзийклмнопрстуфхцчшщъыьэюя""":
            if i in form.nickname.data.strip().lower():
                return render_template('register.html',
                                       error_message='\
Никнейм не должен содержать специальных символов/пробелы/буквы русского '
                                                     'алфавита.',
                                       form=form)

        # Валидатор паролей
        if len(form.password.data) < 5:
            return render_template('register.html',
                                   error_message='\
Пароль должен содержать 5 и более символов.',
                                   form=form)

        if form.password.data != form.password_repeat.data:
            return render_template('register.html',
                                   error_message='\
        Пароли не совпадают.',
                                   form=form)

        # Валидатор О себе
        if form.about.data != '':
            if len(form.about.data) > 100:
                return render_template('register.html',
                                       error_message='\
Превышен лимит символов в графе "О себе": должно быть не более 100.',
                                       form=form)

        # Записываем пользователя в бд
        user = User(
            name=form.nickname.data,
            about=form.about.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               error_message='Неправильный логин или пароль',
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
