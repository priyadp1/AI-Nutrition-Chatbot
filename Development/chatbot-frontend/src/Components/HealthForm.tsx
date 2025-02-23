import { useState } from "react";
import FormField from "./FormField";
const HealthForm = () => {
    const [formData, setFormData] = useState<{ [key: string]: string | number }>({});
    
    const numericFields = ["Alpha Carotene", "Beta Carotene", "Beta Cryptoxanthin", "Carbohydrate",
            "Cholesterol", "Choline", "Fiber", "Lutein and Zeaxanthin", "Lycopene",
            "Niacin", "Protein", "Retinol", "Riboflavin", "Selenium", "Sugar Total",
            "Thiamin", "Water", "Monosaturated Fat", "Polyunsaturated Fat", "Saturated Fat",
            "Total Lipid", "Calcium", "Copper", "Iron", "Magnesium", "Phosphorus",
            "Potassium", "Sodium", "Zinc", "Vitamin A - RAE", "Vitamin B12",
            "Vitamin B6", "Vitamin C", "Vitamin E", "Vitamin K"]

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;

        const parsedValue = numericFields.includes(name) ? parseFloat(value) : value;
        setFormData((prev) => ({
            ...prev,
            [name]: parsedValue,
        }));
        console.log("Changing data")
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            const response = await fetch("http://localhost:5000/recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (response.ok) {
                console.log("Success:", data);
                alert(`Success: ${JSON.stringify(data)}`);
                // setFormData({}); // Kept for testing purposes
            } else {
                console.log(`Error:${data}`)
                alert(`Error: ${data.error}`)
            }
        } catch (error) {
            if (error instanceof Error){
                alert(`Error: ${error.message}`);
            }
            else{
                alert(`Error: An unknown error has occurred`)
            }
        }
    };

    return (
        // "Category","Description","Nutrient Data Bank Number","Data.Alpha Carotene","Data.Beta Carotene","Data.Beta Cryptoxanthin","Data.Carbohydrate","Data.Cholesterol","Data.Choline","Data.Fiber","Data.Lutein and Zeaxanthin","Data.Lycopene","Data.Niacin","Data.Protein","Data.Retinol","Data.Riboflavin","Data.Selenium","Data.Sugar Total","Data.Thiamin","Data.Water","Data.Fat.Monosaturated Fat","Data.Fat.Polysaturated Fat","Data.Fat.Saturated Fat","Data.Fat.Total Lipid","Data.Major Minerals.Calcium","Data.Major Minerals.Copper","Data.Major Minerals.Iron","Data.Major Minerals.Magnesium","Data.Major Minerals.Phosphorus","Data.Major Minerals.Potassium","Data.Major Minerals.Sodium","Data.Major Minerals.Zinc","Data.Vitamins.Vitamin A - RAE","Data.Vitamins.Vitamin B12","Data.Vitamins.Vitamin B6","Data.Vitamins.Vitamin C","Data.Vitamins.Vitamin E","Data.Vitamins.Vitamin K"

        <form method="post" onSubmit={handleSubmit} noValidate>
            <label htmlFor="food">Food</label>
            <input type="text" id="food" className="form-input" name="food" onChange={handleChange}/>
            {[
            "Alpha Carotene", "Beta Carotene", "Beta Cryptoxanthin", "Carbohydrate",
            "Cholesterol", "Choline", "Fiber", "Lutein and Zeaxanthin", "Lycopene",
            "Niacin", "Protein", "Retinol", "Riboflavin", "Selenium", "Sugar Total",
            "Thiamin", "Water", "Monosaturated Fat", "Polyunsaturated Fat", "Saturated Fat",
            "Total Lipid", "Calcium", "Copper", "Iron", "Magnesium", "Phosphorus",
            "Potassium", "Sodium", "Zinc", "Vitamin A - RAE", "Vitamin B12",
            "Vitamin B6", "Vitamin C", "Vitamin E", "Vitamin K"
            ].map((field) => (
                <FormField
                    key={field}
                    name={field}
                    value={formData[field] || ""}
                    onChange={handleChange}
                    type={numericFields.includes(field) ? "number" : "text"}  // Set the field type
                />
            ))}
            
            <input type="submit" />
        </form>
    )
}
export default HealthForm