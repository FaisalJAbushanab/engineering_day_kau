from operator import sub
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
import flask
from flask_login.utils import login_required
from flask_wtf.recaptcha import fields
from pyasn1.type.univ import Null
from app.models import User, UserSchema
from app.forms import (RegistrationForm, LoginForm, UpdateInfoForm,
                        UpdatePermissionsForm, RequestResetForm, ResetPasswordForm)
from app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user
import firebase_admin
from firebase_admin import storage as admin_storage, credentials
import json
import random, os
import string
from flask_mail import Message
import qrcode
from sqlalchemy import or_
from itsdangerous import URLSafeTimedSerializer

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
    if form.validate_on_submit():
        qr_code = ''.join(random.SystemRandom()
            .choice(string.ascii_uppercase + string.digits) for _ in range(20))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        small_email = form.email.data.lower()
        user = User(email=small_email, password=hashed_password, full_name=form.fullname.data, unId=form.unid.data, qrcode = qr_code, field=form.field.data)
        db.session.add(user)
        db.session.commit()
        created = User.query.filter_by(email=form.email.data).first()
        if created:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data('checkout/user/'+str(created.id))
            qr.make()
            img = qr.make_image(fill_color="green", back_color="white")
            img.save('app/static/images/qrcodes/' + qr_code + '.png','PNG')
            path = 'app/static/images/qrcodes/' + qr_code + '.png'
            path_to = '/'+str(created.id)+'/'+qr_code+'.png'
            firebase = firebaseStore(path, path_to)
            if firebase == 'success':
                os.remove(path)
        token = s.dumps(created.email, salt='email-confirm')

        msg = Message('بوابة الهندسة 21 | تفعيل حسابك',
                  sender='noreplay@7alaqh.com', recipients=[created.email])
        msg.html = f'''<h2 style="text-align: center"> <img src="/app/static/images/logo.svg" width="200px" /> </h2> <br> <br> <p style="text-align: right;"> </b> مرحباً عزيزي,,,</b> </p> <br>
<p style="text-align: right;"> نشكرك على تسجيلك للحضور في بوابة الهندسة 21 لتتمكن لدخول إلى بطاقتك الإلكترونية، يتوجب عليك تفعيل حسابك من خلال الضغط على الزر أدناه </p>"
<br> <p style="text-align: center;"> <a href="{url_for('confirm_email', token=token, _external=True)}" style="color: white; background-color: green; padding: 10px 20px;">تفعيل حسابي </a> </p>
<br> <br>
<p style="text-align: right;"> اذا كنت لا تستطيع الضغط على الزر أعلاه فالرجاء نسخ الرابط التالي ولصقه في متصفحك ليتم تفعيل حسابك </P>
<a href="{url_for('confirm_email', token=token, _external=True)}"> {url_for('confirm_email', token=token, _external=True)} </a> 
<br style="text-align: right;">
<p style="text-align: right;"> للدعم والمساعدة الرجاء التواصل معنا عبر البريد الإلكتروني: support@kau-enggate21.com </p>

'''
#     msg.body = f'''لإعاادة تعين كلمة المرور الخاصة بك، الرجاء النقر على الرابط أو لصقه في المتصفح:
# {url_for('reset_token', token=token, _external=True)}

# اذا كنت لم تطلب اعادة تعين كلمة المرور فالرجاء تجاهل هذه الرسالة.
# '''
        mail.send(msg)

        flash('تم ارسال رسالة إلى بريدك '+ created.email + ' تحتوي على معلومات تفعيل حسابك لتتمكن من الوصول لبطاقتك الإلكترونية. في حال لم يصلك البريد تأكد من سلة المهملات spam ', 'warning')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form, page='register')

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
                    login_user(user)
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
        num = User.query.count()
        page = request.args.get('page', 1, type=int)
        visitors = User.query.paginate(page=page, per_page=10)
        return render_template('admin/visitors.html', user=current_user, visitors=visitors, num=num)
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

    path = 'qrcodes/'+ user.qrcode+'.png'
    qrcode_link = getURL(path)
    return render_template('admin/card.html', user=user, qr=qrcode_link, form=form)

@app.route('/home')
@login_required
def home():
    path = 'qrcodes/'+ current_user.qrcode+'.png'
    qrcode_link = getURL(path)
    return render_template('auth/home.html', user = current_user, qr = qrcode_link)

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
    msg = Message('بوابة الهندسة 21 | رابط إعادة تعين كلمة المرور',
                  sender='noreplay@7alaqh.com', recipients=[user.email])
    msg.html = f'''<h2 style="text-align: center"> <img src="/app/static/images/logo.svg" width="200px" /> </h2> <br> <br> <p style="text-align: right;"> </b> مرحباً عزيزي,,,</b> </p> <br>
<p style="text-align: right;"> لقد طلبت اعادة تعين كلمة المرور الخاصة بحسابك في منصة بوابة الهندسة 21" لإعادة تعين كلمة مرور جديدة الرجاء الضغط على زر "إعادة تعين كلمة مرور جديدة </p>"
<br> <p style="text-align: center;"> <a href="{url_for('reset_token', token=token, _external=True)}" style="color: white; background-color: green; padding: 10px 20px;">إعادة تعين كلمة المرور </a> </p>
<br> <br>
<p style="text-align: right;"> اذا كنت لا تستطيع الضغط على الزر أعلاه فالرجاء نسخ الرابط التالي ولصقه في متصفحك ليتم إعادة تعين كلمة المرور </P>
<a href="{url_for('reset_token', token=token, _external=True)}"> {url_for('reset_token', token=token, _external=True)} </a> 
<br style="text-align: right;">
<b style="text-align: right;"> ملاحظة: إذا لت تطلب إعادة تعين كلمة المرور الخاصة بحسابك في منصة بوابة الهندسة 21 الرجاء تجاهل هذه الرسالة ولن يتم تغير أي شيء </b>
<p style="text-align: right;"> للدعم والمساعدة الرجاء التواصل معنا عبر البريد الإلكتروني: support@kau-enggate22.com </p>

'''
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


@app.route('/checkout/user/<int:user_id>')
@login_required
def checkout(user_id):
    user = User.query.get_or_404(user_id)
    user_schema = UserSchema()
    return user_schema.jsonify(user)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('401.html'), 401