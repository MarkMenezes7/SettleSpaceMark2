from flask import send_from_directory
from app import create_app, db
from app.models import User, Property, PropertyImage, Payment, Inquiry, Favorite
import os

app = create_app()

# Add route to serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files from the instance/uploads directory"""
    return send_from_directory(
        os.path.join(app.instance_path, 'uploads'), 
        filename
    )

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Property': Property,
        'PropertyImage': PropertyImage,
        'Payment': Payment,
        'Inquiry': Inquiry,
        'Favorite': Favorite
    }

def create_tables():
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(email='admin@settlespace.com').first()
    if not admin:
        admin = User(
            name='Admin User',
            email='admin@settlespace.com',
            phone='+91 9876543210',
            role='admin',
            is_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@settlespace.com / admin123")

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True)