from app import app
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegisterForm, LoginForm, PostForm
from app.models import User, Post


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/register', methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Get the data from the form
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if either the username or email is already in db
        user_exists = User.query.filter((User.username == username)|(User.email == email)).all()
        # if it is, return back to register
        if user_exists:
            flash(f"User with username {username} or email {email} already exists", "danger")
            return redirect(url_for('register'))
        # Create a new user instance using form data
        User(username=username, email=email, password=password)
        flash("Thank you for registering!", "primary")
        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        
        # Grab the data from the form
        username = form.username.data
        password = form.password.data
       
        # Query user table for user with username
        user = User.query.filter_by(username=username).first()
        
        # if the user does not exist or the user has an incorrect password
        if not user or not user.check_password(password):
            # redirect to login page
            flash('That username and/or password is incorrect', 'danger')
            return redirect(url_for('login'))
        
        # if user does exist and correct password, log user in
        login_user(user)
        flash('You have succesfully logged in', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have successfully logged out", "secondary")
    return redirect(url_for('index'))


@app.route('/posts/<int:post_id>')
@login_required
def post_info(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    if not current_user.is_admin:
        flash("You do not have access.", "warning")
        return redirect(url_for('index'))
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        # Get data from form
        author = form.author.data
        title = form.title.data
        content = form.content.data

        # Update with the new info
        post.author = author
        post.title = title
        post.content = content

        post.save()

        
        # flash message
        flash(f"{post.title} has been updated", "primary")
        return redirect(url_for('post_info', post_id=post.id))

    return render_template('edit_post.html', post=post, form=form)


@app.route('/posts/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    if not current_user.is_admin:
        flash("You do not have access.", "warning")
        return redirect(url_for('index'))
    post = Post.query.get_or_404(post_id)
    post.delete()
    flash(f'{post.title} has been deleted', 'danger')
    return redirect(url_for('index'))