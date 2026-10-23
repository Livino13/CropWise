import { useEffect, useRef, useState } from 'react'
import { sendChat } from '@/api/client'
import type { ChatMessage } from '@/api/types'
import { CROP_META } from '@/utils/cropMeta'

// Compact crop facts so answers stay grounded in what the app supports.
const CROP_CONTEXT = Object.entries(CROP_META)
  .map(([key, m]) => `${key.replace(/_/g, ' ')}: ${m.season}; ${m.waterNeed} water; ${m.description}`)
  .join('\n')

const SUGGESTIONS = [
  'What can I grow in Rabi?',
  'What does soil pH mean?',
  'Pests on tomato',
  'How do I get a recommendation?',
]

const WELCOME: ChatMessage = {
  role: 'assistant',
  content: 'Hi! I am CropWise Assistant. Ask me about crops, seasons, soil, pests, or how to use the app.',
}

function friendlyError(e: unknown) {
  const raw = e instanceof Error ? e.message : ''
  const match = raw.match(/\{"detail":"([^"]+)"/)
  if (match) return match[1]
  return 'Sorry, the assistant is unavailable right now. Please try again.'
}

export function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open && listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight
  }, [messages, open, sending])

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false) }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  async function send(text: string) {
    const trimmed = text.trim()
    if (!trimmed || sending) return
    const userMsg: ChatMessage = { role: 'user', content: trimmed }
    const history = [...messages, userMsg]
    setMessages(history)
    setInput('')
    setError('')
    setSending(true)
    try {
      const { reply } = await sendChat(history, CROP_CONTEXT)
      setMessages([...history, { role: 'assistant', content: reply }])
    } catch (e) {
      setError(friendlyError(e))
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      {open && (
        <div
          role="dialog"
          aria-label="CropWise chat assistant"
          className="fixed bottom-24 right-4 z-40 w-[min(92vw,380px)] h-[min(70vh,540px)] bg-white border border-stone-200 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
        >
          <div className="flex items-center justify-between px-4 py-3 bg-brand-600 text-white">
            <div>
              <div className="text-sm font-semibold">Ask CropWise</div>
              <div className="text-[11px] text-white/80">Crops · soil · pests · app help</div>
            </div>
            <button
              onClick={() => setOpen(false)}
              aria-label="Close chat"
              className="w-8 h-8 grid place-items-center rounded-full hover:bg-white/15"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4" aria-hidden>
                <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>

          <div ref={listRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-3 bg-stone-50">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap ${
                    m.role === 'user'
                      ? 'bg-brand-600 text-white rounded-br-sm'
                      : 'bg-white border border-stone-200 text-stone-700 rounded-bl-sm'
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-white border border-stone-200 rounded-2xl rounded-bl-sm px-3 py-2 text-sm text-stone-400">
                  Thinking…
                </div>
              </div>
            )}
            {error && <p className="text-xs text-red-500">{error}</p>}
          </div>

          {messages.length <= 1 && (
            <div className="px-3 pb-2 flex flex-wrap gap-1.5 bg-stone-50">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-xs px-2.5 py-1.5 rounded-full border border-stone-200 bg-white text-stone-600 hover:border-brand-300 hover:text-brand-700"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          <form
            onSubmit={(e) => { e.preventDefault(); send(input) }}
            className="flex items-center gap-2 border-t border-stone-100 p-2.5 bg-white"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about crops, soil, pests…"
              aria-label="Chat message"
              className="flex-1 text-sm rounded-lg border border-stone-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500/30"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="px-3 py-2 rounded-lg bg-brand-600 text-white text-sm font-medium disabled:opacity-40"
            >
              Send
            </button>
          </form>
        </div>
      )}

      <button
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={open ? 'Close chat assistant' : 'Open chat assistant'}
        className="fixed bottom-5 right-4 z-40 w-14 h-14 rounded-full bg-brand-600 text-white shadow-lg hover:bg-brand-700 transition-colors grid place-items-center"
      >
        {open ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6" aria-hidden>
            <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-6 h-6" aria-hidden>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 12c0 4.42-4.03 8-9 8a9.9 9.9 0 0 1-3.6-.67L4 21l1.3-3.6A7.6 7.6 0 0 1 3 12c0-4.42 4.03-8 9-8s9 3.58 9 8Z" />
            <path strokeLinecap="round" d="M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01" />
          </svg>
        )}
      </button>
    </>
  )
}

export default ChatWidget
