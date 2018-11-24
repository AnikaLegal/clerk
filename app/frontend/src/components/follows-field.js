import React, { Component } from 'react'

import DropdownField from 'components/generic/dropdown-field'


class FollowsField extends Component {

  // onRemove = id => () => {
    // const 
  // }

  onIdChange = e => {
    const { ids } = this.state
    const val = e.target.value
    if (val && !ids.includes(val)) {
      const newIds = [...ids, val]
      this.setState({ ids: newIds})
      this.props.onChange(this.getFormattedData(newIds))
    }
  }

  // onWhenIdChange = e => {

  // }

  // onWhen

  render() {
    return null
    // const { ids, next } = this.state
    // const { script, questionId } = this.props
    // const options = Object.keys(script)
    //   .filter(k => k !== questionId)
    //   .map(k => [k, script[k].prompt])
    // return (
    //   <div className="mb-3">
    //     <p>Previous Questions</p>
    //     {ids.map(id => (
    //       <div key={id} className="mb-1">
    //         <select readOnly className="form-control" value={id}>
    //           <option>{script[id].prompt}</option>
    //         </select>
    //         <button className="close" onClick={this.onRemove(id)} />
    //       </div>
    //     ))}
    //     <div className="input-group">
    //       <select className="form-control" onChange={this.onNextChange}>
    //         <option value="">Follows a previous question</option>
    //         {options.map(([val, display]) => (
    //           <option key={val} value={val}>
    //             {display}
    //           </option>
    //         ))}
    //       </select>
    //     </div>
    //   </div>
    // )
  }
}



export default FollowsField