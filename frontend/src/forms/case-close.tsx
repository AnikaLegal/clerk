import api, { Service } from 'api'
import { TextArea } from 'comps/textarea'
import { OUTCOMES } from 'consts'
import { Formik } from 'formik'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import {
  Button,
  Checkbox,
  Dropdown,
  Form,
  Header,
  Message,
  Segment,
} from 'semantic-ui-react'
import { CaseDetailFormProps } from 'types'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import * as Yup from 'yup'
import { ServiceCategory } from './case-service'

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

export const CloseForm: React.FC<CaseDetailFormProps> = ({
  issue,
  onCancel,
}) => {
  const [isSuccess, setSuccess] = useState(false)
  const [updateCase] = api.useUpdateCaseMutation()

  const servicesResult = api.useGetCaseServicesQuery({
    id: issue.id,
    category: ServiceCategory.Ongoing,
  })
  const isLoadingServices = servicesResult.isLoading

  const findUnfinishedServices = (service: Service) =>
    service.finished_at === null
  const hasUnfinishedServices =
    servicesResult.data?.find(findUnfinishedServices) !== undefined

  const onSubmit = (values, { setSubmitting, setErrors }) => {
    updateCase({
      id: issue.id,
      issueUpdate: values as any,
    })
      .unwrap()
      .then(() => {
        setSubmitting(false)
        setSuccess(true)
        enqueueSnackbar('Case close success', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Case close failed'), {
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
      <Header>Close the case.</Header>
      <p>
        Please make sure you correctly set all of the fields in this form. This
        data is crucial for our reporting and decision making.
      </p>
      <Formik
        validationSchema={FormSchema}
        initialValues={{
          is_open: false,
          stage: 'CLOSED',
          outcome: issue.outcome,
          provided_legal_services: issue.provided_legal_services,
          outcome_notes: issue.outcome_notes,
        }}
        onSubmit={onSubmit}
      >
        {({ values, errors, handleSubmit, isSubmitting, setFieldValue }) => (
          <Form
            onSubmit={handleSubmit}
            success={isSuccess}
            error={Object.keys(errors).length > 0 || hasUnfinishedServices}
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
              onChange={(e) =>
                setFieldValue('outcome_notes', e.target.value, false)
              }
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
                {k != 'non_field_errors' && <div className="header">{k}</div>}
                <p>{v}</p>
              </Message>
            ))}
            {!isLoadingServices && hasUnfinishedServices && (
              <Message error>
                <p>Cannot close case with unfinished ongoing services</p>
              </Message>
            )}
            <Button
              loading={isSubmitting || isLoadingServices}
              disabled={
                isSubmitting || isLoadingServices || hasUnfinishedServices
              }
              positive
              type="submit"
            >
              Close case
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>Case closed</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
