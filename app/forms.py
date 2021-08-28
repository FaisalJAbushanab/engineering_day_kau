from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, PasswordField, RadioField, SubmitField, validators, IntegerField
from wtforms.fields.core import BooleanField, SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Record
from sqlalchemy import or_, and_

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
        user = User.query.filter(and_(User.email==email.data, User.status=='activated')).first()
        if user:
            raise ValidationError('هذا البريد مستخدم من قبل، اذا كنت قد نسيت كلمة المرور الرجاء الضغط على نسية كلمة المرور لتعين كلمة مرور جديدة')

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

class BulkEmailForm(FlaskForm):
    sender = StringField('المرسل', validators=[DataRequired(), Length(min=4, max=23)])
    recipients = SelectField('المستلمون', choices=[('null', '...اختر'), ('all', 'الجميع'), ('select', 'شخص محدد'), ('Admin', 'الادارة'), ('Mod', 'فريق التنظيم'), ('Guest', 'حضور')])
    subject = StringField('العنوان', validators=[DataRequired(), Length(min=4, max=155)])
    submit = SubmitField('ارسال')
    def validate_recipients(self, recipients):
        data = ['null', 'all', 'select', 'Admin', 'Mod', 'Guest']
        if recipients.data == 'null':
            raise ValidationError('يجب اختيار مستلم')
        if recipients.data not in data:
            raise ValidationError('قيمة غير صحيحة')

    def validate_sender(self, sender):
        check = sender.data.find("@")
        if check != -1:
            raise ValidationError('@ اسم المرسل يجب ان لا يحتوى على الرمز')
        if not sender.data.isascii():
            raise ValidationError('اسم المرسل يجب ان يكون بالحروف الانجليزية فقط')

class addRecordForm(FlaskForm):
    fullname = StringField('الاسم الثلاثي',
                            validators=[DataRequired(), Length(min=4, max=155)])
    unid = StringField('الرقم الجامعي', validators=[DataRequired(message="حقل الزامي"), Length(min=7, max=10)])
    email = StringField('البريد الإلكتروني',
                            validators=[DataRequired(message="حقل الزامي"), Email(message="الرجاء ادخال بريد الكتروني صحيح")])
    phone = StringField('رقم الجوال', validators=[DataRequired(message="حقل الزامي"), Length(min=10, max=13)])
    field = SelectField('التخصص', choices=['اختر', 'هندسة مستجد', 'هندسة الطيران', 'الهندسة الكيميائية وهندسة المواد', 'الهندسة المدنية والبيئية', 'الهندسة الكهربائية وهندسة الحاسبات', 'الهندسة الصناعية', 'الهندسة النووية', 'هندسة الإنتاج وتصميم النظم الميكانيكية', 'هندسة التعدين', 'الهندسة الحرارية'], validators=[DataRequired()])
    submit = SubmitField('ارسال')

    def validate_field(self, field):
        data = ['هندسة مستجد', 'هندسة الطيران', 'الهندسة الكيميائية وهندسة المواد', 'الهندسة المدنية والبيئية', 'الهندسة الكهربائية وهندسة الحاسبات', 'الهندسة الصناعية', 'الهندسة النووية', 'هندسة الإنتاج وتصميم النظم الميكانيكية', 'هندسة التعدين', 'الهندسة الحرارية']
        if field.data not in data:
            raise ValidationError('يجب اختيار تخصص صحيح')
    def validate_unid(self, unid):
        if not unid.data.isdecimal():
            raise ValidationError('الرقم الجامعي يجب ان يكون ارقام فقط')
        user = Record.query.filter_by(unId=unid.data).first()
        if user:
            raise ValidationError('لقد قمت بالتسجيل من قبل')

    def validate_phone(self, phone):
        if not phone.data.isdecimal():
            raise ValidationError('يجب اختيار تخصص')
    def validate_email(self, email):
        user = Record.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('لقد قمت بالتسجيل من قبل')
    def validate_fullname(self, fullname):
        user = Record.query.filter_by(full_name=fullname.data).first()
        if user:
            raise ValidationError('لقد قمت بالتسجيل من قبل')
class settingsForm(FlaskForm):
    regForm = BooleanField()
    submit = SubmitField('ارسل')