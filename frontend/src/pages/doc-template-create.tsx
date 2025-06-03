import {
  Button,
  Container,
  FileInput,
  Select,
  Text,
  Title,
} from '@mantine/core'
import { isNotEmpty, useForm } from '@mantine/form'
import { IconPaperclip } from '@tabler/icons-react'
import { useCreateDocumentTemplateMutation } from 'api'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { getAPIErrorMessage, mount } from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: [string, string][]
  }
  list_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const Topics = CONTEXT.choices.topic
const ListUrl = CONTEXT.list_url

interface FormValues {
  topic: string
  files: File[]
}

const App = () => {
  const [createDocumentTemplate] = useCreateDocumentTemplateMutation()

  const form = useForm<FormValues>({
    mode: 'uncontrolled',
    initialValues: { topic: '', files: [] },
    validate: {
      topic: isNotEmpty('required'),
      files: isNotEmpty('required'),
    },
  })

  const handleSubmit = (values: FormValues) => {
    const payload = new FormData()
    payload.append('topic', values.topic)
    values.files.forEach((file) => {
      payload.append('files', file)
    })
    form.setSubmitting(true)
    createDocumentTemplate({ documentTemplateCreate: payload as any })
      .unwrap()
      .then(() => {
        window.location.href = ListUrl
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to create a new document template'),
          {
            variant: 'error',
          }
        )
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  return (
    <Container size="xl">
      <Title order={1}>Create a new document template</Title>
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Select
          {...form.getInputProps('topic')}
          key={form.key('topic')}
          label={
            <Text fw={700} mb="0.25rem">
              Topic
            </Text>
          }
          clearable
          searchable
          size="md"
          placeholder="Select a case type"
          data={Topics.map((x) => ({
            value: x[0],
            label: x[1],
          }))}
          withCheckIcon={false}
          onChange={(value) =>
            form.setFieldValue('topic', (value as string) || '')
          }
        />
        <FileInput
          {...form.getInputProps('files')}
          key={form.key('files')}
          label={
            <Text fw={700} mb="0.25rem">
              <b>Files</b>
            </Text>
          }
          multiple
          clearable
          placeholder="Select to add files"
          size="md"
          mt="md"
          rightSection={
            form.getValues().files.length == 0 ? (
              <IconPaperclip size={16} stroke={1.5} />
            ) : null
          }
        />
        <Button
          type="submit"
          mt="md"
          disabled={form.submitting || !form.isValid()}
          loading={form.submitting}
        >
          Create document template
        </Button>
      </form>
    </Container>
  )
}
mount(App)
