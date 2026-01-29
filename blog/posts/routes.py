from flask import render_template,url_for,flash,redirect,request,abort,Blueprint
from blog.posts.forms import PostForm
from blog import db
from blog.models import Post
from flask_login import current_user,login_required

posts=Blueprint("posts",__name__)



@posts.route("/post/new",methods=["POST","GET"])
@login_required
def new_post():
    form=PostForm()
    if form.validate_on_submit():
        post= Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("You have successfully created a new Post!","success")
        return redirect(url_for("main.home"))
    return render_template("create_post.html",form=form,legend="New Post")


@posts.route("/post/<int:id>")
def view_post(id):
   post=Post.query.get_or_404(id)
   return render_template("post.html",post=post)


@posts.route("/post/<int:id>/update",methods=["POST","GET"])
def update_post(id):
   if current_user.is_authenticated:
       show=True
   else:
       show=False

   post=Post.query.get_or_404(id)
   if post.author != current_user:
       abort(403)

   form=PostForm()
   if form.validate_on_submit():
       post.title=form.title.data
       post.content=form.content.data
       db.session.commit()
       flash("Post Updated Successfully","success")
       return redirect(url_for("posts.view_post",id=post.id))
   elif request.method =="GET":
        form.title.data=post.title
        form.content.data=post.content

   return render_template("create_post.html",form=form,legend="Update Post",show=show)
 


@posts.route("/post/<int:id>/delete",methods=["POST","GET"])
def delete_post(id):
   post=Post.query.get_or_404(id)
   if post.author != current_user:
       abort(403)
   
   db.session.delete(post)
   db.session.commit()
   flash("Your Post has been deleted!","success")
   return redirect(url_for('main.home'))


