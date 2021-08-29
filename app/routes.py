from datetime import timedelta
from operator import sub
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
import flask
from flask_login.utils import login_required
from flask_wtf import form
from flask_wtf.recaptcha import fields
from pyasn1.type.univ import Null
from sqlalchemy.sql.expression import true
from app.models import Settings, User, UserSchema, Record
from app.forms import (RegistrationForm, LoginForm, UpdateInfoForm,
                        UpdatePermissionsForm, RequestResetForm,
                        ResetPasswordForm, BulkEmailForm, addRecordForm,
                        settingsForm, exportForm)
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user
import firebase_admin
from firebase_admin import storage as admin_storage, credentials
import json
import random, os
import string
from flask_mail import Message
import qrcode
from sqlalchemy import or_, and_
from itsdangerous import URLSafeTimedSerializer
import requests, os.path
import pandas as pd

firebaseConfig = {
    "apiKey": "AIzaSyDiXLqriZJblxEBr-acp1L_sG3qR82U434",
    "authDomain": "enggate21-2251e.firebaseapp.com",
    "projectId": "enggate21-2251e",
    "databaseURL" : "",
    "storageBucket": "enggate21-2251e.appspot.com",
    "messagingSenderId": "585912827287",
    "appId": "1:585912827287:web:033f4eedd08680797b58d2"
  }

cred = credentials.Certificate("app/Key.json")
admin = firebase_admin.initialize_app(cred, firebaseConfig)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'], )

def send_email(sender, emails, subject, content):
    requests.post(
        "https://api.mailgun.net/v3/7alaqh.com/messages",
        auth=("api", "47ae4bd7f8f5e76c95294d5aa43abcf8-b892f62e-cd14c5de"),
        data={"from": sender,
              "to": emails,
              "subject": subject,
              "html": content})
def getURL(path):
    
    # firebase = pyrebase.initialize_app(firebaseConfig)
    # url = admin_storage.child(path).get_url(token = None)
    bucket = admin_storage.bucket(app=admin)
    url = bucket.blob(path)
    return url.generate_signed_url(expiration=8000000000)

def firebaseStore(file, to):
    bucket = admin_storage.bucket()
    destination = 'qrcodes/'+ to
    blob = bucket.blob(destination)
    blob.upload_from_filename(file)
    return 'success'

def role(userRole):
    if userRole == 'Admin':
        return 'Admin'
    elif userRole == 'Guest':
        return 'Guest'
    else:
        return False

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.roles == 'Admin':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('home'))
    else:
        return render_template('index.html', page='index')

@app.route('/sign-up', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
#     if form.validate_on_submit():
#         qr_code = ''.join(random.SystemRandom()
#             .choice(string.ascii_uppercase + string.digits) for _ in range(20))
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         small_email = form.email.data.lower()
#         isUser = User.query.filter(and_(User.email==small_email, User.status=='pending')).first()
#         if isUser:
#             token = s.dumps(isUser.email, salt='email-confirm')
#             msg = Message('تأكيد تسجيلك',
#                   sender=('21 بوابة الهندسة', 'noreplay@7alaqh.com'), recipients=[isUser.email])
#             msg.html = render_template('mail/confirm_email.html', token=token, user=isUser)
#             mail.send(msg)

#             flash('تم ارسال رسالة إلى بريدك '+ isUser.email + ' تحتوي على معلومات تفعيل حسابك لتتمكن من الوصول لبطاقتك الإلكترونية. في حال لم يصلك البريد تأكد من سلة المهملات spam ', 'warning')
#             return redirect(url_for('login'))
#         user = User(email=small_email, password=hashed_password, full_name=form.fullname.data, unId=form.unid.data, qrcode = qr_code, field=form.field.data)
#         db.session.add(user)
#         db.session.commit()
#         created = User.query.filter_by(email=form.email.data).first()
#         if created:
#             qr = qrcode.QRCode(
#                 version=1,
#                 error_correction=qrcode.constants.ERROR_CORRECT_M,
#                 box_size=10,
#                 border=4,
#             )
#             qr.add_data('checkout/user/'+str(created.id))
#             qr.make()
#             img = qr.make_image(fill_color="green", back_color="white")
#             img.save('app/static/images/qrcodes/' + qr_code + '.png','PNG')
#             path = 'app/static/images/qrcodes/' + qr_code + '.png'
#             path_to = str(created.id)+'/'+qr_code+'.png'
#             firebase = firebaseStore(path, path_to)
#             if firebase == 'success':
#                 os.remove(path)
#         token = s.dumps(created.email, salt='email-confirm')

#         msg = Message('تأكيد تسجيلك في بوابة الهندسة 21',
#                   sender=('21 بوابة الهندسة', 'noreplay@7alaqh.com'), recipients=[created.email])
#         msg.html = render_template('mail/confirm_email.html', token=token, user=created)
        
# # f'''<h2 style="text-align: center"> <img src="/app/static/images/logo.svg" width="200px" /> </h2> <br> <br> <p style="text-align: right;"> </b> مرحباً عزيزي,,,</b> </p> <br>
# # <p style="text-align: right;"> نشكرك على تسجيلك للحضور في بوابة الهندسة 21 لتتمكن لدخول إلى بطاقتك الإلكترونية، يتوجب عليك تفعيل حسابك من خلال الضغط على الزر أدناه </p>"
# # <br> <p style="text-align: center;"> <a href="{url_for('confirm_email', token=token, _external=True)}" style="color: white; background-color: green; padding: 10px 20px;">تفعيل حسابي </a> </p>
# # <br> <br>
# # <p style="text-align: right;"> اذا كنت لا تستطيع الضغط على الزر أعلاه فالرجاء نسخ الرابط التالي ولصقه في متصفحك ليتم تفعيل حسابك </P>
# # <a href="{url_for('confirm_email', token=token, _external=True)}"> {url_for('confirm_email', token=token, _external=True)} </a> 
# # <br style="text-align: right;">
# # <p style="text-align: right;"> للدعم والمساعدة الرجاء التواصل معنا عبر البريد الإلكتروني: support@kau-enggate21.com </p>

# # '''
# #     msg.body = f'''لإعاادة تعين كلمة المرور الخاصة بك، الرجاء النقر على الرابط أو لصقه في المتصفح:
# # {url_for('reset_token', token=token, _external=True)}

# # اذا كنت لم تطلب اعادة تعين كلمة المرور فالرجاء تجاهل هذه الرسالة.
# # '''
#         mail.send(msg)

#         flash('تم ارسال رسالة إلى بريدك '+ created.email + ' تحتوي على معلومات تفعيل حسابك لتتمكن من الوصول لبطاقتك الإلكترونية. في حال لم يصلك البريد تأكد من سلة المهملات spam ', 'warning')
#         return redirect(url_for('login'))
    return render_template('auth/register.html', form=form, page='register')

@app.route('/register', methods=['GET', 'POST'])
def newData():
    form = addRecordForm()
    stat = Settings.query.get(1)
    if request.method == 'POST':
        if form.validate_on_submit():
            record = Record(email=form.email.data, unId=form.unid.data, phoneNum=form.phone.data, full_name= form.fullname.data, field=form.field.data)
            db.session.add(record)
            db.session.commit()
            flash('تم تسجيل بيانتك للدخول في السحب', 'warning')
            return redirect(url_for('index'))
    if stat.value == False:
        return render_template('add_record.html', form=form, page='register', stat=False)
    else:
        return render_template('add_record.html', form=form, page='register', stat=True)



@app.route('/confirm_email/<token>')
def confirm_email(token):
    email = s.loads(token, salt='email-confirm', max_age=(3600*30))
    user = User.query.filter_by(email=email).first()
    if user:
        user.status = 'activated'
        db.session.commit()
        flash('مبروك! لقد تم تفعيل حسابك بنجاح يمكنك تسجيل الدخول الآن', 'success')
        return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            em = form.email.data.lower()
            user = User.query.filter_by(email=em).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                if user.status == 'activated':
                    login_user(user, remember=true, duration=timedelta(days=3))
                    return redirect(url_for('index'))
                else:
                    flash('لا يمكنك الدخول بسبب عدم تأكيد تسجيلك من خلال الضغط على الرابط المرسل على بريدك، الرجاء تأكيد التسجيل', 'danger')
                    return redirect(url_for('login'))
            else:
                flash('لم تتم عملية تسجيل الدخول، الرجاء التحقق من البيانات المدخلة', )
                return redirect(url_for('login'))
    return render_template('auth/login.html', form=form, page='login')

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        # sound.firebaseRevoke('7Ro1PyuzzrVkS07qDvJZxhPiQZ92')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = User.query.filter_by(email=current_user.email).first()
    visitors = User.query.filter_by(roles='Guest').count()
    mods = User.query.filter_by(roles='Mod').count()
    admins = User.query.filter_by(roles='Admin').count()
    if user.roles in ['Admin', 'Mod']:
        return render_template('admin/dashboard.html', user= current_user, visitors=visitors, mods=mods, admins=admins, page='dashboard')
    else:
        abort(403)

@app.route('/dashboard/visitors')
@login_required
def visitors():
    if current_user.roles in ['Admin', 'Mod']:
        num = User.query.filter_by(status='activated').count()
        page = request.args.get('page', 1, type=int)
        visitors = User.query.filter_by(status='activated').paginate(page=page, per_page=10)
        return render_template('admin/visitors.html', user=current_user, visitors=visitors, num=num)
@app.route('/dashboard/records')
@login_required
def records():
    if current_user.roles in ['Admin', 'Mod']:
        num = Record.query.count()
        page = request.args.get('page', 1, type=int)
        visitors = Record.query.paginate(page=page, per_page=10)
        return render_template('admin/records.html', user=current_user, visitors=visitors, num=num)
@app.route('/dashboard/user/<int:user_id>/viewCard', methods=['GET', 'POST'])
@login_required
def viewCard(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdatePermissionsForm()
    if request.method == 'GET':
        form.role.data = user.roles
    if request.method == 'POST':
        if current_user.roles == 'Admin' and user.roles != form.role.data:
            if form.validate_on_submit():
                user.roles = form.role.data
                db.session.commit()
                flash('تم تغير صلاحية ' + user.full_name, 'success')
                return redirect(url_for('viewCard', user_id=user.id))
        else:
            flash('لا يمكن تنفيذ العملية', )
            return redirect(url_for('viewCard', user_id=user.id))

    path = 'qrcodes/'+ str(user.id) + '/' + user.qrcode+'.png'
    qrcode_link = getURL(path)
    return render_template('admin/card.html', user=user, qr=qrcode_link, form=form)

@app.route('/dashboard/settings', methods=['GET', 'POST'])
@login_required
def settings():
    set = Settings.query.filter_by(key='regForm').first()
    winner = Settings.query.filter_by(key='Winning').first()
    regForm = set.value
    win = winner.value
    settings = {
        "regForm": regForm,
        "win": win
    }
    if request.method == 'POST':
        if 'regForm' in request.form.getlist("mycheckbox"):
            set.value = True
        else:
            set.value = False
        if 'win' in request.form.getlist("mycheckbox"):
            winner.value = True
        else:
            winner.value = False
        db.session.commit()
        flash('تم الحفظ', 'success')
        return redirect(url_for('settings'))
    return render_template('admin/settings.html', settings=settings, page='settings')

def to_dict(row):
    if row is None:
        return None

    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict

@app.route('/dashboard/export_table', methods=['GET', 'POST'])
@login_required
def export():
    form = exportForm()
    path= False
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.table.data == 'records':
                data = Record.query.all()
                data_list =[to_dict(item) for item in data]
                df = pd.DataFrame(data_list)
                filename = 'table.xlsx'
                writer = pd.ExcelWriter(filename)
                df.to_excel(writer, sheet_name='records')
                writer.save()
                path = os.path.exists('table.xlsx')
        
    return render_template('admin/export.html', page='export', form=form, check=path)
@app.route('/home')
@login_required
def home():
    path = 'qrcodes/'+ str(current_user.id) + '/' + current_user.qrcode+'.png'
    qrcode_link = getURL(path)
    return render_template('auth/home.html', user = current_user, qr = qrcode_link)

@app.route('/bulk-messages', methods=['GET', 'POST'])
@login_required
def emailing():
    if current_user.roles != 'Admin':
        abort(401)
    page = 'emailing'
    form = BulkEmailForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # sender = form.sender.data + '@mg.7alaqh.com'
            sender = form.sender.data+'@gmail.com'
            if form.recipients.data == 'all':
                get_users = User.query.filter_by(status='activated').all()
                emails = []
                for user in get_users:
                    emails.append(user.email)
                if len(emails) < 1:
                    flash('مشكلة في الارسال', 'danger')
                    return redirect(url_for('emailing'))
                msg = Message(form.subject.data,
                  sender=('بوابة الهندسة 21', sender), recipients=emails)
                msg.html = request.form.get('editordata')
                mail.send(msg)
                flash('تم الارسال بنجاح', 'success')
                return redirect(url_for('emailing'))
            elif form.recipients.data == 'select':
                get_user = User.query.filter(and_(User.status=='activated', User.email==request.form.get('peremail'))).first()
                if not get_user:
                    flash('البريد الإلكتروني غير متوفر', 'danger')
                    return redirect(url_for('emailing'))
                msg = Message(form.subject.data,
                  sender=sender, recipients=[get_user.email])
                msg.html = f'''{ request.form.get('editordata') }'''
                mail.send(msg)
                flash('تم الارسال بنجاح', 'success')
                return redirect(url_for('emailing'))
            elif form.recipients.data == 'Guest':
                Guests = User.query.filter(and_(User.status=='activated', User.roles=='Guest')).all()
                emails = []
                for Guest in Guests:
                    emails.append(Guest.email)
                if len(emails) < 1:
                    flash('مشكلة في الارسال', 'danger')
                    return redirect(url_for('emailing'))
                msg = Message(form.subject.data,
                  sender=sender, recipients=emails)
                msg.html = request.form.get('editordata')
                mail.send(msg)
                flash('تم الارسال بنجاح', 'success')
                return redirect(url_for('emailing'))
            elif form.recipients.data == "Mod":
                Mods = User.query.filter(and_(User.status=='activated', User.roles=='Mod')).all()
                emails = []
                for Mod in Mods:
                    emails.append(Mod.email)
                if len(emails) < 1:
                    flash('مشكلة في الارسال', 'danger')
                    return redirect(url_for('emailing'))
                msg = Message(form.subject.data,
                  sender=sender, recipients=emails)
                msg.html = request.form.get('editordata')
                mail.send(msg)
                flash('تم الارسال بنجاح', 'success')
                return redirect(url_for('emailing'))
            elif form.recipients.data == "Admin":
                Admins = User.query.filter(and_(User.status=='activated', User.roles=='Admin')).all()
                emails = []
                for Admin in Admins:
                    emails.append(Admin.email)
                if len(emails) < 1:
                    flash('مشكلة في الارسال', 'danger')
                    return redirect(url_for('emailing'))
                msg = Message(form.subject.data,
                  sender=sender, recipients=emails)
                msg.html = request.form.get('editordata')
                mail.send(msg)
                flash('تم الارسال بنجاح', 'success')
                redirect(url_for('emailing'))
            else:
                flash('مشكلة في الارسال', 'danger')
                return redirect(url_for('emailing'))
                

    return render_template('admin/messaging.html', page=page, form=form)
@app.route('/qrcode-scan')
@login_required
def qrscan():
    return render_template('admin/qrscan.html', user = current_user)

@app.route('/edit-info', methods=['GET', 'POST'])
@login_required
def info():
    form = UpdateInfoForm()
    user = User.query.get_or_404(current_user.id)
    if request.method == 'GET':
        form.fullname.data = user.full_name
        form.field.data = user.field
    if request.method == 'POST':
        if form.validate_on_submit():
           count = 0
           if bcrypt.check_password_hash(user.password, form.password.data):
               if user.full_name != form.fullname.data:
                   user.full_name = form.fullname.data
                   count += 1
               if user.field != form.field.data:
                   user.field = form.field.data
                   count += 1
               if count > 0:
                db.session.commit()
                flash('تم تعديل بياناتك', 'success')
                return render_template('auth/edit_info.html', user=current_user, form=form)
           else:
                flash('لم يتم تعديل البيانات, كلمة المرور غير مطابقة', 'danger')
                return render_template('auth/edit_info.html', user=current_user, form=form)
    return render_template('auth/edit_info.html', form=form, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('اعادة تعين كلمة المرور الخاصة بك',
                  sender=('21 بوابة الهندسة', 'noreplay@7alaqh.com'), recipients=[user.email])
    msg.html = render_template('mail/forgot_password.html', token=token, user=user)
    
# f'''<h2 style="text-align: center"> <img src="/app/static/images/logo.svg" width="200px" /> </h2> <br> <br> <p style="text-align: right;"> </b> مرحباً عزيزي,,,</b> </p> <br>
# <p style="text-align: right;"> لقد طلبت اعادة تعين كلمة المرور الخاصة بحسابك في منصة بوابة الهندسة 21" لإعادة تعين كلمة مرور جديدة الرجاء الضغط على زر "إعادة تعين كلمة مرور جديدة </p>"
# <br> <p style="text-align: center;"> <a href="{url_for('reset_token', token=token, _external=True)}" style="color: white; background-color: green; padding: 10px 20px;">إعادة تعين كلمة المرور </a> </p>
# <br> <br>
# <p style="text-align: right;"> اذا كنت لا تستطيع الضغط على الزر أعلاه فالرجاء نسخ الرابط التالي ولصقه في متصفحك ليتم إعادة تعين كلمة المرور </P>
# <a href="{url_for('reset_token', token=token, _external=True)}"> {url_for('reset_token', token=token, _external=True)} </a> 
# <br style="text-align: right;">
# <b style="text-align: right;"> ملاحظة: إذا لت تطلب إعادة تعين كلمة المرور الخاصة بحسابك في منصة بوابة الهندسة 21 الرجاء تجاهل هذه الرسالة ولن يتم تغير أي شيء </b>
# <p style="text-align: right;"> للدعم والمساعدة الرجاء التواصل معنا عبر البريد الإلكتروني: support@kau-enggate22.com </p>

# '''
#     msg.body = f'''لإعاادة تعين كلمة المرور الخاصة بك، الرجاء النقر على الرابط أو لصقه في المتصفح:
# {url_for('reset_token', token=token, _external=True)}

# اذا كنت لم تطلب اعادة تعين كلمة المرور فالرجاء تجاهل هذه الرسالة.
# '''
    mail.send(msg)
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('تم ارسال رابط اعادة تعين كلمة المرور إلى بريدك الإلكتروني، في حال لم يصلك بريد تأكد من صندوق المهملات', 'warning')
        return redirect(url_for('login'))
    return render_template('auth/reset_request.html', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('الرابط غير صحيح أو انتهت مدته', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('تم اعادة تعين كلمة المرور الخاصة بك! يمكنك تسجيل الدخول باستخدام كلمة المرور الجديدة', 'success')
        return redirect(url_for('login'))
    return render_template('auth/reset_token.html', form=form)

@app.route('/draw')
@login_required
def draw():
    users = Record.query.all()
    # user_schema = UserSchema()
    # users = user_schema.jsonify(users)
    return render_template('admin/draw.html', page='draw', users=users)

@app.route('/resources/<page>')
def resources(page):
    page=page
    title = ''
    check = False
    if page == 'engineering_fields':
        title = 'التخصصات الهندسية'
        check = True
    if check:
        return render_template('resources.html', title=title, page='resources', sub=page)
    else:
        abort(404)

@app.route('/checkout/user/<int:user_id>')
@login_required
def checkout(user_id):
    user = User.query.get_or_404(user_id)
    user_schema = UserSchema()
    return user_schema.jsonify(user)

@app.route('/get_users')
@login_required
def winners():
    users = Record.query.all()
    user_schema = UserSchema(many=True)
    return user_schema.jsonify(users)

@app.route('/winner/<int:id>', methods=['POST'])
def recordWinner(id):
    setting = Settings.query.get(2)
    if setting.value:
        winner = Record.query.get_or_404(id)
        winner.winner = 'yes'
        db.session.commit()
        return 'Done'
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('401.html'), 401

@app.route('/loaderio-a30e915499e8b2d6cb9675796e88ec7a/')
def test():
    return render_template('loaderio-a30e915499e8b2d6cb9675796e88ec7a.html')