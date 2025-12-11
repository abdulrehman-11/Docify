import logging
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending appointment-related emails."""
    
    def __init__(self):
        # SMTP Configuration from environment variables
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Hexaa Clinic")
        self.clinic_phone = os.getenv("CLINIC_PHONE", "(518) 400-6003")
        self.clinic_address = os.getenv("CLINIC_ADDRESS", "123 Clinic Way, Suite 200, Springfield, ST")
        
        # Check if email is configured
        self.is_configured = bool(self.smtp_user and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("⚠️  Email service NOT configured - emails will NOT be sent")
            logger.warning("⚠️  Set SMTP_USER and SMTP_PASSWORD in .env.local to enable emails")
        else:
            logger.info(f"✅ Email service configured - will send from {self.from_email}")
    
    def _send_email(self, to_email: str, subject: str, text_body: str, html_body: str) -> bool:
        """Internal method to send email via SMTP."""
        if not self.is_configured:
            logger.warning(f"Email not configured - skipping email to {to_email}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Attach text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send via SMTP
            logger.info(f"📧 Sending email to {to_email}: {subject}")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error(f"❌ SMTP Authentication failed - check SMTP_USER and SMTP_PASSWORD")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error sending email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email to {to_email}: {e}")
            return False
    
    def send_appointment_confirmation(
        self,
        patient_name: str,
        patient_email: str,
        appointment_date: datetime,
        appointment_time_start: str,
        appointment_time_end: str,
        reason: str,
        confirmation_id: str,
        phone: Optional[str] = None
    ) -> bool:
        """Send appointment booking confirmation email."""
        
        # Format date and time
        date_formatted = appointment_date.strftime("%A, %B %d, %Y")
        time_start_formatted = appointment_date.strftime("%I:%M %p").lstrip("0")
        
        try:
            time_end = datetime.fromisoformat(appointment_time_end.replace("Z", "+00:00"))
            time_end_formatted = time_end.strftime("%I:%M %p").lstrip("0")
        except:
            time_end_formatted = "30 min"
        
        subject = f"✅ Appointment Confirmed - {date_formatted}"
        
        # Plain text version
        text_body = f"""
Hello {patient_name},

Your appointment has been successfully confirmed!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPOINTMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Date:           {date_formatted}
⏰ Time:           {time_start_formatted} - {time_end_formatted}
📋 Reason:         {reason}
🔖 Confirmation:   {confirmation_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLINIC LOCATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self.from_name}
{self.clinic_address}
Phone: {self.clinic_phone}

{f"Your contact number: {phone}" if phone else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT REMINDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Please arrive 10-15 minutes early
✓ Bring your insurance card and photo ID
✓ Bring a list of current medications
✓ To cancel or reschedule, call us at least 24 hours in advance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Need to make changes? Call us at {self.clinic_phone}

We look forward to seeing you!

Best regards,
The {self.from_name} Team

---
This is an automated confirmation. Please do not reply to this email.
If you did not book this appointment, please contact us immediately.
        """
        
        # HTML version (beautiful design)
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header .checkmark {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }}
        .details-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 25px;
            margin: 25px 0;
            border-radius: 8px;
        }}
        .details-box h2 {{
            margin-top: 0;
            color: #667eea;
            font-size: 20px;
            margin-bottom: 20px;
        }}
        .detail-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .detail-icon {{
            font-size: 20px;
            width: 30px;
            flex-shrink: 0;
        }}
        .detail-label {{
            font-weight: 600;
            color: #555;
            min-width: 120px;
        }}
        .detail-value {{
            color: #333;
            flex-grow: 1;
        }}
        .location-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
            text-align: center;
        }}
        .location-box h3 {{
            margin-top: 0;
            color: #1976d2;
            font-size: 18px;
        }}
        .location-box p {{
            margin: 8px 0;
            color: #424242;
        }}
        .reminders-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 25px 0;
            border-radius: 8px;
        }}
        .reminders-box h3 {{
            margin-top: 0;
            color: #856404;
            font-size: 18px;
        }}
        .reminders-box ul {{
            margin: 10px 0;
            padding-left: 25px;
            color: #856404;
        }}
        .reminders-box li {{
            margin: 8px 0;
            line-height: 1.5;
        }}
        .btn {{
            display: inline-block;
            padding: 14px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
            transition: transform 0.2s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
        }}
        .cta-section {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 25px;
            text-align: center;
            color: #666;
            font-size: 13px;
            line-height: 1.6;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        @media only screen and (max-width: 600px) {{
            .content {{
                padding: 30px 20px;
            }}
            .detail-row {{
                flex-direction: column;
            }}
            .detail-label {{
                min-width: auto;
                margin-bottom: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="checkmark">✓</div>
            <h1>Appointment Confirmed</h1>
        </div>
        
        <!-- Content -->
        <div class="content">
            <div class="greeting">
                Hello <strong>{patient_name}</strong>,
            </div>
            
            <p>Your appointment has been successfully booked! We look forward to seeing you.</p>
            
            <!-- Appointment Details -->
            <div class="details-box">
                <h2>📋 Appointment Details</h2>
                <div class="detail-row">
                    <span class="detail-icon">📅</span>
                    <span class="detail-label">Date:</span>
                    <span class="detail-value">{date_formatted}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-icon">⏰</span>
                    <span class="detail-label">Time:</span>
                    <span class="detail-value">{time_start_formatted} - {time_end_formatted}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-icon">📋</span>
                    <span class="detail-label">Reason:</span>
                    <span class="detail-value">{reason}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-icon">🔖</span>
                    <span class="detail-label">Confirmation ID:</span>
                    <span class="detail-value">{confirmation_id}</span>
                </div>
            </div>
            
            <!-- Location -->
            <div class="location-box">
                <h3>📍 Clinic Location</h3>
                <p><strong>{self.from_name}</strong></p>
                <p>{self.clinic_address}</p>
                <p><strong>Phone:</strong> {self.clinic_phone}</p>
                {f'<p style="margin-top: 15px;"><strong>Your contact:</strong> {phone}</p>' if phone else ''}
            </div>
            
            <!-- Important Reminders -->
            <div class="reminders-box">
                <h3>⚠️ Important Reminders</h3>
                <ul>
                    <li><strong>Arrive 10-15 minutes early</strong> to complete any necessary paperwork</li>
                    <li>Bring your <strong>insurance card and photo ID</strong></li>
                    <li>Bring a <strong>list of current medications</strong></li>
                    <li>To cancel or reschedule, please call us <strong>at least 24 hours in advance</strong></li>
                </ul>
            </div>
            
            <!-- Call to Action -->
            <div class="cta-section">
                <p style="margin-bottom: 15px; color: #555;">Need to make changes to your appointment?</p>
                <a href="tel:{self.clinic_phone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')}" class="btn">
                    📞 Call Us: {self.clinic_phone}
                </a>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>This is an automated confirmation email from {self.from_name}.</strong></p>
            <p>Please do not reply to this email. For questions, call us at {self.clinic_phone}.</p>
            <p style="margin-top: 15px;">If you did not book this appointment, please contact us immediately.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self._send_email(patient_email, subject, text_body, html_body)
    
    def send_cancellation_email(
        self,
        patient_name: str,
        patient_email: str,
        appointment_date: datetime,
        appointment_time: str,
        reason: str
    ) -> bool:
        """Send appointment cancellation confirmation email."""
        
        date_formatted = appointment_date.strftime("%A, %B %d, %Y")
        time_formatted = appointment_date.strftime("%I:%M %p").lstrip("0")
        
        subject = f"❌ Appointment Cancelled - {date_formatted}"
        
        # Plain text version
        text_body = f"""
Hello {patient_name},

Your appointment has been cancelled as requested.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CANCELLED APPOINTMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Date:     {date_formatted}
⏰ Time:     {time_formatted}
📋 Reason:   {reason}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Would you like to reschedule?

Call us at {self.clinic_phone} to book a new appointment.
We're here to help!

Best regards,
The {self.from_name} Team

---
This is an automated notification. Please do not reply to this email.
        """
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .details-box {{
            background: #fff5f5;
            border-left: 4px solid #dc3545;
            padding: 25px;
            margin: 25px 0;
            border-radius: 8px;
        }}
        .details-box h2 {{
            margin-top: 0;
            color: #dc3545;
            font-size: 20px;
        }}
        .detail-row {{
            padding: 10px 0;
            color: #555;
        }}
        .detail-label {{
            font-weight: 600;
            display: inline-block;
            width: 80px;
        }}
        .cta-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 30px;
            text-align: center;
            border-radius: 8px;
            margin: 25px 0;
        }}
        .cta-box h3 {{
            margin-top: 0;
            color: #1976d2;
        }}
        .btn {{
            display: inline-block;
            padding: 14px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 15px 0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 25px;
            text-align: center;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="icon">✗</div>
            <h1>Appointment Cancelled</h1>
        </div>
        
        <div class="content">
            <p>Hello <strong>{patient_name}</strong>,</p>
            <p>Your appointment has been cancelled as requested.</p>
            
            <div class="details-box">
                <h2>Cancelled Appointment</h2>
                <div class="detail-row">
                    <span class="detail-label">📅 Date:</span>
                    <span>{date_formatted}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">⏰ Time:</span>
                    <span>{time_formatted}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">📋 Reason:</span>
                    <span>{reason}</span>
                </div>
            </div>
            
            <div class="cta-box">
                <h3>Would You Like to Reschedule?</h3>
                <p>We'd love to see you at another time!</p>
                <a href="tel:{self.clinic_phone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')}" class="btn">
                    📞 Call to Reschedule: {self.clinic_phone}
                </a>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>This is an automated notification from {self.from_name}.</strong></p>
            <p>For questions, call us at {self.clinic_phone}.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self._send_email(patient_email, subject, text_body, html_body)
    
    def send_reschedule_email(
        self,
        patient_name: str,
        patient_email: str,
        old_date: datetime,
        old_time: str,
        new_date: datetime,
        new_time_start: str,
        new_time_end: str,
        reason: str,
        confirmation_id: str,
        phone: Optional[str] = None
    ) -> bool:
        """Send appointment reschedule confirmation email."""
        
        old_date_formatted = old_date.strftime("%A, %B %d, %Y")
        old_time_formatted = old_date.strftime("%I:%M %p").lstrip("0")
        
        new_date_formatted = new_date.strftime("%A, %B %d, %Y")
        new_time_start_formatted = new_date.strftime("%I:%M %p").lstrip("0")
        
        try:
            new_time_end_dt = datetime.fromisoformat(new_time_end.replace("Z", "+00:00"))
            new_time_end_formatted = new_time_end_dt.strftime("%I:%M %p").lstrip("0")
        except:
            new_time_end_formatted = "30 min"
        
        subject = f"🔄 Appointment Rescheduled - {new_date_formatted}"
        
        # Plain text version
        text_body = f"""
Hello {patient_name},

Your appointment has been successfully rescheduled!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OLD APPOINTMENT (CANCELLED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Date:     {old_date_formatted}
⏰ Time:     {old_time_formatted}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEW APPOINTMENT (CONFIRMED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Date:           {new_date_formatted}
⏰ Time:           {new_time_start_formatted} - {new_time_end_formatted}
📋 Reason:         {reason}
🔖 Confirmation:   {confirmation_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLINIC LOCATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self.from_name}
{self.clinic_address}
Phone: {self.clinic_phone}

{f"Your contact number: {phone}" if phone else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT REMINDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Please arrive 10-15 minutes early
✓ Bring your insurance card and photo ID
✓ Bring a list of current medications

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Need to make changes? Call us at {self.clinic_phone}

We look forward to seeing you!

Best regards,
The {self.from_name} Team

---
This is an automated confirmation. Please do not reply to this email.
        """
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .old-appointment {{
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        .old-appointment h3 {{
            margin-top: 0;
            color: #c62828;
        }}
        .new-appointment {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 25px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        .new-appointment h2 {{
            margin-top: 0;
            color: #2e7d32;
            font-size: 20px;
        }}
        .detail-row {{
            padding: 10px 0;
            display: flex;
        }}
        .detail-label {{
            font-weight: 600;
            min-width: 130px;
            color: #555;
        }}
        .detail-value {{
            color: #333;
        }}
        .location-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
            text-align: center;
        }}
        .location-box h3 {{
            margin-top: 0;
            color: #1976d2;
        }}
        .reminders-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 25px 0;
            border-radius: 8px;
        }}
        .reminders-box ul {{
            margin: 10px 0;
            padding-left: 25px;
            color: #856404;
        }}
        .btn {{
            display: inline-block;
            padding: 14px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 15px 0;
        }}
        .cta-section {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 25px;
            text-align: center;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="icon">🔄</div>
            <h1>Appointment Rescheduled</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{patient_name}</strong>,</p>
            <p>Your appointment has been successfully rescheduled!</p>
            
            <!-- Old Appointment -->
            <div class="old-appointment">
                <h3>❌ Previous Appointment (Cancelled)</h3>
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    <span class="detail-value">{old_date_formatted}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Time:</span>
                    <span class="detail-value">{old_time_formatted}</span>
                </div>
            </div>
            
            <!-- New Appointment -->
            <div class="new-appointment">
                <h2>✅ New Appointment (Confirmed)</h2>
                <div class="detail-row">
                    <span class="detail-label">📅 Date:</span>
                    <span class="detail-value">{new_date_formatted}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">⏰ Time:</span>
                    <span class="detail-value">{new_time_start_formatted} - {new_time_end_formatted}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">📋 Reason:</span>
                    <span class="detail-value">{reason}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">🔖 Confirmation:</span>
                    <span class="detail-value">{confirmation_id}</span>
                </div>
            </div>
            
            <!-- Location -->
            <div class="location-box">
                <h3>📍 Clinic Location</h3>
                <p><strong>{self.from_name}</strong></p>
                <p>{self.clinic_address}</p>
                <p><strong>Phone:</strong> {self.clinic_phone}</p>
                {f'<p style="margin-top: 15px;"><strong>Your contact:</strong> {phone}</p>' if phone else ''}
            </div>
            
            <!-- Reminders -->
            <div class="reminders-box">
                <h3>⚠️ Important Reminders</h3>
                <ul>
                    <li>Arrive 10-15 minutes early</li>
                    <li>Bring insurance card and photo ID</li>
                    <li>Bring list of current medications</li>
                </ul>
            </div>
            
            <!-- CTA -->
            <div class="cta-section">
                <p>Need to make more changes?</p>
                <a href="tel:{self.clinic_phone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')}" class="btn">
                    📞 Call Us: {self.clinic_phone}
                </a>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>This is an automated confirmation from {self.from_name}.</strong></p>
            <p>For questions, call us at {self.clinic_phone}.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self._send_email(patient_email, subject, text_body, html_body)


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get the singleton email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service