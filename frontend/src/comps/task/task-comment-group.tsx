import React from 'react'
import api, { Task } from 'api'
import { Header, Segment, Comment, Divider, Loader } from 'semantic-ui-react'
import moment from 'moment'
import styled from 'styled-components'

const StyledCommentGroup = styled(Comment.Group)`
  && {
    max-width: 100%;
  }
`

export const TaskCommentGroup = ({ task }: { task: Task }) => {
  const commentResults = api.useGetTaskCommentsQuery({ id: task.id })
  const comments = commentResults.data || []

  return (
    <StyledCommentGroup>
      <Loader inverted inline active={commentResults.isLoading} />
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
              <Comment.Text>{comment.text}</Comment.Text>
            </Comment.Content>
          </Comment>
        </Segment>
      ))}
    </StyledCommentGroup>
  )
}
