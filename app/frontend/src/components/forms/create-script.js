import React, { Component } from 'react'
import { connect } from 'react-redux'

import { actions } from 'state'
import ConfirmationModal from 'components/modals/confirm'
import Button from 'components/generic/button'
import InputField from 'components/generic/input-field'
import FadeIn from 'components/generic/fade-in'

const INITIAL_STATE = {
  loading: false, // Whether form is loading
  showModal: false, // Whether the modal is visible
  isOpen: false, // Whether the form is open / closed
  name: '', // New script name
}


// Form to create a new questionnaire script.
class CreateScriptForm extends Component {
  constructor(props) {
    super(props)
    this.state = { ...INITIAL_STATE }
  }

  onSubmit = () =>
    this.setState({ showModal: true })

  onCancel = () =>
    this.setState({ showModal: false })

  onConfirm = () => {
    const { createScript } = this.props
    const { name } = this.state
    this.setState({ loading: true, showModal: false })
    createScript(name)
      .then(this.setState({ ...INITIAL_STATE }))
  }

  onInputName = e =>
    this.setState({ name: e.target.value })

  toggleOpen = () =>
    this.setState({ isOpen: !this.state.isOpen })

  isFormValid = () =>
    !this.state.loading &&
    this.state.name.length > 3

  render() {
    const { name, isOpen, showModal } = this.state
    if (!isOpen) {
      return (
        <Button onClick={this.toggleOpen}>
          Add Questionnaire
        </Button>
      )
    }
    return (
      <FadeIn>
        <InputField
          label="Name"
          type="text"
          placeholder="Name your new questionnaire"
          value={name}
          onChange={this.onInputName}
          autoFocus
        />
        <div className="mt-2">
          <Button
            className="mr-2"
            onClick={this.onSubmit}
            disabled={!this.isFormValid()}
          >
            Add
          </Button>
          <Button
            onClick={this.toggleOpen}
            btnStyle="danger"
          >
            Close
          </Button>
        </div>
        <ConfirmationModal isVisible={showModal} onConfirm={this.onConfirm} onCancel={this.onCancel}>
          <p>
            <strong>Add Questionnaire</strong>
          </p>
          <p>Create a new questionnaire named "{name}"?</p>
        </ConfirmationModal>
      </FadeIn>
    )
  }
}


const mapStateToProps = () => ({})
const mapDispatchToProps = dispatch => ({
  createScript: name => dispatch(actions.script.create(name)),
})
export default connect(mapStateToProps, mapDispatchToProps)(CreateScriptForm)
