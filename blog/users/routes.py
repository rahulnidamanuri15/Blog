from flask import render_template,url_for,flash,redirect,request,Blueprint
from blog.users.forms import RegistrationForm,LoginForm,UpdateAccountForm,RequestResetForm,PasswordResetForm
from blog import bcrypt,db,mail
from blog.models import User,Post
from flask_login import current_user,login_user,logout_user,login_required
from blog.users.utils import save_p_image,send_reset_email

users=Blueprint("users",__name__)


@users.route("/register",methods=["POST","GET"])
def register():
    if current_user.is_authenticated:
        return redirect('home')
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Yor Account has been successfully Created! Now You are able to LogIn.","success")
        return redirect(url_for('users.login'))
    return render_template("register.html",form=form)


@users.route("/login",methods=["POST","GET"])
def login():
    if current_user.is_authenticated:
        return redirect('home')
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            flash(f"Yor Account has been successfully LoggedIn.","success")
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash("Login Unsuccessful! please check email and Password.","danger")
            return redirect(url_for('users.login'))
    return render_template("login.html",form=form)




@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account",methods=["POST","GET"])
@login_required
def account():
    form=UpdateAccountForm()
    p_image=url_for("static",filename="profilepics/"+current_user.p_image)
    if form.validate_on_submit():
        if form.p_image.data:
            pfimage=save_p_image(form.p_image.data)
            current_user.p_image=pfimage

        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash("Your Details are Updated Successfully.","success")
        return redirect(url_for("users.account"))
    elif request.method=="GET":
        form.username.data=current_user.username
        form.email.data=current_user.email
    return render_template("account.html",form=form,p_image=p_image)

@users.route("/user/<string:username>")
def user_posts(username):
    page= request.args.get('page',1,type=int)
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template("user_posts.html",posts=posts,user=user)



 
@users.route("/reset_password",methods=["POST","GET"])
def request_reset():
    if current_user.is_authenticated:
        return redirect('home')
    form=RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has sent with instructions for password reset","success")
        return redirect(url_for("users.login"))
    return render_template("request_reset.html",form=form)


@users.route("/reset_password/<token>",methods=["POST","GET"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('home')
    user=User.verify_reset_token(token)
    if user is None:
        flash("The Link has expired or invalid!","warning")
        return redirect(url_for("users.request_reset"))
    form=PasswordResetForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash(f"Your Password Updated Successfully!","success")
        return redirect(url_for('users.login'))
    return render_template("reset_password.html",form=form)