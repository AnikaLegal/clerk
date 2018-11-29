import urls from 'urls'
import ScriptListContainer from 'containers/script-list'
import ScriptDetailsContainer from 'containers/script-details'

// Top level routes for React Router
// Some routes will have sub-routes defined inside their components.
const routes = [
  {
    name: 'Questionnaires',
    path: urls.client.script.list(),
    RouteComponent: ScriptListContainer,
    header: true,
    exact: true,
  },
  {
    name: 'Build Questionnaire',
    path: urls.client.script.details(':id'),
    RouteComponent: ScriptDetailsContainer,
    header: false,
    exact: false,
  },
]

export default routes
