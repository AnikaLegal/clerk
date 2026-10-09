import React from 'react'
import { Button, Group, Paper, Text, Textarea, Title } from '@mantine/core'
import { DateInput } from '@mantine/dates'
import { useForm } from '@mantine/form'
import dayjs from 'dayjs'
import { yupResolver } from 'mantine-form-yup-resolver'
import moment from 'moment'
import { enqueueSnackbar } from 'notistack'
import * as Yup from 'yup'

import { TimelineNote } from 'comps/timeline-item'
import { MarkdownExplainer } from 'comps/markdown-editor'
import { useCreateCaseNoteMutation } from 'api'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { CaseDetailFormProps } from 'types'

const ReviewNoteSchema = Yup.object().shape({
  text: Yup.string().required('File note cannot be empty'),
  event: Yup.string().required('Next review date is required'),
})

type ReviewNoteValues = { text: string; event: string }

export const ReviewForm: React.FC<CaseDetailFormProps> = ({
  issue,
  onCancel,
}) => {
  const [createCaseNote] = useCreateCaseNoteMutation()
  const form = useForm<ReviewNoteValues>({
    initialValues: { text: '', event: '' },
    validate: yupResolver(ReviewNoteSchema),
  })

  const handleSubmit = (values: ReviewNoteValues) => {
    form.setSubmitting(true)
    createCaseNote({
      id: issue.id,
      issueNoteCreate: {
        note_type: 'REVIEW',
        text: values.text,
        event: moment.utc(values.event, 'YYYY-MM-DD').format(),
      },
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('File note created', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(err, 'Failed to create a file note'),
          { variant: 'error' }
        )
        const requestErrors = getAPIFormErrors(err)
        if (requestErrors) {
          form.setErrors(requestErrors)
        }
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  return (
    <Paper withBorder p="md">
      <Title order={3}>Add a coordinator case review note</Title>
      <Text mt="md">
        Leave a case review note for other coordinators to read. This note is
        not visible to paralegals.
      </Text>
      <form autoComplete="off" onSubmit={form.onSubmit(handleSubmit)}>
        <Textarea
          {...form.getInputProps('text')}
          autoComplete="off"
          autosize
          minRows={3}
          size="md"
          mt="md"
          label="Review"
          placeholder="Write your review here (this is not a filenote, paralegals cannot see this)"
          disabled={form.submitting}
        />
        <DateInput
          {...form.getInputProps('event')}
          autoComplete="off"
          clearable
          highlightToday
          locale="en-au"
          label="Next review date"
          size="md"
          mt="md"
          placeholder="Select or enter a date"
          valueFormat="DD/MM/YYYY"
          dateParser={(value) =>
            dayjs(value, 'DD/MM/YYYY').format('YYYY-MM-DD')
          }
          minDate={dayjs().format('YYYY-MM-DD')}
          disabled={form.submitting}
        />
        <Group mt="lg">
          <Button
            type="submit"
            disabled={form.submitting}
            loading={form.submitting}
            color="green"
            size="md"
          >
            Create note
          </Button>
          <Button
            variant="default"
            onClick={onCancel}
            disabled={form.submitting}
            size="md"
          >
            Close
          </Button>
        </Group>
        <MarkdownExplainer />
        <TimelineNote
          note={{
            note_type: 'REVIEW',
            created_at: 'Now',
            event: form.values.event
              ? moment(form.values.event, 'YYYY-MM-DD').format()
              : undefined,
            text_display: form.values.text || 'start typing...',
            creator: {
              full_name: 'You',
            },
          }}
        />
      </form>
    </Paper>
  )
}
