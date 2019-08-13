from flask import Flask

app = Flask('name')
@app.route('/')

def hi_world():
    return "Hi world!"


if __name__ == '__main__':
    app.run()