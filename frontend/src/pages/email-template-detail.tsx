import { Center, Container, Loader, Text, Title } from '@mantine/core'
import {
  EmailTemplate,
  EmailTemplateCreate,
  useDeleteEmailTemplateMutation,
  useGetEmailTemplateQuery,
  useUpdateEmailTemplateMutation,
} from 'api'
import { EmailTemplateForm } from 'forms'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { getAPIErrorMessage, mount } from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: [string, string][]
  }
  list_url: string
  template_id: number
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const Topics = CONTEXT.choices.topic.sort((a, b) => a[1].localeCompare(b[1]))
const ListUrl = CONTEXT.list_url
const TemplateId = CONTEXT.template_id

const App = () => {
  const [updateEmailTemplate] = useUpdateEmailTemplateMutation()
  const [deleteEmailTemplate] = useDeleteEmailTemplateMutation()

  const handleDelete = () => {
    deleteEmailTemplate({ id: TemplateId })
      .unwrap()
      .then(() => {
        window.location.href = ListUrl
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to delete this email template'),
          {
            variant: 'error',
          }
        )
      })
  }

  const handleSubmit = (values: EmailTemplateCreate) => {
    updateEmailTemplate({
      id: TemplateId,
      emailTemplateCreate: values,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Updated email template', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to update email template'),
          {
            variant: 'error',
          }
        )
      })
  }

  const result = useGetEmailTemplateQuery({ id: TemplateId })
  return (
    <Container size="xl">
      <Title order={1}>Email Template</Title>
      <EmailTemplateDetailsForm
        result={result}
        onSubmit={handleSubmit}
        onDelete={handleDelete}
      />
    </Container>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  const message = getAPIErrorMessage(error, 'Could not load email template')

  React.useEffect(() => {
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])
  return (
    <Center>
      <Text c="red">{message}</Text>
    </Center>
  )
}

const LoadingState = () => (
  <Center>
    <Loader />
  </Center>
)

const EmptyState = () => (
  <Center>
    <Text>No email template found</Text>
  </Center>
)

interface EmailTemplateDetailsFormProps {
  result: ReturnType<typeof useGetEmailTemplateQuery>
  onSubmit: (values: EmailTemplateCreate) => void
  onDelete: () => void
}

const EmailTemplateDetailsForm = ({
  result,
  onSubmit,
  onDelete,
}: EmailTemplateDetailsFormProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data: EmailTemplate = result.data
  if (!data) {
    return <EmptyState />
  }

  return (
    <EmailTemplateForm
      topicChoices={Topics}
      initialData={{
        topic: data.topic,
        name: data.name,
        subject: data.subject,
        text: data.text,
      }}
      onSubmit={onSubmit}
      onDelete={onDelete}
    />
  )
}

mount(App)
