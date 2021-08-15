from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, PasswordField, RadioField, SubmitField, validators
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    fullname = StringField('الاسم الثلاثي',
                            validators=[DataRequired(), Length(min=4, max=60)])
    unid = StringField('الرقم الجامعي', validators=[DataRequired(), Length(min=7, max=7)])
    email = StringField('البريد الإلكتروني',
                            validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), validators.EqualTo('confirm_password', message='Passwords must match'), Length(min=8, max=150)])
    confirm_password = PasswordField('تأكيد كلمة المرور', 
                                    validators=[DataRequired(), EqualTo('password')])
    field = SelectField('التخصص', choices=['اختر', 'هندسة مستجد', 'هندسة الطيران', 'الهندسة الكيميائية وهندسة المواد', 'الهندسة المدنية والبيئية', 'الهندسة الكهربائية وهندسة الحاسبات', 'الهندسة الصناعية', 'الهندسة النووية', 'هندسة الإنتاج وتصميم النظم الميكانيكية', 'هندسة التعدين', 'الهندسة الحرارية'], validators=[DataRequired()])
    submit = SubmitField('تسجيل')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('تم التسجيل باستخدام هذا البريد الإلكتروني مسبقاَ، برجاء استخدام بريد اخر')

    def validate_field(self, field):
        data = ['هندسة مستجد', 'هندسة الطيران', 'الهندسة الكيميائية وهندسة المواد', 'الهندسة المدنية والبيئية', 'الهندسة الكهربائية وهندسة الحاسبات', 'الهندسة الصناعية', 'الهندسة النووية', 'هندسة الإنتاج وتصميم النظم الميكانيكية', 'هندسة التعدين', 'الهندسة الحرارية']
        if field.data not in data:
            raise ValidationError('التخصص غير صحيح')
    
    def validate_unid(self, unid):
        if not unid.data.isdecimal():
            raise ValidationError('الرقم الجامعي غير صحيح')

class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني',
                            validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=8, max=150)])
    submit = SubmitField('دخول')

class UpdateInfoForm(FlaskForm):
    fullname = StringField('الاسم الثلاثي',
                            validators=[DataRequired(), Length(min=4, max=60)])
    field = SelectField('التخصص', choices=['هندسة مستجد', 'هندسة الطيران', 'الهندسة الكيميائية وهندسة المواد', 'الهندسة المدنية والبيئية', 'الهندسة الكهربائية وهندسة الحاسبات', 'الهندسة الصناعية', 'الهندسة النووية', 'هندسة الإنتاج وتصميم النظم الميكانيكية', 'هندسة التعدين', 'الهندسة الحرارية'], validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=8, max=150)])
    submit = SubmitField('تعديل')
    def validate_field(self, field):
        data = ['هندسة مستجد', 'هندسة الطيران', 'الهندسة الكيميائية وهندسة المواد', 'الهندسة المدنية والبيئية', 'الهندسة الكهربائية وهندسة الحاسبات', 'الهندسة الصناعية', 'الهندسة النووية', 'هندسة الإنتاج وتصميم النظم الميكانيكية', 'هندسة التعدين', 'الهندسة الحرارية']
        if field.data not in data:
            raise ValidationError('التخصص غير صحيح')

class UpdatePermissionsForm(FlaskForm):
    role = SelectField('الصلاحيات', choices=[('Admin', 'الادارة'), ('Mod', 'فريق التنظيم'), ('Guest', 'حضور')])
    submit = SubmitField('تعديل')
    def validate_role(self, role):
        data = ['Admin', 'Mod', 'Guest']
        if role.data not in data:
            raise ValidationError('قيمة غير صحيحة')

class RequestResetForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    submit = SubmitField('اعادة تعين كلمة المرور')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('لا يوجد حساب مسجل بالبريد الإلكتروني المدخل, يجب عليك التسجيل أولا')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('كلمة المرور الجديد', validators=[DataRequired(), validators.EqualTo('confirm_password', message='كلمة المرور غير مطابقة'),  Length(min=8, max=150)])
    confirm_password = PasswordField('تأكيد كلمة المرور الجديدة', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('اعادة تعين كلمة المرور')