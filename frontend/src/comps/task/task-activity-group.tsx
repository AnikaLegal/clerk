import { TaskActivity, TaskComment, TaskEvent } from 'api'
import { RichTextDisplay } from 'comps/rich-text'
import moment from 'moment'
import React, { useMemo } from 'react'
import {
  Comment,
  Label,
  Loader,
  Segment,
  SemanticCOLORS,
} from 'semantic-ui-react'
import styled from 'styled-components'
import { TaskDetailChoices } from 'types/task'
import { choiceToMap } from 'utils'

const StyledCommentGroup = styled(Comment.Group)`
  && {
    max-width: 100%;
  }
`

export interface TaskActivityGroupProps {
  activities: TaskActivity[]
  choices: TaskDetailChoices
  loading: boolean
}

export const TaskActivityGroup = ({
  activities,
  choices,
  loading,
}: TaskActivityGroupProps) => {
  return (
    <StyledCommentGroup>
      <Loader inverted inline active={loading} />
      {activities.map((activity) => {
        if (activity.type == 'comment') {
          return (
            <TaskCommentSegment
              key={activity.id}
              comment={activity.data as TaskComment}
            />
          )
        } else if (activity.type == 'event') {
          return (
            <TaskEventSegment
              key={activity.id}
              event={activity.data as TaskEvent}
              choices={choices}
            />
          )
        }
      })}
    </StyledCommentGroup>
  )
}

export interface TaskCommentSegmentProps {
  comment: TaskComment
}

export const TaskCommentSegment = ({ comment }: TaskCommentSegmentProps) => {
  const color: SemanticCOLORS = 'blue'
  return (
    <Segment>
      <Label attached="top" color={color}>
        <a href={comment.creator.url} style={{ opacity: 'inherit' }}>
          {comment.creator.full_name}
        </a>
        <Label.Detail>
          {moment(comment.created_at).format('DD/MM/YY [at] h:mmA')}
        </Label.Detail>
      </Label>
      <Label attached="top right" color={color}>
        Comment
      </Label>
      <RichTextDisplay content={comment.text} />
    </Segment>
  )
}

export interface TaskEventSegmentProps {
  event: TaskEvent
  choices: TaskDetailChoices
}

export const TaskEventSegment = ({ event, choices }: TaskEventSegmentProps) => {
  const eventTypeLabels = useMemo(() => choiceToMap(choices.event_type), [choices.event_type])
  const typeLabel = eventTypeLabels.get(event.type)
  return (
    <Segment>
      <Label attached="top">
        {typeLabel}
        <Label.Detail>
          {moment(event.created_at).format('DD/MM/YY [at] h:mmA')}
        </Label.Detail>
      </Label>
      <Label attached="top right">Event</Label>
      <RichTextDisplay content={event.desc_html} />
      {event.note_html && (
        <RichTextDisplay
          style={{ marginTop: '0.5rem' }}
          content={`<blockquote>${event.note_html}</blockquote>`}
        />
      )}
    </Segment>
  )
}
