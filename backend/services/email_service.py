import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def send_email(subject, recipient, body_html, body_text):
    """
    Sends an email to the recipient using smtplib.
    If mail configurations are not provided, it prints/logs the email to simulated logs.
    """
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT', 2525)
    use_tls = current_app.config.get('MAIL_USE_TLS', True)
    use_ssl = current_app.config.get('MAIL_USE_SSL', False)
    default_sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@rentflatmate.com')
    
    # Check if configurations are present. If not, log instead of raising an error.
    if not mail_server or not mail_username or not mail_password:
        logger.info("========== Simulated Email Notification (Local Development Mode) ==========")
        logger.info(f"To: {recipient}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body:\n{body_text}")
        logger.info("=========================================================================")
        return True
        
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = default_sender
        msg['To'] = recipient
        
        # Attach plain text and HTML bodies
        part1 = MIMEText(body_text, 'plain')
        part2 = MIMEText(body_html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect to server
        if use_ssl:
            server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=10)
        else:
            server = smtplib.SMTP(mail_server, mail_port, timeout=10)
            if use_tls:
                server.starttls()
                
        server.login(mail_username, mail_password)
        server.sendmail(default_sender, recipient, msg.as_string())
        server.quit()
        logger.info(f"Email successfully sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        # Print fallback logs on connection failure
        logger.info("========== Simulated Email Notification (Failed to connect to SMTP) ==========")
        logger.info(f"To: {recipient}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body:\n{body_text}")
        logger.info("=============================================================================")
        return False


def notify_owner_of_high_compatibility_interest(owner_email, tenant_email, listing_title, score):
    subject = f"🔥 High Compatibility Tenant Alert! {score}% score"
    
    body_text = f"""
    Hello,
    
    A tenant ({tenant_email}) has shown interest in your listing "{listing_title}".
    Our compatibility engine calculated a score of {score}% between them and your listing details.
    
    Log in to your dashboard to review their profile details, view their compatibility breakdown, and accept/reject their request.
    
    Best regards,
    Rent & Flatmate Finder Team
    """
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #6366f1;">🔥 High Compatibility Tenant Alert!</h2>
          <p>Hello,</p>
          <p>A tenant (<strong>{tenant_email}</strong>) has shown interest in your listing <strong>"{listing_title}"</strong>.</p>
          <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; border-left: 4px solid #6366f1; margin: 20px 0;">
            <p style="margin: 0; font-size: 18px; font-weight: bold; color: #1f2937;">Compatibility Score: {score}%</p>
          </div>
          <p>Log in to your dashboard to review their profile details, view their compatibility breakdown, and accept or reject their request.</p>
          <br/>
          <p style="font-size: 12px; color: #666;">Best regards,<br/>Rent & Flatmate Finder Team</p>
        </div>
      </body>
    </html>
    """
    return send_email(subject, owner_email, body_html, body_text)


def notify_tenant_request_accepted(tenant_email, owner_email, listing_title):
    subject = "🎉 Your Interest Request was Accepted!"
    
    body_text = f"""
    Hello,
    
    Great news! The property owner ({owner_email}) has accepted your interest request for the listing "{listing_title}".
    
    Real-time chat is now unlocked! Log in to your dashboard, navigate to the Chat tab, and message the owner to schedule a viewing or discuss details.
    
    Best regards,
    Rent & Flatmate Finder Team
    """
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #10b981;">🎉 Your Interest Request was Accepted!</h2>
          <p>Hello,</p>
          <p>Great news! The property owner (<strong>{owner_email}</strong>) has accepted your interest request for the listing <strong>"{listing_title}"</strong>.</p>
          <div style="background-color: #ecfdf5; padding: 15px; border-radius: 6px; border-left: 4px solid #10b981; margin: 20px 0;">
            <p style="margin: 0; font-weight: bold; color: #065f46;">Real-time Chat is now UNLOCKED!</p>
          </div>
          <p>Log in to your dashboard, navigate to the Chat tab, and message the owner directly to arrange a viewing or discuss further details.</p>
          <br/>
          <p style="font-size: 12px; color: #666;">Best regards,<br/>Rent & Flatmate Finder Team</p>
        </div>
      </body>
    </html>
    """
    return send_email(subject, tenant_email, body_html, body_text)


def notify_tenant_request_rejected(tenant_email, listing_title):
    subject = "Update on your Interest Request"
    
    body_text = f"""
    Hello,
    
    We wanted to inform you that your interest request for the listing "{listing_title}" has been declined by the owner.
    
    Don't lose hope! There are many listings available. Log in to your dashboard to keep searching for rooms that match your compatibility profile.
    
    Best regards,
    Rent & Flatmate Finder Team
    """
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #ef4444;">Update on your Interest Request</h2>
          <p>Hello,</p>
          <p>We wanted to inform you that your interest request for the listing <strong>"{listing_title}"</strong> has been declined by the owner.</p>
          <p>Don't lose hope! There are many options available. Log in to your dashboard to keep searching for rooms that match your compatibility profile.</p>
          <br/>
          <p style="font-size: 12px; color: #666;">Best regards,<br/>Rent & Flatmate Finder Team</p>
        </div>
      </body>
    </html>
    """
    return send_email(subject, tenant_email, body_html, body_text)
