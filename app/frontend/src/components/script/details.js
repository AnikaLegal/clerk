import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import classNames from 'classnames/bind'

import { actions } from 'state'
import FadeIn from 'components/generic/fade-in'
import FirstQuestionForm from 'components/forms/first-question'
import CreateQuestionForm from 'components/forms/create-question'
import UpdateQuestionForm, {
  getQuestionKey,
} from 'components/forms/update-question'

// Questionnaire script details page,
// where a user can view and update a questionnaire.
class ScriptDetails extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
      firstQuestion: PropTypes.number.isRequired,
    }).isRequired,
  }

  render() {
    const { script, questions } = this.props
    return (
      <FadeIn duration="0.2">
        <div className="list-group mb-3">
          <div className="list-group-item">
            <FirstQuestionForm script={script} key={script.firstQuestion} />
          </div>
          {questions.list
            .filter(q => q.script === script.id)
            .sort((a, b) => (a.id > b.id ? 1 : -1))
            .map(q => (
              <UpdateQuestionForm
                script={script}
                question={q}
                key={getQuestionKey(q)}
              />
            ))}
        </div>
        <CreateQuestionForm script={script} />
      </FadeIn>
    )
  }
}

const mapStateToProps = state => ({
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ScriptDetails)
