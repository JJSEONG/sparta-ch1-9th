from flask import Flask, render_template
import items

app = Flask(__name__)

app.register_blueprint(items.blue_items)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)