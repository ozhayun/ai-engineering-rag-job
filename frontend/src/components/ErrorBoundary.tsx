import { ReactNode, Component, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen flex items-center justify-center" style={{ background: 'var(--color-bg-darker)' }}>
          <div className="text-center p-8 max-w-md">
            <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--color-accent)' }}>
              Something went wrong
            </h1>
            <p className="mb-6" style={{ color: 'var(--color-text-secondary)' }}>
              An unexpected error occurred. Please refresh the page to continue.
            </p>
            {this.state.error && (
              <pre className="text-xs mb-6 p-4 rounded bg-red-900 bg-opacity-20 overflow-auto" style={{ color: '#ff6b6b' }}>
                {this.state.error.message}
              </pre>
            )}
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 rounded-lg font-semibold"
              style={{
                background: 'linear-gradient(135deg, var(--color-accent), var(--color-primary-dark))',
                color: 'var(--color-bg-darker)',
              }}
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
