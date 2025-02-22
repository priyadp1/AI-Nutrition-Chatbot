from flask import Flask, request, jsonify
import json
app = Flask(__name__)
@app.route('/foods')
def loadData():
     with open('food.json', 'r') as file:
        data = json.load(file)
        return data if isinstance(data, list) else data.get("data", [])
def getData():
    return jsonify(loadData())
@app.route('/recommend' , methods=['POST'])
def getReccomendation():
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

    return jsonify({"meals": filteredMeals}), 200




if __name__== '__main__':
    app.run(debug=True)
