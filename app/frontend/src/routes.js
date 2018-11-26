import urls from 'urls'
import ScriptListContainer from 'containers/script-list'
import ScriptDetailsContainer from 'containers/script-details'
// import FormGraph from 'components/form-graph'
// import Questionnaire from 'components/questionnaire'

// Routes for React Router
const routes = [
  {
    name: 'Questionnaires',
    path: urls.client.script.list(),
    RouteComponent: ScriptListContainer,
    header: true,
  },
  {
    name: 'Questionnaire',
    path: urls.client.script.details(':id'),
    RouteComponent: ScriptDetailsContainer,
    header: false,
  },
  // {
  //   name: 'Test Form',
  //   path: '',
  //   component: Questionnaire,
  // },
  // {
  //   name: 'View Form',
  //   path: '',
  //   component: FormGraph,
  // },
  // {
]

export default routes
