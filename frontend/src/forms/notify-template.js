import React from 'react'
import { Button, Input, Dropdown, Form } from 'semantic-ui-react'

import { TextArea } from 'comps/textarea'
import { STAGES } from 'consts'

const TOPIC_OPTIONS = [
  { key: 'GENERAL', value: 'GENERAL', text: 'General' },
  { key: 'REPAIRS', value: 'REPAIRS', text: 'Repairs' },
  { key: 'BONDS', value: 'BONDS', text: 'Bonds' },
  { key: 'EVICTION', value: 'EVICTION', text: 'Eviction' },
]

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

export const NotifyTemplateForm = ({
  create,
  editable,
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
        disabled={!editable}
      />
    </div>
    <div className={`field ${errors.topic && 'error'}`}>
      <label>Case Type</label>
      <Dropdown
        fluid
        selection
        placeholder="Select a case type"
        options={TOPIC_OPTIONS}
        onChange={(e, { value }) => setFieldValue('topic', value)}
        value={values.topic}
        disabled={!editable}
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
        disabled={!editable}
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
          disabled={!editable}
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
        disabled={!editable}
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
        disabled={!editable}
      />
    </div>
    <div className={`field ${errors.target && 'error'}`}>
      <label>Message text</label>

      <TextArea
        onChange={(e) => setFieldValue('text', e.target.value, false)}
        disabled={isSubmitting}
        placeholder="The message text."
        rows={5}
        value={values.text}
      />
    </div>

    {Object.entries(errors).map(([k, v]) => (
      <div key={k} className="ui error message">
        <div className="header">{k}</div>
        <p>{v}</p>
      </div>
    ))}
    {editable ? (
      <Button
        primary
        type="submit"
        disabled={isSubmitting}
        loading={isSubmitting}
      >
        {create
          ? 'Create notification template'
          : 'Update notification template'}
      </Button>
    ) : null}
  </Form>
)
