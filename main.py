import datetime
from flask import Flask, render_template, session
# from flask_login import LoginManager


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


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
