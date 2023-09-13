from flask import (Flask, render_template, 
                  request, redirect, url_for)
from flask_sqlalchemy import SQLAlchemy
from matplotlib import pyplot
import os

app=Flask(__name__)
app.config['SECRET_KEY']='keep_it_secret'

base_dir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(base_dir, 'user.db')
db=SQLAlchemy(app)
app.app_context().push()  

@app.route('/')
def index():
    return render_template('index.html')


#############################################################################################
########################################## MANAGER ##########################################
#############################################################################################


@app.route('/mlogin', methods=['GET','POST'])
def mlogin():
    if request.method=='POST':
        if request.form['username']=='manager1' and request.form['password']=='pass1':
            return redirect('/mdashboard')
        else:
            return f"Wrong entry!! <a href='/mlogin'> Click here </a> to try again with a different username and password."
        
    return render_template('mlogin.html')

class Category(db.Model):
    category_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name=db.Column(db.String(50), nullable=False, unique=True)
    products=db.relationship('Product',backref='category')
  
class Product(db.Model):
    product_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name=db.Column(db.String(50), nullable=False, unique=True)
    product_unit=db.Column(db.String(50), nullable=False)
    product_rate=db.Column(db.Integer, nullable=False)
    product_quantity=db.Column(db.Float, nullable=False)
    category_id=db.Column(db.Integer, db.ForeignKey("category.category_id"),nullable=False)
    
    
@app.route('/mdashboard', methods=['GET','POST'])
def mdashboard():
    if request.method=='POST': 
        category=Category(category_name=request.form['category'])
        db.session.add(category)
        db.session.commit()
    categories=Category.query.all()
    return render_template('mdashboard.html',categories=categories)
    

@app.route('/add_category')    
def add_category():
    return render_template('add_category.html')
    
@app.route('/edit_category/<int:id>')
def edit_category(id):
    cat=Category.query.filter_by(category_id=id).first()
    return render_template('edit_category.html',category=cat)

@app.route('/change_category_name/<int:id>',methods=['GET','POST'])
def change_category_name(id):
    if request.method=='GET':
        return render_template('category_name.html',id=id)
    elif request.method=='POST':
        cat=Category.query.filter_by(category_id=id).first()
        name=request.form['new_name']
        cat.category_name=name
        db.session.add(cat)
        db.session.commit()
        return render_template('edit_category.html',category=cat)

       
@app.route('/remove_category/<int:Category_id>', methods=['GET','POST'])
def remove_category(Category_id):
    if request.method=='GET':
        return render_template('mconfirmation.html',item_id=Category_id)
    elif request.method=='POST':
        if request.form['username']=='manager1' and request.form['password']=='pass1' and request.form['choice']=='yes':
            cat=Category.query.filter_by(category_id=Category_id).first()
            pro=Product.query.filter_by(category_id=Category_id)
            for item in pro:
                db.session.delete(item)
                db.session.commit()
            # db.session.delete(pro)
            db.session.delete(cat)
            db.session.commit()   
            return redirect('/mdashboard')
        elif request.form['username']!='manager1' or request.form['password']!='pass1':
            return f"Wrong entry!! <a href='/remove_category/{Category_id}'>click here</a> to try again with correct uesrname and password."
        else: 
            return redirect('/mdashboard')

@app.route('/add_product/<int:Category_id>', methods=['GET','POST'])
def add_product(Category_id):
    if request.method=='POST':
        # cat=Category.query.get(Category_id)
        product=Product(
            product_name=request.form['product'],
            product_unit=request.form['unit'],
            product_rate=request.form['rate'],
            product_quantity=request.form['quantity'],
            category_id=Category_id)
        db.session.add(product)
        db.session.commit()
        return redirect('/mdashboard')
    return render_template('add_product.html',category_id=Category_id)

@app.route('/update/<int:sno>', methods=['GET','POST'])
def update(sno):
    pro=Product.query.filter_by(product_id=sno).first()
    if request.method=="POST":
        pro.product_name=request.form['product']
        pro.product_unit=request.form['unit']
        pro.product_rate=request.form['rate']
        pro.product_quantity=request.form['quantity']
        
        db.session.add(pro)
        db.session.commit()
        return redirect('/mdashboard')
    return render_template('update.html',product=pro)
    
@app.route('/delete/<int:sno>',methods=['GET','POST'])
def delete(sno):
    if request.method=='GET':
        return render_template('confirmation.html',item_id=sno)
    elif request.method=='POST':
        if request.form['username']=='manager1' and request.form['password']=='pass1' and request.form['choice']=='yes':
            pro=Product.query.filter_by(product_id=sno).first()
            db.session.delete(pro)
            db.session.commit()
            return redirect('/mdashboard')
        elif request.form['username']!='manager1' or request.form['password']!='pass1':
            return f"Wrong entry!! <a href='/delete/{sno}'>click here</a> to try again."
        else: 
            return redirect('/mdashboard')
        
#########################################################################################################
########################################### USER ########################################################
#########################################################################################################

class User(db.Model):
    user_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(50), nullable=False, unique=True)
    password=db.Column(db.String(100), nullable=False)
    bookings=db.relationship('Bookings',backref='user')
    cart=db.relationship('Cart',backref='user')
    
class Bookings(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String,nullable=False)
    Quantity=db.Column(db.Float)
    Total=db.Column(db.Float)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    # product_id=db.Column(db.Integer,db.ForeignKey('product.product_id'),nullable=False)
    
class Cart(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String,nullable=False)
    Quantity=db.Column(db.Float)
    Total=db.Column(db.Float)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    # product_id=db.Column(db.Integer,db.ForeignKey('product.product_id'),nullable=False)


db.create_all() 


@app.route('/uregister', methods=['GET','POST'])
def uregister():
    if request.method=='POST':
        uname=request.form['username']
        upass=request.form['password']
        
        user=User(username=uname, password=upass)
        db.session.add(user)
        db.session.commit()
        print(f"Welcome {uname}, You are successfully registered into our Grocery Store!!!")
        return redirect('/ulogin')
    return render_template('register.html')



@app.route('/ulogin', methods=['GET','POST'])
def ulogin():
    if request.method=='POST':
        uname=request.form['username']
        upass=request.form['password']
        users=User.query.all()
        if len(users)==0:
            return redirect('/uregister')    
        for user in users:
            if uname==user.username and upass==user.password:
                # flash(f"Welcome {uname}, You are logged into Grocery Store!!!") 
                return redirect(url_for('udashboard',id=user.user_id))               
        return redirect('/uregister')
    return render_template('login.html')


@app.route('/inventory', methods=['GET','POST'])
def Inventory():
    categories=Category.query.all()
    return render_template('inventory.html',categories=categories)


@app.route('/udashboard/<int:id>')
def udashboard(id):
    categories=Category.query.all()
    user=User.query.get(id)
    return render_template('udashboard.html',user=user,categories=categories)

@app.route('/add2cart/<int:id>/<int:user_id>', methods=['GET','POST'])
def add2cart(id, user_id):
    if request.method=='POST':
        pro=Product.query.get(id)
        Name=pro.product_name
        qty=float(request.form['Quantity'])
        total=qty*pro.product_rate
        if Cart.query.filter_by(name=Name,user_id=user_id).first():
            return f"Product already in cart!! <a href='/cart/{user_id}'> Click here </a> to Visit your cart "
        if pro.product_quantity>=qty:            
            added=Cart(name=Name, Quantity=qty, Total=total, user_id=user_id)
            db.session.add(added)
            db.session.commit()
            return f"Added Successfully!! <a href='/cart/{user_id}'>click here</a> to view your Cart."  
        else:
            return f'Could not add in cart!! Available quantity: {pro.product_quantity} {pro.product_unit}'
    product=Product.query.get(id)
    category=product.category
    return render_template('add2cart.html',product=product,category=category,user_id=user_id)
    
@app.route('/cart/<int:user_id>')
def cart(user_id):
    user=User.query.get(user_id) 
    cart=Cart.query.filter_by(user_id=user_id).all()
    Grand_total=0
    for item in cart:
        Grand_total+=item.Total
    return render_template('cart.html',user=user,Grand_total=Grand_total)

@app.route('/delete_cart/<int:id>/<int:user_id>')
def remove_cart(id,user_id):
    item=Cart.query.filter_by(id=id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('cart',id=id,user_id=user_id))

        
@app.route('/buy/<int:id>/<int:user_id>', methods=['GET','POST'])
def buy(id, user_id):
    if request.method=='POST':
        pro=Product.query.get(id)
        Name=pro.product_name
        qty=float(request.form['Quantity'])
        total=qty*pro.product_rate
        if Bookings.query.filter_by(name=Name,user_id=user_id).first():
            return f"Order was not placed!! {Name} is ordered already. <a href='/bookings/{user_id}'>click here</a> to check your orders."
        if pro.product_quantity>=qty:            
            booked=Bookings(name=Name, Quantity=qty, Total=total, user_id=user_id)
            db.session.add(booked)
            pro.product_quantity-=qty
            db.session.commit()   
            return f"Order placed Succesfully!! <a href='/bookings/{user_id}'>click here</a> to check your orders."
        else:
            return f'Order was not placed!! Available quantity: {pro.product_quantity} {pro.product_unit}'
    product=Product.query.get(id)
    category=product.category
    return render_template('buy.html',product=product,category=category,user_id=user_id)

@app.route('/bookings/<int:user_id>')
def bookings(user_id):
    user=User.query.get(user_id)
    bookings=Bookings.query.filter_by(user_id=user_id).all()
    Grand_total=0
    for item in bookings:
        Grand_total+=item.Total
    return render_template('bookings.html',user=user,Grand_total=Grand_total)


@app.route('/delete_order/<int:id>/<int:user_id>')
def remove_order(id,user_id):
    item=Bookings.query.filter_by(id=id).first()
    qty=item.Quantity
    pro=Product.query.filter_by(product_name=item.name).first()
    pro.product_quantity+=qty
    db.session.delete(item)
    db.session.commit()
    
    return redirect(url_for('bookings',id=id,user_id=user_id))


@app.route('/checkout/<int:user_id>')
def checkout(user_id):
    cart=Cart.query.filter_by(user_id=user_id).all()
    for item in cart:
        Name=item.name
        qty=item.Quantity
        total=item.Total
        pro=Product.query.filter_by(product_name=item.name).first()
        pro.product_quantity-=qty
        booked=Bookings(name=Name, Quantity=qty, Total=total, user_id=user_id)
        db.session.add(booked)
        db.session.delete(item)
        db.session.commit()
    return redirect(f'/bookings/{user_id}')


@app.route('/search',methods=['GET','POST'])
def search():
    if request.method=="POST":
        name=request.form['keyword']
        query='%'+name+'%'
        category=Category.query.filter(Category.category_name.like(query)).all()
        product=Product.query.filter(Product.product_name.like(query)).all()
        if category:            
            return render_template('search_results.html',category=category)
        elif product:
            return render_template('seek_results.html',product=product)
        else:
            return f"No category or product found with the keyword '{name}'!!"
    return render_template('search.html')


@app.route('/search_by_price',methods=['GET','POST'])
def search_by_price():
    if request.method=="POST":
        price=request.form['choice']
        if price=='1':
            products=Product.query.filter(Product.product_rate<=50).all()
        elif price=='2':
            products=Product.query.filter(Product.product_rate.between(50, 100)).all()
        elif price=='3':
            products=Product.query.filter(Product.product_rate.between(100, 200)).all()
        elif price=='4':
            products=Product.query.filter(Product.product_rate>=200).all()
        else:
            return f'Product not found!!'
    return render_template('seek_results.html',product=products)


@app.route('/graph')
def graph():
    categories=Category.query.all()
    for category in categories:
        x=[]
        y=[]
        for pro in category.products:
            x.append(pro.product_name)
            qty=0
            bookings=Bookings.query.filter_by(name=pro.product_name).all()
            for item in bookings:
                qty+=item.Quantity
            y.append(qty)
        pyplot.bar(x,y)
        pyplot.xlabel('Products')
        pyplot.ylabel('Quantity-sold')
        pyplot.title(f'{category.category_name}')
        figure=os.path.join('static','category_graphs',f"{category.category_name}.png")
        pyplot.savefig(figure)
        pyplot.close()
    return render_template('graph.html',figure=figure,categories=categories)

    
if __name__=="__main__":
    app.run(debug=True)
    

