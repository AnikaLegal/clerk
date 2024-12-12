import { useClickOutside, useDebouncedCallback } from '@mantine/hooks'
import { TaskTemplate } from 'api'
import {
  EditorEvents,
  RichTextEditor,
  RichTextEditorProps,
} from 'comps/rich-text'
import {
  ErrorMessage,
  FieldArray,
  FieldArrayRenderProps,
  Formik,
  FormikHelpers,
  FormikProps,
  useField,
} from 'formik'
import React, { useState } from 'react'
import {
  Button,
  ButtonProps,
  Dropdown,
  DropdownProps,
  Form,
  Grid,
  Header,
  Icon,
  IconProps,
  Input,
  InputProps,
  Modal,
  Segment,
  Table,
} from 'semantic-ui-react'
import { choiceToMap, choiceToOptions } from 'utils'

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
  const [, meta, helpers] = useField(name)

  const handleUpdate = ({ editor, transaction }: EditorEvents['update']) => {
    if (editor) {
      helpers.setValue(editor.getHTML())
      if (props.onUpdate) {
        props.onUpdate({ editor, transaction })
      }
    }
  }

  return (
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <RichTextEditor
        {...props}
        initialContent={meta.initialValue}
        onUpdate={handleUpdate}
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

export const TaskTemplateForm: React.FC<TaskTemplateFormProps> = ({
  create,
  onDelete,
  choices,
  formik: { values, errors, handleSubmit, isSubmitting },
}) => {
  const [showEventStage, setShowEventStage] = useState<boolean>(
    values.event === 'STAGE'
  )
  const [showAddTask, setShowAddTask] = useState(false)

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
          placeholder="Select which event stage will trigger task creation"
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
        {(arrayHelpers) => {
          return (
            <>
              <Grid>
                <Grid.Row columns={2} style={{ alignItems: 'center' }}>
                  <Grid.Column>
                    <Header as="h3">Tasks</Header>
                  </Grid.Column>
                  <Grid.Column>
                    {!showAddTask && (
                      <AddTaskTemplateButton
                        floated="right"
                        size="mini"
                        type="button"
                        arrayHelpers={arrayHelpers}
                        choices={choices}
                      >
                        Add task
                      </AddTaskTemplateButton>
                    )}
                  </Grid.Column>
                </Grid.Row>
              </Grid>
              <TaskTemplateTable
                arrayHelpers={arrayHelpers}
                templates={values.templates}
                choices={choices}
              />
            </>
          )
        }}
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

interface TaskTemplateTableProps {
  arrayHelpers: FieldArrayRenderProps
  templates: TaskTemplate[]
  choices: any
}

export const TaskTemplateTable = ({
  arrayHelpers,
  templates,
  choices,
}: TaskTemplateTableProps) => {
  const typeLabels = choiceToMap(choices.task_type)

  if (templates.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No tasks found.</p>
      </Segment>
    )
  }
  return (
    <Table celled>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Name</Table.HeaderCell>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Due In</Table.HeaderCell>
          <Table.HeaderCell>Urgent?</Table.HeaderCell>
          <Table.HeaderCell></Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {templates.map((template, index) => (
          <Table.Row key={template.id}>
            <Table.Cell>{template.name}</Table.Cell>
            <Table.Cell>{typeLabels.get(template.type)}</Table.Cell>
            <Table.Cell>{template.due_in}</Table.Cell>
            <Table.Cell>{template.is_urgent ? 'Yes' : 'No'}</Table.Cell>
            <Table.Cell collapsing textAlign="center">
              <TaskTemplateActionIcons
                templates={templates}
                index={index}
                arrayHelpers={arrayHelpers}
                choices={choices}
              />
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  )
}

export interface TaskTemplateActionIconProps {
  templates: TaskTemplate[]
  index: number
  arrayHelpers: FieldArrayRenderProps
  choices: any
}

export const TaskTemplateActionIcons = ({
  templates,
  index,
  arrayHelpers,
  choices,
}: TaskTemplateActionIconProps) => {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false)

  /* Handle a situation where a click event does not trigger due to element
   * resizing when attempting to click an action icon on another row of the same
   * table when a confirm delete button is already showing. This delays the
   * element resize which allows the click event to trigger. This feels nasty and
   * probably is and I presume it might not always work but gets the job done
   * most of the time */
  const delayedHideConfirmDelete = useDebouncedCallback(() => {
    setShowConfirmDelete(false)
  }, 100)
  const ref = useClickOutside(() => delayedHideConfirmDelete())

  if (showConfirmDelete) {
    return (
      <div ref={ref}>
        <Button
          negative
          compact
          size="mini"
          onClick={(event) => {
            event.preventDefault()
            arrayHelpers.remove(index)
            setShowConfirmDelete(false)
          }}
        >
          Confirm delete
        </Button>
      </div>
    )
  }
  return (
    <>
      <EditTaskTemplateIcon
        link
        name="pencil"
        templates={templates}
        index={index}
        choices={choices}
        arrayHelpers={arrayHelpers}
      />
      <Icon
        link
        name="trash alternate outline"
        onClick={() => setShowConfirmDelete(true)}
      />
      {templates.length > 1 && (
        <>
          <Icon
            link
            name="arrow up"
            onClick={() => arrayHelpers.move(index, index - 1)}
            disabled={index == 0}
          />
          <Icon
            link
            name="arrow down"
            onClick={() => arrayHelpers.move(index, index + 1)}
            disabled={index == templates.length - 1}
          />
        </>
      )}
    </>
  )
}

export interface EditTaskTemplateIconProps {
  templates: TaskTemplate[]
  index: number
  choices: any
  arrayHelpers: FieldArrayRenderProps
}

export const EditTaskTemplateIcon = ({
  templates,
  index,
  choices,
  arrayHelpers,
  ...props
}: EditTaskTemplateIconProps & IconProps) => {
  const [open, setOpen] = useState(false)

  const handleSubmit = (
    template: TaskTemplate,
    { resetForm }: FormikHelpers<TaskTemplate>
  ) => {
    arrayHelpers.replace(index, template)
    resetForm()
    setOpen(false)
  }

  return (
    <>
      <TaskTemplateModal
        initialValues={templates[index]}
        choices={choices}
        open={open}
        setOpen={setOpen}
        handleSubmit={handleSubmit}
        label="Update task"
      />
      <Icon {...props} onClick={() => setOpen(true)} />
    </>
  )
}

export interface AddTaskTemplateButtonProps {
  choices: any
  arrayHelpers: FieldArrayRenderProps
  children: string | number
}

export const AddTaskTemplateButton = ({
  choices,
  arrayHelpers,
  children,
  ...props
}: AddTaskTemplateButtonProps & ButtonProps) => {
  const [open, setOpen] = useState(false)

  const handleSubmit = (
    template: TaskTemplate,
    { resetForm }: FormikHelpers<TaskTemplate>
  ) => {
    arrayHelpers.push(template)
    resetForm()
    setOpen(false)
  }

  return (
    <>
      <TaskTemplateModal
        initialValues={{
          type: '',
          name: '',
          due_in: null,
          is_urgent: false,
          description: '',
        }}
        choices={choices}
        open={open}
        setOpen={setOpen}
        handleSubmit={handleSubmit}
        label={children}
      />
      <Button {...props} onClick={() => setOpen(true)}>
        {children}
      </Button>
    </>
  )
}

export interface TaskTemplateModalProps {
  open: boolean
  setOpen: React.Dispatch<React.SetStateAction<boolean>>
  initialValues: TaskTemplate
  handleSubmit: (
    values: TaskTemplate,
    helpers: FormikHelpers<TaskTemplate>
  ) => void
  label: string | number
  choices: any
}

export const TaskTemplateModal = ({
  open,
  setOpen,
  initialValues,
  handleSubmit,
  label,
  choices,
}: TaskTemplateModalProps) => {
  return (
    <Formik
      enableReinitialize
      initialValues={initialValues}
      onSubmit={handleSubmit}
    >
      {({ handleSubmit, errors, resetForm }) => {
        const closeHandler = () => {
          resetForm()
          setOpen(false)
        }
        return (
          <Modal size="large" open={open} onClose={closeHandler}>
            <Modal.Header>{label}</Modal.Header>
            <Modal.Content>
              <Form
                onSubmit={handleSubmit}
                error={Object.keys(errors).length > 0}
              >
                <DropdownField
                  name="type"
                  label="Task type"
                  placeholder="Select the task type"
                  options={choiceToOptions(choices.task_type)}
                />
                <InputField
                  name="name"
                  label="Task name"
                  placeholder="Provide more specific task information"
                />
                <InputField
                  name="due_in"
                  type="number"
                  label="Due in"
                  placeholder="The number of days from when the task is assigned until it is due"
                />
                <DropdownField
                  name="is_urgent"
                  label="Urgent?"
                  placeholder="Is the task urgent?"
                  options={[
                    { key: 'yes', text: 'Yes', value: true },
                    { key: 'no', text: 'No', value: false },
                  ]}
                />
                <RichTextField
                  name="description"
                  label="Task description"
                  placeholder="Describe the task in detail"
                />
              </Form>
            </Modal.Content>
            <Modal.Actions>
              <Button primary type="submit" onClick={() => handleSubmit()}>
                {label}
              </Button>
              <Button onClick={closeHandler}>Close</Button>
            </Modal.Actions>
          </Modal>
        )
      }}
    </Formik>
  )
}
