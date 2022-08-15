import React, { useState } from 'react'
import { Formik } from 'formik'
import {
  Header,
  Form,
  Button,
  Message,
  Segment,
  Checkbox,
  Dropdown,
} from 'semantic-ui-react'
import { DateInput } from 'semantic-ui-calendar-react'
import moment from 'moment'

import { api } from 'api'
import { STAGES } from 'consts'

const STAGE_OPTIONS = Object.entries(STAGES)
  .filter(([k, v]) => k !== 'CLOSED')
  .map(([k, v]) => ({
    key: k,
    value: k,
    text: v,
  }))

export const submitCaseUpdate =
  (issue, setIssue, setSuccess) =>
  (values, { setSubmitting, setErrors }) => {
    api.case.update(issue.id, values).then(({ resp, data }) => {
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
  }

export const ProgressForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false)
  return (
    <Segment>
      <Header>Update the stage of the case.</Header>
      <Formik
        initialValues={{
          stage: issue.stage,
          provided_legal_services: issue.provided_legal_services,
        }}
        validate={() => {}}
        onSubmit={submitCaseUpdate(issue, setIssue, setSuccess)}
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
              value={values.stage}
              style={{ margin: '1em 0' }}
              loading={isSubmitting}
              placeholder="Select a case stage"
              options={STAGE_OPTIONS}
              onChange={(e, { value }) => setFieldValue('stage', value, false)}
            />
            <div style={{ margin: '1em 0' }}>
              <Checkbox
                label="Provided legal services"
                checked={values.provided_legal_services}
                onChange={(e, { checked }) =>
                  setFieldValue(
                    'provided_legal_services',
                    Boolean(checked),
                    false
                  )
                }
                disabled={isSubmitting}
              />
            </div>
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
            <Message success>Case status updated</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
