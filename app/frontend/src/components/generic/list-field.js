import React, { Component } from 'react'

import DropdownField from 'components/generic/dropdown-field'


class ListField extends Component {

  constructor(props) {
    super(props)
    this.state = { 
      list: [],
    }
  }

  onNextChange = e => {
    const { list } = this.state
    const val = e.target.value
    if (val && !list.includes(val)) {
      const newList = [...list, val]
      this.setState({ list: newList})
      this.props.onChange(newList)
    }
  }

  render() {
    const { list, next } = this.state
    const { label, placeholder, options } = this.props
    return (
      <div>
        {list.map(el => (
          <DropdownField
            key={el}
            label={label}
            placeholder={placeholder}
            value={el}
            options={options}
            readOnly
          />
        ))}
        <DropdownField
          label={label}
          placeholder={placeholder}
          onChange={this.onNextChange}
          options={options}
          />
      </div>
    )
  }

}


export default ListField