# main file
from flask import Flask, render_template, request, redirect, url_for,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from products import *
import random
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:232324@localhost:5432/mikhmed'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = create_engine('postgresql+psycopg2://postgres:232324@localhost:5432/mikhmed')
Session = sessionmaker(bind=engine)
session = Session()
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15))


class UserFactory:
    @staticmethod
    def create_user(id, username, email, password, phone_number):
        return Users(id=id, name=username, email=email, password=password, phone_number=phone_number)


@app.route('/home/logout')
def logout():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    logged = request.cookies.get('logged')

    user = Users.query.filter_by(name=username).first()
    email = user.email
    phone_number = user.phone_number

    return render_template('logout.html', username=username, password=password, email=email, phone_number=phone_number, is_logged=logged)


@app.route('/home/logout/logout_button_clicked', methods=['POST'])
def logout_button_clicked():
    response = make_response(redirect(url_for('home')))
    for cookie in request.cookies:
        response.set_cookie(cookie, '', expires=0)
    return response


@app.route('/home/catalog/submit', methods=['POST'])
def submit():
    product_id = request.form.get('product_id')
    delivery_time = request.form.get('delivery_time')
    address = request.form.get('address')
    return redirect(url_for('product_page', product_id=product_id))


@app.route('/home/catalog/deliver_submit', methods=['POST'])
def deliver_submit():
    product_id = request.form.get('product_id')
    username = request.cookies.get('username')
    return redirect(url_for('delivery_page', product_id=product_id, username=username))


@app.route('/home/delivery/<int:product_id>')
def delivery_page(product_id):
    username = request.cookies.get('username')
    logged = request.cookies.get('logged')
    return render_template('delivery_page.html', product_id=product_id, all_products=all_products, username=username, is_logged=logged)


@app.route('/home/catalog/product/<int:product_id>')
def product_page(product_id):
    logged = request.cookies.get('logged')
    username = request.cookies.get('username')


    return render_template('product_page.html', product_id=product_id, all_products=all_products, is_logged=logged, username=username)
    # return f'Product ID: {product_id}'


@app.route('/')
def index():
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('logged', 'False')
    resp.set_cookie('username', 'None', 0)
    resp.set_cookie('password', 'None', 0)
    return resp


@app.route('/home/catalog')
def catalog():
    logged = request.cookies.get('logged')
    username = request.cookies.get('username')

    # CATALOG РАБОТА С ВЫГРУЗКОЙ ТОВАРОВ В СИСТЕМУ
    return render_template('catalog.html', username=username, is_logged=logged, products1=products1, products2=products2, products3=products3)


@app.route('/home/about')
def about():
    logged = request.cookies.get('logged')
    username = request.cookies.get('username')
    return render_template('about.html', username=username, is_logged=logged)


@app.route('/home/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user = Users.query.filter_by(name=username).first()

        if password == confirm_password:
            if user.password == password:
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('username', username)
                resp.set_cookie('password', password)
                resp.set_cookie('logged', 'True')
                return resp
        else:
            return render_template('login.html', error='Пароли не совпадают. Пожалуйста, повторите ввод.')

    return render_template('login.html')


@app.route('/home/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id = random.randint(1000, 100000)
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        phone_number = request.form.get('phone_number')

        # проверяем, есть ли уже такое имя пользователя в бд
        user = Users.query.filter_by(name=username).first()
        if user:
            return render_template('register.html', error='Имя пользователя уже существует!')

        password_length = len(password)
        if password_length > 7:
            # добавляем данные в бд после валидаций
            new_user = UserFactory.create_user(id, username, email, password, phone_number)
            db.session.add(new_user)
            db.session.commit()

            # добавляем id пользователя в куки
            user = Users.query.filter_by(name=username).first()
            if user:
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('username', username)
                resp.set_cookie('password', password)
                resp.set_cookie('logged', 'True')
                return resp
            else:
                return render_template('register.html', error='Ошибка добавления в куки')
        else:
            return render_template('register.html', error='Пароль должен содержать больше 7 символов!')

    return render_template('register.html')


@app.route('/home')
def home():
    username = request.cookies.get('username')
    logged = request.cookies.get('logged')
    return render_template('home.html', username=username, is_logged=logged)


if __name__ == '__main__':
    app.run(debug=True)
