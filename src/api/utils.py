from flask import current_app
from flask_email import Message

def send_reset_email(to_email, reset_url):
    mail=current_app.extensions['mail']
    
    html = open("src/templates/activation-email.html").read().replace(
        "{{activation_url}}", reset_url)
    msg = Message(
        subject='Recuperación de contraseña FMA Admin Panel',
        sender='fmapaneladmin@mgbdevops.es',
        recipients=[to_email],
        html=html
    )
    
    mail.send(msg)