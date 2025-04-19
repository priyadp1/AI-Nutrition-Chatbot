
import sqlite3
from flask import Flask, redirect, request, jsonify, render_template, session
from flask_session import Session
import json
import os
from dotenv import load_dotenv
import re
from collections import defaultdict, Counter
import math
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)

app.config['SESSION_PERMANENT'] = os.getenv('SESSION_PERMANENT')
app.config['SESSION_TYPE'] = os.getenv('SESSION_TYPE')
Session(app)

def initdb():
    with sqlite3.connect("./meow.sqlite") as dbconn:
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
        return redirect("/login")
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("name", None)
        password = request.form.get("pass", None)

        with sqlite3.connect("./meow.sqlite") as dbconn:
            dbconn.execute("""
            CREATE TABLE IF NOT EXISTS login(
                username TEXT PRIMARY KEY,
                password TEXT
            )
            """)

            cursor = dbconn.cursor()
            cursor.execute("SELECT password FROM login WHERE username = ?", (username,))
            row = cursor.fetchone()

            if row:
                stored_hashed_pw = row[0]
                if check_password_hash(stored_hashed_pw, password):
                    session["name"] = username
                    return redirect("/")
                else:
                    return "Invalid username or password", 403
            else:
                hashed_pw = generate_password_hash(password)
                dbconn.execute("INSERT INTO login (username, password) VALUES (?, ?)", (username, hashed_pw))
                session["name"] = username
                dbconn.commit()
                return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

def tokenize(text):
    return re.findall(r'\b\w+\b' , text.lower())

def buildBigram(tokens):
    return [(tokens[i] , tokens[i+ 1]) for i in range(len(tokens) - 1)]

def bigramProb(text):
    tokens = tokenize(text)
    bigrams = buildBigram(tokens)
    bigramCounts = Counter(bigrams)
    unigramCounts = Counter(tokens)
    vocabSize = len(set(tokens))

    probs = {}
    for bigram in bigramCounts:
        first = bigram[0]
        probs[bigram] = (bigramCounts[bigram] + 1) / (unigramCounts[first] + vocabSize)
    for wi in unigramCounts:
        for wj in unigramCounts:
            bg = (wi, wj)
            if bg not in probs:
                probs[bg] = 1 / (unigramCounts[wi] + vocabSize)
    return probs

# POST request
@app.route("/personalization", methods=['GET','POST'])
def personalize():
    username = request.args.get("username")
    if not username:
        return jsonify({"success": False, "message": "User not logged in"})

    foodRequest = request.get_json()
    food = foodRequest.get("food" , "").lower()
    vitamin = foodRequest.get("vitamins" , None)
    mineral = foodRequest.get("minerals" , None)
    protein = foodRequest.get("protein", 0)
    carbs = foodRequest.get("carbs" , 0)
    fats = foodRequest.get("fats", 0)
    
    with sqlite3.connect("./meow.sqlite") as dbconn:
        dbconn.execute("""
        INSERT INTO preferences
        VALUES (?,?,?,?,?,?,?)
        """, (username,food,vitamin,mineral,protein,carbs,fats))


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

        with sqlite3.connect("./meow.sqlite") as dbconn:
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

def buildResponse(meal, vitamins, minerals):
    desc = meal.get("Description", "This meal")
    data = meal.get("Data", {})
    protein = data.get("Protein", 0)
    carbs = data.get("Carbohydrate", 0)
    fats = data.get("Fat.Total Lipid", 0)

    vitList = ', '.join(vitamins) if vitamins else "essential vitamins"
    minList = ', '.join(minerals) if minerals else "important minerals"

    summaries = [
        f"{desc} is rich in nutrients and provides {protein}g of protein, {carbs}g of carbs, and {fats}g of fat. It's ideal for those needing {vitList} and {minList}.",
        f"{desc} offers {protein}g of protein and supports diets rich in {vitList} and {minList}. It's a great choice for balanced nutrition.",
        f"With {protein}g of protein, {carbs}g carbs, and {fats}g fat, {desc} supports a balanced diet and contributes to your {vitList} and {minList} intake.",
        f"{desc} contains about {protein}g protein, {carbs}g carbs, and {fats}g fat. It’s a suitable meal for those seeking nutrients like {vitList} and {minList}.",
    ]

    def ppl(text):
        tokens = tokenize(text)
        bigrams = buildBigram(tokens)
        probs = bigramProb(text)
        logProbSum = 0
        for bigram in bigrams:
            prob = probs.get(bigram, 1e-8)
            logProbSum += math.log2(prob)
        avgLogProb = logProbSum / len(bigrams) if bigrams else 0
        return 2 ** (-avgLogProb)

    bestSummary = min(summaries, key=ppl)
    return bestSummary

@app.route('/recommend', methods=['POST'])
def getRecommendation():
    if request.method == 'POST':
        foodRequest = request.get_json()
        food = foodRequest.get("food", "").lower()
        vitamin = foodRequest.get("vitamins", [])
        mineral = foodRequest.get("minerals", [])
        dietPrefs = foodRequest.get("diet", [])
        protein = foodRequest.get("protein", 0)
        carbs = foodRequest.get("carbs", 0)
        fats = foodRequest.get("fats", 0)

        vitaminMap = {
            "A": "Vitamin A - RAE", "B12": "Vitamin B12", "C": "Vitamin C",
            "D": "Vitamin D", "E": "Vitamin E", "K": "Vitamin K"
        }
        mineralMap = {
            "Calcium": "Calcium", "Magnesium": "Magnesium", "Iron": "Iron",
            "Zinc": "Zinc", "Potassium": "Potassium"
        }

        foodData = loadData()
        if not isinstance(foodData, list):
            return jsonify({"error": "Data format is incorrect"}), 500

        scoredMeals = []

        for item in foodData:
            score = 0
            desc = item.get("Description", "").lower()
            tags = item.get("DietaryTags", {})

            # Normalize and enforce diet tag filtering
            if dietPrefs:
                selectedDiet = dietPrefs[0] if isinstance(dietPrefs, list) else dietPrefs
                normalizedDiet = selectedDiet.strip().lower().capitalize()
                if not tags.get(normalizedDiet, False):
                    continue

            # Ingredient match
            if food and food in desc:
                score += 10

            # Vitamin scoring
            score += sum(
                1 for v in vitamin
                if item.get("Data", {}).get("Vitamins", {}).get(vitaminMap.get(v, v), 0) > 0
            )

            # Mineral scoring
            score += sum(
                1 for m in mineral
                if item.get("Data", {}).get("Major Minerals", {}).get(mineralMap.get(m, m), 0) > 0
            )

            # Macronutrient scoring
            if item.get("Data", {}).get("Protein", 0) >= protein:
                score += 3
            if item.get("Data", {}).get("Carbohydrate", 0) <= carbs:
                score += 2
            if item.get("Data", {}).get("Fat.Total Lipid", 0) <= fats:
                score += 2

            if score > 0:
                item["score"] = score
                item["explanation"] = buildResponse(item, vitamin, mineral)
                scoredMeals.append(item)

        if scoredMeals:
            topMeals = sorted(scoredMeals, key=lambda x: x["score"], reverse=True)[:3]
            return jsonify({"meals": topMeals}), 200
        else:
            return jsonify({"message": "No suitable meals found."}), 404

    return jsonify({"error": "Incorrect HTTP method."}), 401


if __name__== '__main__':
   app.run(host='0.0.0.0', port=5000)
