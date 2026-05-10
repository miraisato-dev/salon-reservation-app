# salon_reservation_app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, EmailField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, ValidationError, Length
from models import Stylists


# =======================
# Formクラス
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝======

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
    


# ログイン用入力クラス
class LoginForm(FlaskForm):
    username = StringField('ユーザー名: ',
                            validators=[DataRequired('ユーザー名は必須入力です')])
    # パスワード：パスワード入力
    password = PasswordField('パスワード: ',
                            validators=[Length(4, 10,
                                    'パスワードの長さは4文字以上10文字以内です')])
    # ボタン
    submit = SubmitField('ログイン')

    # カスタムバリデータ
    # 英数字と記号が含まれているかチェック
    def validate_password(self, password):
        if not (any(c.isalpha() for c in password.data)) and \
            any (c.isdigit() for c in password.data) and \
            any (c in "!@#$%^&*()" for c in password.data):
            raise ValidationError('パスワードには【英数字と記号: !@#$%^&*()】を含める必要があります')

# サインアップ用入力クラス
class SignUpForm(LoginForm):
    # ボタン
    submit = SubmitField('サインアップ')
    # カスタムバリデータ
    def validate_username(self, username):
        user = Stylists.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('そのユーザー名はすでに使用されています')