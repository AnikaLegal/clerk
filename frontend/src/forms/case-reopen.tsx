import React, { useState } from 'react'
import { Formik } from 'formik'
import {
  Header,
  Form,
  Button,
  Message,
  Segment,
  Dropdown,
} from 'semantic-ui-react'
import * as Yup from 'yup'
import { useSnackbar } from 'notistack'

import { CaseDetailFormProps } from 'types/case'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { useUpdateCaseMutation } from 'api'
import { CASE_STAGES } from 'consts'

const STAGE_OPTIONS = Object.entries(CASE_STAGES)
  .filter(([k, v]) => k !== 'CLOSED')
  .map(([k, v]) => ({
    key: k,
    value: k,
    text: v,
  }))

const FormSchema = Yup.object().shape({
  stage: Yup.string().required('Required'),
})

export const ReopenForm: React.FC<CaseDetailFormProps> = ({
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
        enqueueSnackbar('Case re-open success', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Case re-open failed'), {
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
      <Header>Re-open the case.</Header>
      <Formik
        initialValues={{
          is_open: true,
          stage: '',
        }}
        validationSchema={FormSchema}
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
              value={values.stage}
              style={{ margin: '1em 0' }}
              loading={isSubmitting}
              placeholder="Select a case stage"
              options={STAGE_OPTIONS}
              onChange={(e, { value }) => setFieldValue('stage', value, false)}
            />
            {Object.entries(errors).map(([k, v]) => (
              <Message error key={k}>
                <div className="header">{k}</div>
                <p>{v as string}</p>
              </Message>
            ))}
            <Button
              loading={isSubmitting}
              disabled={isSubmitting}
              positive
              type="submit"
            >
              Re-open case.
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>Case re-opened</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
