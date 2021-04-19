from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired

entrcount = 1
questcount = 1


class Answers(FlaskForm):
    content = TextAreaField("Вопрос")
    answer = FieldList(StringField('ответ'), min_entries=4)
    scores = FieldList(IntegerField("Количество баллов"), min_entries=4)


class TestForm(FlaskForm):
    name = StringField('Название теста', validators=[DataRequired()])
    description = TextAreaField("Описание")
    questions = FieldList(FormField(Answers), min_entries=1)
    add_result = SubmitField('Создать результат')
    add_answer = SubmitField('Создать ответ')
    del_answer = SubmitField('Удалить ответ')
    submit_con = SubmitField('Создать условие')
    res_point = IntegerField("Больше столки очков")
    result = TextAreaField("Результат")
    submit_res = SubmitField('Сохранить результат')
    submit = SubmitField('Сохранить тест')
    run_test = SubmitField('Пройти тест')
    add_picture = SubmitField('Добавить изображение')
    but_answer = SubmitField("Выбрать")
    teggs = TextAreaField("Теги (через запятую)")
    sub_teggs = SubmitField("Найти")
    sub_name = SubmitField("Найти")
    ar_teggs = TextAreaField("Тег:")
    ar_name = TextAreaField("Назвавние:")
    ar_id = TextAreaField("Id:")
    sub_id = SubmitField("Найти")


class Account_submit(FlaskForm):
    ac_id = IntegerField("Введите id аккаунта")
    submit = SubmitField('Найти аккаунт')
