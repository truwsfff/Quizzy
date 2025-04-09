from flask import Flask, render_template


app = Flask(__name__)
app.config['SECRET_KEY'] = ''


@app.route('/test')
def test():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
