from flask import Flask, render_template, redirect, make_response, request, session, abort
from data import db_session
from data.users import User
from data.news import News
from forms.user import RegisterForm, LoginForm
from forms.news import TestForm, Account_submit
import forms.news as new
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms import StringField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


# session.permanent = True


def main():
    db_session.global_init("db/blogs.db")

    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    posts = 'Записи в блоге'
    # news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            ((News.user == current_user) | (News.is_private != True) | current_user.admin))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, posts=posts)


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/search_teggs")
def search_teggs():
    form = TestForm()
    return render_template("search_teggs.html", form=form)


@app.route("/search_name")
def search_name():
    form = TestForm()
    return render_template("search_name.html", form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/tests/<action>', methods=['GET', 'POST'])
@login_required
def add_test(action):
    form = TestForm()
    count_conditions = []
    num = len(count_conditions) + 1
    if action == 'create':
        new.entrcount = 1
    if action == 'add_ans':
        new.entrcount += 1
        form.answer.min_entries = new.entrcount
        while len(form.answer) < form.answer.min_entries:
            form.answer.entries.append(form.answer.entries[0])
        form.scores.min_entries = new.entrcount
        while len(form.scores) < form.scores.min_entries:
            form.scores.entries.append(form.scores.entries[0])
    if action == 'del_ans':
        new.entrcount -= 1
        form.answer.min_entries = new.entrcount
        while len(form.answer) < form.answer.min_entries:
            form.answer.entries.append(form.answer.entries[0])
        form.scores.min_entries = new.entrcount
        while len(form.scores) < form.scores.min_entries:
            form.scores.entries.append(form.scores.entries[0])

    return render_template('news.html', num=num, form=form, title='Добавление теста')


@app.route('/tests_page//<int:f>', methods=['GET', 'POST'])
@login_required
def edit_news(f):
    form = TestForm()
    db_sess = db_session.create_session()
    b = db_sess.query(News.title).filter(News.id == f).first()
    for i in b:
        name = i
    c = db_sess.query(News.content).filter(News.id == f).first()
    for i in c:
        content = i
    d = db_sess.query(News.id).filter(News.id == f).first()
    for i in d:
        id_t = i
    e = db_sess.query(News.user_id).filter(News.id == f).first()
    for i in e:
        user_id = i
    f = db_sess.query(News.created_date).filter(News.id == f).first()
    for i in f:
        date = i
    return render_template('test.html', name=name, content=content, id_t=id_t, user_id=user_id, date=date, form=form)


@app.route('/tests_run', methods=['GET', 'POST'])
@login_required
def run_news():
    form = TestForm()
    return render_template('run_test.html', title="Какой ты хлеб?", num="1", form=form)


@app.route('/acc_page_id//<int:f>', methods=['GET', 'POST'])
@login_required
def acc_page_id(f):
    x1 = []
    y1 = []
    x = []
    y = []
    t1 = ''
    t2 = ''
    t3 = ''
    t4 = ''
    des1 = ''
    des2 = ''
    des3 = ''
    des4 = ''
    form = TestForm()
    db_sess = db_session.create_session()
    b = db_sess.query(User.name).filter(User.id == f).first()
    for i in b:
        name = i
    c = db_sess.query(User.about).filter(User.id == f).first()
    for i in c:
        description = i
    e = db_sess.query(User.admin).filter(User.id == f).first()
    for i in e:
        if i:
            ad = 1
        else:
            ad = 0
    k = db_sess.query(News.title).filter(News.user_id == f)
    for i in k:
        x1.append(i)
    for i in x1:
        for w in i:
            x.append(w)
    g = db_sess.query(News.content).filter(News.user_id == f)
    for i in g:
        y1.append(i)
    for i in y1:
        for w in i:
            y.append(w)
    if len(x) >= 4:
        t1 = x[0]
        t2 = x[1]
        des1 = y[0]
        des2 = y[1]
        t3 = x[2]
        t4 = x[3]
        des3 = y[2]
        des4 = y[3]
        a = 4
    elif len(x) == 3:
        t1 = x[0]
        des1 = y[0]
        t2 = x[1]
        des2 = y[1]
        t3 = x[2]
        des3 = y[2]
        a = 3
    elif len(x) == 2:
        t1 = x[0]
        des1 = y[0]
        t2 = x[1]
        des2 = y[1]
        a = 2
    elif len(x) == 1:
        t1 = x[0]
        des1 = y[0]
        a = 1
    else:
        a = 0
    lo = db_sess.query(User.id).filter(User.id == f).first()
    for i in lo:
        id_a = i
    f = db_sess.query(User.created_date).filter(News.id == f).first()
    for i in f:
        date = i
    return render_template('acc_page_id.html', name=name, a=a, description=description, ad=ad, t1=t1, t2=t2, des1=des1,
                           des2=des2, t3=t3, t4=t4, des3=des3, des4=des4, id_a=id_a, date=date, form=form)


@app.route('/acc_page', methods=['GET', 'POST'])
def acc_page():
    form = Account_submit()
    b = form.validate_on_submit()
    if b:
        a = "/acc_page_id/" + str(form.ac_id.data)
        return redirect(a)
    return render_template('acc_page.html', form=form)


@app.route('/tests_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    if not current_user.admin:
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
    else:
        news = db_sess.query(News).filter(News.id == id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
