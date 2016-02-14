from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
from modules import test 

app = Flask(__name__)
mysql = MySQLConnector('wall')
app.secret_key = "ThisIsSecret"

@app.route('/')
def index():
	if not 'user_id' in session:
		return render_template('landing.html')
	else:
		return render_template('dashboard.html')
@app.route('/registration', methods=["POST"])
def reg():
	user_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ('{}','{}','{}','{}', NOW(), NOW())".format(request.form['first_name'],request.form['last_name'],request.form['email'],request.form['password'])
	mysql.run_mysql_query(user_query)
	return redirect('/')

@app.route('/login', methods=["POST"])
def login():
	check_user_query = "SELECT * FROM users WHERE users.email = '{}'".format(request.form['email'])
	user_info = mysql.fetch(check_user_query)
	if user_info[0]['password'] == request.form['password']:
		session['first_name'] = user_info[0]['first_name']
		session['user_id'] = user_info[0]['id']
		return redirect('/dashboard')
	else:
		return redirect('/')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')

@app.route('/dashboard')
def dashboard():
	get_all_messages_query = "SELECT users.first_name, users.last_name, messages.* FROM messages LEFT JOIN users ON messages.user_id = users.id ORDER BY messages.created_at DESC"
	all_messages = mysql.fetch(get_all_messages_query)
	print all_messages
	return render_template('dashboard.html', messages =  all_messages)

@app.route('/message/<message_id>')
def message_wall(message_id):
	get_message_query = "SELECT users.first_name, users.last_name, messages.* FROM messages LEFT JOIN users ON messages.user_id = users.id WHERE messages.id = '{}'".format(message_id)
	message = mysql.fetch(get_message_query)

	get_comments_query = "SELECT users.first_name, users.last_name, comments.comment, comments.created_at AS comment_created_at FROM comments LEFT JOIN users ON comments.user_id = users.id LEFT JOIN messages ON comments.message_id = messages.id WHERE comments.message_id='{}' ORDER BY comment_created_at ASC".format(message[0]['id'])
	comments = mysql.fetch(get_comments_query)
	message[0]['fetch_comments'] = comments
	return render_template('wall.html', message = message)

@app.route('/message/<user_id>', methods=['POST'])
def post_message(user_id):
	post_message_query = "INSERT INTO messages (user_id,message,created_at,updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(user_id, request.form['message'])
	mysql.run_mysql_query(post_message_query)
	return redirect('/wall')

@app.route('/message/<message_id>/show')
def show_message(message_id):
	get_message_query = "SELECT users.first_name, users.last_name, messages.* FROM messages LEFT JOIN users ON messages.user_id = users.id WHERE messages.id = '{}'".format(message_id)
	message = mysql.fetch(get_message_query)
	return render_template('update.html', message = message[0])

@app.route('/message/<message_id>/update', methods=["POST"])
def update_message(message_id):
	update_message_query = "UPDATE `wall`.`messages` SET `message`='{}', `topic`='{}'  WHERE `id`='{}'".format(request.form['message'],request.form['topic'], message_id)
	mysql.run_mysql_query(update_message_query)
	return redirect('dashboard')

@app.route('/message/<message_id>/delete')
def delete_message(message_id):
	delete_message_query = "DELETE FROM `wall`.`messages` WHERE `id`='{}'".format(message_id)
	mysql.run_mysql_query(delete_message_query)
	return redirect('dashboard.html')


@app.route('/comment/<user_id>/<message_id>', methods=["POST"])
def post_comment(user_id,message_id):
	post_comment_query = "INSERT INTO comments (message_id, user_id, comment, created_at, updated_at) VALUES ('{}','{}','{}', NOW(), NOW())".format(message_id, user_id, request.form['comment'])
	mysql.run_mysql_query(post_comment_query)
	return redirect('/wall')

app.run(debug=True)

