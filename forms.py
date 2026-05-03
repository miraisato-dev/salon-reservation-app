# salon_reservation_app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional, ValidationError

class CustomerForm(FlaskForm):
    full_name = StringField('氏名', validators=[DataRequired('名前は必須入力です')])
    # 国番号の関係上文字型の方が都合が良い phone_numberかemailのどちらかは必須
    phone_number = StringField('電話番号', validators=[Optional()])
    email = EmailField('メール', validators=[Optional(), Email('メールアドレスのフォーマットではありません')])    
    # birthdate = DateField('生年月日', validators=[])
    note = TextAreaField('備考')
    submit = SubmitField('登録')


    # phone_numberかemailのどちらか必須
    def validate(self, extra_validators):
        # if not super().validate(extra_validators=extra_validators):
        #     return False

        # if not self.phone_number.data and not self.email.data:
        #     self.phone_number.errors.append('電話番号かメールのどちらかは必須です')
        #     return False

        # return True
        is_valid = super().validate(extra_validators=extra_validators)

        if not self.phone_number.data and not self.email.data:
            self.phone_number.errors.append('電話番号かメールのどちらかは必須です')
            self.email.errors.append('電話番号かメールのどちらかは必須です')
            is_valid = False

        return is_valid