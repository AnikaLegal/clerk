import React from "react";

import { markdownToHtml } from "utils";

export const TimelineItem = ({
  title,
  detail,
  content,
  label,
  bottomLabel,
  color,
}) => (
  <div className="ui segment padded">
    <div className={`ui top attached label ${color}`}>
      {title}
      <div className="detail">{detail}</div>
    </div>
    <div
      style={{ marginBottom: bottomLabel ? "1rem" : 0 }}
      dangerouslySetInnerHTML={{ __html: markdownToHtml(content) }}
    />
    {label && (
      <div className={`ui top right attached label ${color}`}>{label}</div>
    )}
    {bottomLabel && (
      <div className="ui bottom right attached label">{bottomLabel}</div>
    )}
  </div>
);

export const TimelineNote = ({ note }) => {
  return NOTE_TYPES[note.note_type](note);
};

const NOTE_TYPES = {
  PARALEGAL: (note) => (
    <TimelineItem
      title={note.creator.full_name}
      detail={note.created_at}
      content={note.text_display}
      label="File note"
      color="primary"
    />
  ),
  EVENT: (note) => (
    <TimelineItem
      title="Case Update"
      detail={note.created_at}
      content={note.text_display}
      color="primary"
    />
  ),
  ELIGIBILITY_CHECK_SUCCESS: (note) => (
    <TimelineItem
      title={
        <span>
          Eligibility check <strong>cleared</strong> by {note.creator.full_name}
        </span>
      }
      detail={note.created_at}
      content={note.text_display}
    />
  ),
  ELIGIBILITY_CHECK_FAILURE: (note) => (
    <TimelineItem
      title={
        <span>
          Eligibility check <strong>not cleared</strong> by{" "}
          {note.creator.full_name}
        </span>
      }
      detail={note.created_at}
      content={note.text_display}
    />
  ),
  CONFLICT_CHECK_SUCCESS: (note) => (
    <TimelineItem
      title={
        <span>
          Conflict check <strong>cleared</strong> by {note.creator.full_name}
        </span>
      }
      detail={note.created_at}
      content={note.text_display}
    />
  ),
  CONFLICT_CHECK_FAILURE: (note) => (
    <TimelineItem
      title={
        <span>
          Conflict check <strong>not cleared</strong> by{" "}
          {note.creator.full_name}
        </span>
      }
      detail={note.created_at}
      content={note.text_display}
    />
  ),
  REVIEW: (note) => (
    <TimelineItem
      title={note.creator.full_name}
      detail={note.created_at}
      content={note.text_display}
      label="Case review"
      color="orange"
      bottomLabel={<span>Next review {note.event}</span>}
    />
  ),
  PERFORMANCE: (note) => (
    <TimelineItem
      title={note.creator.full_name}
      detail={note.created_at}
      content={note.text_display}
      label="Performance review"
      color="teal"
      bottomLabel={
        <span>
          About&nbsp;
          <a href={note.reviewee.url}>{note.reviewee.full_name}</a>
        </span>
      }
    />
  ),
  EMAIL: (note) => null,
};
