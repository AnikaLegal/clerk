import React, { useState, useEffect } from 'react'
import { Formik } from 'formik'
import {
  Header,
  Form,
  Button,
  Message,
  Segment,
  Dropdown,
} from 'semantic-ui-react'
import { DateInput } from 'semantic-ui-calendar-react'
import moment from 'moment'

import { api } from 'api'

export const AssignForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [paralegals, setParalegals] = useState([])
  const [lawyers, setLawyers] = useState([])
  useEffect(() => {
    api.accounts
      .search({ group: 'Paralegal' })
      .then(({ resp, data }) => setParalegals(data))
      .then(() => api.accounts.search({ group: 'Lawyer' }))
      .then(({ resp, data }) => setLawyers(data))
      .then(() => setIsLoading(false))
  }, [])
  return (
    <Segment>
      <Header>Assign a paralegal to this case.</Header>
      <Formik
        initialValues={{
          paralegal: issue.paralegal ? issue.paralegal.id : null,
          lawyer: issue.lawyer ? issue.lawyer.id : null,
        }}
        validate={({ paralegal, lawyer }) => {
          const errors = {}
          if (paralegal && !lawyer)
            errors.lawyer =
              'A lawyer must be selected if a paralegal is assigned'
          return errors
        }}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          api.case.assign(issue.id, values).then(({ resp, data }) => {
            if (resp.status === 400) {
              setErrors(data)
            } else if (resp.ok) {
              setIssue(data.issue)
              setSuccess(true)
            } else {
              setErrors({
                'Submission failure':
                  'We could not perform this action because something went wrong.',
              })
            }
            setSubmitting(false)
          })
        }}
      >
        {({
          values,
          errors,
          handleChange,
          handleSubmit,
          isSubmitting,
          setFieldValue,
        }) => (
          <Form
            onSubmit={handleSubmit}
            success={isSuccess}
            error={Object.keys(errors).length > 0}
          >
            <Dropdown
              fluid
              selection
              search
              value={values.paralegal}
              style={{ margin: '1em 0' }}
              loading={isSubmitting || isLoading}
              placeholder="Select a paralegal"
              options={[{ id: null, email: '-' }, ...paralegals].map((u) => ({
                key: u.id,
                value: u.id,
                text: u.email,
              }))}
              onChange={(e, { value }) =>
                setFieldValue('paralegal', value, false)
              }
            />
            <Dropdown
              fluid
              selection
              search
              value={values.lawyer}
              style={{ margin: '1em 0' }}
              loading={isSubmitting || isLoading}
              placeholder="Select a lawyer"
              options={[{ id: null, email: '-' }, ...lawyers].map((u) => ({
                key: u.id,
                value: u.id,
                text: u.email,
              }))}
              onChange={(e, { value }) => setFieldValue('lawyer', value, false)}
            />
            {Object.entries(errors).map(([k, v]) => (
              <Message error key={k}>
                <div className="header">{k}</div>
                <p>{v}</p>
              </Message>
            ))}
            <Button
              loading={isSubmitting}
              disabled={isSubmitting}
              positive
              type="submit"
            >
              Update
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>Case assignment successful</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
