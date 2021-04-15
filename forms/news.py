from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    name = StringField('Название теста', validators=[DataRequired()])
    content = TextAreaField("Условия")
    answer = TextAreaField("Ответ")
    scores = IntegerField("Количество баллов")
    add_answer = SubmitField('Создать ответ')
    submit = SubmitField('Сохранить условие')


    save_question = False
    a = 5
