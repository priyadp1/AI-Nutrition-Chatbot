from flask import Flask, request, jsonify
import json
app = Flask(__name__)
@app.route('/foods')
def getData():
    with open('food.json', 'r') as file:
        data = json.load(file)
    return jsonify(data)
@app.route('/recommend' , methods=['POST'])
def getReccomendation():
    foodRequest = request.get_json()
    diet = foodRequest.get("diet" , "").lower()
    vitamin = foodRequest.get("vitamins" , None)
    mineral = foodRequest.get("minerals" , None)
    protein = foodRequest.get("protein", 0)
    carbs = foodRequest.get("carbs" , 0)
    fats = foodRequest.get("fats", 0)
    calories = (4 * carbs) + (4 * protein) + (9 * fats)
    foodData = getData()
    filteredMeals = [
    item for item in foodData
    if (diet.lower() in item.get("diet", "").lower()) and
       (item.get("calories", 0) <= calories) and
       (vitamin in item.get("vitamins", [])if vitamin else True) and
       (mineral in item.get("minerals", [])if mineral else True) and
       (item.get("protein", 0) >= protein) and
       (item.get("carbs", 0) <= carbs) and
       (item.get("fats", 0) <= fats)
]
    if not filteredMeals:
        return jsonify({"message": "No meals found matching your criteria"}), 404

    return jsonify({"meals": filteredMeals}), 200




if __name__== '__main__':
    app.run(debug=True)
