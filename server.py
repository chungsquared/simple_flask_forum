from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt 
from flask.ext.login import LoginManager
from modules import regValidations, functions 
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector('wall')
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "ThisIsSecret"

@app.route('/')
def index():
	if not 'user_id' in session:
		return render_template('landing.html')
	else:
		return render_template('dashboard.html')

@app.route('/registration', methods=["POST"])
def reg():
	reg_info = {
		'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': request.form['password'],
        'password_confirm': request.form['password_confirm']
	}

	validate = loginReg.validate(reg_info)

	if validate["status"]:
		pw_hash = bcrypt.generate_password_hash(reg_info['password'])
		new_user_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ('{}','{}','{}','{}', NOW(), NOW())".format(reg_info['first_name'],reg_info['last_name'],reg_info['email'],pw_hash)
		mysql.run_mysql_query(new_user_query)
		flash("You have successfully registered")

	else:
		for error in validate['errors']:
			flash(error)

	return redirect('/')

@app.route('/login', methods=["POST"])
def login():
	user_query = "SELECT * FROM users WHERE email = '{}' LIMIT 1".format(request.form['email'])
	user = mysql.fetch(user_query)
	if user == []:
		flash("The email inputted does not match our records. Please try again")

	elif bcrypt.check_password_hash(user[0]['password'],request.form['password']):
		session['first_name'] = user[0]['first_name']
		session['user_id'] = user[0]['id']
		return redirect('/dashboard')

	else:
		flash("Incorrect Password")

	return redirect('/')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')

@app.route('/dashboard')
def dashboard():
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	get_all_messages_query = "SELECT users.first_name, users.last_name, messages.* FROM messages LEFT JOIN users ON messages.user_id = users.id ORDER BY messages.created_at DESC"
	all_messages = mysql.fetch(get_all_messages_query)
	return render_template('dashboard.html', messages =  all_messages)

@app.route('/message/<message_id>')
def message_wall(message_id):
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	get_message_query = "SELECT users.first_name, users.last_name, messages.* FROM messages LEFT JOIN users ON messages.user_id = users.id WHERE messages.id = '{}'".format(message_id)
	message = mysql.fetch(get_message_query)

	get_comments_query = "SELECT users.first_name, users.last_name, comments.id AS comment_id, comments.user_id AS comment_user_id, comments.comment, comments.created_at AS comment_created_at FROM comments LEFT JOIN users ON comments.user_id = users.id LEFT JOIN messages ON comments.message_id = messages.id WHERE comments.message_id='{}' ORDER BY comment_created_at ASC".format(message[0]['id'])
	comments = mysql.fetch(get_comments_query)
	message[0]['fetch_comments'] = comments
	return render_template('wall.html', message = message)

@app.route('/message/new')
def new_message():
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	return render_template('postTopic.html')

@app.route('/message/<user_id>', methods=['POST'])
def post_message(user_id):
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	post_message_query = "INSERT INTO messages (user_id,message,topic,created_at,updated_at) VALUES ('{}', '{}', '{}', NOW(), NOW())".format(user_id, re.escape(request.form['message']),re.escape(request.form['topic']))
	mysql.run_mysql_query(post_message_query)
	return redirect('/dashboard')

@app.route('/message/<message_id>/show')
def show_message(message_id):
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	get_message_query = "SELECT users.first_name, users.last_name, messages.* FROM messages LEFT JOIN users ON messages.user_id = users.id WHERE messages.id = '{}'".format(message_id)
	message = mysql.fetch(get_message_query)
	return render_template('update.html', message = message[0])

@app.route('/message/<message_id>/update', methods=["POST"])
def update_message(message_id):
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	update_message_query = "UPDATE `wall`.`messages` SET `message`='{}', `topic`='{}'  WHERE `id`='{}'".format(re.escape(request.form['message']),re.escape(request.form['topic']), message_id)
	mysql.run_mysql_query(update_message_query)
	return redirect('dashboard')

@app.route('/message/<message_id>/delete')
def delete_message(message_id):
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	delete_message_query = "DELETE FROM `wall`.`messages` WHERE `id`='{}'".format(message_id)
	mysql.run_mysql_query(delete_message_query)
	return redirect('/dashboard')

@app.route('/comment/<user_id>/<message_id>', methods=["POST"])
def post_comment(user_id,message_id):
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	post_comment_query = "INSERT INTO comments (message_id, user_id, comment, created_at, updated_at) VALUES ('{}','{}','{}', NOW(), NOW())".format(message_id, user_id, re.escape(request.form['comment']))
	mysql.run_mysql_query(post_comment_query)
	return redirect('/message/'+message_id)

@app.route('/comment/<comment_id>/<message_id>/delete')
def delete_comment(comment_id, message_id):
	if not 'user_id' in session:
		flash("You must be logged in to view this page")
		return redirect('/')

	delete_comment_query = "DELETE FROM `wall`.`comments` WHERE `id`='{}'".format(comment_id)
	mysql.run_mysql_query(delete_comment_query)
	return redirect('/message/' + message_id)

app.run(debug=True)

