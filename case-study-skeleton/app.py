from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

#Code goes below here


config = {
  "apiKey": "AIzaSyC_bDgCFc_cRR7ox7l9Mi18qW5GYdcRTmg",
  "authDomain": "group-project-69856.firebaseapp.com",
  "projectId": "group-project-69856",
  "storageBucket": "group-project-69856.appspot.com",
  "messagingSenderId": "645554792214",
  "appId": "1:645554792214:web:765fa8513cb5719f859237",
  "databaseURL":"https://group-project-69856-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase=pyrebase.initialize_app(config)
auth=firebase.auth()
db=firebase.database()

@app.route('/')
def hello():
    return render_template('/index.html')

@app.route('/home')
def home():
    return render_template('/home.html')

@app.route('/questions')
def questions():
    return render_template('/questions.html')

@app.route('/recipes')
def recipes():
    return render_template('/recipes.html') 

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('home'))
        except:
            error = "Authentication failed"
    return render_template("signin.html", error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        name = request.form['name']  
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            new_user={"name":name, "email":email, "password":password}
            db.child("users").child("uid").child(UID).set(new_user)
            return redirect(url_for('home'))
        except:
            error = "Authentication failed"
    return render_template("signup.html", error=error)



@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        message = request.form['message']
        if message.strip() != "":
            UID = login_session['user']['localId']
            my_user=db.child("users").child("uid").child(UID).get().val()
            
            print(my_user["name"])
            sender = my_user["name"]
            my_email=my_user["email"]
            store_chat_message(sender, message,my_email)
    messages = get_chat_messages()
    return render_template('chat.html', messages=messages, login_session=login_session)

def store_chat_message(sender, message, my_email):
    try:

        new_message_ref = db.child("messages").push({"sender": sender, "content": message, "email":my_email})
        print(new_message_ref)
        message_id = new_message_ref["name"]  
        print(message_id)
        db.child("messages").child(message_id).update({"message_id": message_id})
    except Exception as e:
        print("Error storing message:", e)

def get_chat_messages():
    try:
        chat_ref = db.child("messages").get()
        messages = []
        for message in chat_ref.each():
            messages.append(message.val())
        return messages
    except Exception as e:
        print("Error fetching messages:", e)
        return []

@app.route('/remove_message/<message_id>',methods=['GET', 'POST'])
def remove_message(message_id):
    try:
        message = db.child("messages").child(message_id).get().val()
        print(message.get('email'))
        if message and message.get('email') == login_session['user']['email']:
            db.child("messages").child(message_id).remove()
    except Exception as e:
        print("Error removing message:", e)
    return redirect(url_for('chat'))



#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)