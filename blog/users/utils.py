import secrets
import os
from PIL import Image
from flask import url_for,current_app
from blog import mail
from flask_mail import Message

def save_p_image(form_p_image):
    random_hex=secrets.token_hex(8)
    _,p_ext=os.path.splitext(form_p_image.filename)
    p_fn = random_hex+p_ext
    p_path=os.path.join(current_app.root_path,"static/profilepics",p_fn)

    output_size=(225,225)
    i=Image.open(form_p_image)
    i.thumbnail(output_size)
    i.save(p_path)
    return p_fn


def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message("Password Reset Request",sender="noreply@demo.com",recipients=[user.email])
    msg.body=f'''To Reset Your Password, Please Visit below Link
    {url_for('users.reset_token',token=token,_external=True)}
If this is not done by You,Please Ignore it.
'''
    mail.send(msg)