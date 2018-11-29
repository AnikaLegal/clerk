import React, { Component } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames/bind'

import Button from 'components/generic/button'
import styles from 'styles/test/boolean.module.scss'

const cx = classNames.bind(styles)

class BooleanInput extends Component {
  static propTypes = {
    prompt: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
  }

  onClick = val => () => {
    // Send a fake event object up to the parent.
    this.props.onChange({ target: { value: String(val) } })
  }

  render() {
    const { prompt, value, onChange } = this.props
    return (
      <div className={cx('wrapper')}>
        <div className={cx('prompt')}>{prompt}</div>
        <div>
          <Button
            btnStyle={value === 'true' ? 'primary' : 'secondary'}
            className={cx('input')}
            onClick={this.onClick(true)}
          >
            Yes
          </Button>
          <Button
            btnStyle={value === 'false' ? 'primary' : 'secondary'}
            className={cx('input')}
            onClick={this.onClick(false)}
          >
            No
          </Button>
        </div>
      </div>
    )
  }
}

export default BooleanInput
