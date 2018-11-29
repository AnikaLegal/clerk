import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import Dracula from 'graphdracula'

const Graph = Dracula.Graph
const Renderer = Dracula.Renderer.Raphael
const Layout = Dracula.Layout.Spring

class ScriptGraph extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
      firstQuestion: PropTypes.number.isRequired,
    }).isRequired,
  }

  constructor(props) {
    super(props)
  }

  getQuestions = () =>
    this.props.questions.list.filter(q => q.script === this.props.script.id)

  componentDidMount() {
    this.drawGraph()
  }

  componentDidUpdate() {
    this.drawGraph()
  }

  drawGraph() {
    const { script, questions } = this.props
    const questionList = this.getQuestions()
    if (!script.firstQuestion || questionList.length < 1) return
    const graph = new Graph()

    // Find and draw all connected questions using depth-first-search,
    // implemented using a while-loop and a stack.
    const visited = new Set()
    const first = questions.lookup[script.firstQuestion]
    const stack = []
    stack.push(first)
    while (stack.length > 0) {
      const current = stack.pop()
      if (visited.has(current.id)) {
        // If we've seen this before, then ignore
        continue
      } else {
        // Mark the current question as 'visited'
        visited.add(current.id)
      }
      // Find all the transitions that follow the current question
      const transitions = questionList
        .reduce((trans, q) => [...trans, ...q.parentTransitions], [])
        .filter(trans => trans.previous === current.id)

      // Draw all edges leading from the current question
      for (let transition of transitions) {
        const source = current
        const target = questions.lookup[transition.next]
        stack.push(target)
        graph.addEdge(source.name, target.name, {
          directed: true,
        })
      }
    }

    // Draw all unvisited questions
    const notVisited = questionList.filter(q => !visited.has(q.id))
    for (let question of notVisited) {
      graph.addNode(question.name)
    }

    const layout = new Layout(graph)
    const renderer = new Renderer('#graph', graph, 800, 500)
    renderer.draw()
  }

  render() {
    const questionList = this.getQuestions()
    if (questionList.length < 1) {
      return <p>No questions to visualize</p>
    }
    return <div id="graph" />
  }
}

const mapStateToProps = state => ({
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ScriptGraph)
