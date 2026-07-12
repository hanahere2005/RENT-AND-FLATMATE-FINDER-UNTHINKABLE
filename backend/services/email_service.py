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
    default_sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@staylio.com')
    
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


def notify_owner_of_interest(owner_email, listing_title, tenant_email, budget_min, budget_max, move_in_date, score=None):
    """
    Sends an email notification to the property owner when a tenant expresses interest.
    """
    subject = "🏠 New Interested Tenant Alert!"
    if score and score >= 80:
        subject = f"🔥 High Compatibility Tenant Alert! {score}% score"
        
    tenant_name = tenant_email.split('@')[0].capitalize()
    dashboard_link = "http://localhost:5173/owner-dashboard"
    
    body_text = f"""
    Hello,
    
    A tenant ({tenant_name}) has expressed interest in your listing "{listing_title}".
    
    Tenant Details:
    - Name: {tenant_name}
    - Email: {tenant_email}
    - Budget: ${budget_min} - ${budget_max} / month
    - Move-in Date: {move_in_date}
    """
    if score is not None:
        body_text += f"- Compatibility Score: {score}%\n"
        
    body_text += f"""
    Please log in to your owner dashboard to review their profile details, view their compatibility breakdown, and accept/decline their request.
    
    Owner Dashboard Link: {dashboard_link}
    
    Best regards,
    Staylio Team
    """
    
    # HTML version
    score_html = ""
    if score is not None:
        badge_color = "#10b981" if score >= 80 else ("#f59e0b" if score >= 50 else "#ef4444")
        score_html = f"""
          <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; border-left: 4px solid {badge_color}; margin: 20px 0;">
            <p style="margin: 0; font-size: 18px; font-weight: bold; color: #1f2937;">Compatibility Score: {score}% Match</p>
          </div>
        """
        
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #2563eb;">🏠 New Interested Tenant Alert!</h2>
          <p>Hello,</p>
          <p>A tenant has expressed interest in your listing <strong>"{listing_title}"</strong>.</p>
          
          <h3 style="border-bottom: 1px solid #eee; padding-bottom: 5px; color: #4b5563;">Tenant Details</h3>
          <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin-bottom: 8px;"><strong>Name:</strong> {tenant_name}</li>
            <li style="margin-bottom: 8px;"><strong>Email:</strong> <a href="mailto:{tenant_email}">{tenant_email}</a></li>
            <li style="margin-bottom: 8px;"><strong>Budget:</strong> ${budget_min} - ${budget_max} / month</li>
            <li style="margin-bottom: 8px;"><strong>Move-in Date:</strong> {move_in_date}</li>
          </ul>
          
          {score_html}
          
          <p>Log in to your dashboard to review their profile details, view their compatibility breakdown, and accept or reject their request.</p>
          <p style="margin-top: 25px;">
            <a href="{dashboard_link}" style="background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Go to Owner Dashboard</a>
          </p>
          <br/>
          <p style="font-size: 12px; color: #666;">Best regards,<br/>Staylio Team</p>
        </div>
      </body>
    </html>
    """
    return send_email(subject, owner_email, body_html, body_text)


def notify_tenant_request_accepted(tenant_email, owner_name, owner_email, listing_title):
    """
    Sends an email notification to the tenant when the owner accepts their interest request.
    """
    subject = "Your request has been accepted 🎉"
    chat_link = "http://localhost:5173/chat"
    
    body_text = f"""
    Hello,
    
    Great news! Your interest request for the property "{listing_title}" has been accepted by the owner, {owner_name}.
    
    Owner Details:
    - Name: {owner_name}
    - Email: {owner_email}
    
    Chat Availability:
    Real-time chat is now unlocked and available! You can now message the owner directly on our platform to arrange a viewing or discuss details.
    
    Chat Link: {chat_link}
    
    Best regards,
    Staylio Team
    """
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #10b981;">Your request has been accepted 🎉</h2>
          <p>Hello,</p>
          <p>Great news! Your interest request for the property <strong>"{listing_title}"</strong> has been accepted by the owner, <strong>{owner_name}</strong>.</p>
          
          <h3 style="border-bottom: 1px solid #eee; padding-bottom: 5px; color: #4b5563;">Owner Details</h3>
          <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin-bottom: 8px;"><strong>Name:</strong> {owner_name}</li>
            <li style="margin-bottom: 8px;"><strong>Email:</strong> <a href="mailto:{owner_email}">{owner_email}</a></li>
          </ul>
          
          <div style="background-color: #ecfdf5; padding: 15px; border-radius: 6px; border-left: 4px solid #10b981; margin: 20px 0;">
            <p style="margin: 0; font-weight: bold; color: #065f46;">💬 Real-time Chat is now UNLOCKED!</p>
            <p style="margin: 5px 0 0 0; font-size: 13px; color: #047857;">You can now message the owner in real-time on our platform to arrange viewings or ask questions.</p>
          </div>
          
          <p>Click the link below to go directly to your chats and connect with the owner:</p>
          <p style="margin-top: 20px;">
            <a href="{chat_link}" style="background-color: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Open Chat Room</a>
          </p>
          <br/>
          <p style="font-size: 12px; color: #666;">Best regards,<br/>Staylio Team</p>
        </div>
      </body>
    </html>
    """
    return send_email(subject, tenant_email, body_html, body_text)


def notify_tenant_request_rejected(tenant_email, listing_title):
    """
    Sends a polite email notification to the tenant when the owner declines their interest request.
    """
    subject = "Update on your Interest Request"
    
    body_text = f"""
    Hello,
    
    Thank you for your interest in the listing "{listing_title}".
    
    We wanted to politely inform you that the owner has decided to decline your interest request at this time.
    
    Don't lose hope! There are many other listings available. Log in to your tenant dashboard to continue your search and find rooms that match your compatibility profile.
    
    Best regards,
    Staylio Team
    """
    
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #ef4444;">Update on your Interest Request</h2>
          <p>Hello,</p>
          <p>Thank you for your interest in the listing <strong>"{listing_title}"</strong>.</p>
          <p>We wanted to politely inform you that the owner has decided to decline your interest request at this time.</p>
          <p>Don't lose hope! There are many other options available. Log in to your tenant dashboard to continue searching for rooms that match your compatibility profile.</p>
          <br/>
          <p style="font-size: 12px; color: #666;">Best regards,<br/>Staylio Team</p>
        </div>
      </body>
    </html>
    """
    return send_email(subject, tenant_email, body_html, body_text)


def notify_tenant_listing_booked(tenant_email, listing_title):
    """
    Sends an email notification to the tenant when the listing is marked as booked.
    """
    subject = f"Property Update: '{listing_title}' is no longer available"
    body_text = f"""
    Hello,
    
    Thank you for your interest in the listing "{listing_title}".
    
    We wanted to inform you that this property has now been booked and is no longer available.
    
    We encourage you to log back into Staylio and explore other great properties matching your compatibility score!
    
    Best regards,
    Staylio Team
    """
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
          <h2 style="color: #ef4444;">Update: Listing Booked</h2>
          <p>Hello,</p>
          <p>Thank you for your interest in the listing <strong>"{listing_title}"</strong>.</p>
          <p>We wanted to inform you that this property has now been booked and is no longer available.</p>
          <p>We encourage you to log back into Staylio and explore other great properties matching your compatibility score!</p>
          <br/>
          <p style="font-size: 12px; color: #666;">Best regards,<br/>Staylio Team</p>
        </div>
      </body>
    </html>
    """
    return send_email(subject, tenant_email, body_html, body_text)
