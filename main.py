import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Content Blog", validators=[DataRequired()])
    submit = SubmitField("Submit Post")




@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    posts = db.session.query(BlogPost).all()
    requested_post = None
    for blog_post in posts:
        if blog_post.to_dict()['id'] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route('/new-post', methods=['GET', 'POST'])
def make_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        blog_content = form.body.data
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=datetime.date.today(),
            body=blog_content,
            author=form.author.data,
            img_url=form.img_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form, is_edit=False)


@app.route('/edit-post/', methods=['GET', 'POST'])
def edit_post():
    id = request.args.get('id')
    post = BlogPost.query.get(id)
    form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        body=post.body,
        author=post.author,
        img_url=post.img_url
    )
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.date = datetime.date.today()
        post.body = form.body.data
        post.author = form.author.data
        post.img_url = form.img_url.data
        db.session.commit()
        return redirect(url_for('show_post', index=id))
    return render_template('make-post.html', form=form, is_edit=True)

@app.route('/delete/<id>')
def delete_post(id):
    post_to_delete = BlogPost.query.get(id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
