import {
  Badge,
  Button,
  Container,
  Group,
  Loader,
  Select,
  SelectProps,
  Text,
  Title,
} from '@mantine/core'
import { createFormContext } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks'
import api, {
  Client,
  IssueCreate,
  Tenancy,
  TenancyCreate,
  useCreateCaseMutation,
  useGetClientsQuery,
} from 'api'
import { TextButton } from 'comps/button'
import {
  MinimalClientFormModal,
  MinimalTenancyFormModal,
  RequiredClientSchema,
  RequiredTenancySchema,
} from 'comps/modal'
import { yupResolver } from 'mantine-form-yup-resolver'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { RequiredKeysOf } from 'type-fest'
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'
import * as Yup from 'yup'

interface DjangoContext {
  choices: {
    topic: string[][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const Topics = CONTEXT.choices.topic.sort((a, b) => a[1].localeCompare(b[1]))

type ClientLikeData = Pick<Client, 'id' | 'first_name' | 'last_name' | 'email'>
type TenancyLikeData = Pick<Tenancy, 'id' | 'address' | 'suburb' | 'postcode'>

export type CaseProperties = Pick<
  IssueCreate,
  | RequiredKeysOf<IssueCreate>
  | 'client_id'
  | 'client'
  | 'tenancy_id'
  | 'tenancy'
>

/* One of each of the following mutually exclusive properties are required:
 * - client or client_id
 * - tenancy or tenancy_id
 */
export const CreateCaseSchema: Yup.ObjectSchema<CaseProperties> =
  Yup.object().shape(
    {
      topic: Yup.string().required(),
      client: RequiredClientSchema.when('client_id', {
        is: (value) => value === undefined,
        then: (schema) => schema.required().default(undefined),
        otherwise: (schema) => schema.optional().default(undefined),
      }),
      client_id: Yup.string().when('client', {
        is: (value) => value === undefined || Object.keys(value).length == 0,
        then: (schema) => schema.required(),
        otherwise: (schema) => schema.optional(),
      }),
      tenancy: RequiredTenancySchema.when('tenancy_id', {
        is: (value) => value === undefined,
        then: (schema) => schema.required().default(undefined),
        otherwise: (schema) => schema.optional().default(undefined),
      }),
      tenancy_id: Yup.number().when('tenancy', {
        is: (value) => value === undefined || Object.keys(value).length == 0,
        then: (schema) => schema.required(),
        otherwise: (schema) => schema.optional(),
      }),
    },
    [
      ['client_id', 'client'],
      ['tenancy_id', 'tenancy'],
    ]
  )

type CaseFormValues = Yup.InferType<typeof CreateCaseSchema>

const [CaseFormProvider, useCaseFormContext, useCaseForm] =
  createFormContext<CaseFormValues>()

const getAddress = (tenancy: Tenancy | TenancyCreate) => {
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

const App = () => {
  const [createCase] = useCreateCaseMutation()
  const form = useCaseForm({
    mode: 'uncontrolled',
    validate: yupResolver(CreateCaseSchema),
    enhanceGetInputProps: ({ field, form }) => {
      const values = form.getValues()
      if (field === 'client' && values.client) {
        return { defaultValue: values.client.email }
      } else if (field === 'tenancy' && values.tenancy) {
        return { defaultValue: getAddress(values.tenancy) }
      } else if (field === 'tenancy_id' && values.tenancy_id) {
        return { defaultValue: values.tenancy_id.toString() }
      }
    },
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
    <Container size="xl">
      <Title order={1} mb="md">
        Create a new case
      </Title>
      <CaseFormProvider form={form}>
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Select
            {...form.getInputProps('topic')}
            key={form.key('topic')}
            label="Topic"
            placeholder="Select case topic"
            size="md"
            mt="md"
            data={Topics.map(([value, label]) => ({
              value,
              label,
            }))}
            withCheckIcon={false}
          />
          <ClientSelectField size="md" mt="md" />
          <TenancySelectField size="md" mt="md" />
          <Button
            type="submit"
            mt="md"
            disabled={form.submitting || !form.isValid()}
            loading={form.submitting}
          >
            Create case
          </Button>
        </form>
      </CaseFormProvider>
    </Container>
  )
}
mount(App)

const ClientSelectField = (props: SelectProps) => {
  const [opened, handlers] = useDisclosure(false)
  const [data, setData] = useState<ClientLikeData[]>([])

  const result = useGetClientsQuery({ pageSize: -1 }) // returns all results.
  const form = useCaseFormContext()

  const values = form.getValues()
  const inputPropsName = values.client ? 'client' : 'client_id'

  useEffect(() => {
    setData(result.data?.results || [])
  }, [result.isLoading])

  const handleSubmit = (modalForm, values) => {
    handlers.close()
    modalForm.reset()

    setData((prev) => [{ id: values.email, ...values }, ...prev])
    form.setValues({ client: values, client_id: undefined })
  }

  const handleChange = (value) => {
    if (!value) {
      form.setValues({ client: undefined, client_id: undefined })
    } else {
      const client = data.find((client) => client.id === value)
      if (client) {
        if (client.id === client.email) {
          const { id, ...remaining } = client
          form.setValues({ client: remaining, client_id: undefined })
        } else {
          form.setValues({ client_id: value, client: undefined })
        }
      }
    }
  }

  const renderOption = ({ option }) => {
    const client = data.find((client) => client.id === option.value)
    if (!client) {
      return undefined
    }
    return (
      <Group gap="sm" justify="space-between" w="100%">
        <div>
          <Text size="md">
            {client.first_name} {client.last_name}
          </Text>
          <Text size="sm" opacity={0.5}>
            {client.email}
          </Text>
        </div>
        {client.id === client.email && <Badge radius="xs">PENDING</Badge>}
      </Group>
    )
  }

  return (
    <>
      <MinimalClientFormModal
        title="Create a new client"
        submitButtonLabel="Create client"
        opened={opened}
        onClose={handlers.close}
        onFormSubmit={handleSubmit}
      />
      <Select
        {...props}
        key={form.key('client_id')}
        {...form.getInputProps(inputPropsName)}
        clearable
        searchable
        renderOption={renderOption}
        rightSection={result.isFetching && <Loader size="sm" />}
        nothingFoundMessage="No clients found"
        placeholder="Search for an existing client"
        limit={100}
        data={data.map((client) => ({
          value: client.id,
          label: `${client.first_name} ${client.last_name} (${client.email})`,
        }))}
        label={
          <Group wrap="nowrap" gap="sm" justify="space-between">
            <span>Client</span>
            <TextButton onClick={handlers.open} aria-label="Create client">
              create
            </TextButton>
          </Group>
        }
        labelProps={{ labelElement: 'div' }}
        styles={{ label: { width: '100%' } }}
        onChange={handleChange}
      />
    </>
  )
}

const TenancySelectField = (props: SelectProps) => {
  const [opened, handlers] = useDisclosure(false)

  const [data, setData] = useState<TenancyLikeData[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [getCases] = api.useLazyGetCasesQuery()

  const form = useCaseFormContext()

  const values = form.getValues()
  const inputPropsName = values.tenancy ? 'tenancy' : 'tenancy_id'
  const placeholder = values.client
    ? 'Create a new tenancy'
    : !values.client_id
      ? 'Select a client first'
      : 'Select an existing tenancy or create a new one'

  /* Load the clients tenancies when the client id changes */
  form.watch('client_id', (clientId) => {
    if (clientId.value !== clientId.previousValue) {
      setData([])
      form.setValues({
        tenancy_id: undefined,
        tenancy: undefined,
      })

      if (!clientId.value) {
        setIsLoading(false)
      } else {
        setIsLoading(true)
        getCases({ client: clientId.value, pageSize: -1 })
          .unwrap()
          .then((response) => {
            const tenancies = response.results.map((issue) => issue.tenancy)
            const uniqueTenancies = Object.values(
              Object.fromEntries(
                tenancies.map((tenancy) => [tenancy.id, tenancy])
              )
            )
            setData(uniqueTenancies)

            if (uniqueTenancies.length == 1) {
              form.setValues({
                tenancy_id: uniqueTenancies[0].id,
                tenancy: undefined,
              })
            }
          })
          .catch(() => {
            enqueueSnackbar('Failed to load tenancies', { variant: 'error' })
          })
          .finally(() => {
            setIsLoading(false)
          })
      }
    }
  })
  form.watch('client', (client) => {
    if (
      client.value &&
      client.previousValue &&
      client.value !== client.previousValue
    ) {
      setData([])
      form.setValues({
        tenancy_id: undefined,
        tenancy: undefined,
      })
    }
  })

  const handleSubmit = (modalForm, values) => {
    handlers.close()
    modalForm.reset()

    setData((prev) => [{ id: getAddress(values), ...values }, ...prev])
    form.setValues({ tenancy: values, tenancy_id: undefined })
  }

  const handleChange = (value: string | null) => {
    if (value) {
      const tenancy = data.find((tenancy) => tenancy.id.toString() === value)
      if (tenancy) {
        if (tenancy.id.toString() === getAddress(tenancy)) {
          const { id, ...remaining } = tenancy
          form.setValues({ tenancy: remaining, tenancy_id: undefined })
        } else {
          form.setValues({ tenancy_id: tenancy.id, tenancy: undefined })
        }
      }
    }
  }

  const renderOption = ({ option }) => {
    const tenancy = data.find(
      (tenancy) => tenancy.id.toString() === option.value
    )
    if (!tenancy) {
      return undefined
    }
    return (
      <Group gap="sm" justify="space-between" w="100%">
        <div>
          <Text size="md">{option.label}</Text>
        </div>
        {option.value === getAddress(tenancy) && (
          <Badge radius="xs">PENDING</Badge>
        )}
      </Group>
    )
  }

  return (
    <>
      <MinimalTenancyFormModal
        title="Create a new tenancy"
        submitButtonLabel="Create tenancy"
        opened={opened}
        onClose={handlers.close}
        onFormSubmit={handleSubmit}
      />
      <Select
        {...props}
        key={form.key('tenancy_id')}
        {...form.getInputProps(inputPropsName)}
        placeholder={placeholder}
        nothingFoundMessage="No tenancies found"
        data={data.map((tenancy) => ({
          value: tenancy.id.toString(),
          label: getAddress(tenancy),
        }))}
        renderOption={renderOption}
        disabled={isLoading}
        rightSection={isLoading && <Loader size="sm" />}
        label={
          <Group wrap="nowrap" gap="sm" justify="space-between">
            <span>Tenancy</span>
            <TextButton onClick={handlers.open} aria-label="Create tenancy">
              create
            </TextButton>
          </Group>
        }
        labelProps={{ labelElement: 'div' }}
        styles={{ label: { width: '100%' } }}
        withCheckIcon={false}
        onChange={handleChange}
      />
    </>
  )
}
