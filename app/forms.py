from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, PasswordField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CustomerRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class SellerRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    upi_id = StringField('UPI ID', validators=[DataRequired(), Length(min=5, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class PropertyForm(FlaskForm):
    title = StringField('Property Title', validators=[DataRequired(), Length(min=10, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=100, max=2000)], widget=TextArea())
    category = SelectField('Category', choices=[('buy', 'Buy'), ('rent', 'Rent'), ('pg', 'PG/Hostel')], validators=[DataRequired()])
    property_type = SelectField('Property Type', choices=[
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('plot', 'Plot'),
        ('office', 'Office'),
        ('shop', 'Shop'),
        ('warehouse', 'Warehouse'),
        ('pg', 'PG'),
        ('hostel', 'Hostel')
    ], validators=[DataRequired()])
    price = IntegerField('Price (₹)', validators=[DataRequired(), NumberRange(min=1000)])
    location = StringField('Location', validators=[DataRequired(), Length(min=5, max=200)])
    area = IntegerField('Area (sq ft)', validators=[DataRequired(), NumberRange(min=100)])
    bedrooms = IntegerField('Bedrooms', validators=[DataRequired(), NumberRange(min=0, max=10)])
    bathrooms = IntegerField('Bathrooms', validators=[DataRequired(), NumberRange(min=1, max=10)])
    amenities = TextAreaField('Amenities (comma separated)')
    
    # Category specific fields
    property_age = IntegerField('Property Age (years)', validators=[Optional(), NumberRange(min=0, max=100)])
    security_deposit = IntegerField('Security Deposit (₹)', validators=[Optional(), NumberRange(min=0)])
    furnishing_status = SelectField('Furnishing Status', choices=[
        ('', 'Select Status'),
        ('fully', 'Fully Furnished'),
        ('semi', 'Semi Furnished'),
        ('unfurnished', 'Unfurnished')
    ], validators=[Optional()])
    gender_preference = SelectField('Gender Preference', choices=[
        ('', 'Select Preference'),
        ('male', 'Male Only'),
        ('female', 'Female Only'),
        ('coed', 'Co-ed')
    ], validators=[Optional()])
    meal_included = BooleanField('Meals Included')
    
    # File uploads
    images = MultipleFileField('Property Images (3-4 images)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    submit = SubmitField('Submit Property')

class PaymentForm(FlaskForm):
    transaction_id = StringField('UPI Transaction ID', validators=[DataRequired(), Length(min=5, max=100)])
    screenshot = FileField('Payment Screenshot', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Submit Payment Proof')

class InquiryForm(FlaskForm):
    message = TextAreaField('Your Message', validators=[DataRequired(), Length(min=10, max=500)], widget=TextArea())
    submit = SubmitField('Send Inquiry')

class SearchForm(FlaskForm):
    search = StringField('Search Properties')
    category = SelectField('Category', choices=[('', 'All Categories'), ('buy', 'Buy'), ('rent', 'Rent'), ('pg', 'PG/Hostel')])
    location = StringField('Location')
    min_price = IntegerField('Min Price (₹)', validators=[Optional(), NumberRange(min=0)])
    max_price = IntegerField('Max Price (₹)', validators=[Optional(), NumberRange(min=0)])
    property_type = SelectField('Property Type', choices=[
        ('', 'Any Type'),
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('plot', 'Plot'),
        ('office', 'Office'),
        ('shop', 'Shop'),
        ('warehouse', 'Warehouse'),
        ('pg', 'PG'),
        ('hostel', 'Hostel')
    ])
    bedrooms = SelectField('Min Bedrooms', choices=[('', 'Any'), ('1', '1+'), ('2', '2+'), ('3', '3+'), ('4', '4+'), ('5', '5+')])
    submit = SubmitField('Search')