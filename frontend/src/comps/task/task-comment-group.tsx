import React from 'react'
import { TaskComment } from 'api'
import { Segment, Comment, Loader } from 'semantic-ui-react'
import moment from 'moment'
import styled from 'styled-components'
import { RichtextDisplay } from 'comps/richtext-editor'

const StyledCommentGroup = styled(Comment.Group)`
  && {
    max-width: 100%;
  }
`

export const TaskCommentGroup = ({
  comments,
  loading,
}: {
  comments: TaskComment[]
  loading: boolean
}) => {
  return (
    <StyledCommentGroup>
      <Loader inverted inline active={loading} />
      {comments.map((comment) => (
        <Segment key={comment.id}>
          <Comment>
            <Comment.Content>
              <Comment.Author as="a">
                {comment.creator.full_name}
              </Comment.Author>
              <Comment.Metadata>
                <div>{moment(comment.created_at).fromNow()}</div>
              </Comment.Metadata>
              <RichtextDisplay content={comment.richtext} />
            </Comment.Content>
          </Comment>
        </Segment>
      ))}
    </StyledCommentGroup>
  )
}
