import React from 'react'
import { TaskComment } from 'api'
import { Segment, Comment, Loader } from 'semantic-ui-react'
import moment from 'moment'
import styled from 'styled-components'
import { RichTextDisplay } from 'comps/rich-text'

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
              {comment.type == 'USER' ? (
                <Comment.Author as="a" href={comment.creator.url}>
                  {comment.creator.full_name}
                </Comment.Author>
              ) : (
                <Comment.Author as="span">Task Update</Comment.Author>
              )}
              <Comment.Metadata>
                <div>{moment(comment.created_at).format("DD/MM/YY [at] h:mmA")}</div>
              </Comment.Metadata>
              <RichTextDisplay content={comment.text} />
            </Comment.Content>
          </Comment>
        </Segment>
      ))}
    </StyledCommentGroup>
  )
}
