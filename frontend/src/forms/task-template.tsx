import React from 'react'
import { FormikProps, ErrorMessage } from 'formik'
import { Button, Input, Dropdown, Form } from 'semantic-ui-react'
import { choiceToOptions } from 'utils'

interface TaskTemplateFormProps {
  create?: boolean
  onDelete?: (e: any) => void
  choices: {
    topic: string[][]
    event: string[][]
    event_stage: string[][]
    tasks_assignment_role: string[][]
  }
  formik: FormikProps<any>
}

export const TaskTemplateForm: React.FC<TaskTemplateFormProps> = ({
  create,
  onDelete,
  choices,
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
        placeholder="Describe the template"
        value={values.name}
        name="name"
        onChange={handleChange}
        disabled={isSubmitting}
      />
      <ErrorMessage name="name" />
    </div>
    <div className={`field ${errors.topic && 'error'}`}>
      <label>Case Type</label>
      <Dropdown
        fluid
        selection
        placeholder="Select a case type"
        options={choiceToOptions(choices.topic)}
        onChange={(e, { value }) => setFieldValue('topic', value)}
        value={values.topic}
        disabled={isSubmitting}
      />
      <ErrorMessage name="topic" />
    </div>
    <div className={`field ${errors.event && 'error'}`}>
      <label>Trigger event</label>
      <Dropdown
        fluid
        selection
        placeholder="Select which event will trigger task creation"
        options={choiceToOptions(choices.event)}
        onChange={(e, { value }) => setFieldValue('event', value)}
        value={values.event}
        disabled={isSubmitting}
      />
      <ErrorMessage name="event" />
    </div>
    {values.event == 'STAGE_CHANGE' && (
      <div className={`field ${errors.event_stage && 'error'}`}>
        <label>Trigger stage</label>
        <Dropdown
          fluid
          selection
          placeholder="Event is triggered when this stage is reached"
          options={choiceToOptions(choices.event_stage)}
          onChange={(e, { value }) => setFieldValue('event_stage', value)}
          value={values.event_stage}
          disabled={isSubmitting}
        />
        <ErrorMessage name="event_stage" />
      </div>
    )}
    <div className={`field ${errors.tasks_assignment_role && 'error'}`}>
      <label>Assignment Role</label>
      <Dropdown
        fluid
        selection
        placeholder="Select the role of the user to which the task(s) should be assigned"
        options={choiceToOptions(choices.tasks_assignment_role)}
        onChange={(e, { value }) =>
          setFieldValue('tasks_assignment_role', value)
        }
        value={values.tasks_assignment_role}
        disabled={isSubmitting}
      />
      <ErrorMessage name="tasks_assignment_role" />
    </div>
    <Button
      primary
      type="submit"
      disabled={isSubmitting}
      loading={isSubmitting}
    >
      {create ? 'Create task template' : 'Update task template'}
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
