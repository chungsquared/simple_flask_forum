from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re

app = Flask(__name__)
mysql = MySQLConnector('wall')
app.secret_key = "ThisIsSecret"

@app.route('/')
def index():
	return render_template('index.html')

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
		return redirect('/wall')
	else:
		return redirect('/')

@app.route('/wall')
def wall():
	get_messages_query = "SELECT users.first_name, users.last_name, messages.* FROM messages LEFT JOIN users ON messages.user_id = users.id ORDER BY messages.created_at DESC"
	messages = mysql.fetch(get_messages_query)
	for message in messages:
		get_comments_query = "SELECT users.first_name, users.last_name, comments.comment, comments.created_at AS comment_created_at FROM comments LEFT JOIN users ON comments.user_id = users.id LEFT JOIN messages ON comments.message_id = messages.id WHERE comments.message_id='{}' ORDER BY comment_created_at ASC".format(message['id'])
		comments = mysql.fetch(get_comments_query)
		message['fetch_comments'] = comments

	return render_template('wall.html', messages = messages)

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')

@app.route('/message/<user_id>', methods=['POST'])
def post_message(user_id):
	post_message_query = "INSERT INTO messages (user_id,message,created_at,updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(user_id, request.form['message'])
	mysql.run_mysql_query(post_message_query)
	return redirect('/wall')

@app.route('/comment/<user_id>/<message_id>', methods=["POST"])
def post_comment(user_id,message_id):
	print user_id
	print message_id
	post_comment_query = "INSERT INTO comments (message_id, user_id, comment, created_at, updated_at) VALUES ('{}','{}','{}', NOW(), NOW())".format(message_id, user_id, request.form['comment'])
	mysql.run_mysql_query(post_comment_query)
	return redirect('/wall')

app.run(debug=True)