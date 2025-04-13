import datetime
from flask import Flask, render_template, session, redirect
# from flask_login import LoginManager
# from forms.login_form import LoginForm
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = ''
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
# login_manager = LoginManager()
# login_manager.init_app(app)


@app.route('/')
def test():
    return render_template('start.html', username='truwsfff')


'''@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)'''


@app.route('/profile')
def profile():
    tests_list = [
    ]
    return render_template('profile.html', tests=tests_list)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='0.0.0.0')
