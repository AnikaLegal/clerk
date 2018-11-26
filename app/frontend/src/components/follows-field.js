import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import { actions } from 'state'
import DropdownField from 'components/generic/dropdown-field'

class FollowsField extends Component {
  static propTypes = {
    question: PropTypes.shape({
      follows: PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.string,
          when: PropTypes.shape({
            id: PropTypes.string,
            value: PropTypes.string,
          }),
        })
      ),
    }),
  }

  constructor(props) {
    super(props)
    this.state = { prev: '', when: '', value: '' }
  }

  getOptions = () =>
    Object.keys(this.props.script)
      .filter(id => id !== this.props.question.id)
      .map(id => [id, this.props.script[id].prompt])

  onRemove = (id, follows) => () => {
    this.props.onRemove(id, follows)
  }

  onAdd = () => {
    const { prev, when, value } = this.state
    if (!this.isValid()) return
    this.props.onAdd(this.props.question.id, prev, when, value)
    this.setState({ prev: '', when: '', value: '' })
  }

  onInput = fieldName => e => this.setState({ [fieldName]: e.target.value })

  isValid = () => this.state.prev && ((!this.state.when && !this.state.value) || (this.state.when && this.state.value))

  render() {
    const { question, script } = this.props
    const options = this.getOptions()
    return (
      <div>
        {question.follows.map(f => (
          <div key={f.id + (f.when ? f.when.id + f.when.value : '')} className="mb-1">
            <button className="close mr-3" onClick={this.onRemove(question.id, f)}>
              <span>&times;</span>
            </button>
            <span>
              Follows "{script[f.id].prompt}"{f.when ? <span> when it is "{f.when.value}"</span> : null}
            </span>
          </div>
        ))}
        <div className="mb-1">
          <span>Follows </span>
          <select value={this.state.prev} onChange={this.onInput('prev')}>
            <option value="">question</option>
            {options.map(([val, display]) => (
              <option key={val} value={val}>
                {display}
              </option>
            ))}
          </select>
          <span> when </span>
          <select value={this.state.when} onChange={this.onInput('when')}>
            <option value="">question</option>
            {options.map(([val, display]) => (
              <option key={val} value={val}>
                {display}
              </option>
            ))}
          </select>
          <span> is </span>
          <input type="text" value={this.state.value} onChange={this.onInput('value')} />
          <button onClick={this.onAdd} disabled={!this.isValid()} className="btn btn-primary">
            Add
          </button>
        </div>
      </div>
    )
  }
}

const mapStateToProps = state => ({
  script: state.script,
})
const mapDispatchToProps = dispatch => ({
  onRemove: (id, follows) => dispatch(actions.question.removeFollows(id, follows)),
  onAdd: (id, prev, when, value) => dispatch(actions.question.addFollows(id, prev, when, value)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(FollowsField)
