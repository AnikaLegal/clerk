import urls from 'urls'
import FormBuilder from 'components/form-builder'
import FormGraph from 'components/form-graph'
import ScriptList from 'components/script-list'
import ScriptDetails from 'components/script-details'
import Questionnaire from 'components/questionnaire'

// Routes for React Router
const routes = [
  {
    name: 'Questionnaires',
    path: urls.client.script.list(),
    RouteComponent: ScriptList,
    header: true,
  },
  {
    name: 'Questionnaire',
    path: urls.client.script.details(':id'),
    RouteComponent: ScriptDetails,
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
  //   name: 'Build Form',
  //   path: '',
  //   component: FormBuilder
  // },
]

export default routes
