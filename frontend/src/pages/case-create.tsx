import { ComboboxData, Group, Loader, Text } from '@mantine/core'
import api, {
  IssueCreate,
  Tenancy,
  useCreateCaseMutation,
  useGetClientsQuery,
} from 'api'
import { Formik, FormikProps } from 'formik'
import { DropdownField, SelectField, SelectFieldProps } from 'forms/formik'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import {
  Button,
  Container,
  DropdownItemProps,
  Form,
  Header,
} from 'semantic-ui-react'
import {
  getAPIErrorMessage,
  getAPIFormErrors,
  mount,
  useEffectLazy,
} from 'utils'
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
  const [clients, setClients] = useState({})

  return (
    <Container>
      <Header as="h1">Create a new case</Header>
      <Formik
        validateOnMount
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
        {(formik) => {
          return (
            <Form
              onSubmit={formik.handleSubmit}
              error={Object.keys(formik.errors).length > 0}
            >
              <Header as="h3">Case</Header>
              <DropdownField
                name="topic"
                label="Topic"
                placeholder="Select case topic"
                options={CONTEXT.topic_options}
              />
              <ClientSelectField
                name="client_id"
                label="Client"
                placeholder="Select client"
              />
              <TenancyDropdownField
                clientId={formik.values.client_id}
                name="tenancy_id"
                label="Tenancy"
                placeholder="Select tenancy"
                formik={formik}
              />
              <Button
                primary
                type="submit"
                disabled={formik.isSubmitting || !formik.isValid}
                loading={formik.isSubmitting}
              >
                Create case
              </Button>
            </Form>
          )
        }}
      </Formik>
    </Container>
  )
}
mount(App)

interface ClientInfo {
  full_name: string
  email: string
}

export function ClientSelectField(props: SelectFieldProps) {
  const [page, setPage] = useState(1)
  const [isFinished, setIsFinished] = useState(false)
  const [clients, setClients] = useState<Record<string, ClientInfo>>({})
  const results = useGetClientsQuery({ page: page, pageSize: 200 })

  if (results.isError) {
    enqueueSnackbar(
      getAPIErrorMessage(results.error, 'Failed to load clients'),
      { variant: 'error' }
    )
    setIsFinished(true)
  } else if (!isFinished && !results.isLoading) {
    const newClients = results.data?.results.reduce(
      (acc, client) => ({
        ...acc,
        [client.id]: {
          full_name: client.full_name,
          email: client.email,
        },
      }),
      {}
    )
    setClients((prevClients) => {
      return { ...prevClients, ...newClients }
    })

    if (results.data?.next) {
      setPage(results.data.next)
    } else {
      setIsFinished(true)
    }
  }

  const renderOption = ({ option }) => {
    const client = clients[option.value]
    return (
      <Group gap="sm">
        <div>
          <Text size="md">{client.full_name}</Text>
          <Text size="sm" opacity={0.5}>
            {client.email}
          </Text>
        </div>
      </Group>
    )
  }

  const data: ComboboxData = Object.entries(clients).map(([id, client]) => ({
    value: id,
    label: `${client.full_name} (${client.email})`,
  }))

  return (
    <SelectField
      {...props}
      data={data}
      renderOption={renderOption}
      limit={25}
      nothingFoundMessage="No clients found"
      rightSection={!isFinished && <Loader size="sm" />}
    />
  )
}

interface TenancyDropdownFieldProps {
  clientId: string
  name: string
  label: string
  placeholder: string
  formik: FormikProps<any>
}

export function TenancyDropdownField({
  clientId,
  name,
  label,
  placeholder,
  formik,
}: TenancyDropdownFieldProps) {
  const [options, setOptions] = useState<DropdownItemProps[]>([])
  const [notFound, setNotFound] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [getCases] = api.useLazyGetCasesQuery()

  const getAddress = (tenancy: Tenancy) => {
    const address: string[] = []
    if (tenancy.address) {
      address.push(tenancy.address)
    }
    if (tenancy.suburb) {
      address.push(tenancy.suburb)
    }
    if (tenancy.postcode) {
      address.push(tenancy.postcode)
    }
    return address.join(', ')
  }

  const search = () => {
    setOptions([])
    if (!clientId) {
      setIsLoading(false)
      setNotFound(false)
      return
    }
    setIsLoading(true)
    getCases({ client: clientId, page: page })
      .unwrap()
      .then((response) => {
        const tenancies = response.results.map((issue) => issue.tenancy)
        const uniqueTenancies = Object.values(
          Object.fromEntries(tenancies.map((tenancy) => [tenancy.id, tenancy]))
        )
        const options = uniqueTenancies.map((tenancy) => ({
          key: tenancy.id,
          value: tenancy.id,
          text: getAddress(tenancy),
        }))
        setOptions((prevOptions) => [...prevOptions, ...options])

        if (response.next) {
          setPage(response.next)
        } else {
          setIsLoading(false)

          if (options.length == 0) {
            setNotFound(true)
          } else if (options.length == 1) {
            formik.setFieldValue(name, options[0].value)
          }
        }
      })
      .catch(() => {
        setIsLoading(false)
        enqueueSnackbar('Failed to load tenancies', { variant: 'error' })
      })
  }
  useEffectLazy(() => search(), [clientId, page])

  return (
    <DropdownField
      error={notFound}
      name={name}
      label={label}
      placeholder={notFound ? 'No tenancies found' : placeholder}
      options={options}
      disabled={!clientId || isLoading || notFound}
      loading={isLoading}
    />
  )
}
