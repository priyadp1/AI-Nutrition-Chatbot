from flask import Flask, request, jsonify
import json
import pandas as pd
app = Flask(__name__)
@app.route('/food')
def getData():
    with open('food.json', 'r') as file:
        data = json.load(file)
    return jsonify(data)
@app.route('/recommend')
def getReccomendation():
    foodRequest = request.get_json()
    diet = foodRequest("diet")
    calories = foodRequest("calories")
    getData()
    calorieFilter = [item for item in getData() if item.get()]




if __name__== '__main__':
    app.run(debug=True)
