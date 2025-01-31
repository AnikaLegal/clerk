import React from 'react'
import { TaskActivity, TaskComment } from 'api'
import { Segment, Comment, Loader } from 'semantic-ui-react'
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
        const comment = activity.data
        return (
          <Segment key={comment.id}>
            <Comment>
              <Comment.Content>
                <Comment.Author as="a" href={comment.creator.url}>
                  {comment.creator.full_name}
                </Comment.Author>
                <Comment.Metadata>
                  <div>
                    {moment(comment.created_at).format('DD/MM/YY [at] h:mmA')}
                  </div>
                </Comment.Metadata>
                <RichTextDisplay content={comment.text} />
              </Comment.Content>
            </Comment>
          </Segment>
        )
      })}
    </StyledCommentGroup>
  )
}
