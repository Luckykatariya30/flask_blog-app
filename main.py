from flask import Flask,render_template, request , redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
import json
import os
import math
from werkzeug.utils import secure_filename

with open('config.py','r')as c:
    params =json.load(c)['params']
app = Flask(__name__)
app.config['Uloaded_File'] = params['uploaded_file']
app.secret_key = 'super secret-key by lucky'
# app.config.update(
# 	#EMAIL SETTINGS
# 	MAIL_SERVER='smtp.gmail.com',
# 	MAIL_PORT=465,
# 	MAIL_USE_SSL=True,
# 	MAIL_USERNAME = 'luckykatariya36@gmail.com',
# 	MAIL_PASSWORD = 'lks123lk'
# 	)
# mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']
db = SQLAlchemy(app)


class Profile(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    phone_num = db.Column(db.String(20), nullable=False)
    msg = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"Name : {self.name}, Email: {self.email} , Phone No. {self.phone_num}"

class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=False, nullable=False)
    slug = db.Column(db.String(20),  nullable=False)
    context = db.Column(db.String(200), nullable=False)
    img_file =db.Column(db.String(12),nullable=False)
    date = db.Column(db.String(50), nullable=True)
    tagline = db.Column(db.String(50), nullable=False)
    
class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(255),nullable = False)
    userpass = db.Column(db.String(232),nullable = False)
    date = db.Column(db.String(50), nullable = False)
    
@app.route("/")
def home():
    post = Post.query.filter_by().all()
    last = math.ceil(len(post)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    post = post[(page-1)*int(params['no_of_posts']) : (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page+1)
    elif page  == last:
        prev = "/?page=" + str(page-1)
        next = "#"
    else:
        prev = "/?page=" + str(page-1)
        next = "/?page="+ str(page+1)
    return render_template('index.html', posts = post , prev=prev, next = next)



@app.route("/logout")
def logout():
    if ('user' in session and session['user'] == params['user_name']):
        session.pop('user')
        return redirect("/dashboard")
    
    
    
@app.route("/about")
def about():
    return render_template('about.html')




@app.route("/post/<string:post_slug>",methods=['GET'])
def sinmle_post(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    print(post)
    return render_template('post.html',post = post)





@app.route("/contact",methods = ['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone_no')
        message = request.form.get('message')
        date = datetime.now()
        entry = Profile(name = name, email=email, phone_num = phone, msg = message ,date = date)
        db.session.add(entry)
        db.session.commit()
        # msg = Message("Send Mail Tutorial!",
        #               sender='luckykatariya36@gmail.com',
        #               recipients=['luckykatariya30@gmail.com'])
        # msg.body = 'yo!\nHave you heard the good word of python'
        # mail.send(msg)
    return render_template('contact.html')





@app.route("/dashboard",methods = ['GET','POST'])
def dashboard():
    if ('user' in session and session['user'] == params['user_name']):
        posts = Post.query.all()
        return render_template('dashboard.html', posts = posts)
    if request.method=="POST":
        username = request.form.get('username')
        userpass = request.form.get('userpass')
        if username == params['user_name'] and userpass==params['user_pass']:
            #set the session variable
            session['user']= username
            posts = Post.query.all()
            return render_template('dashboard.html', posts=posts)
    else:
        return render_template('login.html')
    
    
@app.route("/edit/<string:sno>" , methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['user_name']):
        if request.method=="POST":
            print(sno)
            title = request.form.get('title')
            slug = request.form.get('slug')
            img_file = request.form.get('img_file')
            content = request.form.get('content')
            tagline = request.form.get('tagline')
            date = datetime.now()
            if sno == '0':
                post =Post(title = title,slug = slug, context = content, img_file= img_file, date = date,tagline=tagline)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(sno = sno).first()
                post.title = title
                post.slug = slug
                post.context = content
                post.img_file = img_file
                post.date = date
                post.tagline = tagline
                db.session.add(post)
                db.session.commit()
        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html',post= post)
    

@app.route("/delete/<string:sno>")
def delete(sno):
    if ('user' in session and session['user'] == params['user_name']):
        post = Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')
    
@app.route("/uploaded" , methods=['GET','POST'])
def uploaded():
    if ('user' in session and session['user'] == params['user_name']):
        if request.method=="POST":
            f= request.files['file']
            f.save(os.path.join(app.config['Uloaded_File'],secure_filename(f.filename)))
            return f"Uploaded by this path {app.config['Uloaded_File']} succesefuly..."

if __name__=='__main__':
    app.run(debug=True)