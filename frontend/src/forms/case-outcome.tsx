import React, { useState } from 'react'
import { Formik } from 'formik'
import {
  Header,
  Form,
  Button,
  Message,
  Segment,
  Dropdown,
  Checkbox,
} from 'semantic-ui-react'
import * as Yup from 'yup'
import { useSnackbar } from 'notistack'

import { CaseDetailFormProps } from 'types'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { useUpdateCaseMutation } from 'api'
import { OUTCOMES } from 'consts'
import { TextArea } from 'comps/textarea'

const OUTCOME_OPTIONS = Object.entries(OUTCOMES).map(([k, v]) => ({
  key: k,
  value: k,
  text: v,
}))

const FormSchema = Yup.object().shape({
  outcome: Yup.string().nullable().required('Required'),
  outcome_notes: Yup.string().required('Required'),
  provided_legal_services: Yup.bool(),
})

export const OutcomeForm: React.FC<CaseDetailFormProps> = ({
  issue,
  onCancel,
}) => {
  const [isSuccess, setSuccess] = useState(false)
  const [updateCase] = useUpdateCaseMutation()
  const { enqueueSnackbar } = useSnackbar()

  const onSubmit = (values, { setSubmitting, setErrors }) => {
    updateCase({
      id: issue.id,
      issueUpdate: values as any,
    })
      .unwrap()
      .then(() => {
        setSubmitting(false)
        setSuccess(true)
        enqueueSnackbar('Case update success', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Case update failed'), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(err)
        if (requestErrors) {
          setErrors(requestErrors)
        }
        setSubmitting(false)
      })
  }
  return (
    <Segment>
      <Header>Edit case outcome.</Header>
      <p>
        Please make sure you correctly set all of the fields in this form. This
        data is crucial for our reporting and decision making.
      </p>
      <Formik
        validationSchema={FormSchema}
        initialValues={{
          outcome: issue.outcome,
          provided_legal_services: issue.provided_legal_services,
          outcome_notes: issue.outcome_notes,
        }}
        onSubmit={onSubmit}
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
              value={values.outcome}
              style={{ margin: '1em 0' }}
              loading={isSubmitting}
              placeholder="Select a case outcome"
              options={OUTCOME_OPTIONS}
              onChange={(e, { value }) =>
                setFieldValue('outcome', value, false)
              }
            />
            <TextArea
              onChange={(e) => setFieldValue('outcome_notes', e.target.value)}
              disabled={isSubmitting}
              rows={3}
              value={values.outcome_notes}
              style={{ marginBottom: '1em' }}
              placeholder="Write outcome notes here"
            />
            <div style={{ margin: '0 0 1em 0' }}>
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
              Update outcome
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>Outcome updated</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
