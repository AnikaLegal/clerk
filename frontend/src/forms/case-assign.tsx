import { useGetUsersQuery, useUpdateCaseMutation } from 'api'
import { Formik } from 'formik'
import { useSnackbar } from 'notistack'
import React, { useState } from 'react'
import {
  Button,
  Dropdown,
  Form,
  Header,
  Message,
  Segment,
} from 'semantic-ui-react'
import { CaseDetailFormProps } from 'types/case'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'

export const AssignForm: React.FC<CaseDetailFormProps> = ({
  issue,
  onCancel,
}) => {
  const [updateCase] = useUpdateCaseMutation()
  const { enqueueSnackbar } = useSnackbar()
  const [isSuccess, setSuccess] = useState(false)
  const paralegalResults = useGetUsersQuery({ group: 'Paralegal', isActive: true, sort: "email" })
  const lawyerResults = useGetUsersQuery({ group: 'Lawyer', isActive: true, sort: "email" })
  const isLoading = paralegalResults.isFetching || lawyerResults.isFetching

  const lawyers = lawyerResults.data ?? []
  const paralegals = paralegalResults.data ?? []

  const onSubmit = (values, { setSubmitting, setErrors }) => {
    updateCase({
      id: issue.id,
      issueUpdate: {
        paralegal_id: values.paralegal,
        lawyer_id: values.lawyer,
      } as any,
    })
      .unwrap()
      .then(() => {
        setSubmitting(false)
        setSuccess(true)
        enqueueSnackbar('Assignment success', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Assignment failed'), {
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
        onSubmit={onSubmit}
      >
        {({ values, errors, handleSubmit, isSubmitting, setFieldValue }) => (
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
              options={paralegals.map((u) => ({
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
                <p>{v as string}</p>
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
