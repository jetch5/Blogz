from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:admin@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return render_template('blog.html')

@app.route('/blog', methods=['GET'])
def blog():
    blog_id = request.args.get('id')
    
    if blog_id == None:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts, title='Build-a-blog')
    else:
        post = Blog.query.get(blog_id)
        return render_template('newpost.html', posts=posts title='New Entry')

@app.route('/entry', methods=['POST', 'GET'])
def new_post():
    
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a title"
        if not blog_body:
            body_error = "Please enter a blog to post"

        if not body_error or title_error:
            new_entry = Blog(blog_title, blog_body)
            db.session.add(new_entry)
            db.session.commit()
            return render_template('newpost.htlm', /blog?id={}'.format(new_entry.id))
        else:
            return render_template('entry.html', title='New Entry', title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')


if __name__ == "__main__":
    app.run()