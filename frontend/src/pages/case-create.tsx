import {
  Button,
  ComboboxItem,
  Container,
  Group,
  Loader,
  Select,
  SelectProps,
  Title,
} from '@mantine/core'
import { createFormContext } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks'
import api, {
  IssueCreate,
  Tenancy,
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
import { ClientLikeData, ClientSelectInput } from 'forms/mantine/input'
import { yupResolver } from 'mantine-form-yup-resolver'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { RequiredKeysOf } from 'type-fest'
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'
import * as Yup from 'yup'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: string[][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const Topics = CONTEXT.choices.topic.sort((a, b) => a[1].localeCompare(b[1]))

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

const App = () => {
  const [createCase] = useCreateCaseMutation()
  const form = useCaseForm({
    mode: 'controlled',
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
          <ClientSelectField
            {...form.getInputProps('client_id')}
            key={form.key('client_id')}
            size="md"
            mt="md"
          />
          <TenancySelectField
            {...form.getInputProps('tenancy_id')}
            key={form.key('tenancy_id')}
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
      </CaseFormProvider>
    </Container>
  )
}
mount(App)

const ClientSelectField = (props: SelectProps) => {
  const result = useGetClientsQuery({ pageSize: -1 }) // returns all results.
  const form = useCaseFormContext()
  const [opened, handlers] = useDisclosure(false)
  const [data, setData] = useState<ClientLikeData[]>([])
  const [value, setValue] = useState<string | undefined>(undefined)

  useEffect(() => {
    setData(result.data?.results || [])
  }, [result])

  form.watch('client', (client) => {
    if (client.value) {
      const { client_id, ...values } = form.getValues()
      form.setValues(values)
      setValue(client.value.email)
    }
  })
  form.watch('client_id', (clientId) => {
    if (clientId.value) {
      const { client, ...values } = form.getValues()
      form.setValues(values)
      setValue(undefined)
    }
  })

  const handleSubmit = (modalForm, values) => {
    form.setValues({ client: values })
    setData((prev) => [{ id: values.email, ...values }, ...prev])
    handlers.close()
    modalForm.reset()
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
      <ClientSelectInput
        {...props}
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
        value={value}
        data={data}
        isLoading={result.isFetching}
      />
    </>
  )
}

const TenancySelectField = (props: SelectProps) => {
  const form = useCaseFormContext()
  const [options, setOptions] = useState<ComboboxItem[]>([])
  const [createdOptions, setCreatedOptions] = useState<ComboboxItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [getCases] = api.useLazyGetCasesQuery()
  const [opened, handlers] = useDisclosure(false)
  const [value, setValue] = useState<string | undefined>(undefined)

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

  /* Load the clients tenancies when the client id changes */
  form.watch('client_id', (clientId) => {
    if (clientId.value !== clientId.previousValue) {
      setOptions([])
      form.setValues({ tenancy_id: null! })
      setValue(undefined)

      if (!clientId.value) {
        setIsLoading(false)
        return
      }
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
          const options = uniqueTenancies.map((tenancy) => ({
            value: tenancy.id.toString(),
            label: getAddress(tenancy),
          }))
          setOptions(options)

          if (options.length == 1) {
            form.setValues({ tenancy_id: Number(options[0].value) })
          }
        })
        .catch(() => {
          enqueueSnackbar('Failed to load tenancies', { variant: 'error' })
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  })

  form.watch('tenancy', (tenancy) => {
    if (tenancy.value) {
      const { tenancy_id, ...values } = form.getValues()
      form.setValues(values)
      setValue(getAddress(tenancy.value))
    }
  })
  form.watch('tenancy_id', (tenancyId) => {
    if (tenancyId.value) {
      const { tenancy, ...values } = form.getValues()
      form.setValues(values)
      setValue(tenancyId.value.toString())
    }
  })

  const handleSubmit = (modalForm, values) => {
    form.setValues({ tenancy: values })

    const address = getAddress(values)
    const option = {
      value: address,
      label: address,
    }
    setCreatedOptions((prev) => [...prev, option])

    handlers.close()
    modalForm.reset()
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
        placeholder={
          !form.getValues().client_id
            ? 'Select a client first'
            : 'Select an existing tenancy'
        }
        nothingFoundMessage="No tenancies found"
        value={value}
        data={[...options, ...createdOptions]}
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
      />
    </>
  )
}
