const FIELD_KEYS = ['name', 'start', 'prompt', 'options', 'help', 'details', 'then', 'type']
const FIELD_TYPES = ['text', 'email', 'multiple choice', 'single choice', 'boolean', 'date', 'info', 'number']
const MANDATORY_FIELDS = ['name', 'prompt', 'type']
const CONDITIONS = [
  'is',
  'is not',
  'is greater than', // (int)
  'is less than', // (int)
]

export { FIELD_KEYS, FIELD_TYPES, MANDATORY_FIELDS, CONDITIONS }
