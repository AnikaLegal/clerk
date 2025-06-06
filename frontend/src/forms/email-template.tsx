import {
  Button,
  Grid,
  Group,
  Paper,
  Select,
  Textarea,
  TextInput,
  Text,
} from '@mantine/core'
import { useForm } from '@mantine/form'
import { modals } from '@mantine/modals'
import { EmailTemplateCreate } from 'api'
import MarkdownInfoIconWithPopover from 'comps/markdown-info-icon'
import { RichTextDisplay } from 'comps/rich-text'
import React, { ChangeEvent, MouseEvent } from 'react'
import { markdownToHtml } from 'utils'

interface EmailTemplateFormProps {
  topicChoices: [string, string][]
  onSubmit: (values: EmailTemplateCreate) => void
  initialData?: EmailTemplateCreate
  onDelete?: () => void
}

export const EmailTemplateForm = ({
  topicChoices,
  onSubmit,
  initialData,
  onDelete,
}: EmailTemplateFormProps) => {
  const [html, setHtml] = React.useState<string>(
    markdownToHtml(initialData?.text || '')
  )

  const isUpdate = !!initialData

  const form = useForm({
    mode: 'uncontrolled',
    initialValues: initialData,
  })

  const handleTextChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setHtml(markdownToHtml(event.target.value))

    const props = form.getInputProps('text')
    if (props.onChange) {
      props.onChange(event)
    }
  }

  const handleDelete = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    if (onDelete) {
      modals.openConfirmModal({
        title: <Text fw={700}>Delete Email Template</Text>,
        children: <Text>Are you sure you want to delete this template?</Text>,
        centered: true,
        labels: { confirm: 'Delete email template', cancel: 'Cancel' },
        confirmProps: { color: 'red' },
        onConfirm: () => onDelete(),
      })
    }
  }

  return (
    <form onSubmit={form.onSubmit(onSubmit)}>
      <Select
        {...form.getInputProps('topic')}
        key={form.key('topic')}
        label={
          <Text fw={700} mb="0.25rem">
            Case topic
          </Text>
        }
        size="md"
        mt="md"
        data={topicChoices.map(([value, label]) => ({
          value,
          label,
        }))}
        withCheckIcon={false}
      />
      <TextInput
        {...form.getInputProps('name')}
        key={form.key('name')}
        label={
          <Text fw={700} mb="0.25rem">
            Template name
          </Text>
        }
        size="md"
        mt="md"
      />
      <TextInput
        {...form.getInputProps('subject')}
        key={form.key('subject')}
        label={
          <Text fw={700} mb="0.25rem">
            Email subject
          </Text>
        }
        size="md"
        mt="md"
      />
      <Grid mt="md">
        <Grid.Col span={6} pb={0}>
          <Group justify="space-between">
            <Text fw={700}>Email body</Text>
            <MarkdownInfoIconWithPopover width={300} shadow="md" />
          </Group>
        </Grid.Col>
        <Grid.Col span={6} pb={0}>
          <Text fw={700}>Preview</Text>
        </Grid.Col>
        <Grid.Col span={6} pt="0.25rem">
          <Textarea
            {...form.getInputProps('text')}
            key={form.key('text')}
            size="md"
            minRows={5}
            autosize
            onChange={handleTextChange}
            placeholder="Dear Ms Example..."
            autoComplete="off"
          />
        </Grid.Col>
        <Grid.Col span={6} pt="0.25rem">
          <Paper
            withBorder
            p="xs"
            mih="100%"
            style={{ borderColor: 'var(--mantine-color-default-border)' }}
          >
            <RichTextDisplay content={html} />
          </Paper>
        </Grid.Col>
      </Grid>
      <Group gap="sm">
        <Button
          type="submit"
          mt="md"
          disabled={form.submitting || !form.isValid()}
          loading={form.submitting}
        >
          {isUpdate ? 'Update email template' : 'Create email template'}
        </Button>
        {onDelete && (
          <Button
            mt="md"
            disabled={form.submitting}
            loading={form.submitting}
            onClick={handleDelete}
            color="red"
          >
            Delete
          </Button>
        )}
      </Group>
    </form>
  )
}

export default EmailTemplateForm
