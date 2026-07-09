from flask import current_app
from flask_mail import Message
from flask import render_template


def send_reset_email(to_email, reset_url):
    mail = current_app.extensions['mail']

    html = render_template("reset-password.html", activation_url=reset_url)
    msg = Message(
        subject='Recuperación de contraseña FMA Admin Panel',
        sender='soporte@coexca03.es',
        recipients=[to_email],
        html=html
    )

    mail.send(msg)
