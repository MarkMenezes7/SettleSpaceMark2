import smtplib
import logging

# Fixed import for Python 3.13 compatibility
try:
    from email.mime.text import MIMEText as MimeText
    from email.mime.multipart import MIMEMultipart as MimeMultipart
except ImportError:
    import email.mime.text
    import email.mime.multipart
    MimeText = email.mime.text.MIMEText
    MimeMultipart = email.mime.multipart.MIMEMultipart

# Optional Twilio import
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Warning: Twilio not available. SMS functionality will be disabled.")

from flask import current_app, flash

class TwoFactorService:
    """Service class for handling 2FA operations"""
    
    @staticmethod
    def send_email_otp(email, name, otp_code):
        """Send OTP via email using Gmail SMTP"""
        try:
            # Email configuration
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            sender_email = current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                current_app.logger.error("Email credentials not configured")
                return False
            
            # Create message
            message = MimeMultipart("alternative")
            message["Subject"] = "Settle Space - Verification Code"
            message["From"] = sender_email
            message["To"] = email
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Verification Code</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
                    .otp-code {{ background: #28a745; color: white; font-size: 32px; font-weight: bold; 
                               text-align: center; padding: 20px; margin: 20px 0; border-radius: 5px; 
                               letter-spacing: 5px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏠 Settle Space</h1>
                        <h2>Verification Code</h2>
                    </div>
                    <div class="content">
                        <h3>Hello {name}!</h3>
                        <p>Your verification code is:</p>
                        <div class="otp-code">{otp_code}</div>
                        <div class="warning">
                            <strong>⚠️ Important:</strong>
                            <ul>
                                <li>This code expires in <strong>10 minutes</strong></li>
                                <li>Never share this code with anyone</li>
                                <li>Settle Space will never ask for this code over phone or email</li>
                            </ul>
                        </div>
                        <p>If you didn't request this code, please ignore this email or contact support.</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 Settle Space | Find Your Perfect Property</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Settle Space - Verification Code
            
            Hello {name}!
            
            Your verification code is: {otp_code}
            
            IMPORTANT:
            - This code expires in 10 minutes
            - Never share this code with anyone
            
            © 2025 Settle Space
            """
            
            text_part = MimeText(text_content, "plain")
            html_part = MimeText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            current_app.logger.info(f"OTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send email OTP to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_sms_otp_verify_api(phone, name, otp_code):
        """Send OTP via SMS using Twilio Verify API"""
        print(f"\n{'='*70}")
        print(f"VERIFY API DEBUG - Starting SMS Verification")
        print(f"{'='*70}")
        print(f"Target Phone: {phone}")
        print(f"User Name: {name}")
        
        if not TWILIO_AVAILABLE:
            print("❌ ERROR: Twilio library not installed")
            current_app.logger.error("Twilio not available for SMS")
            return False
            
        try:
            # Get configuration
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            verify_service_sid = current_app.config.get('TWILIO_VERIFY_SERVICE_SID')
            
            print(f"\nConfiguration Check:")
            print(f"  Account SID: {account_sid[:10]}... (length: {len(account_sid) if account_sid else 0})")
            print(f"  Auth Token: {'*' * 10}... (length: {len(auth_token) if auth_token else 0})")
            print(f"  Verify Service SID: {verify_service_sid[:10] if verify_service_sid else 'MISSING'}... (length: {len(verify_service_sid) if verify_service_sid else 0})")
            
            if not all([account_sid, auth_token, verify_service_sid]):
                print("\n❌ ERROR: Missing Twilio credentials")
                print(f"   Account SID present: {bool(account_sid)}")
                print(f"   Auth Token present: {bool(auth_token)}")
                print(f"   Verify Service SID present: {bool(verify_service_sid)}")
                current_app.logger.error("Twilio Verify credentials not configured")
                return False
            
            # Initialize client
            print("\nInitializing Twilio client...")
            client = Client(account_sid, auth_token)
            print("✓ Client initialized successfully")
            
            # Format phone number
            original_phone = phone
            clean_phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
            
            # Indian phone number formatting
            if clean_phone.startswith('91') and len(clean_phone) == 12:
                formatted_phone = '+' + clean_phone
            elif len(clean_phone) == 10:
                formatted_phone = '+91' + clean_phone
            else:
                formatted_phone = '+91' + clean_phone.lstrip('0')
            
            print(f"\nPhone Number Formatting:")
            print(f"  Original: {original_phone}")
            print(f"  Cleaned: {clean_phone}")
            print(f"  Formatted: {formatted_phone}")
            
            # Send verification
            print(f"\nSending verification to Twilio Verify API...")
            print(f"  Service SID: {verify_service_sid}")
            print(f"  To: {formatted_phone}")
            print(f"  Channel: sms")
            
            verification = client.verify.v2.services(verify_service_sid) \
                .verifications \
                .create(to=formatted_phone, channel='sms')
            
            print(f"\n✅ SUCCESS! Verification request sent")
            print(f"  Verification SID: {verification.sid}")
            print(f"  Status: {verification.status}")
            print(f"  Channel: {verification.channel}")
            print(f"  To: {verification.to}")
            print(f"  Valid: {verification.valid}")
            print(f"{'='*70}\n")
            
            current_app.logger.info(f"Verify API SMS sent to {formatted_phone}, SID: {verification.sid}")
            return True
            
        except TwilioRestException as e:
            print(f"\n❌ TWILIO API ERROR")
            print(f"  Error Code: {e.code}")
            print(f"  Error Message: {e.msg}")
            print(f"  Status: {e.status}")
            print(f"  More Info: {e.uri}")
            print(f"{'='*70}\n")
            current_app.logger.error(f"Twilio API error: {e.code} - {e.msg}")
            return False
            
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR")
            print(f"  Error Type: {type(e).__name__}")
            print(f"  Error Message: {str(e)}")
            import traceback
            print(f"\nFull Traceback:")
            traceback.print_exc()
            print(f"{'='*70}\n")
            current_app.logger.error(f"Failed to send Verify API SMS: {str(e)}")
            return False

    @staticmethod
    def verify_sms_otp_verify_api(phone, otp_code):
        """Verify OTP code using Twilio Verify API"""
        print(f"\n{'='*70}")
        print(f"VERIFY API DEBUG - Verifying OTP Code")
        print(f"{'='*70}")
        print(f"Phone: {phone}")
        print(f"Code: {otp_code}")
        
        if not TWILIO_AVAILABLE:
            print("❌ ERROR: Twilio not available")
            return False
            
        try:
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            verify_service_sid = current_app.config.get('TWILIO_VERIFY_SERVICE_SID')
            
            if not all([account_sid, auth_token, verify_service_sid]):
                print("❌ ERROR: Missing credentials")
                return False
            
            client = Client(account_sid, auth_token)
            
            # Format phone (same as sending)
            clean_phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
            
            if clean_phone.startswith('91') and len(clean_phone) == 12:
                formatted_phone = '+' + clean_phone
            elif len(clean_phone) == 10:
                formatted_phone = '+91' + clean_phone
            else:
                formatted_phone = '+91' + clean_phone.lstrip('0')
            
            print(f"Formatted phone: {formatted_phone}")
            print(f"Checking code with Twilio...")
            
            verification_check = client.verify.v2.services(verify_service_sid) \
                .verification_checks \
                .create(to=formatted_phone, code=otp_code)
            
            print(f"\nVerification Result:")
            print(f"  Status: {verification_check.status}")
            print(f"  Valid: {verification_check.valid}")
            print(f"  SID: {verification_check.sid}")
            print(f"{'='*70}\n")
            
            return verification_check.status == 'approved'
            
        except TwilioRestException as e:
            print(f"\n❌ TWILIO VERIFICATION ERROR")
            print(f"  Error Code: {e.code}")
            print(f"  Error Message: {e.msg}")
            print(f"{'='*70}\n")
            return False
            
        except Exception as e:
            print(f"\n❌ VERIFICATION ERROR: {str(e)}")
            print(f"{'='*70}\n")
            return False
    
    @staticmethod
    def send_otp(user, method='email'):
        """Send OTP using specified method"""
        try:
            if method == 'email':
                otp_code = user.generate_otp(method)
                success = TwoFactorService.send_email_otp(user.email, user.name, otp_code)
                if success:
                    flash(f'Verification code sent to your email: {user.email[:3]}***@{user.email.split("@")[1]}', 'info')
                else:
                    flash('Failed to send email verification. Please try SMS instead.', 'error')
                return success
                
            elif method == 'sms':
                # Use Verify API - don't generate OTP ourselves
                success = TwoFactorService.send_sms_otp_verify_api(user.phone, user.name, None)
                
                if success:
                    masked_phone = user.phone[:3] + '*' * (len(user.phone) - 6) + user.phone[-3:]
                    flash(f'Verification code sent to your phone: {masked_phone}', 'info')
                else:
                    flash('Failed to send SMS verification. Please try email instead.', 'error')
                return success
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error sending OTP to user {user.id}: {str(e)}")
            flash('Failed to send verification code. Please try again.', 'error')
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email after successful registration"""
        try:
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            sender_email = current_app.config.get('MAIL_USERNAME')
            sender_password = current_app.config.get('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                return False
            
            message = MimeMultipart("alternative")
            message["Subject"] = "Welcome to Settle Space!"
            message["From"] = sender_email
            message["To"] = user.email
            
            role_specific_content = {
                'customer': {
                    'welcome_msg': 'Welcome to Settle Space! Start exploring amazing properties.',
                    'features': [
                        'Browse thousands of verified properties',
                        'Save your favorite properties',
                        'Send direct inquiries to property owners',
                        'Get personalized property recommendations'
                    ]
                },
                'seller': {
                    'welcome_msg': 'Welcome to Settle Space! Start listing your properties.',
                    'features': [
                        'List unlimited properties',
                        'Receive direct inquiries from buyers',
                        'Manage all your listings in one place',
                        'Track payment status and approvals'
                    ]
                }
            }
            
            content = role_specific_content.get(user.role, role_specific_content['customer'])
            features_html = ''.join([f'<li>{feature}</li>' for feature in content['features']])
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Welcome to Settle Space</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #007bff, #0056b3); color: white; 
                               padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .features {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                    .cta-button {{ background: #28a745; color: white; padding: 15px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block; 
                                  margin: 20px 0; font-weight: bold; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏠 Welcome to Settle Space!</h1>
                        <h2>Hello {user.name}!</h2>
                    </div>
                    <div class="content">
                        <p>{content['welcome_msg']}</p>
                        <div class="features">
                            <h3>What you can do:</h3>
                            <ul>{features_html}</ul>
                        </div>
                        <div style="text-align: center;">
                            <a href="{current_app.config.get('SERVER_URL', 'http://localhost:5000')}/login" 
                               class="cta-button">Login to Your Account</a>
                        </div>
                        <p>Need help? Our support team is always here to assist you.</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 Settle Space | Find Your Perfect Property</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_part = MimeText(html_content, "html")
            message.attach(html_part)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return False