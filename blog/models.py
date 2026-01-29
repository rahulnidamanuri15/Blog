from blog import db
from datetime import datetime
from flask import current_app
from blog import login_manager
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    p_image=db.Column(db.String(100),nullable=False,default="account_circle1.png")
    password=db.Column(db.String(60),nullable=False)
    posts=db.relationship("Post",backref="author",lazy=True)

    def get_reset_token(self):
        s=URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps(self.id,salt="password-reset")
    
    @staticmethod
    def verify_reset_token(token,expires_sec=1800):
        s=URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            user_id=s.loads(token,salt="password-reset",max_age=expires_sec)
        except:
            None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.p_image}')"


class Post(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),unique=True,nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    content=db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"),nullable=False)


    def __repr__(self):
        return f"Post('{self.title}','{self.content}')"
