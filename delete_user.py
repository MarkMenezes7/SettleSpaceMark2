"""
Script to delete a user account and all related data from the database
Usage: python delete_user.py
"""

from app import create_app, db
from app.models import User, Property, PropertyImage, Payment, Inquiry, Favorite, OTPCode
import os

def delete_user_by_phone(phone_number):
    """
    Delete a user and all their related data from the database
    """
    app = create_app()
    
    with app.app_context():
        # Find user by phone number
        user = User.query.filter_by(phone=phone_number).first()
        
        if not user:
            print(f"❌ No user found with phone number: {phone_number}")
            return False
        
        print(f"Found user: {user.name} ({user.email})")
        print(f"Role: {user.role}")
        print(f"Created: {user.created_at}")
        
        # Confirm deletion
        confirm = input("\n⚠️  Are you sure you want to delete this user? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Deletion cancelled.")
            return False
        
        print("\n🗑️  Starting deletion process...")
        
        try:
            # 1. Delete OTP codes
            otp_count = OTPCode.query.filter_by(user_id=user.id).delete()
            print(f"✓ Deleted {otp_count} OTP codes")
            
            # 2. Delete favorites
            favorite_count = Favorite.query.filter_by(user_id=user.id).delete()
            print(f"✓ Deleted {favorite_count} favorites")
            
            # 3. Delete inquiries (both sent and received)
            inquiries_sent = Inquiry.query.filter_by(customer_id=user.id).delete()
            inquiries_received = Inquiry.query.filter_by(seller_id=user.id).delete()
            print(f"✓ Deleted {inquiries_sent} inquiries sent")
            print(f"✓ Deleted {inquiries_received} inquiries received")
            
            # 4. Delete payments
            payment_count = Payment.query.filter_by(seller_id=user.id).delete()
            print(f"✓ Deleted {payment_count} payments")
            
            # 5. Delete property images and properties (if seller)
            if user.role == 'seller':
                properties = Property.query.filter_by(seller_id=user.id).all()
                
                for prop in properties:
                    # Delete physical image files
                    images = PropertyImage.query.filter_by(property_id=prop.id).all()
                    for img in images:
                        img_path = os.path.join('app/static/uploads', img.filename)
                        if os.path.exists(img_path):
                            os.remove(img_path)
                            print(f"  ✓ Deleted image file: {img.filename}")
                    
                    # Delete property images from DB
                    PropertyImage.query.filter_by(property_id=prop.id).delete()
                    
                # Delete properties
                property_count = Property.query.filter_by(seller_id=user.id).delete()
                print(f"✓ Deleted {property_count} properties")
            
            # 6. Finally, delete the user
            db.session.delete(user)
            db.session.commit()
            
            print(f"\n✅ User account for {phone_number} has been completely deleted!")
            print("   All related data has been removed from the database.")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during deletion: {str(e)}")
            return False

if __name__ == '__main__':
    # The phone number you want to delete
    PHONE_TO_DELETE = '8452857820'
    
    print("=" * 60)
    print("USER ACCOUNT DELETION SCRIPT")
    print("=" * 60)
    print(f"\nTarget phone number: {PHONE_TO_DELETE}")
    
    delete_user_by_phone(PHONE_TO_DELETE)