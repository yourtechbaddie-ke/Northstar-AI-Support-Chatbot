import { useMemo, useState } from 'react'
import { ArrowUp, Sparkles, RotateCcw, ShoppingBag, RefreshCcw, MessageCircle } from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const starters = [
  { label: 'Find a product', icon: ShoppingBag, prompt: 'Can you help me find a product?' },
  { label: 'Check availability', icon: Sparkles, prompt: 'Is the Sovereign Shearling Trench in stock?' },
  { label: 'Returns & exchanges', icon: RefreshCcw, prompt: 'What is your return policy?' },
]

function ProductCard({ product }) {
  const [failed, setFailed] = useState(false)
  const image = product.image_url
  return (
    <article className="product-card">
      <div className="product-image">
        {image && !failed ? (
          <img src={image} alt={product.name} onError={() => setFailed(true)} />
        ) : (
          <span className="product-placeholder">NORTHSTAR</span>
        )}
      </div>
      <div className="product-info">
        <strong>{product.name}</strong>
        <small>{product.category} · ${Number(product.price || 0).toLocaleString()}</small>
        <b className={product.status === 'OUT_OF_STOCK' ? 'out' : product.status === 'LOW_STOCK' ? 'limited' : ''}>
          {product.status === 'OUT_OF_STOCK' ? 'Out of stock' : product.status === 'LOW_STOCK' ? 'Limited availability' : 'Available'}
        </b>
      </div>
    </article>
  )
}

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Welcome to Northstar. I’m your intelligent retail concierge. Ask me about products, availability, or returns.' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const sessionId = useMemo(() => crypto.randomUUID(), [])

  async function send(text = input) {
    const message = text.trim()
    if (!message || loading) return
    setMessages(prev => [...prev, { role: 'user', text: message }])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId }),
      })
      if (!res.ok) throw new Error('Request failed')
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', text: data.message, products: data.products || [] }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', text: 'I’m having trouble reaching Northstar Support right now. Please try again in a moment.' }])
    } finally { setLoading(false) }
  }

  function reset() {
    setMessages([{ role: 'assistant', text: 'Welcome to Northstar. I’m your intelligent retail concierge. How can I help?' }])
    setInput('')
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">N</span><span>NORTHSTAR</span></div>
        <nav><a className="active">AI Support</a><a>Products</a><a>Help</a></nav>
        <div className="status"><span /> AI ONLINE</div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow"><span /> PRIVATE RETAIL CONCIERGE</p>
          <h1>Your Northstar,<br /><em>with intelligence.</em></h1>
          <p className="lede">A thoughtful digital concierge for product discovery, availability, returns and customer support.</p>
          <div className="hero-rule" />
          <div className="hero-meta"><span>CREWAI</span><span>FASTAPI</span><span>FIREBASE</span></div>
        </div>

        <section className="chat-card" aria-label="Northstar AI Support">
          <div className="chat-head">
            <div><p className="mini-label">NORTHSTAR AI</p><h2>How can I help?</h2></div>
            <button className="icon-button" onClick={reset} aria-label="Reset conversation"><RotateCcw size={16} /></button>
          </div>
          <div className="conversation">
            {messages.map((m, i) => <div className={`message-row ${m.role}`} key={i}>
              <div className="avatar">{m.role === 'assistant' ? 'N' : 'Y'}</div>
              <div className="message-content">
                <span className="speaker">{m.role === 'assistant' ? 'Northstar AI' : 'You'}</span>
                <p>{m.text}</p>
                {m.products?.map(product => <ProductCard product={product} key={product.id} />)}
              </div>
            </div>)}
            {loading && <div className="thinking"><span /><span /><span /> Northstar AI is checking your request</div>}
          </div>
          <div className="starter-row">{starters.map(({ label, icon: Icon, prompt }) => <button key={label} onClick={() => send(prompt)}><Icon size={14} />{label}</button>)}</div>
          <form className="composer" onSubmit={e => { e.preventDefault(); send() }}>
            <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask Northstar anything..." aria-label="Message" />
            <button type="submit" aria-label="Send message"><ArrowUp size={18} /></button>
          </form>
          <p className="disclaimer"><MessageCircle size={12} /> Northstar AI responds using verified catalog and policy information.</p>
        </section>
      </section>
      <footer><span>NORTHSTAR AI SUPPORT</span><span>Intelligent retail. Refined assistance.</span></footer>
    </main>
  )
}

export default App
