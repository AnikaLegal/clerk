module.exports = {
  FIELD_KEYS: [
    'name',
    'start',
    'prompt',
    'options',
    'help',
    'details',
    'then',
    'type',
  ],
  FIELD_TYPES: [
    'text',
    'email',
    'multiple choice',
    'single choice',
    'boolean',
    'date',
    'info',
    'number',
  ],
  MANDATORY_FIELDS: [
    'name',
    'prompt',
    'type',
  ],
  CONDITIONS: [
    'is',
    'is not',
    'is greater than', // (int)
    'is less than', // (int)
  ],
}
