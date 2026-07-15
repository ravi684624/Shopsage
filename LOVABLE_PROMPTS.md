# Lovable Prompts — ShopSage Landing Page & UI Demo

[Lovable](https://lovable.dev) builds React + Tailwind + Supabase web apps from
prompts. It's a great way to make a polished **landing page / product demo
shell** for ShopSage to show alongside your Streamlit app in the PPT or a
portfolio — it is not meant to replace the LangChain Python backend, which
Lovable can't run natively. Use these prompts in order, one at a time,
letting Lovable finish each step before pasting the next.

---

### Prompt 1 — Initial scaffold

```
Build a landing page for "ShopSage", an AI shopping assistant that recommends
products by asking clarifying questions and explaining its reasoning, like a
helpful in-store assistant.

Design direction:
- Clean, modern e-commerce feel. Warm coral/red accent color (#FF5A5F) on a
  white/near-white background, dark charcoal text.
- Hero section: bold headline "Shopping advice that actually listens.",
  subheadline about asking questions before recommending, a primary CTA
  button "Try the demo" and a secondary "See how it works".
- Below the hero, a 3-step "How it works" section with icons: 1) Tell
  ShopSage what you need 2) It asks a clarifying question or two
  3) It recommends with clear reasoning and a comparison view.
- Use a clean sans-serif font, generous whitespace, rounded cards with soft
  shadows.
```

### Prompt 2 — Chat demo mock-up

```
Add a "Live demo" section below the how-it-works section. Build a mocked chat
interface (no real backend needed, just local React state) that shows a
sample conversation:

User: "I need a laptop for video editing, budget around ₹1,00,000"
ShopSage: "Got it — a couple quick questions: do you need it to be
lightweight for travel, or is raw power more important?"
User: "Raw power, I don't travel much with it"
ShopSage: "Based on that, I'd recommend the AeroBook Pro 15 — it has a
dedicated GPU and 32GB RAM well within your budget, ideal for video editing.
The Nimbus Creator 16 is faster but goes over budget."

Style it like a real chat UI: user messages right-aligned in a coral bubble,
assistant messages left-aligned in a light gray bubble with a small shopping-bag
avatar icon. Add a typing indicator animation that plays once on page load
before the assistant message appears.
```

### Prompt 3 — Comparison view component

```
Add a "Comparison view" section that shows a responsive card-based comparison
of 3 sample products (AeroBook Air 13, AeroBook Pro 15, Nimbus Creator 16)
side by side. Each card shows: product name, price, star rating, 3 key
features as small tags, and a "Best value" or "Best performance" badge on
the top-scoring card. Add a subtle highlight border on the recommended card.
```

### Prompt 4 — Budget-aware ranking widget

```
Add an interactive "Budget-aware ranking" widget: a slider from ₹20,000 to
₹1,50,000 that re-sorts the 3 products from the comparison section live as
the user drags it, showing a small ranked list (1, 2, 3) with a one-line
reason per rank (e.g. "Best value for this budget", "Slightly over budget
but strongest performance"). Use simple client-side logic based on price and
rating, no backend needed — this is a visual mock of the real ranking logic.
```

### Prompt 5 — Footer + tech credibility section

```
Add a footer section titled "Built with" showing logos/badges for LangChain,
Streamlit, and Python, plus a short line: "Open source on GitHub" linking to
a placeholder GitHub URL. Keep the footer minimal and on-brand with the rest
of the page.
```

### Prompt 6 — Polish pass

```
Do a final polish pass: ensure consistent spacing between sections, add
smooth scroll-to-section behavior from the nav bar, make sure the page is
fully responsive on mobile (stack the comparison cards vertically), and add
a subtle fade-in animation as each section scrolls into view.
```

---

## Tips for using these prompts

- Paste one prompt per turn — Lovable works best with incremental, focused
  instructions rather than one giant prompt.
- After each step, actually look at the preview before moving on; adjust
  wording (e.g. "make the coral less saturated") if something looks off.
- This Lovable site is a **presentation/demo shell** — the real agent logic
  (LangChain + catalog tool + Streamlit) lives in the Python project. You can
  link to a screen-recording or the live Streamlit app from the "Try the
  demo" button.
