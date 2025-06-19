#DEMUX HACKATHON 2024
from flask import Flask, render_template, session, request, flash, redirect, url_for, jsonify
from flask_session import Session
import google.generativeai as genai
import pymongo
from bson.objectid import ObjectId
import bcrypt

genai.configure(api_key="AIzaSyAmMUlrCJrh_AKOg37SD893gfmY9gfOqUg")
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_with_gemini(text_bytes):
    input_prompt = '''
    You are an expert in text extraction from files. Extract the text content and provide it as output.
    '''
    response = model.generate_content([
        input_prompt,
        {
            "text": text_bytes.decode('utf-8')  
        }
    ])
    return response.text.strip()


def get_gemini_grade_feedback(question, paragraph):
    input_prompt = f'''
    You are an expert grader. Please evaluate the following answer only if its length is more than 150 words based on the given question. 
    Provide a grade (out of 10) and give constructive feedback in 50 words.
    Question: {question}
    Answer: {paragraph}
    '''
    response = model.generate_content([input_prompt])
    
    print("API Response:", response.text)
    
    try:
        response_text = response.text.strip()
        
        grade_start = response_text.find("Grade: ") + len("Grade: ")
        grade_end = response_text.find("/10", grade_start)
        grade = response_text[grade_start:grade_end].strip()

        feedback_start = response_text.find("\n", grade_end) + 1
        feedback = response_text[feedback_start:].strip()
        
        return grade, feedback
    except Exception as e:
        print(f"Error extracting grade and feedback: {str(e)}")
        return None, "Error parsing the response"

app = Flask(__name__)

app.secret_key = 'udaykiranjogu2005' 


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

client = pymongo.MongoClient("mongodb+srv://udaykiranjogu2005:udaykiran2005@edugrader.dog6lyc.mongodb.net/?retryWrites=true&w=majority&appName=EduGrader")

db = client.edugrader_  

users_collection = db.users  

history_collection = db.history 

def extract_text_with_gemini(text_bytes):
    input_prompt = '''
    You are an expert in text extraction from files. Extract the text from it just extract donot generate anything
    '''
    response = model.generate_content([
        input_prompt, 
        {
            "text": text_bytes.decode('utf-8')  # Assuming the file is UTF-8 encoded
        }
    ])
    
    return response.text.strip()

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different username.", "danger")
            return render_template("register.html")

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        users_collection.insert_one({"username": username, "password": hashed_password, "email": email})
        flash("Registration successful. Please log in.", "success")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = users_collection.find_one({"username": username})

        if existing_user and bcrypt.checkpw(password.encode('utf-8'), existing_user["password"]):
            session["username"] = username
            session["id"] = str(existing_user["_id"])
            flash("Login successful", 'success')
            return redirect("/grading")
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template("login.html")

@app.route('/grading', methods=["POST", "GET"])
def grading():
    if not session.get("username"):
        return redirect("/login")
    
    if request.method == "POST":
        question = request.form.get("question").strip()
        answer = request.form.get("answer").strip()
        question_file = request.files.get("questionFile")
        answer_file = request.files.get("answerFile")

        # Extract text from uploaded files using Gemini
        if question_file and question_file.filename != '':
            question = extract_text_with_gemini(question_file.read())
        if answer_file and answer_file.filename != '':
            answer = extract_text_with_gemini(answer_file.read())

        if not question or not answer:
            flash("Both question and answer fields are required.", "danger")
            return render_template('grading.html')

        user_id = session.get("id")
        marks, feedback = get_gemini_grade_feedback(question, answer)

        if marks and feedback:
            history_collection.insert_one({"question": question, "answer": answer, "user_id": ObjectId(user_id), "marks": marks, "feedback": feedback})
            return render_template('grading.html', marks=marks, feedback=feedback, question=question, answer=answer)
        else:
            flash('Error in grading process. Please try again.', 'danger')
            return render_template('grading.html')

    return render_template('grading.html')



@app.route("/profile")
def profile():
    username = session.get("username")
    if not username:
        return redirect('/login')
    
    profile_details = users_collection.find_one({"username": username})
    
    if profile_details:
        email = profile_details["email"]
        return render_template('profile.html', username=username, email=email)
    else:
        return redirect('/login')



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route('/subscribe')
def subscribe():
    if not session.get("username"):
        return redirect("/login")
    return render_template('subscribe.html')

@app.route('/history')
def history():
    if not session.get("username"):
        return redirect("/login")
    user_id = session.get('id')
    history = list(history_collection.find({"user_id": ObjectId(user_id)}))
    return render_template('history.html', history=history)

@app.route('/delete/<string:qno>', methods=['POST'])
def delete(qno):
    if not session.get("username"):
        return redirect("/login")
    history_collection.delete_one({"_id": ObjectId(qno)})
    return redirect('/history')

if __name__ == '__main__':
    app.run(debug=False)
