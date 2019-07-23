from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'today'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/')
def base():
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/signup')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('You are logged in' + username)
            return redirect('/newpost.html')
        else:
            flash('User password incorrect or user does not exist')
            return redirect('/login')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        existing_user = User.query.filter_by(username=username).first()
        username_error = ""
        if len(username) < 3 or len(username)> 20:
            username_error = "Length is not valid"
        elif not username:
            username_error = "Username is required"
        elif existing_user:
            username_error = "Username already in use"
       

        password = request.form['password']
        password_error = ""
        if not password:
            password_error = "Password is required"
        elif len(password) < 3 or len(password) > 20:
            password_error = "Password length is not valid"
        

        verify = request.form['verify']
        verify_error = ""
        if verify != password:
            verify_error = "Does not match password"
        else:
            pass
        
        if not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', username_error=username_error, password_error= password_error, verify_error=verify_error)
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    
    if blog_id == None:
        users = User.query.all()
        return render_template('blog.html', users=users, title='Blogz')
    else:
        post = Blog.query.filter_by(owner_id=blog_id)
        return render_template('allposts.html', post=post, title='Blog Post')

@app.route('/allposts', methods=['GET'])
def allposts():
    blog_post = request.args.get('id')
    
    if blog_post == None:
        blogs = Blog.query.all()
        return render_template('allposts.html', blogs=blogs, title='Blogz')
    else:
        post = Blog.query.filter_by(owner_id=blog_post).all()
        return render_template('allposts.html', blogs=post, title='Blog Post')


@app.route('/newpost')
def entry_form():
    return render_template('newpost.html', title = "")

@app.route('/entryCheck', methods=['POST', 'GET'])
def new_post():
    blog_title = ""
    blog_body = ""
    title_error = ""
    blog_error = ""
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        owner = User.query.filter_by(username=session['username']).first()
        owner_id = owner.id
        if not blog_title:
            title_error = "Please enter a title"
        if not blog_body:
            blog_error = "Please enter a blog to post"
        if not blog_error and not title_error:
            new_post = Blog(blog_title, blog_body, owner_id)
            db.session.add(new_post)
            db.session.commit()
            return render_template('singleUser.html', post = new_post, title='Blog Post')
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, blog_error=blog_error, blog_title=blog_title, blog_body=blog_body)

if __name__ == "__main__":
    app.run()