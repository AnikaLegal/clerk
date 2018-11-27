import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { FIELD_TYPES, FIELD_TYPES_DISPLAY } from 'consts'
import { actions } from 'state'
import Button from 'components/generic/button'
import InputField from 'components/generic/input-field'
import DropdownField from 'components/generic/dropdown-field'

// Form to create a new questionnaire script.
class FirstQuestionForm extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
    }).isRequired,
  }

  constructor(props) {
    super(props)
    this.state = {
      loading: false, // Whether form is loading
      firstQuestion: props.script.firstQuestion || '',
    }
  }

  onInput = e => {
    const { script, setFirstQuestion } = this.props
    const input = e.target.value
    if (!input) return
    const firstQuestionId = Number(input)
    this.setState({ firstQuestion: firstQuestionId, loading: true })
    setFirstQuestion(script.id, firstQuestionId)
  }

  render() {
    const { firstQuestion, loading } = this.state
    const { script, questions } = this.props
    return (
      <div>
        <DropdownField
          label="Start"
          placeholder="Select the starting question"
          value={firstQuestion}
          disabled={loading}
          onChange={this.onInput}
          options={questions.list
            .filter(q => q.script === script.id)
            .map(q => [q.id, q.name])}
        />
      </div>
    )
  }
}

const mapStateToProps = state => ({
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({
  setFirstQuestion: (...args) =>
    dispatch(actions.script.setFirstQuestion(...args)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(FirstQuestionForm)
