import React from "react";

interface FormFieldProps {
    name: string;
    value: string | number;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    type?: "text" | "number";  // Type can be "text" or "number"
}

const FormField: React.FC<FormFieldProps> = ({ name, value, onChange, type = "text" }) => {
    return (
        <div className="form-group">
            <label htmlFor={name}>{name}</label>
            <input
                id={name}
                name={name}
                type={type}  // Dynamically set the input type
                value={value}
                onChange={onChange}
                className="form-input"
                required
            />
        </div>
    );
};

export default FormField;