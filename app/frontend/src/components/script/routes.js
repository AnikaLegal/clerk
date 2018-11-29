import urls from 'urls'
import ScriptDetails from './details'
import ScriptGraph from './graph'
import ScriptTest from './test'

// Script details routes for React Router
const routes = [
  {
    name: 'Build',
    path: urls.client.script.details(':id'),
    RouteComponent: ScriptDetails,
  },
  {
    name: 'View',
    path: urls.client.script.graph(':id'),
    RouteComponent: ScriptGraph,
  },
  {
    name: 'Test',
    path: urls.client.script.test(':id'),
    RouteComponent: ScriptTest,
  },
]

export default routes
