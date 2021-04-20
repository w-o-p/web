from flask import Flask, render_template, redirect, make_response, request, session, abort
from data import db_session
from data.users import User
from data.news import News, Tests
from forms.user import RegisterForm, LoginForm
from forms.news import TestForm, Account_submit, Answers, Test_id, Test_name_submit, Test_teggs_submit
import forms.news as new
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, FieldList, FormField

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
    tests = db_sess.query(Tests)
    return render_template("index.html", news=tests, posts=posts)


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/search_teggs", methods=['GET', 'POST'])
def search_teggs():
    form = Test_teggs_submit()
    return render_template("search_teggs.html", form=form)


@app.route("/search_name", methods=['GET', 'POST'])
def search_name():
    form = Test_name_submit()
    c = form.validate_on_submit()
    db_sess = db_session.create_session()
    if c:
        try:
            b = db_sess.query(Tests.id).filter(Tests.title == form.ar_name.data).first()
            for i in b:
                name = i
            a = "/tests_page/" + str(name)
            return redirect(a)
        except Exception:
            a = "/tests_page/99999999999999999999999999999999999999999"
            return redirect(a)
    return render_template("search_name.html", form=form)


@app.route("/search_id", methods=['GET', 'POST'])
def search_id():
    form = Test_id()
    c = form.validate_on_submit()
    if c:
        a = "/tests_page/" + str(form.ar_id.data)
        return redirect(a)
    return render_template('search_id.html', form=form)


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

    if form.validate_on_submit():  # сохранение в sql
        # print(form.questions.data)  # Условие 1;%ответ 1;$баллы;%ответ 2;$баллы;условие 2
        # print(form.result.data)

        st = ''
        for i in range(len(form.questions.data)):
            st += form.questions.data[i]['content'] + ';'
            for j in range(len(form.questions.data[i]['answer'])):
                st += '%' + form.questions.data[i]['answer'][j] + ';'
                st += '$' + str(form.questions.data[i]['scores'][j]) + ';'

        st2 = ''  # TODO собрать сюда результаты

        # print(st)

        db_sess = db_session.create_session()
        test = Tests()
        test.title = form.name.data
        test.content = form.description.data
        test.tegs = form.teggs.data
        test.questions = st
        test.user_id = current_user.get_id()
        test.result = st2
        db_sess.add(test)
        db_sess.commit()

        return redirect('/')

    elif action == 'create':
        new.entrcount = 1
        new.questcount = 1
        new.resultcount = 1
    elif action == 'add_ans':  # пока что не вызывается но мб потом будет
        new.entrcount += 1
        form.answer.min_entries = new.entrcount
        while len(form.answer) < form.answer.min_entries:
            form.answer.entries.append(form.answer.entries[0])
        form.scores.min_entries = new.entrcount
        while len(form.scores) < form.scores.min_entries:
            form.scores.entries.append(form.scores.entries[0])
    elif action == 'del_ans':  # пока что не вызывается но мб потом будет
        new.entrcount -= 1
        form.answer.min_entries = new.entrcount
        while len(form.answer) < form.answer.min_entries:
            form.answer.entries.append(form.answer.entries[0])
        form.scores.min_entries = new.entrcount
        while len(form.scores) < form.scores.min_entries:
            form.scores.entries.append(form.scores.entries[0])
    elif action == 'add_quest':
        new.questcount += 1
        while len(form.questions) < new.questcount:
            form.questions.append_entry(FormField(Answers))
    elif action == 'del_quest':
        if new.questcount > 1:
            new.questcount -= 1
        while len(form.questions) < new.questcount:
            form.questions.append_entry(FormField(Answers))
    elif action == 'add_result':
        new.resultcount += 1
        while len(form.res_point) < new.resultcount:
            form.res_point.append_entry(IntegerField("Больше стольки очков"))
        while len(form.result) < new.resultcount:
            form.result.append_entry(TextAreaField("Результат"))

        for i in range(len(form.result.entries)):
            form.result.entries[i].data = None
        for i in range(len(form.result.data)):
            form.result.data[i] = None

    elif action == 'del_result':
        if new.resultcount > 1:
            new.resultcount -= 1
        while len(form.res_point) < new.resultcount:
            form.res_point.append_entry(IntegerField("Больше стольки очков"))
        while len(form.result) < new.resultcount:
            form.result.append_entry(TextAreaField("Результат"))

        for i in range(len(form.result.entries)):
            form.result.entries[i].data = None
        for i in range(len(form.result.data)):
            form.result.data[i] = None

    return render_template('news.html', num=num, form=form, title='Добавление теста')


@app.route('/tests_page//<int:f>', methods=['GET', 'POST'])
@login_required
def edit_news(f):
    name = ''
    content = ''
    id_t = 0
    user_id = 0
    date = ''
    crea = 0
    form = TestForm()
    db_sess = db_session.create_session()
    try:
        b = db_sess.query(Tests.title).filter(Tests.id == f).first()
        for i in b:
            name = i
        c = db_sess.query(Tests.content).filter(Tests.id == f).first()
        for i in c:
            content = i
        d = db_sess.query(Tests.id).filter(Tests.id == f).first()
        for i in d:
            id_t = i
        e = db_sess.query(Tests.user_id).filter(Tests.id == f).first()
        for i in e:
            user_id = i
        f = db_sess.query(Tests.created_date).filter(Tests.id == f).first()
        for i in f:
            date = i
    except Exception:
        crea = 1
    return render_template('test.html', name=name, content=content, id_t=id_t, user_id=user_id, date=date,
                           crea=crea,
                           form=form)


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
    id_t = []
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
    crea = 0
    name = ''
    description = ''
    date = ''
    ad = 0
    a = 0
    id_t1 = 0
    id_t2 = 0
    id_t3 = 0
    id_t4 = 0
    id_a = 0
    try:
        b = db_sess.query(User.name).filter(User.id == f).first()
        for i in b:
            name = i
        c = db_sess.query(User.about).filter(User.id == f).first()
        for i in c:
            description = i
        lo = db_sess.query(User.id).filter(User.id == f).first()
        for i in lo:
            id_a = i
        f12 = db_sess.query(User.created_date).filter(User.id == f).first()
        for i in f12:
            date = i
    except Exception:
        crea = 1
    try:
        k = db_sess.query(Tests.title).filter(Tests.user_id == f)
        for i in k:
            x1.append(i)
        for i in x1:
            for w in i:
                x.append(w)
        g = db_sess.query(Tests.content).filter(Tests.user_id == f)
        for i in g:
            y1.append(i)
        g12 = db_sess.query(Tests.id).filter(Tests.user_id == f)
        for i in g12:
            for w in i:
                id_t.append(w)
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
            id_t1 = id_t[0]
            id_t2 = id_t[1]
            id_t3 = id_t[2]
            id_t4 = id_t[3]
            a = 4
        elif len(x) == 3:
            t1 = x[0]
            des1 = y[0]
            t2 = x[1]
            des2 = y[1]
            t3 = x[2]
            des3 = y[2]
            id_t1 = id_t[0]
            id_t2 = id_t[1]
            id_t3 = id_t[2]
            a = 3
        elif len(x) == 2:
            t1 = x[0]
            des1 = y[0]
            t2 = x[1]
            des2 = y[1]
            id_t1 = id_t[0]
            id_t2 = id_t[1]
            a = 2
        elif len(x) == 1:
            t1 = x[0]
            des1 = y[0]
            id_t1 = id_t[0]
            a = 1
        else:
            a = 0
    except Exception:
        a = 0

    return render_template('acc_page_id.html', name=name, a=a, description=description, t1=t1, t2=t2, des1=des1,
                           des2=des2, t3=t3, t4=t4, des3=des3, des4=des4, id_a=id_a, date=date, crea=crea, id_t1=id_t1,
                           id_t2=id_t2, id_t3=id_t3, id_t4=id_t4, form=form)


@app.route('/acc_page_id', methods=['GET', 'POST'])
def acc_page():
    form = Account_submit()
    b = form.validate_on_submit()
    if b:
        a = "/acc_page_id/" + str(form.ac_id.data)
        return redirect(a)
    return render_template('acc_page.html', form=form)


@app.route('/acc_page_name', methods=['GET', 'POST'])
def acc_page_name():
    form = Account_submit()
    c = form.validate_on_submit()
    db_sess = db_session.create_session()
    if c:
        try:
            b = db_sess.query(User.id).filter(User.name == form.ac_name.data).first()
            for i in b:
                name = i
            a = "/acc_page_id/" + str(name)
            return redirect(a)
        except Exception:
            a = "/acc_page_id/99999999999999999999999999999999999999999"
            return redirect(a)
    return render_template('acc_page_name.html', form=form)


@app.route('/acc_page_search', methods=['GET', 'POST'])
def acc_page_search():
    form = Account_submit()
    return render_template('acc_page_search.html', form=form)


@app.route('/tests_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    if not current_user.admin:
        news = db_sess.query(Tests).filter(Tests.id == id,
                                           Tests.user == current_user
                                           ).first()
    else:
        news = db_sess.query(Tests).filter(Tests.id == id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
