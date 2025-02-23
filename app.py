import sqlite3
from flask import Flask, redirect, request, jsonify, render_template, session
from flask_session import Session
import json
import os
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

app.config['SESSION_PERMANENT'] = os.getenv('SESSION_PERMANENT')
app.config['SESSION_TYPE'] = os.getenv('SESSION_TYPE')
Session(app)

chatbot_model = pipeline("text-generation", model="gpt2" , tokenizer="gpt2")

def initdb():
    with sqlite3.connect("databases/meow.sqlite") as dbconn:
        dbconn.execute("""
        CREATE TABLE IF NOT EXISTS preferences(
            ID PRIMARY KEY,
            username TEXT,
            password TEXT
        )
        """)
        dbconn.commit()

@app.route("/")
def home():
    if not session.get("name"):
        return redirect("login.html")
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":

        session["name"] = request.form.get("name")
        username = request.form.get("name" , None)
        password = request.form.get("pass" , None)
        with sqlite3.connect("databases/meow.sqlite") as dbconn:
            dbconn.execute("""
            CREATE TABLE IF NOT EXISTS login(
                username TEXT PRIMARY KEY,
                password TEXT
            )
            """)
            dbconn.execute("""
            INSERT INTO login
            VALUES (?,?)
            """, (username,password))
            dbconn.commit()
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

# POST request
@app.route("/personalization", methods=['GET','POST'])
def personalize():
    if request.method=='POST':
        foodRequest = request.get_json()
        food = foodRequest.get("food" , "").lower()
        vitamin = foodRequest.get("vitamins" , None)
        mineral = foodRequest.get("minerals" , None)
        protein = foodRequest.get("protein", 0)
        carbs = foodRequest.get("carbs" , 0)
        fats = foodRequest.get("fats", 0)
        with sqlite3.connect("databases/meow.sqlite") as dbconn:
            dbconn.execute("""
            INSERT INTO preferences
            VALUES (?,?,?,?,?,?)
            """, (food,vitamin,mineral,protein,carbs,fats))
            dbconn.commit()
        return jsonify({"success":"Record added to database"}), 200
    else:
        return jsonify({"error":"Unauthorized HTTP method."}), 401

@app.route('/foods')
def loadData():
    with open('food.json', 'r') as file:
        data = json.load(file)
        return data if isinstance(data, list) else data.get("data", [])

def getData():
    return jsonify(loadData())

# this is the GET method, that will be used for retrieving
@app.route('/remember', methods=['GET'])
def remember():
    if "name" in session:
        username = session["name"]

        with sqlite3.connect("databases/meow.sqlite") as dbconn:
            cursor = dbconn.cursor()
            
            cursor.execute("SELECT * FROM preferences WHERE username = ?", (username,))
            user_preferences = cursor.fetchall()

        if user_preferences:
            preferences_list = [
                {
                    "id": row[0],
                    "food": row[1], 
                    "vitamins": row[2], 
                    "minerals": row[3], 
                    "protein": row[4], 
                    "carbs": row[5], 
                    "fats": row[6]
                }
                for row in user_preferences
            ]

            return jsonify({"preferences": preferences_list}), 200
        else:
            return jsonify({"message": "No preferences found for this user"}), 404
    else:
        return jsonify({"error": "Unauthorized"}), 401

# although this is a POST method, this is primarily used for the chatbot 
@app.route('/recommend' , methods=['POST'])
def getRecommendation():
    if request.method=='POST':
        foodRequest = request.get_json()
        food = foodRequest.get("food" , "").lower()
        vitamin = foodRequest.get("vitamins" , None)
        mineral = foodRequest.get("minerals" , None)
        protein = foodRequest.get("protein", 0)
        carbs = foodRequest.get("carbs" , 0)
        fats = foodRequest.get("fats", 0)
        calories = (4 * carbs) + (4 * protein) + (9 * fats)
        vitamin_map = {
            "A": "Vitamin A - RAE",
            "B12": "Vitamin B12",
            "C": "Vitamin C",
            "D": "Vitamin D",
            "E": "Vitamin E",
            "K": "Vitamin K",
        }
        mineral_map = {
            "Calcium": "Calcium",
            "Magnesium": "Magnesium",
            "Iron": "Iron",
            "Zinc": "Zinc",
            "Potassium": "Potassium",
        }
        vitamin_keys = [f"Data.Vitamins.{vitamin_map.get(v, v)}" for v in vitamin] if vitamin else []
        mineral_keys = [f"Data.Major Minerals.{mineral_map.get(m, m)}" for m in mineral] if mineral else []
        foodData = loadData()
        if not isinstance(foodData, list):
            return jsonify({"error": "Data format is incorrect"}), 500
        filteredMeals = [
        item for item in foodData
        if (food in item.get("Description", "").lower()) and
        (item.get("calories", 0) <= calories) and
        (any(item.get(v, 0) > 0 for v in vitamin_keys) if vitamin_keys else True) and
        (any(item.get(m, 0) > 0 for m in mineral_keys) if mineral_keys else True) and
        (item.get("Data.Protein", 0) >= protein) and
        (item.get("Data.Carbohydrate", 0) <= carbs) and
        (item.get("Data.Fat.Total Lipid", 0) <= fats)
    ]
        if not filteredMeals:
            return jsonify({"message": "No meals found matching your criteria"}), 404
        for meal in filteredMeals:
            meal_description = f"{meal['Description']} is high in {', '.join(vitamin) if vitamin else 'various vitamins'} and {', '.join(mineral) if mineral else 'various minerals'}."

            # Advanced Prompt Engineering (Example)
            prompt = f"""
            You are a registered dietitian. Explain why {meal['Description']} is a good meal choice, considering it is high in {', '.join(vitamin) if vitamin else 'various vitamins'} and {', '.join(mineral) if mineral else 'various minerals'}.  Be concise.
            """

            try:
                response = chatbot_model(
                    prompt,
                    max_length=100,  # Adjust as needed
                    do_sample=True,
                    temperature=0.7,  # Adjust as needed
                    top_k=30,      # Adjust as needed
                    top_p=0.95,     # Adjust as needed
                    repetition_penalty=1.1 # Adjust as needed
                )

                # Correct way to access the generated text:
                aiResponse = response[0]['generated_text'].strip()  # Crucial change

                meal["ai_explanation"] = aiResponse

            except Exception as e:
                print(f"GPT-2 Error for {meal['Description']}: {e}")  # More informative error message
                meal["ai_explanation"] = meal_description

        return jsonify({"meals": filteredMeals}), 200
    else:
        return jsonify({"error":"Incorrect HTTP method."}), 401 
    
if __name__== '__main__':
    app.run(debug=True)