import { Component, type ReactNode } from "react";

type Props = { children: ReactNode; fallback?: ReactNode };
type State = { error: Error | null };

/**
 * Catches render/effect errors so a crash in one part (e.g. the 3D scene)
 * never blanks the entire experience. Logs the full error to console and
 * shows a minimal fallback (keeps the DOM content alive).
 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: { componentStack?: string }) {
    console.error("[ErrorBoundary]", error, info?.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        this.props.fallback ?? (
          <div className="sr-only" role="alert">
            Something went wrong.
          </div>
        )
      );
    }
    return this.props.children;
  }
}