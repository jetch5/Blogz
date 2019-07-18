from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

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
    stamp = db.Column(db.Date)

    def __init__(self, title, body, owner_id, stamp):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        self.stamp = stamp

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

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
def register():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #TODO validate user data
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            #TODO - user better response messaging
            return '<h1>Duplicate User - username already in use</h1>'
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def base():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    
    if blog_id == None:
        users = User.query.all()
        return render_template('blog.html', users=users, title='Blogz')
    else:
        post = Blog.query.filter_by(owner_id=blog_id)
        return render_template('newpost.html', post=post, title='Blog Post')

@app.route('/entry')
def entry_form():
    return render_template('entry.html', title = "")

@app.route('/entryCheck', methods=['POST', 'GET'])
def new_post():
    blog_title = ""
    blog_body = ""
    title_error = ""
    blog_error = ""
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        if not blog_title:
            title_error = "Please enter a title"
        if not blog_body:
            blog_error = "Please enter a blog to post"
        if not blog_error and not title_error:
            new_post = Blog(blog_title, blog_body)
            db.session.add(new_post)
            db.session.commit()
            return render_template('newpost.html', post = new_post, title='Blog Post')
        else:
            return render_template('entry.html', title='New Entry', title_error=title_error, blog_error=blog_error, blog_title=blog_title, blog_body=blog_body)

if __name__ == "__main__":
    app.run()