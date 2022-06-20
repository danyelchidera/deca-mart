from core import db, bcrypt, login_manager
import datetime
import enum
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Role(enum.Enum):
    Buyer = 1
    Merchant = 2

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(length = 30), nullable = False, unique = True)
    password_hash = db.Column(db.String(length = 60), nullable = False)
    wallet = db.Column(db.Integer(), nullable = False, default = 10000)
    role = db.Column(db.String(8), nullable = False)
    items = db.relationship('Items', backref='owner', lazy = True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    

class Items(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length = 150), nullable = False) 
    description = db.Column(db.String(length=200), nullable = False)
    quantity = db.Column(db.Integer(), nullable=False)
    category = db.Column(db.String())
    price = db.Column(db.Integer(), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), nullable=False)
    file_name =db.Column(db.String(length = 200), nullable = False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    cart_items = db.relationship('Cart_Items', backref = 'item', lazy = True)
    order_items = db.relationship('Order_Items', backref = 'item', lazy = True)


class Carts(db.Model):
    cart_id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    cart_items = db.relationship('Cart_Items', backref='cart', lazy=True)


class Cart_Items(db.Model):
    cart_item_id = db.Column(db.Integer(), primary_key = True)
    item_id = db.Column(db.Integer(), db.ForeignKey('items.id'))
    cart_id = db.Column(db.Integer(), db.ForeignKey('carts.cart_id'))
    item_quantity = db.Column(db.Integer(), default = 1)

class Orders(db.Model):
    order_id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.String(), db.ForeignKey('users.id'))
    order_items = db.relationship('Order_Items', backref = 'orders', lazy = True)


class Order_Items(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    item_id = db.Column(db.Integer(), db.ForeignKey('items.id'))
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.order_id'))