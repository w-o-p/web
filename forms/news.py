from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, FieldList
from wtforms.validators import DataRequired

entrcount = 1


class TestForm(FlaskForm):
    name = StringField('Название теста', validators=[DataRequired()])
    content = TextAreaField("Условия")
    answer = FieldList(StringField('ответ'), min_entries=4)
    description = TextAreaField("Описание")
    scores = IntegerField("Количество баллов")
    add_result = SubmitField('Создать результат')
    submit_con = SubmitField('Сохранить условие')
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
    ac_id = IntegerField("Введите id аккаунта")

class Addanswer(FlaskForm):
    add_answer = SubmitField('Создать ответ')
