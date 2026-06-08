import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center m-6">
          <p className="text-red-700 font-medium">{this.props.fallback || 'Something went wrong'}</p>
          <p className="text-red-500 text-sm mt-1">{this.state.error?.message || 'Check that the API server is running.'}</p>
          <button
            onClick={() => { this.setState({ hasError: false, error: null }) }}
            className="mt-3 text-sm px-3 py-1.5 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Retry
          </button>
        </div>
      )
    }
    return this.props.children
  }
}