from mysqlconnection import MySQLConnector 
import re


mysql = MySQLConnector('wall')
EMAIL_REGEX = re.compile(r'^[a-za-z0-9\.\+_-]+@[a-za-z0-9\._-]+\.[a-za-z]*$')

def validate(info): 
    errors = []

    email_exist(info['email'])
    if not info['first_name'] or not info['last_name']:
        errors.append('Name cannot be blank')
    elif len(info['first_name']) < 2 or len(info['last_name']) < 2:
        errors.append('Name must be at least 2 characters long')
    if not info['email']:
        errors.append('Email cannot be blank')
    elif not EMAIL_REGEX.match(info['email']):
        errors.append('Email format must be valid!')
    elif email_exist(info['email']):
        errors.append('This email has already been registered')
    if not info['password']:
        errors.append('Password cannot be blank')
    elif len(info['password']) < 8:
        errors.append('Password must be at least 8 characters long')
    elif info['password'] != info['password_confirm']:
        errors.append('Password and confirmation must match!')
  # check if there are any errors, if there are any return the array
   # otherwise return True
    if errors:
        return {"status": False, "errors": errors}
    else:
        return {"status": True}

# Check if email already exists in db.
def email_exist(email):
    check = mysql.fetch("SELECT * FROM users WHERE users.email = '{}' ".format(email))
    if len(check) > 0:
        return True
    else:
        return False