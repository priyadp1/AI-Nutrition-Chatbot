const FormField = (props: any) => {
    return (
        <>
            <label htmlFor={props.name}>{props.name}</label>
            <input id={props.name} name={props.name} type="text" required/>
        </>
    )
}
export default FormField