from threading import Thread
from flask_mail import Message
from portfolio import portfolio, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(sender, recipients, subject, message):
    try:
        print(f"***** {sender=} {recipients=} {subject=} {message=}")
        msg = Message(subject, sender=sender, recipients=[recipients])
        msg.body = message
        Thread(target=send_async_email, args=(portfolio, msg)).start()
    except Exception as e:
        print(e)
