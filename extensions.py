from flask_mail import Mail, Message

mail = Mail()

def send_email(to, subject, html):
    msg = Message(subject, recipients=[to])
    msg.html = html
    mail.send(msg)   # requires an active app context