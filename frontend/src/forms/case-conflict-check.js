import React, { useState } from 'react'
import { Formik } from 'formik'
import {
  Header,
  Form,
  Button,
  Message,
  Segment,
  Dropdown,
} from 'semantic-ui-react'

import { TimelineNote } from 'comps/timeline-item'
import { MarkdownExplainer } from 'comps/markdown-editor'
import { TextArea } from 'comps/textarea'
import { submitNote } from './case-file-note'

export const ConflictForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false)
  return (
    <Segment>
      <Header>Log a conflict check</Header>
      <p>
        Leave a note to record that you have performed a conflict check for this
        case.
      </p>
      <Formik
        initialValues={{ text: '', note_type: '' }}
        validate={({ text, note_type }) => {
          const errors = {}
          if (!text) errors.text = 'File note cannot be empty'
          if (!note_type) errors.note_type = 'Outcome is required'
          return errors
        }}
        onSubmit={submitNote(issue, setIssue, setNotes, setSuccess)}
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
            <Dropdown
              fluid
              selection
              loading={isSubmitting}
              placeholder="Select an outcome"
              options={[
                {
                  key: 'CONFLICT_CHECK_SUCCESS',
                  value: 'CONFLICT_CHECK_SUCCESS',
                  text: 'Cleared',
                },
                {
                  key: 'CONFLICT_CHECK_FAILURE',
                  value: 'CONFLICT_CHECK_FAILURE',
                  text: 'Not cleared',
                },
              ]}
              onChange={(e, { value }) =>
                setFieldValue('note_type', value, false)
              }
            />

            <TextArea
              onChange={(e) => setFieldValue('text', e.target.value, false)}
              disabled={isSubmitting}
              placeholder="Write a note describing why the outcome was chosen."
              rows={3}
              value={values.text}
              style={{ margin: '1em 0' }}
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
              Create record
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>Conflict check created</Message>
            <MarkdownExplainer />
            <TimelineNote
              note={{
                note_type: values.note_type || 'CONFLICT_CHECK_SUCCESS',
                created_at: 'Now',
                text_display: values.text || 'start typing...',
                creator: {
                  full_name: 'You',
                },
              }}
            />
          </Form>
        )}
      </Formik>
    </Segment>
  )
}
