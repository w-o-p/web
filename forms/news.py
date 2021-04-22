from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, FieldList, FormField, RadioField
from wtforms.validators import DataRequired

anscount = 1
questcount = 1
resultcount = 1
answersp = []
numquest = 1


class Answers(FlaskForm):
    content = TextAreaField("Вопрос")
    answer = FieldList(StringField('ответ'), min_entries=1)
    scores = FieldList(IntegerField("Количество баллов"), min_entries=1)


class TestForm(FlaskForm):
    name = StringField('Название теста', validators=[DataRequired()])
    description = TextAreaField("Описание")
    questions = FieldList(FormField(Answers), min_entries=1)
    add_answer = SubmitField('Создать ответ')
    del_answer = SubmitField('Удалить ответ')
    submit_con = SubmitField('Создать вопрос')
    del_con = SubmitField('Удалить вопрос')
    res_point = FieldList(IntegerField("От стольки очков"), min_entries=1)
    res_point_max = FieldList(IntegerField("До стольки очков"), min_entries=1)
    result = FieldList(TextAreaField("Результат"), min_entries=1)
    add_res = SubmitField('Создать результат')
    del_res = SubmitField('Удалить результат')
    submit = SubmitField('Сохранить тест')
    run_test = SubmitField('Пройти тест')
    add_picture = SubmitField('Добавить изображение')
    but_answer = SubmitField("Выбрать")
    teggs = TextAreaField("Теги (через ; пробелов)")


class Account_submit(FlaskForm):
    ac_id = IntegerField("Введите id аккаунта")
    ac_name = TextAreaField("Введите имя аккаунта")
    submit = SubmitField('Найти аккаунт')


class Test_id(FlaskForm):
    ar_id = IntegerField("Введите id теста")
    submit = SubmitField('Найти аккаунт')


class Test_name_submit(FlaskForm):
    ar_name = TextAreaField("Введите имя теста")
    submit = SubmitField('Найти аккаунт')


class Test_teggs_submit(FlaskForm):
    ar_teggs = TextAreaField("Введите  тегги теста")
    submit = SubmitField('Найти аккаунт')


class TestAnswers(FlaskForm):
    answers = RadioField('Ответы', choices=[])
    submit = SubmitField('Отправить ответ')
