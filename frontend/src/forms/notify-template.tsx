import React from 'react'
import { FormikProps } from 'formik'
import { Button, Input, Dropdown, Form } from 'semantic-ui-react'

import { STAGES } from 'consts'
import { SlackyMarkdownEditor } from 'comps/markdown-editor'

const STAGE_OPTIONS = Object.entries(STAGES)
  .filter(([k, v]) => k !== 'UNSTARTED')
  .map(([k, v]) => ({
    key: k,
    value: k,
    text: v,
  }))

const EVENT_OPTIONS = [
  { key: 'STAGE_CHANGE', value: 'STAGE_CHANGE', text: 'Stage changed' },
]

const CHANNEL_OPTIONS = [
  { key: 'SLACK', value: 'SLACK', text: 'Send a Slack message' },
]

const TARGET_OPTIONS = [
  { key: 'PARALEGAL', value: 'PARALEGAL', text: 'Assigned paralegal' },
  { key: 'LAWYER', value: 'LAWYER', text: 'Assigned lawyer' },
]

interface NotifyTemplateFormProps {
  create?: boolean
  onDelete?: (e: any) => void
  topicOptions: any[]
  formik: FormikProps<any>
}

export const NotifyTemplateForm: React.FC<NotifyTemplateFormProps> = ({
  create,
  onDelete,
  topicOptions,
  formik: {
    values,
    errors,
    handleChange,
    handleSubmit,
    isSubmitting,
    setFieldValue,
  },
}) => (
  <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
    <div className={`field ${errors.name && 'error'}`}>
      <label>Name</label>
      <Input
        placeholder="Describe this notification"
        value={values.name}
        name="name"
        onChange={handleChange}
        disabled={isSubmitting}
      />
    </div>
    <div className={`field ${errors.topic && 'error'}`}>
      <label>Case Type</label>
      <Dropdown
        fluid
        selection
        placeholder="Select a case type"
        options={topicOptions}
        onChange={(e, { value }) => setFieldValue('topic', value)}
        value={values.topic}
        disabled={isSubmitting}
      />
    </div>
    <div className={`field ${errors.event && 'error'}`}>
      <label>Trigger event</label>
      <Dropdown
        fluid
        selection
        placeholder="Select which event will trigger this notification"
        options={EVENT_OPTIONS}
        onChange={(e, { value }) => setFieldValue('event', value)}
        value={values.event}
        disabled={isSubmitting}
      />
    </div>
    {values.event == 'STAGE_CHANGE' && (
      <div className={`field ${errors.event_stage && 'error'}`}>
        <label>Trigger stage</label>
        <Dropdown
          fluid
          selection
          placeholder="Event is triggered when this stage is reached"
          options={STAGE_OPTIONS}
          onChange={(e, { value }) => setFieldValue('event_stage', value)}
          value={values.event_stage}
          disabled={isSubmitting}
        />
      </div>
    )}
    <div className={`field ${errors.channel && 'error'}`}>
      <label>Message channel</label>
      <Dropdown
        fluid
        selection
        placeholder="Select the channel to send the notification through"
        options={CHANNEL_OPTIONS}
        onChange={(e, { value }) => setFieldValue('channel', value)}
        value={values.channel}
        disabled={isSubmitting}
      />
    </div>
    <div className={`field ${errors.target && 'error'}`}>
      <label>Message target</label>
      <Dropdown
        fluid
        selection
        placeholder="Select who will receive the message"
        options={TARGET_OPTIONS}
        onChange={(e, { value }) => setFieldValue('target', value)}
        value={values.target}
        disabled={isSubmitting}
      />
    </div>
    <div className={`field ${errors.target && 'error'}`}>
      <label>Message text</label>
      <SlackyMarkdownEditor
        text={values.raw_text}
        disabled={isSubmitting}
        placeholder="The message text."
        onChangeText={(text) => setFieldValue('raw_text', text)}
        onChangeSlackyMarkdown={(markdown) =>
          setFieldValue('message_text', markdown)
        }
      />
    </div>
    {Object.entries(errors).map(([k, v]) => (
      <div key={k} className="ui error message">
        <div className="header">{k}</div>
        <p>{v}</p>
      </div>
    ))}
    <Button
      primary
      type="submit"
      disabled={isSubmitting}
      loading={isSubmitting}
    >
      {create ? 'Create notification template' : 'Update notification template'}
    </Button>
    {!create && onDelete && (
      <Button
        color="red"
        disabled={isSubmitting}
        loading={isSubmitting}
        onClick={onDelete}
      >
        Delete
      </Button>
    )}
  </Form>
)
