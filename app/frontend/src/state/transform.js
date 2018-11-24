const importScript = imported =>
	imported.reduce((obj, question) => ({ ...obj, [question.id]: question }), {})


const exportScript = script =>
	Object.values(script)


export {
	importScript,
	exportScript
}
