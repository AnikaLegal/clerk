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
import api, { IssueCreate, Tenancy, useCreateCaseMutation } from 'api'
import { TextButton } from 'comps/button'
import { CreateClientModal, CreateTenancyModal } from 'comps/modal'
import { ClientSelectInput } from 'forms/mantine/input'
import { yupResolver } from 'mantine-form-yup-resolver'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
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
const Topics = CONTEXT.choices.topic.sort((a, b) => a[1].localeCompare(b[1]))

export const CreateCaseSchema: Yup.ObjectSchema<RequiredProps<IssueCreate>> =
  Yup.object({
    topic: Yup.string().required(),
    client_id: Yup.string().required(),
    tenancy_id: Yup.number().required(),
  })

type CaseFormValues = Yup.InferType<typeof CreateCaseSchema>

const [CaseFormProvider, useCaseFormContext, useCaseForm] =
  createFormContext<CaseFormValues>()

const App = () => {
  const [createCase] = useCreateCaseMutation()
  const form = useCaseForm({
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
  const [opened, handlers] = useDisclosure(false)
  const form = useCaseFormContext()

  const onCreateSuccess = (modalForm, client) => {
    /* Reset & close the modal */
    modalForm.reset()
    handlers.close()

    form.setValues({ client_id: client.id })
    enqueueSnackbar('Client created', { variant: 'success' })
  }

  const onCreateFailed = (modalForm, exception) => {
    enqueueSnackbar(getAPIErrorMessage(exception, 'Failed to create client'), {
      variant: 'error',
    })
  }

  return (
    <>
      <CreateClientModal
        opened={opened}
        onClose={handlers.close}
        onSuccess={onCreateSuccess}
        onFailure={onCreateFailed}
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

  const onCreateSuccess = (modalForm, tenancy) => {
    /* Reset & close the modal */
    modalForm.reset()
    handlers.close()

    const option = {
      value: tenancy.id.toString(),
      label: getAddress(tenancy),
    }
    setCreatedOptions((prev) => [...prev, option])
    form.setValues({ tenancy_id: tenancy.id })

    enqueueSnackbar('Tenancy created', { variant: 'success' })
  }

  const onCreateFailed = (modalForm, exception) => {
    enqueueSnackbar(getAPIErrorMessage(exception, 'Failed to create tenancy'), {
      variant: 'error',
    })
  }

  return (
    <>
      <CreateTenancyModal
        opened={opened}
        onClose={handlers.close}
        onSuccess={onCreateSuccess}
        onFailure={onCreateFailed}
      />
      <Select
        {...props}
        placeholder={
          !form.getValues().client_id
            ? 'Select a client first'
            : 'Select an existing tenancy'
        }
        nothingFoundMessage="No tenancies found"
        data={[...options, ...createdOptions]}
        disabled={isLoading}
        rightSection={isLoading && <Loader size="sm" />}
        value={form.getValues().tenancy_id?.toString() || null}
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
