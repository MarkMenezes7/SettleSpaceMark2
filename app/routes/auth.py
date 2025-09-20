from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.models import User
from app.forms import LoginForm, CustomerRegistrationForm, SellerRegistrationForm
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.role == 'admin':
                    next_page = url_for('admin.dashboard')
                elif user.role == 'seller':
                    next_page = url_for('seller.dashboard')
                else:
                    next_page = url_for('main.index')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page)
        flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth/register_choice.html')

@bp.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = CustomerRegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('auth/register_customer.html', form=form)
        
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            role='customer'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_customer.html', form=form)

@bp.route('/register/seller', methods=['GET', 'POST'])
def register_seller():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = SellerRegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('auth/register_seller.html', form=form)
        
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            upi_id=form.upi_id.data,
            role='seller'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in and start listing properties.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_seller.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))