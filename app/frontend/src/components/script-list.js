import React, { Component } from 'react'
import { connect } from 'react-redux'
import uniqid from 'uniqid'

import { actions } from 'state'

class ScriptList extends Component {
  componentDidMount() {
    this.props.listQuestions()
  }
  render() {
    const { scripts } = this.props
    return (
    	<div>
    		{Object.values(scripts).map(script => (
					<ul key={uniqid()} className="list-group mb-3">
						{Object.values(script).map(question => question && (
					  	<li key={question.id} className="list-group-item">{question.prompt}</li>
						))}
					</ul>
    		))}
    	</div>
  	)
  }
}

const mapStateToProps = state => ({
	scripts: state.data.script.list
})
const mapDispatchToProps = dispatch => ({
  listQuestions: () => dispatch(actions.script.list()),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ScriptList)
