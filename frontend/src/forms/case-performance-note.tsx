import React, { useState } from 'react'
import { Formik } from 'formik'
import { Header, Form, Button, Message, Segment } from 'semantic-ui-react'

import { TimelineNote } from 'comps/timeline-item'
import { MarkdownExplainer } from 'comps/markdown-editor'

export const PerformanceForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false)
  const submitNote = (values, { setSubmitting, setErrors }) => null
  return (
    <Segment>
      <Header> Add a paralegal performance review</Header>
      <p>
        Leave a paralegal performance review note for{' '}
        {issue.paralegal.full_name}. This note is not visible to paralegals.
      </p>
      <Formik
        initialValues={{ text: '', note_type: 'PERFORMANCE' }}
        validate={({ text }) =>
          text ? null : { 'File note text': 'File note cannot be empty' }
        }
        onSubmit={submitNote}
      >
        {({
          values,
          errors,
          handleChange,
          handleSubmit,
          isSubmitting,
          setFieldValue,
        }) => (
          <Form
            onSubmit={handleSubmit}
            success={isSuccess}
            error={Object.keys(errors).length > 0}
          >
            <textarea
              onChange={(e) => setFieldValue('text', e.target.value)}
              disabled={isSubmitting}
              rows={3}
              value={values.text}
              placeholder="Write your review here (this is not a filenote, paralegals cannot see this)"
              style={{ marginBottom: '1em' }}
            />
            {Object.entries(errors).map(([k, v]) => (
              <Message error key={k}>
                <div className="header">{k}</div>
                <p>{v}</p>
              </Message>
            ))}
            <Button
              loading={isSubmitting}
              disabled={isSubmitting}
              positive
              type="submit"
            >
              Create note
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>Performance note created</Message>
            <MarkdownExplainer />
            <TimelineNote
              note={{
                note_type: values.note_type,
                created_at: 'Now',
                text_display: values.text || 'start typing...',
                creator: {
                  full_name: 'You',
                },
                reviewee: issue.paralegal,
              }}
            />
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
