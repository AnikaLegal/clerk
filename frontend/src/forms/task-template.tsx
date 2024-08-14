import React, { useState } from 'react'
import { FormikProps, ErrorMessage, FieldArray, useField } from 'formik'
import {
  Accordion,
  Button,
  Dropdown,
  DropdownProps,
  Form,
  Grid,
  Header,
  Icon,
  Input,
  InputProps,
} from 'semantic-ui-react'
import { choiceToOptions, choiceToMap } from 'utils'
import {
  RichTextEditor,
  RichTextEditorProps,
  EditorEvents,
} from 'comps/richtext-editor'
import { TaskTemplate } from 'api'

interface TaskTemplateFormProps {
  create?: boolean
  onDelete?: (e: any) => void
  choices: {
    topic: string[][]
    event: string[][]
    event_stage: string[][]
    tasks_assignment_role: string[][]
    task_type: string[][]
  }
  formik: FormikProps<any>
}

const RichTextField = ({
  name,
  label,
  ...props
}: { name: string; label: string } & RichTextEditorProps) => {
  const [field, meta, helpers] = useField(name)

  const handleBlur = ({ editor, event, transaction }: EditorEvents['blur']) => {
    if (editor) {
      helpers.setValue(editor.getHTML())
      if (props.onBlur) {
        props.onBlur({ editor, event, transaction })
      }
    }
  }

  return (
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <RichTextEditor
        {...props}
        content={field.value || ''}
        onBlur={handleBlur}
      />
      <ErrorMessage name={name} />
    </div>
  )
}

const InputField = ({
  name,
  label,
  ...props
}: { name: string; label: string } & InputProps) => {
  const [field, meta] = useField(name)

  return (
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <Input {...field} {...props} />
      <ErrorMessage name={name} />
    </div>
  )
}

const DropdownField = ({
  name,
  label,
  ...props
}: { name: string; label: string } & DropdownProps) => {
  const [field, meta, helpers] = useField(name)
  const handleChange = (e, data) => {
    helpers.setValue(data.value)
    if (props.onChange) {
      props.onChange(e, data)
    }
  }

  return (
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <Dropdown fluid selection {...field} {...props} onChange={handleChange} />
      <ErrorMessage name={name} />
    </div>
  )
}

const TemplateHeaderText = ({
  index,
  type,
  name,
}: {
  index: number
  type: string | undefined
  name: string | undefined
}) => {
  let header = `${index + 1}.`
  if (type) {
    header += ' ' + type
  }
  if (name) {
    if (type) {
      header += ' -'
    }
    header += ' ' + name
  }
  return <span>{`${header}`}</span>
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
}) => {
  const [activeIndex, setActiveIndex] = useState<number>(-1)
  const [showEventStage, setShowEventStage] = useState<boolean>(
    values.event === 'STAGE'
  )
  const taskTypes = choiceToMap(choices.task_type)

  const handleAccordionClick = (e, titleProps) => {
    const { index } = titleProps
    const newIndex = activeIndex === index ? -1 : index
    setActiveIndex(newIndex)
  }

  // By default, show an empty template input area when creating a template.
  if (values.templates) {
    if (values.templates.length == 0) {
      values.templates.push({} as TaskTemplate)
      setActiveIndex(0)
    }
  }

  return (
    <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
      <InputField
        name="name"
        label="Name"
        placeholder="Describe the task template"
        disabled={isSubmitting}
      />
      <DropdownField
        name="topic"
        label="Case type"
        placeholder="Select a case type"
        options={choiceToOptions(choices.topic)}
        disabled={isSubmitting}
      />
      <DropdownField
        name="event"
        label="Trigger event"
        placeholder="Select which event will trigger task creation"
        options={choiceToOptions(choices.event)}
        onChange={(e, { value }) => {
          setShowEventStage(value === 'STAGE')
        }}
        disabled={isSubmitting}
      />

      {showEventStage && (
        <DropdownField
          name="event_stage"
          label="Trigger stage"
          placeholder="Event is triggered when this stage is reached"
          options={choiceToOptions(choices.event_stage)}
          disabled={isSubmitting}
        />
      )}

      <DropdownField
        name="tasks_assignment_role"
        label="Assignment role"
        placeholder="Select the role of the user to which the task(s) should be assigned"
        options={choiceToOptions(choices.tasks_assignment_role)}
        disabled={isSubmitting}
      />
      <FieldArray name="templates">
        {(arrayHelpers) => (
          <div>
            <Grid style={{ marginBottom: '0.25rem' }}>
              <Grid.Row columns={2} style={{ alignItems: 'center' }}>
                <Grid.Column>
                  <Header as="h2">Tasks</Header>
                </Grid.Column>
                <Grid.Column>
                  <Button
                    floated="right"
                    size="mini"
                    type="button"
                    onClick={() => {
                      /* NOTE: The push function doesn't update synchronously so
                       * to have confidence that the index is for the last item in
                       * the array (i.e. the one we are about to push), we set
                       * the index before the push */
                      setActiveIndex(values.templates?.length || 0)
                      arrayHelpers.push({})
                    }}
                  >
                    Add task
                  </Button>
                </Grid.Column>
              </Grid.Row>
            </Grid>
            {values.templates && values.templates.length > 0 && (
              <Accordion fluid styled>
                {values.templates.map(
                  (template: TaskTemplate, index: number) => (
                    <div key={index}>
                      <Accordion.Title
                        active={activeIndex === index}
                        index={index}
                        onClick={handleAccordionClick}
                      >
                        <Icon
                          name={
                            activeIndex === index
                              ? 'chevron up'
                              : 'chevron down'
                          }
                          style={{ marginTop: '5px', marginRight: '1rem' }}
                        />
                        <TemplateHeaderText
                          index={index}
                          type={taskTypes.get(template.type)}
                          name={template.name}
                        />
                        <div style={{ float: 'right' }}>
                          <Icon
                            name="delete"
                            link
                            style={{ marginTop: '5px' }}
                            onClick={(e) => {
                              e.preventDefault()
                              e.stopPropagation()
                              arrayHelpers.remove(index)
                              setActiveIndex(
                                activeIndex === index ? -1 : activeIndex - 1
                              )
                            }}
                          />
                        </div>
                      </Accordion.Title>
                      <Accordion.Content active={activeIndex === index}>
                        <DropdownField
                          name={`templates.${index}.type`}
                          label="Task type"
                          placeholder="Select the task type"
                          options={choiceToOptions(choices.task_type)}
                          disabled={isSubmitting}
                          value={template.type || ''}
                        />
                        <InputField
                          name={`templates.${index}.name`}
                          label="Task name"
                          disabled={isSubmitting}
                          placeholder="Provide more specific task information"
                          value={template.name || ''}
                        />
                        <InputField
                          type="number"
                          name={`templates.${index}.due_in`}
                          label="Due in"
                          disabled={isSubmitting}
                          placeholder="The number of days from when the task is assigned until it is due"
                          value={template.due_in || ''}
                          onChange={(e, { value }) => {
                            setFieldValue(
                              `templates.${index}.due_in`,
                              value !== '' ? value : null
                            )
                          }}
                        />
                        <DropdownField
                          name={`templates.${index}.is_urgent`}
                          label="Urgent?"
                          placeholder="Is the task urgent?"
                          options={[
                            { key: 'yes', text: 'Yes', value: true },
                            { key: 'no', text: 'No', value: false },
                          ]}
                          disabled={isSubmitting}
                          value={template.is_urgent || false}
                        />
                        <RichTextField
                          name={`templates.${index}.description`}
                          label="Task description"
                          disabled={isSubmitting}
                          placeholder="Describe the task in detail"
                          content={template.description || ''}
                        />
                      </Accordion.Content>
                    </div>
                  )
                )}
              </Accordion>
            )}
          </div>
        )}
      </FieldArray>
      <Button
        primary
        type="submit"
        disabled={isSubmitting}
        loading={isSubmitting}
        style={{ marginTop: '1rem' }}
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
}
