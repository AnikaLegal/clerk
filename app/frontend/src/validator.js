import {
  FIELD_KEYS,
  FIELD_TYPES,
  CONDITIONS,
  MANDATORY_FIELDS,
} from 'consts'

// Used to validate new questions, which are added to the script.
export default class ScriptValidator {
  constructor(script) {
    this.script = script
    this.errors = {}
  }

  // Returns true if the question being added is valid
  canAddQuestion = q => {
    this.errors = []
    // Do initial validation
    this.validateMandatoryFields(q)
    this.validateFieldWhitelist(q)
    // Bail if initial validation fails
    if (this.hasErrors()) return false
    // Validate each field
    const fieldValidators = {
      'name': this.validateName,
      'start': this.validateStart,
      'type': this.validateType,
      'options': this.validateOptions,
      'help': this.validateHelp,
      'details': this.validateDetails,
      'then': this.validateThen,
      'prompt': this.validatePrompt,
    }
    for (let fieldName of Object.keys(q)) {
      fieldValidators[fieldName](q)
    }
    return !this.hasErrors()
  }

  // All mandatory fields should be present
  validateMandatoryFields = q => {
    for (let fieldName of MANDATORY_FIELDS) {
      if (!q[fieldName]) {
        this.addError(`Field "${fieldName}" is required.`)
      }
    }
  }

  // All fields should be from the whitelist
  validateFieldWhitelist  = q => {
    for (let fieldName of Object.keys(q)) {
      if (!FIELD_KEYS.includes(fieldName)) {
        this.addError(`Field "${fieldName}" is not allowed.`)
      }
    }
  }

  // Validate the 'start' field.
  validateStart = q => {
    const numStarts = Object.values(this.script)
      .filter(question => q.name !== question.name)
      .map(question => question.start ? 1 : 0)
      .reduce((count, num) => count + num, 0)
    if (numStarts > 0 && q.start) {
      this.addError('Cannot have two start questions.')
    } else if (typeof(q.start) !== "boolean") {
      this.addError('Start field must be "true" or "false"')
    }
  }

  // Validate the 'type' field.
  validateType = q => {
    if (!FIELD_TYPES.includes(q.type)) {
      this.addError('Invalid value for "type')
    }
    const typeValidators = {
      'text': q => {},
      'email': q => {},
      'multiple choice': this.validateMultipleChoice,
      'single choice': this.validateSingleChoice,
      'boolean': q => {},
      'date': q => {},
      'info': q => {},
      'number': q => {},
    }
    typeValidators[q.type](q)
  }

  // Validate the 'options' field.
  validateOptions = q => {
    if (typeof(q.options !== "object")) {
      this.addError('Options field must be a list')
    }
    if (!q.options.every(this.validateOption)) {
      this.addError('Each option must have a hint and text field')
    }
  }

  validateOption = option => (
    typeof(option) === "object" &&
    (!option.hint || typeof(option.hint) === "string") &&
    option.text && typeof(option.text) === "string"
  )

  // Validate the 'help' field.
  validateHelp = q => {
    if (q.help && typeof(q.help !== "string")) {
      this.addError('The "help" field must only contain text.')
    }
  }

  // Validate the 'details' field.
  validateDetails = q => {
    if (typeof(q.details !== "object")) {
      this.addError('Details field must be a list')
    } else {
      for (let detail of q.details) {
        this.validateConditionalThen(q, detail, 'detail')
      }
    }
  }

  // Validate the 'then' field.
  validateThen = q => {
    if (typeof(q.then === "string")) {
      if (!this.getQuestionNames(q).includes(q.then)) {
        this.addError('The "then" field must reference another question')
      }
    } else if (typeof(q.then === "object")) {
      for (let then of q.then) {
        this.validateConditionalThen(q, then, 'then')
      }
    } else {
      this.addError('The "then" field must be a string or list')
    }
  }

  validateConditionalThen = (q, conditionalThen, fieldName) => {
    const then = conditionalThen.then
    const when = conditionalThen.when
    if (!then || !this.getQuestionNames(q).includes(then)) {
      this.addError(`The ${fieldName} field must have a "then" field which references another question`)
    }
    if (!when) return
    if (!when.variable || !when.condition || !when.value) {
      this.addError(`The ${fieldName} field must have a "when" field which has a variable, condition and value`)
      return
    }
    if (!this.getQuestionNames(q).includes(when.variable)) {
      this.addError(`The ${fieldName} field\'s "when" variables must reference another question`)
    }
    if (!(when.condition in CONDITIONS)) {
      this.addError(`The ${fieldName} field\'s "when" conditions must be a valid condition.`)
    }
  }

  // Validate the 'prompt' field.
  validatePrompt = q => {
    if (typeof(q.prompt) !== "string") {
      this.addError('The "prompt" field must only contain text.')
    }
  }

  // Validate the 'name' field.
  validateName = q => {
    if (typeof(q.name) !== "string") {
      this.addError('The "name" field must only contain text.')
    }
  }

  // Validate a 'multiple choice' type question.
  validateMultipleChoice = q => {
    if (!q.options) {
      this.addError('Multiple choice questions must have options')
    }
  }

  // Validate a 'single choice' type question.
  validateSingleChoice = q => {
    if (!q.options) {
      this.addError('Single choice questions must have options')
    }
  }

  // Get a list of all possible question names
  getQuestionNames = q => [
    ...Object.keys(this.script),
    q.name
  ]

  // Add error to the error list
  addError = (msg) =>
    this.errors.push(msg)

  // Get a count for how many errors we have
  getErrorCount = () =>
    this.errors.length

  // Returns true if the validator has errors
  hasErrors = () =>
    this.errors.length > 0
}
