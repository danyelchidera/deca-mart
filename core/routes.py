from fileinput import filename
import os
from core import app, db
from flask import render_template, redirect, url_for, flash, request
from core.models import Items, Users, Carts, Cart_Items
from core.forms import RegisterForm, LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from core import ALLOWED_EXTENSIONS



@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/summary')
@login_required
def summary():
    items = db.session.query(Items).all()
    return render_template('summary.html', items = items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = Users(first_name = form.first_name.data, last_name = form.last_name.data, email = form.email.data, password = form.password.data, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash(f'Account created succesfully, you are now logged in as {new_user.first_name} ', category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err in form.errors.values():
            flash(f'Operation failed: {err}', category = 'danger')
    return render_template('register.html', form = form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Users.query.filter_by(email = form.email.data).first()

        if attempted_user and attempted_user.check_password(attempted_password = form.password.data):
            login_user(attempted_user)
            flash(f'Login succesful', category='success')
            return redirect(url_for('home_page'))
        else:
            flash(f'username or password incorrect', category='danger')



    return render_template('login.html', form = form)

# TO DO
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        
        # Get input fields
        title = request.form.get('title')
        description = request.form.get('description')
        quantity= request.form.get('quantity')
        category= request.form.get('category')
        price = request.form.get('price')
       
        # Upload file
        if 'file' not in request.files:
            flash('No file part', category= 'danger')
            return render_template('merchant_upload.html') 
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.name == '':
            flash('No selected file', category= 'danger')
            return render_template('merchant_upload.html') 
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
    
            # Save item to database 
            new_item = Items(title = title, description = description, quantity = quantity, category = category, price = price, user_id = current_user.id, file_name = filename)
            db.session.add(new_item)
            db.session.commit()
            flash('Item has been saved', category = 'success')
    
    return render_template('merchant_upload.html')


# TO DO
@app.route('/traditional')
def traditional_category():
    goods = []
    items = Items.query.all()
    for item in items:
        if item.category == 'Traditional':
            goods.append(item)
    return render_template('category.html', goods = goods)

   


# TO DO
@app.route('/corporate')
def corporate_category():
    goods = []
    items = Items.query.all()
    for item in items:
        if item.category == 'Formal':
            goods.append(item)
    return render_template('category.html', goods = goods)



# TO DO
@app.route('/casual')
def casual_category():
    goods = []
    items = Items.query.all()
    for item in items:
        if item.category == 'Casual':
            goods.append(item)
    return render_template('category.html', goods = goods)

  



# TO DO 
@app.route('/cart')
def cart():
    return render_template('home.html')


# TO DO 
@app.route('/buy')
def buy():

    return render_template('home.html')



# TO DO
@app.route('/transactions')
def transaction_summary():
    
    return render_template('transaction.html')
# Transaction Summary Buyer


# TO DO 



@app.route('/logout')
def logout():
    logout_user()
    flash(f'you have been logged out', category='info')
    return redirect(url_for('home_page'))

@app.route('/view', methods=['GET', 'POST'])
@login_required
def item_view():
    if request.method == "GET":
        itemId = request.args.get('item')
        item = db.session.query(Items).filter_by(id = itemId).first()
        print(item)
        return render_template('item_page.html', item = item)
    if request.method == "POST":
        itemId = request.form.get('itemId')
        cart = Carts.query.filter_by(user_id = current_user.id).first()
        if cart is None:
            new_cart = Carts(user_id = current_user.id)
            db.session.add(new_cart)
            db.session.commit()
        cart_item = Cart_Items(item_id = itemId, cart_id = cart.cart_id, item_quantity = 1)
        db.session.add(cart_item)
        db.session.commit()
        flash(f'Item Succesfully added to cart', category='success')
        return redirect(f'/view?item={itemId}')

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == "GET":
        checkout = getCheckoutItems()
        if checkout is None:
            return render_template('checkout.html')
        else:
            return render_template('checkout.html', items = checkout[0], total = checkout[1])

    if request.method == "POST":
        cart_item = Cart_Items.query.filter_by(item_id = request.form.get('itemId')).first()
        db.session.delete(cart_item)
        db.session.commit()
        return redirect(url_for('checkout'))
    
def getCheckoutItems():
    cart = Carts.query.filter_by(user_id = current_user.id).first()
    if cart is None:
        return None
    cartId = cart.cart_id
    cart_items_id = db.session.query(Cart_Items.item_id).filter_by(cart_id = cartId)
    cart_items_id=[i[0] for i in cart_items_id]
    items = db.session.query(Items).filter(Items.id.in_(cart_items_id))
    total = 0
    for item in items:
        total = total + item.price
    return items, total

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    return render_template("payment.html")

@app.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    checkout = getCheckoutItems()
    if checkout[1] > current_user.wallet:
         flash(f'You do not have enough money to make this order', category='danger')
    else:
        current_user.wallet = current_user.wallet - checkout[1] 
        db.session.commit()
        flash(f'Order successful', category='success')
    return redirect("/payment")