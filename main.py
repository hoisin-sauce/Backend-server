from flask import Flask, jsonify, send_file #https://backend-server.18jchadwick.repl.co/
from threading import Thread
import filehandler
import datahandler
import random
import hashlib
import os

# define global variables
token_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
token_chars_len = len(token_chars)-1
token_len = 32
salt_len = 64
basic_salt = "\x83f^\xfb\xba\x86\xa7\xbcC\x1c\x11\x872\xa3\x83;\xa6\xf1\xdd\xac\x0b\x9b\xab\x1e\xe5\xf5@4Y4vx"

app = Flask('')

password_db = filehandler.File("pw.csv")
token_db = filehandler.File("token.csv")
user_data_db = filehandler.File("user.csv")
film_db = filehandler.File("films.csv")
like_db = filehandler.File("likes.csv")
salt_db = filehandler.File("salts.csv")

db_lookup = {"film":film_db, "user":user_data_db, "pw":password_db, "token": token_db, "like":like_db, "salt":salt_db}

homepage = ""

# server interactions

# homepage
@app.route('/')
def home():
  with open("index.html", "r") as file:
    homepage = file.read()
    return homepage

# api documentation
@app.route('/api')
def api_lookup():
  with open("api.html", "r") as file:
    homepage = file.read()
    return homepage
  
# re-verify token
@app.route('/api/token/<string:user>/<string:pw>', methods=['GET'])
def token_interation(user, pw):
	return update_token(user, pw)

# get films from token
@app.route('/api/films/token/<string:token>', methods=['GET'])
def films_interation(token):
  return films(token)

# register user
@app.route('/api/register/<string:user>/<string:pw>/<string:genres>/<string:birthdate>', methods=['GET'])
def register_interation(user, pw, genres, birthdate):
  return register(user, pw, genres, birthdate)

@app.route('/api/like/<string:token>/<string:film_name>/', methods=['GET'])
def like_interaction(token, film_name):
  return like(token, film_name)

# generic functions

def like(token, film_name):
  film_id = film_exists(film_name)
  user_id = token_exists(token)
  rows = like_db.get_data()
  output = "success"
  try:
    if film_liked(token, film_name):
      row = ",".join([i for i in rows[user_id].split(",") if i != str(film_id)]).replace("\n", "")
    else:
      row = f"{film_id},{rows[user_id]}"
    like_db.replace_line(user_id, row)
  except Exception:
    output = "failed"
    
  return output

def change_pw_verification(name, old_pw, new_pw, new_salt=True, json=True):
  user = user_exists(name)

  # if user does not exist fail search
  if user == -1:
    return False

  output = "null"
  # verify password
  #try:
  if True:
    if get_pw(user) == hash(old_pw, salt=get_salt(user)):
      # generate_new salt
      output = change_pw(name, new_pw, new_salt=new_salt)
  #finally:
    return output

def change_pw(name, new_pw, new_salt=True):
  user = user_exists(name)
  if new_salt:
    _salt = generate_salt()
  else:
    _salt = get_salt(user)
  hashed_pw = hash(new_pw, _salt)
  salt_db.replace_line_bytes(user-1, _salt)
  password_db.replace_line(user, hashed_pw)
  output = update_token(name, new_pw)
  return output

def films(token):
  row = token_exists(token)

  # ensure token exists
  if row == -1:
    return jsonify({})

  # lookup genre
  genres = genre_lookup(row)

  # match films for genres
  return get_films(token, filters = [genres])

def register(user, pw, genres, birthdate, json=True):
  # check if user already exists
  if user_exists(user) != -1:
    return "null"

  # update databases
  salt = generate_salt()
  password_db.append(hash(pw, salt=salt))
  salt_db.append_bytes(salt)
  user_data_db.append(f"{user},{genres},{birthdate}")
  token = generate_token()
  token_db.append(token)
  like_db.append(",")

  # return token data
  if json:
    return jsonify({"token":  token})
  return token

# verify token and re-generate it
def update_token(user, pw):
  if check_pw(user, pw):
    if True:
      token = generate_token()
      token_db.replace_line(user_exists(user), token)
      return token
    return
  return "null"

# produce token of predefined length
def generate_token():
  return "".join([token_chars[random.randint(0, token_chars_len)] for _ in range(token_len)])

def generate_salt():
  return b"".join([os.urandom(2) for _ in range(salt_len)]).replace(b"\n", b"") # produce bytes without \n

def hash(pw, salt=basic_salt):
  # hash passwords using pbkdf2
  if isinstance(salt, str):
    dk = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 10000)
  else:
    dk = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, 10000)
  
  return dk.hex()

def check_pw(name, pw):
  # match user row
  user = user_exists(name)

  # if user does not exist fail search
  if user == -1:
    return False

  # check hash
  try:
    if get_pw(user) == hash(pw, salt=get_salt(user)):
      return True
  finally:
    pass
    
  return False

def get_pw(id):
  data = password_db.get_data()
  return data[id].split("\n")[0]

def get_salt(id):
  data = salt_db.get_data_bytes()
  return data[id-1].replace(b"\n", b"")

def user_exists(name):
  # search for index of user
  found = False
  for i, user in enumerate(user_data_db.get_data()):
    # pre-filter data (doesn' work in statement for some reason)
    filtered_data = user.split(",")[0].split("\n")[0]
    if name == filtered_data:
      found = True
      index = i
      break
  if found:
    return index
  return -1

def film_liked(token, name):
  row = token_exists(token)
  data = like_db.get_data()[row].split(",")
  return str(film_exists(name)) in data

# returns row of token or -1
def token_exists(token):
  # search for index of user
  for i, user in enumerate(token_db.get_data()):
    if token == user.split("\n")[0]:
      return i
  return -1

# match genre from rowpppp
def genre_lookup(index):
  user_data = user_data_db.get_data()[index]
  return user_data.split(",")[1]

def film_exists(name):
  # search for index of user
  for i, user in enumerate(film_db.get_data()):
    # pre-filter data (doesn' work in statement for some reason)
    filtered_data = user.split(",")[0].split("\n")[0]
    if name == filtered_data:
      return i
  return -1 

def get_films(token, filters=None, exclusions=None, json=True):
  filtering = True
  if filters is None:
    filters = list()
    filtering = False

  if exclusions is None:
    exclusions = list()
    
  output = list()
  for line in film_db.get_data():
    film = datahandler.Film(line)

    if not (filtering and not film.genre in filters) and not film.genre in exclusions:
      output.append(film)

  if json:
    return_data = list()

    for film in output:
      
      return_data.append( {"name":film.name, "link": film.link.split("\n")[0], "genre":film.genre, "liked":str(film_liked(token, film.name)).lower()})

    output = str(return_data)

  return output
           
def console_interface():
  while True:
    #try:
    if True:
      n = input(">>>")
      split_n = n.split(" ")
      if split_n[0] == "clear":
        if split_n[1] == "all":
          password_db.clear_file()
          token_db.clear_file()
          user_data_db.clear_file()
          salt_db.clear_file()
          like_db.clear_file()

        else:
          for val in split_n[1:]:
            db_lookup[val].clear_file()
      elif n == "token":
        print(generate_token())
        
      elif n == "chars":
        print(token_chars)
        
      elif split_n[0] == "hash":
        print(hash(split_n[1]))
        
      elif split_n[0] == "register":
        print(register(split_n[1],split_n[2], split_n[3], split_n[4], json=False))
        
      elif split_n[0] == "verify":
        print(update_token(split_n[1], split_n[2]))
        
      elif split_n[0] == "films":
        print(films(split_n[1]))
        
      elif split_n[0] == "changepw":
        print(change_pw_verification(split_n[1], split_n[2], split_n[3], json=False))
        
      elif split_n[0] == "dump":

        if split_n[1] == "all":
          print(password_db.get_data())
          print(token_db.get_data())
          print(user_data_db.get_data())
          print(salt_db.get_data_bytes())
          print(like_db.get_data())
          print(film_db.get_data())

        else:
          for val in split_n[1:]:
            print(db_lookup[val].get_data_bytes())

      elif split_n[0] == "liked":
        print(film_liked(split_n[1], split_n[2]))

      elif split_n[0] == "like":
        print(like(split_n[1], split_n[2]))
        
    #except Exception:
    #  print('incorrect arguments')

# main program

def main():
  global homepage

  with open("index.html", "r") as file:
    homepage = file.read()
  
  # start server connection
  t = Thread(target=run)
  t.start()
  console_interface()

def run():
	app.run(host='0.0.0.0',port=8080)

if __name__ == "__main__":
  main()