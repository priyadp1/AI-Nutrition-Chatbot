const FormField = ({ name, onChange }: { name: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void }) => {
    return (
        <div>
            <label htmlFor={name}>{name}</label>
            <input id={name} name={name} type="text" required onChange={onChange}/>
        </div>
    )
}
export default FormField