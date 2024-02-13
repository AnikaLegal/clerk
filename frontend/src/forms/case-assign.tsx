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

import { User } from 'types'
import { api } from 'api'

export const AssignForm = ({ issue, setIssue, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [paralegalResults, setParalegals] = useState<User[]>([])
  const [lawyerResults, setLawyers] = useState<User[]>([])
  useEffect(() => {
    api.accounts
      .search({ group: 'Paralegal' })
      .then(({ data }) => setParalegals(data))
      .then(() => api.accounts.search({ group: 'Lawyer' }))
      .then(({ data }) => setLawyers(data))
      .then(() => setIsLoading(false))
  }, [])

  const lawyers = [
    ...(lawyerResults ?? [])
  ].filter(x => x.is_active)
   .sort((a, b) => (a.email > b.email) ? 1 : -1)

  const paralegals = [
    ...(paralegalResults ?? [])
  ].filter(x => x.is_active)

  const ids = new Set(paralegalResults.map(x => x.id));
  const merged = [
    ...paralegalResults,
    ...lawyerResults.filter(x => !ids.has(x.id))
  ].sort((a, b) => (a.email > b.email) ? 1 : -1)

  return (
    <Segment>
      <Header>Assign a paralegal to this case.</Header>
      <Formik
        initialValues={{
          paralegal: issue.paralegal ? issue.paralegal.id : null,
          lawyer: issue.lawyer ? issue.lawyer.id : null,
        }}
        validate={({ paralegal, lawyer }) => {
          const errors: any = {}
          if (paralegal && !lawyer)
            errors.lawyer =
              'A lawyer must be selected if a paralegal is assigned'
          return errors
        }}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          api.case.assign(issue.id, values).then(({ resp, data, errors }) => {
            if (resp.status === 400) {
              setErrors(errors)
            } else if (resp.ok) {
              setIssue(data.issue)
              setSuccess(true)
            } else {
              setErrors({
                // @ts-ignore
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
              clearable
              fluid
              selection
              search
              value={values.paralegal}
              style={{ margin: '1em 0' }}
              loading={isSubmitting || isLoading}
              placeholder="Select a paralegal"
              options={merged.map((u) => ({
                key: u.id,
                value: u.id,
                text: u.email,
              }))}
              onChange={(e, { value }) =>
                setFieldValue('paralegal', value, false)
              }
            />
            <Dropdown
              clearable
              fluid
              selection
              search
              value={values.lawyer}
              style={{ margin: '1em 0' }}
              loading={isSubmitting || isLoading}
              placeholder="Select a lawyer"
              options={lawyers.map((u) => ({
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
