import { Container, Title } from '@mantine/core'
import { EmailTemplateCreate, useCreateEmailTemplateMutation } from 'api'
import { EmailTemplateForm } from 'forms'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { getAPIErrorMessage, mount } from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: [string, string][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const Topics = CONTEXT.choices.topic.sort((a, b) => a[1].localeCompare(b[1]))

const App = () => {
  const [createEmailTemplate] = useCreateEmailTemplateMutation()

  const handleSubmit = (values: EmailTemplateCreate) => {
    createEmailTemplate({
      emailTemplateCreate: values,
    })
      .unwrap()
      .then((template) => {
        window.location.href = template.url
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to create email template'),
          {
            variant: 'error',
          }
        )
      })
  }

  return (
    <Container size="xl">
      <Title order={1}>Email Template</Title>
      <EmailTemplateForm topicChoices={Topics} onSubmit={handleSubmit} />
    </Container>
  )
}

mount(App)
