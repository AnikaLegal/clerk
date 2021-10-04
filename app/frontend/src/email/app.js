import React, { useState } from 'react'

import { http } from 'http'

// Read initial data embedded in HTML by Django
const INIT_DATA = {
  caseEmailAddress: window.initialData.caseEmailAddress,
  drafts: window.initialData.drafts,
}
export const App = () => {
  const { drafts, caseEmailAddress } = INIT_DATA

  return (
    <>
      <h2 style={{ marginTop: '1rem' }}>Emails</h2>
      <p>
        Case email address: <strong>{caseEmailAddress}</strong>
      </p>
      <div className="ui segment padded">
        <h3>Drafts</h3>
        {drafts && (
          <div className="ui relaxed divided list">
            {drafts.map((email) => (
              <DraftEmail key={email.id} email={email} />
            ))}
          </div>
        )}
        <a href="#">
          <button className="ui button primary" type="submit">
            New Draft
          </button>
        </a>
      </div>
    </>
  )
}

const DraftEmail = ({ email }) => {
  const [isOpen, setIsOpen] = useState(false)
  const onSubmit = (e) => {
    e.preventDefault()
    const data = new FormData(e.target)
    http.patch('./api/draft').then()
  }
  return (
    <div className="item">
      <i className="large mail middle aligned icon"></i>
      <div className="content">
        <a onClick={() => setIsOpen(!isOpen)} className="header">
          {email.subject}
        </a>
        <div className="description">to {email.to_address}</div>
        {isOpen && (
          <form
            method="post"
            className="ui form"
            encType="multipart/form-data"
            onSubmit={onSubmit}
          >
            <input
              type="hidden"
              name="csrfmiddlewaretoken"
              value={window.CSRFToken}
            />
            <TextField
              label="Subject"
              name="subject"
              value={email.subject}
              placeholder="A very important email"
            />
            <TextField
              label="To Address"
              name="to_address"
              value={email.to_address}
              placeholder="jane@example.com"
            />
            <TextField
              label="CC Addresses"
              name="cc_addresses"
              value={email.cc_addresses}
              placeholder="anne@example.com, mark@example.com"
            />
            <TextAreaField
              label="Email Body"
              name="text"
              value={email.text}
              rows={12}
              placeholder="Dear Ms Example..."
            />
            <label>Attachments</label>
            <input type="file" multiple name="attachments" />
            <button className="ui positive button" type="submit">
              Update draft
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

const TextField = ({ label, name, value, placeholder, errors }) => (
  <div className={`field ${errors} && "error"`}>
    <label>{label}</label>
    <input
      type="text"
      name={name}
      defaultValue={value}
      placeholder={placeholder}
    />
  </div>
)

const TextAreaField = ({ label, name, rows, value, placeholder, errors }) => (
  <div className={`field ${errors} && "error"`}>
    <label>{label}</label>
    <textarea
      rows={rows || 3}
      name={name}
      placeholder={placeholder}
      defaultValue={value}
    />
  </div>
)
