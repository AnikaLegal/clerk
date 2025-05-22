import {
  Issue,
  IssueCreate,
  useCreateCaseMutation,
  useGetCasesQuery,
  useGetTenancyQuery,
} from 'api'
import { Formik } from 'formik'
import { ClientSelectSearchField, DropdownField } from 'forms/formik'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { Button, Container, Form, Header } from 'semantic-ui-react'
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'
import * as Yup from 'yup'

interface DjangoContext {
  topic_options: { key: string; value: string; text: string }[]
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

Yup.setLocale({ mixed: { required: 'This field is required.' } })

export const CreateCaseSchema: Yup.ObjectSchema<IssueCreate> = Yup.object({
  topic: Yup.string().required(),
  client_id: Yup.string().required(),
  tenancy_id: Yup.number().required(),
  stage: Yup.string().optional(),
  outcome: Yup.string().nullable().optional(),
  outcome_notes: Yup.string().optional(),
  provided_legal_services: Yup.boolean().optional(),
  paralegal_id: Yup.number().nullable().optional(),
  lawyer_id: Yup.number().nullable().optional(),
  support_worker_id: Yup.number().nullable().optional(),
  employment_status: Yup.string().optional(),
  weekly_income: Yup.number().nullable().optional(),
  referrer: Yup.string().optional(),
  referrer_type: Yup.string().optional(),
  weekly_rent: Yup.number().nullable().optional(),
})

const App = () => {
  const [createCase] = useCreateCaseMutation()
  return (
    <Container>
      <Header as="h1">Create a new case</Header>
      <Formik
        initialValues={{
          topic: '',
          client_id: '',
          tenancy_id: undefined!,
        }}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          createCase({ issueCreate: values })
            .unwrap()
            .then((caseResponse) => {
              window.location.href = caseResponse.url
            })
            .catch((e) => {
              enqueueSnackbar(
                getAPIErrorMessage(e, 'Failed to create a new case'),
                {
                  variant: 'error',
                }
              )
              const requestErrors = getAPIFormErrors(e)
              if (requestErrors) {
                setErrors(requestErrors)
              }
              setSubmitting(false)
            })
        }}
        validationSchema={CreateCaseSchema}
      >
        {({ handleSubmit, values, errors, isSubmitting }) => (
          <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
            <Header as="h3">Case</Header>
            <DropdownField
              name="topic"
              label="Topic"
              placeholder="Select case topic"
              options={CONTEXT.topic_options}
            />
            <ClientSelectSearchField name="client_id" label="Client" />
            <TenancyDropdownField
              clientId={values.client_id}
              name="tenancy_id"
              label="Tenancy"
              placeholder="Select client tenancy"
            />
            <Button
              primary
              type="submit"
              disabled={isSubmitting}
              loading={isSubmitting}
            >
              Create case
            </Button>
          </Form>
        )}
      </Formik>
    </Container>
  )
}
mount(App)

interface TenancyDropdownFieldProps {
  clientId: string
  name: string
  label: string
  placeholder: string
}

export function TenancyDropdownField({
  clientId,
  name,
  label,
  placeholder,
}: TenancyDropdownFieldProps) {
  const [tenancyOptions, setTenancyOptions] = useState<
    { key: number; value: number; text: string }[]
  >([])

  const results = useGetCasesQuery({ client: clientId }, { skip: !clientId })
  useEffect(() => {
    if (results.data) {
      const options = results.data.results.map((issue: Issue) => ({
        key: issue.tenancy.id,
        value: issue.tenancy.id,
        text: issue.tenancy.address,
      }))
      setTenancyOptions(options)
    }
    if (results.error) {
      enqueueSnackbar('Failed to load tenancy options', { variant: 'error' })
    }
  }, [results])

  return (
    <DropdownField
      name={name}
      label={label}
      placeholder={placeholder}
      options={tenancyOptions}
      disabled={!clientId || results.isFetching}
    />
  )
}
