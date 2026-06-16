export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-8" role="status" aria-live="polite">
      <div className="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
      <span className="sr-only">Loading...</span>
    </div>
  )
}

