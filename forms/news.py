from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    name = StringField('Название теста', validators=[DataRequired()])
    content = TextAreaField("Условия")
    answer = TextAreaField("Ответ")
    description = TextAreaField("Описание")
    scores = IntegerField("Количество баллов")
    add_answer = SubmitField('Создать ответ')
    add_result = SubmitField('Создать результат')
    submit_con = SubmitField('Сохранить условие')
    res_point = IntegerField("Больше столки очков")
    result = TextAreaField("Результат")
    submit_res = SubmitField('Сохранить результат')
    submit = SubmitField('Сохранить тест')
    run_test = SubmitField('Пройти тест')
    add_picture = SubmitField('Добавить изображение')
    but_answer = SubmitField("Раньше 8")


    save_question = False
    a = 5
