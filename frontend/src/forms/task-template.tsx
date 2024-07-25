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
  Input,
  InputProps,
} from 'semantic-ui-react'
import { choiceToOptions, choiceToMap } from 'utils'
import { Editor } from '@tiptap/react'
import { RichTextEditor, RichTextEditorProps } from 'comps/richtext-editor'

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

  const handleUpdate = ({ editor }: { editor: Editor }) => {
    helpers.setValue(editor.getHTML())
    if (props.onUpdate) {
      props.onUpdate(editor)
    }
  }

  return (
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <RichTextEditor {...props} onUpdate={handleUpdate} />
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
      <Dropdown fluid selection {...props} onChange={handleChange} />
      <ErrorMessage name={name} />
    </div>
  )
}

const TemplateHeader = ({
  index,
  type,
  name,
  typeMap,
}: {
  index: number
  type: string | undefined
  name: string | undefined
  typeMap: Map<string, string>
}) => {
  let header = `${index + 1}.`
  if (type) {
    header += ' ' + typeMap.get(type)
  }
  if (name) {
    if (type) {
      header += ' -'
    }
    header += ' ' + name
  }
  return <p>{`${header}`}</p>
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
        {({ insert, remove, push }) => (
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
                      push({})
                      setActiveIndex(values.templates.length)
                    }}
                  >
                    Add task
                  </Button>
                </Grid.Column>
              </Grid.Row>
            </Grid>
            {values.templates.length > 0 && (
              <Accordion fluid styled>
                {values.templates.map((template, index) => (
                  <div key={index}>
                    <Accordion.Title
                      active={activeIndex === index}
                      index={index}
                      onClick={handleAccordionClick}
                    >
                      <TemplateHeader
                        index={index}
                        type={template.type}
                        name={template.name}
                        typeMap={taskTypes}
                      />
                    </Accordion.Title>
                    <Accordion.Content active={activeIndex === index}>
                      <DropdownField
                        name={`templates.${index}.type`}
                        label="Task type"
                        placeholder="Select the task type"
                        options={choiceToOptions(choices.task_type)}
                        disabled={isSubmitting}
                      />
                      <InputField
                        name={`templates.${index}.name`}
                        label="Task name"
                        disabled={isSubmitting}
                      />
                      <RichTextField
                        name={`templates.${index}.description`}
                        label="Task description"
                        disabled={isSubmitting}
                      />
                    </Accordion.Content>
                  </div>
                ))}
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
