import { FormEvent, useState } from 'react'

import { api } from '../api'
import { logException } from '../utils'

interface Errors {
  name?: string
  phoneNumber?: string
}

// Validation rules ported from the old form's noemail.js.
const validate = (name: string, phoneNumber: string): Errors => {
  const errors: Errors = {}
  if (!name) {
    errors.name = 'Hold on, a name is required'
  } else if (!/[a-z, A-Z]/.test(name)) {
    errors.name = "Hold on, that name doesn't look valid"
  }
  if (!phoneNumber) {
    errors.phoneNumber = 'Hold on, a phone number is required'
  } else if (phoneNumber.trim().length < 10 || !/[0-9]/.test(phoneNumber)) {
    errors.phoneNumber = "Hold on, that phone number doesn't look valid"
  }
  return errors
}

/**
 * Contact fallback for users without an email address: takes a name and
 * phone number and asks the coordinators to call them back.
 */
export const NoEmailPage = () => {
  const [name, setName] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [consented, setConsented] = useState(true)
  const [errors, setErrors] = useState<Errors>({})
  const [isSubmitted, setIsSubmitted] = useState(false)

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const validationErrors = validate(name, phoneNumber)
    setErrors(validationErrors)
    if (Object.keys(validationErrors).length > 0) return
    try {
      await api.noemail.create(name, phoneNumber)
      setIsSubmitted(true)
      setName('')
      setPhoneNumber('')
    } catch (error) {
      logException(error)
    }
  }

  return (
    <div className="intake-splash">
      <h1>
        Anika Legal is an online service, with the majority of communication and
        advice sent via email.
      </h1>
      <p>
        If you don't have an email address, please complete the form below and
        we'll call you to see if we're able to help. If not then we'll be able
        to direct you to another organisation.
      </p>
      <form className="intake-noemail-form" onSubmit={onSubmit}>
        <input
          placeholder="Name"
          type="text"
          name="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {errors.name && <p className="intake-error">{errors.name}</p>}
        <input
          placeholder="Phone Number"
          type="tel"
          name="phone_number"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
        />
        {errors.phoneNumber && (
          <p className="intake-error">{errors.phoneNumber}</p>
        )}
        <label className="intake-checkbox">
          <input
            type="checkbox"
            checked={consented}
            onChange={() => setConsented(!consented)}
            required
          />
          I agree to share my details with Anika Legal by ticking this box.
        </label>
        <button type="submit" className="d-btn d-btn-primary">
          Contact Us
        </button>
        {isSubmitted && <p>Contact request submitted</p>}
      </form>
    </div>
  )
}
