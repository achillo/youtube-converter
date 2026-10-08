import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState('Bereit')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()

    const trimmedUrl = url.trim()

    if (!trimmedUrl) {
      setStatus('Bitte gib eine YouTube-URL ein.')
      return
    }

    if (!/^https?:\/\/(www\.)?(youtube\.com|youtu\.be)\//i.test(trimmedUrl)) {
      setStatus('Bitte gib eine gültige YouTube-URL ein.')
      return
    }

    setIsLoading(true)
    setStatus('Download wird gestartet...')

    try {
      const response = await fetch('/api/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: trimmedUrl,
          mode: 'mp3',
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Download fehlgeschlagen.')
      }

      setStatus(data.message || 'Download wurde gestartet.')
    } catch (error) {
      setStatus(error.message || 'Ein Fehler ist aufgetreten.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <form className="download-form" onSubmit={handleSubmit}>
        <div className="form-header">
          <p className="eyebrow">YouTube Converter</p>
          <h1>Video herunterladen</h1>
        </div>

        <label htmlFor="youtube-url" className="sr-only">
          YouTube URL
        </label>

        <input
          id="youtube-url"
          type="url"
          name="youtube-url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          autoComplete="off"
        />

        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Wird gestartet...' : 'Starten'}
        </button>

        <p className="status" role="status" aria-live="polite">
          {status}
        </p>
      </form>
    </main>
  )
}

export default App
