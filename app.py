import re
from flask import Flask, session, request, redirect, render_template, flash, url_for

import db.data_layer as db
from db.data_layer import get_all_quotes, get_all_quotes_for, get_user_by_email, get_user_by_id, get_user_by_name, search_by_user_or_email, create_quote, create_user, delete_quote, check_login
'''
USAGE:        db.<function_name>
EXAMPLES:     db.search_by_user_or_email('Smith')
              db.search_by_user_or_email('gmail.com')
'''

EMAIL_REGEX = re.compile(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')

app = Flask(__name__)
app.secret_key = '0d599f0ec05c3bda8c3b8a68c32a1b47'

@app.route('/')
def index():
    quotes = get_all_quotes()
    return render_template('index.html', quotes = quotes)

@app.route('/create_quote', methods=["POST"])
def createquote():
    user_id = session['user_id']
    content = request.form.get("content")
    create_quote(user_id, content)
    return redirect('/') 
    

@app.route('/delete/<quote_id>')
def deletequote(quote_id):
    delete_quote(quote_id)
    return redirect('/') 

@app.route('/search')
def search():
    return redirect(url_for('search_users', query=request.args['html_query']))
    
@app.route('/results/<query>')
def search_users(query):
    users = search_by_user_or_email(query)
    return render_template('index.html', users = users)

@app.route('/user/<user_id>')
def user_quotes(user_id):
    quotes = get_all_quotes_for(user_id)
    return render_template('index.html', quotes = quotes)
    
@app.route('/authenticate')
def authenticate():
    pass

@app.route('/register', methods=["GET", "POST"])
def register():
    if 'user_id' not in session: #check if user not yet login
        if request.method == 'POST':
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm = request.form.get("confirm")
            if password == confirm:
                if len(password)>7:
                    if EMAIL_REGEX.match(email):
                            user = create_user(email, username, password)
                            session['user_id'] = user.id
                            session['username'] = user.email
                            return redirect('/')
                    else:
                        flash("Please input correct email")
                        return redirect('/register') 
                else:
                    flash("password minimum 8 char")
                    return redirect('/register') 
            else:
                flash("password must be same with confirm")
                return redirect('/register') 

        else:
            return render_template('page_register.html')


    return redirect('/') #redirect if already login


@app.route('/login', methods=["GET", "POST"])
def login():
    if 'user_id' not in session: #check if user not yet login
        if request.method == 'POST':
            email = request.form.get("email")
            password = request.form.get("password")
            try:
                user = check_login(email, password)
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect('/')
            except:
                flash("email or password not found")
                return redirect('/login') 
                
        else:
            return render_template('page_login.html')

    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

def setup_web_session(user):
    pass


app.run(debug=True)