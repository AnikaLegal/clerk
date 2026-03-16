// Store user's form data in local storage
const FORM_DATA_KEY = 'intakeFormData'

export const loadFormData = (): Object | void => {
  const loadedDataStr = localStorage.getItem(FORM_DATA_KEY)
  if (loadedDataStr) {
    return JSON.parse(loadedDataStr)
  }
}

export const storeFormData = (data: Object) => {
  localStorage.setItem(FORM_DATA_KEY, JSON.stringify(data))
}
