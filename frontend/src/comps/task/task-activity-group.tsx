import React from 'react'
import { TaskActivity, TaskComment, TaskEvent } from 'api'
import { Segment, Comment, Loader, Label } from 'semantic-ui-react'
import moment from 'moment'
import styled from 'styled-components'
import { RichTextDisplay } from 'comps/rich-text'

const StyledCommentGroup = styled(Comment.Group)`
  && {
    max-width: 100%;
  }
`

export interface TaskActivityGroupProps {
  activities: TaskActivity[]
  loading: boolean
}

export const TaskActivityGroup = ({
  activities,
  loading,
}: TaskActivityGroupProps) => {
  return (
    <StyledCommentGroup>
      <Loader inverted inline active={loading} />
      {activities.map((activity) => {
        if (activity.type == 'comment') {
          return (
            <TaskCommentSegment
              activity={activity}
              comment={activity.data as TaskComment}
            />
          )
        } else if (activity.type == 'event') {
          return (
            <TaskEventSegment
              activity={activity}
              event={activity.data as TaskEvent}
            />
          )
        }
      })}
    </StyledCommentGroup>
  )
}

export interface TaskCommentSegmentProps {
  activity: TaskActivity
  comment: TaskComment
}

export const TaskCommentSegment = ({
  activity,
  comment,
}: TaskCommentSegmentProps) => {
  return (
    <Segment key={activity.id}>
      <Label attached="top">
        <a href={comment.creator.url} style={{ opacity: 'inherit' }}>
          {comment.creator.full_name}
        </a>
        <Label.Detail>
          {moment(comment.created_at).format('DD/MM/YY [at] h:mmA')}
        </Label.Detail>
      </Label>
      <RichTextDisplay content={comment.text} />
    </Segment>
  )
}

export interface TaskEventSegmentProps {
  activity: TaskActivity
  event: TaskEvent
}

export const TaskEventSegment = ({
  activity,
  event,
}: TaskEventSegmentProps) => {
  return (
    <Segment key={activity.id}>
      <span>
        <RichTextDisplay
          style={{ display: 'inline-block' }}
          content={event.desc_html}
        />
        <span style={{ padding: '0rem 0.5rem' }}>·</span>
        <span style={{ fontSize: '0.85rem', opacity: '0.8' }}>
          {moment(event.created_at).format('DD/MM/YY [at] h:mmA')}
        </span>
      </span>
      {event.note_html && (
        <RichTextDisplay
          style={{ marginTop: '0.5rem' }}
          content={`<blockquote>${event.note_html}</blockquote>`}
        />
      )}
    </Segment>
  )
}
