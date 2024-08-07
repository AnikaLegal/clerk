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
import { useSnackbar } from 'notistack'

import { CaseDetailFormProps } from 'types/case'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { useUpdateCaseMutation } from 'api'
import { STAGES } from 'consts'

const STAGE_OPTIONS = Object.entries(STAGES)
  .filter(([k, v]) => k !== 'CLOSED')
  .map(([k, v]) => ({
    key: k,
    value: k,
    text: v,
  }))

export const ProgressForm: React.FC<CaseDetailFormProps> = ({
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
      <Header>Update the stage of the case.</Header>
      <Formik
        initialValues={{
          stage: issue.stage,
          provided_legal_services: issue.provided_legal_services,
        }}
        validate={() => {}}
        onSubmit={onSubmit}
      >
        {({ values, errors, handleSubmit, isSubmitting, setFieldValue }) => (
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
