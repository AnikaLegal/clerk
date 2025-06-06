import {
  Button,
  ComboboxData,
  ComboboxItem,
  Group,
  Loader,
  Select,
  SelectProps,
  Text,
  Title,
} from '@mantine/core'
import { createFormContext } from '@mantine/form'
import api, { IssueCreate, Tenancy, useCreateCaseMutation } from 'api'
import { yupResolver } from 'mantine-form-yup-resolver'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { Container, Header } from 'semantic-ui-react'
import {
  getAPIErrorMessage,
  getAPIFormErrors,
  mount,
  RequiredProps,
} from 'utils'
import * as Yup from 'yup'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: string[][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

export const CreateCaseSchema: Yup.ObjectSchema<RequiredProps<IssueCreate>> =
  Yup.object({
    topic: Yup.string().required(),
    client_id: Yup.string().required(),
    tenancy_id: Yup.number().required(),
  })

type FormValues = Yup.InferType<typeof CreateCaseSchema>

const [FormProvider, useFormContext, useForm] = createFormContext<FormValues>()

const App = () => {
  const [createCase] = useCreateCaseMutation()
  const form = useForm({
    mode: 'controlled',
    initialValues: {
      topic: '',
      client_id: '',
      tenancy_id: null!,
    },
    validate: yupResolver(CreateCaseSchema),
  })

  const handleSubmit = (values: typeof form.values) => {
    createCase({ issueCreate: values })
      .unwrap()
      .then((response) => {
        window.location.href = response.url
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to create a new case'), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          form.setErrors(requestErrors)
        }
        form.setSubmitting(false)
      })
  }

  return (
    <Container>
      <Title order={1} mb="md">
        Create a new case
      </Title>
      <FormProvider form={form}>
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Header as="h3">Case</Header>
          <Select
            {...form.getInputProps('topic')}
            key={form.key('topic')}
            label={
              <Text fw={700} mb="0.25rem">
                Topic
              </Text>
            }
            placeholder="Select case topic"
            size="md"
            mt="md"
            data={CONTEXT.choices.topic.map(([value, label]) => ({
              value,
              label,
            }))}
          />
          <ClientSelectField
            {...form.getInputProps('client_id')}
            key={form.key('client_id')}
            label={
              <Text fw={700} mb="0.25rem">
                Client
              </Text>
            }
            placeholder="Select client"
            size="md"
            mt="md"
          />
          <TenancyDropdownField
            {...form.getInputProps('tenancy_id')}
            key={form.key('tenancy_id')}
            label={
              <Text fw={700} mb="0.25rem">
                Tenancy
              </Text>
            }
            placeholder="Select tenancy"
            size="md"
            mt="md"
          />
          <Button
            type="submit"
            mt="md"
            disabled={form.submitting || !form.isValid()}
            loading={form.submitting}
          >
            Create case
          </Button>
        </form>
      </FormProvider>
    </Container>
  )
}
mount(App)

interface ClientInfo {
  full_name: string
  email: string
}

const ClientSelectField = (props: SelectProps) => {
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [clients, setClients] = useState<Record<string, ClientInfo>>({})
  const [getClients] = api.useLazyGetClientsQuery()

  useEffect(() => {
    getClients({ page: page, pageSize: 200 }, true /* preferCacheValue */)
      .unwrap()
      .then((response) => {
        const newClients = response.results.reduce(
          (a, client) => ({
            ...a,
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
        if (response.next) {
          setPage(response.next)
        } else {
          setIsLoading(false)
        }
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to load clients'), {
          variant: 'error',
        })
        setIsLoading(false)
      })
  }, [page])

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
    <Select
      {...props}
      clearable
      searchable
      data={data}
      renderOption={renderOption}
      limit={25}
      nothingFoundMessage="No clients found"
      rightSection={isLoading && <Loader size="sm" />}
    />
  )
}

const TenancyDropdownField = (props: SelectProps) => {
  const form = useFormContext()
  const [options, setOptions] = useState<ComboboxItem[]>([])
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

  form.watch('client_id', (clientId) => {
    if (clientId.value !== clientId.previousValue) {
      setOptions([])
      form.setValues({ tenancy_id: null! })

      if (!clientId.value) {
        setIsLoading(false)
        setNotFound(false)
        return
      }
      setIsLoading(true)
      getCases({ client: clientId.value, page: page })
        .unwrap()
        .then((response) => {
          const tenancies = response.results.map((issue) => issue.tenancy)
          const uniqueTenancies = Object.values(
            Object.fromEntries(
              tenancies.map((tenancy) => [tenancy.id, tenancy])
            )
          )
          const options = uniqueTenancies.map((tenancy) => ({
            value: tenancy.id.toString(),
            label: getAddress(tenancy),
          }))
          setOptions((prevOptions) => [...prevOptions, ...options])

          if (response.next) {
            setPage(response.next)
          } else {
            if (options.length == 0) {
              setNotFound(true)
            } else if (options.length == 1) {
              form.setValues({ tenancy_id: Number(options[0].value) })
            }
            setIsLoading(false)
          }
        })
        .catch(() => {
          setIsLoading(false)
          enqueueSnackbar('Failed to load tenancies', { variant: 'error' })
        })
    }
  })

  return (
    <Select
      {...props}
      error={notFound ? 'No tenancies found' : undefined}
      data={options}
      disabled={isLoading}
      rightSection={isLoading && <Loader size="sm" />}
      value={form.getValues().tenancy_id?.toString() || null}
    />
  )
}
