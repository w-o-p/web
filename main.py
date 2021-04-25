from pickle import dumps

from flask import Flask, render_template, redirect, make_response, request, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms import StringField, TextAreaField, IntegerField, FormField

from data import db_session
from data.news import Tests, Tegs
from data.users import User
from forms.news import TestForm, Account_submit, Answers, Test_id, Test_name_submit, Test_teggs_submit, TestAnswers
from forms.user import RegisterForm, LoginForm

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
    c = form.validate_on_submit()
    k = ''
    name = []
    db_sess = db_session.create_session()
    if c:
        try:
            b = db_sess.query(Tegs.test_id).filter(Tegs.teg == form.ar_teggs.data).first()
            for i in b:
                name = str(i)
            k = "/tests_page/" + name
            return redirect(k)
        except Exception:
            return redirect("/tests_page/999999999999999999999999999")
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
        if form.data['submit']:
            st = ''
            for i in range(len(form.questions.data)):
                st += form.questions.data[i]['content'] + ';'
                for j in range(len(form.questions.data[i]['answer'])):
                    st += '%' + form.questions.data[i]['answer'][j] + ';'
                    st += '$' + str(form.questions.data[i]['scores'][j]) + ';'

            sp2 = []

            for i in range(len(form.res_point.data)):
                sp2.append('{}-{};&{}'.format(form.res_point.data[i], form.res_point_max.data[i], form.result.data[i]))

            st2 = ';'.join(sp2)

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

    if form.data['add_answer']:
        for i in range(len(form.questions.entries)):
            form.questions.entries[i].form.answer.append_entry(StringField('ответ'))
            form.questions.entries[i].form.answer.entries[-1].data = None

            form.questions.entries[i].form.scores.append_entry(IntegerField("Количество баллов"))
            form.questions.entries[i].form.scores.entries[-1].data = None
    elif form.data['del_answer']:
        if len(form.questions.entries[0].form.answer) > 1:
            for i in range(len(form.questions.entries)):
                form.questions.entries[i].form.answer.pop_entry()
                form.questions.entries[i].form.scores.pop_entry()
    elif form.data['submit_con']:
        form.questions.append_entry(FormField(Answers))

        while len(form.questions.entries[-1].form.answer) < len(form.questions.entries[0].form.answer):
            form.questions.entries[-1].form.answer.append_entry(StringField('ответ'))
            form.questions.entries[-1].form.answer.entries[-1].data = None

            form.questions.entries[-1].form.scores.append_entry(IntegerField("Количество баллов"))
            form.questions.entries[-1].form.scores.entries[-1].data = None
    elif form.data['del_con']:
        if len(form.questions) > 1:
            form.questions.pop_entry()
    elif form.data['add_res']:
        form.res_point.append_entry(IntegerField("Больше стольки очков"))
        form.res_point_max.append_entry(IntegerField("Больше стольки очков"))
        form.result.append_entry(TextAreaField("Результат"))
        form.result.entries[-1].data = None
    elif form.data['del_res']:
        if len(form.res_point) > 1:
            form.res_point.pop_entry()
            form.res_point_max.pop_entry()
            form.result.pop_entry()

    return render_template('news.html', num=num, form=form, title='Добавление теста')


@app.route('/tests_run/<int:num>', methods=['GET', 'POST'])
def run_news(num):
    form = TestAnswers()
    if form.data['submit'] and form.data['answers'] is not None:  # надеюсь будет работать
        form.sp.append(form.data['answers'])
        return redirect('/tests_run/{}'.format(num))
    db_sess = db_session.create_session()
    all_values = db_sess.query(Tests).filter(Tests.id == num).first()
    title = all_values.title
    cicle = 0
    question = ''
    answers = []
    scores = []
    parsed_quest = all_values.questions.split(';')
    del parsed_quest[-1]
    num_q = len(list(filter(lambda x: x[0] != '$' and x[0] != '%', parsed_quest)))
    print(form.sp)
    if num_q <= len(form.sp):
        s = sum(list(map(int, form.sp)))
        TestAnswers.sp = []
        return redirect('/tests_run/end/{}&{}'.format(num, s))
    else:
        for i in range(len(parsed_quest)):
            if parsed_quest[i][0] == '%':
                if cicle - 1 == len(form.sp):
                    answers.append(parsed_quest[i][1::])
            elif parsed_quest[i][0] == '$':
                if cicle - 1 == len(form.sp):
                    scores.append(parsed_quest[i][1::])
            else:
                cicle += 1
                if cicle - 1 == len(form.sp):
                    question = parsed_quest[i]
            if cicle > len(form.sp) + 1:
                break

        for i in range(len(answers)):
            form.answers.choices.append((int(scores[i]), answers[i]))

        # form.answers.choices.append(('val2', 'dont choose this'))
        return render_template('run_test.html', title=title, num=len(form.sp) + 1, form=form, question=question)


@app.route('/tests_run/end/<int:num>&<int:s>', methods=['GET', 'POST'])
def end(num, s):
    sum_ans = s
    db_sess = db_session.create_session()
    all_results = db_sess.query(Tests).filter(Tests.id == num).first()
    parsed_res = all_results.result.split(';')
    test_result = ''
    results = []
    scrs = []
    for i in range(len(parsed_res)):
        if parsed_res[i][0] == '&':
            results.append(parsed_res[i][1::])
        else:
            scrs.append(parsed_res[i].split('-'))
    for i in range(len(scrs)):
        if int(scrs[i][0]) <= sum_ans < int(scrs[i][1]):
            test_result = results[i]
    # '<a href="/">еще не сделал<a/> <br/> <p>{}<p/>'.format(test_result)
    return render_template('test_end.html', test_result=test_result)


@app.route('/tests_page//<int:f>', methods=['GET', 'POST'])
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
        j = db_sess.query(Tests.created_date).filter(Tests.id == f).first()
        for i in j:
            date = i

        if form.data['run_test']:
            return redirect('/tests_run/{}'.format(id_t))

    except Exception:
        crea = 1
    return render_template('test.html', name=name, content=content, id_t=id_t, user_id=user_id, date=date,
                           crea=crea, form=form)


@app.route('/api_id/<int:f>', methods=['GET', 'POST'])
def api_id(f):
    db_sess = db_session.create_session()
    id_t = []
    title_id = []
    con_t = []
    x = []
    try:
        k1 = {}
        b = db_sess.query(User.name).filter(User.id == f).first()
        for i in b:
            name = i
        k1.update({"name": name})
        b = db_sess.query(User.about).filter(User.id == f).first()
        for i in b:
            about = i
        k1.update({"about": about})
        b = db_sess.query(Tests.id).filter(Tests.user_id == f).all()
        for w in b:
            for i in w:
                id_t.append(i)
        b = db_sess.query(Tests.title).filter(Tests.user_id == f).all()
        for w in b:
            for i in w:
                title_id.append(i)
        b = db_sess.query(Tests.content).filter(Tests.user_id == f).all()
        for w in b:
            for i in w:
                con_t.append(i)
        if len(id_t) > 0:
            for i in range(len(id_t)):
                x = []
                id_l = i + 1
                x.append(id_t[i])
                x.append(title_id[i])
                x.append(con_t[i])
                k1.update({id_l: x})
        # print(k1)
        k = dumps(k1)
    except Exception:
        k = "Данного аккаунта не существует"
    return k


@app.route('/acc_page_id//<int:f>', methods=['GET', 'POST'])
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


@app.route('/secret')
def sec():
    return render_template('table.html', title='пасхалочка')


if __name__ == '__main__':
    main()
