from flask import Flask

app = Flask(__name__)


# session.permanent = True


def main():
    app.run()


@app.route("/")
def index():
    return "Привет от приложения Flask"


if __name__ == '__main__':
    main()