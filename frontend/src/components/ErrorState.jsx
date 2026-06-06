export default function ErrorState({ message }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <p className="text-red-700 font-medium">{message || 'Something went wrong'}</p>
      <p className="text-red-500 text-sm mt-1">Check that the API server is running.</p>
    </div>
  )
}
