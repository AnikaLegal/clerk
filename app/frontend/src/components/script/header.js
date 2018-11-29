import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link, withRouter } from 'react-router-dom'

import Button from 'components/generic/button'
import FadeIn from 'components/generic/fade-in'
import routes from './routes'

// Questionnaire script page header,
// used to navigate between different views of a script.
class ScriptHeader extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
    }).isRequired,
  }

  render() {
    const { script } = this.props
    return (
      <FadeIn duration="0.2">
        <h1 className="mb-3">{script.name}</h1>
        {routes.map(({ path, name }) => (
          <Link key={path} to={path.replace(':id', script.id)}>
            <Button className="mr-1" btnStyle="secondary">
              {name}
            </Button>
          </Link>
        ))}
      </FadeIn>
    )
  }
}

export default withRouter(ScriptHeader)
