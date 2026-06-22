# Personal Agent Architecture — Based on n8n Template #8237

**Source:** https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/
**Creator:** Derek Cheung
**Date Studied:** 2026-06-05
**Purpose:** Define Systack Personal Agent product architecture

---

## Template Overview: "Jackie" — Personal Life Manager

**What it does:**
AI assistant ("Jackie") that operates through Telegram, managing email, calendar, tasks with voice + text input and persistent memory.

**Node Count:** If + Edit Fields (Set) + Telegram + 6 more

---

## Architecture Breakdown

### 1. Trigger Layer
```
Telegram Trigger
├── Voice message → Voice file retrieval → OpenAI transcription
└── Text message → Direct pass-through
```

**Input handling:**
- Detects message type (voice vs text)
- Voice: Downloads file, sends to OpenAI Whisper API, gets transcript
- Text: Direct to AI

### 2. AI Agent Core
```
AI Agent (OpenRouter-powered)
├── System prompt defines personality + capabilities
├── Receives user intent (text or transcribed voice)
├── Has access to TOOLS:
│   ├── Get Email (Gmail API)
│   ├── Google Calendar (events retrieval)
│   ├── Google Tasks (create + retrieve)
│   └── Current date/time context
└── Maintains conversation MEMORY
```

**Key insight:** The AI agent doesn't just chat — it has **TOOLS** it can call based on user intent.

### 3. Tool Layer

| Tool | Integration | Purpose |
|------|------------|---------|
| **Get Email** | Gmail API | Fetch unread emails with sender/date/subject/summary |
| **Google Calendar** | Google Calendar API | Retrieve events for specified dates |
| **Google Tasks** | Google Tasks API | Create new tasks, retrieve existing |
| **Date/Time** | Built-in | Current context for scheduling |

### 4. Memory Layer
```
Conversation Memory (Simple Memory)
├── Stores conversation history
├── Provides context for multi-turn interactions
└── Enables continuity across sessions
```

### 5. Response Layer
```
AI generates response → Telegram message (Markdown format)
├── Based on gathered data from tools
├── Includes current date context
├── References conversation history
└── Sent back to user via Telegram
```

---

## Credentials Required

| Service | Credential Type | How to Get |
|---------|----------------|-----------|
| Telegram Bot | Bot Token | @BotFather on Telegram |
| OpenAI | API Key | platform.openai.com |
| OpenRouter | API Key | openrouter.ai |
| Google OAuth2 | OAuth2 | Google Cloud Console |

---

## How This Maps to Systack Personal Agent

### What We Need to Build

#### Phase 1: Core Agent (Same as Jackie)
- [ ] Telegram bot interface
- [ ] Voice → text (OpenAI Whisper or local Whisper)
- [ ] AI agent with memory (OpenRouter or local Ollama)
- [ ] System prompt defining "Sol" personality
- [ ] Basic tools: notes, reminders, search

#### Phase 2: Google Integration (Same as Jackie)
- [ ] Gmail: Read, summarize, draft replies
- [ ] Calendar: Check schedule, create events
- [ ] Tasks: Create, complete, list
- [ ] Drive: Search files, get summaries

#### Phase 3: Extended Tools (Beyond Jackie)
- [ ] **Browser automation:** "Search for X", "Check price of Y"
- [ ] **Local file access:** "Read my notes", "Find document about Z"
- [ ] **n8n integration:** "Run backup", "Check workflow status"
- [ ] **SMS/Phone:** Twilio integration for non-Telegram users
- [ ] **Home automation:** Smart home control (future)

#### Phase 4: Multi-Channel (Beyond Jackie)
- [ ] **Web interface:** Browser-based chat
- [ ] **WhatsApp:** Business API
- [ ] **Slack:** Workspace integration
- [ ] **Email:** Respond to emails directly
- [ ] **Voice call:** Phone call interface (future)

---

## Systack Personal Agent — Full Architecture

```
┌─────────────────────────────────────────┐
│           USER INTERFACE LAYER           │
│  Telegram │ Web │ WhatsApp │ Slack      │
└───────────┬─────────────────────────────┘
            │
┌───────────▼─────────────────────────────┐
│         INPUT PROCESSING LAYER          │
│  Voice → Whisper → Text                 │
│  Text → Direct pass-through             │
│  Image → Vision model → Description     │
└───────────┬─────────────────────────────┘
            │
┌───────────▼─────────────────────────────┐
│           AI AGENT CORE                  │
│  Model: OpenRouter / Ollama / Gemini    │
│  Memory: Persistent conversation store  │
│  Personality: "Sol" (defined in prompt)   │
└───────────┬─────────────────────────────┘
            │
┌───────────▼─────────────────────────────┐
│           TOOL ORCHESTRATION           │
│  Intent classifier → Route to tool     │
│  Tools:                                │
│   • Gmail (read, draft, send)          │
│   • Calendar (read, create)            │
│   • Tasks (create, complete, list)     │
│   • Notes (Obsidian/Memories)          │
│   • Search (web, local files)          │
│   • n8n (run workflows, check status)   │
│   • Browser (navigate, extract)        │
│   • System (time, weather, calc)       │
└───────────┬─────────────────────────────┘
            │
┌───────────▼─────────────────────────────┐
│          RESPONSE GENERATION            │
│  AI synthesizes tool outputs            │
│  Formats for channel (Markdown, etc.)    │
│  Includes context + memory              │
└─────────────────────────────────────────┘
```

---

## Data Flow Example

**User:** "What meetings do I have today?"

```
1. Telegram receives message
2. Classify intent: calendar_query
3. Tool: Google Calendar → fetch today's events
4. Tool returns: ["10am: Client call", "2pm: Team standup"]
5. AI synthesizes: "You have two meetings today. At 10am..."
6. Send response via Telegram
7. Store in memory for context
```

**User:** "Remind me to call John tomorrow"

```
1. Telegram receives message
2. Classify intent: create_reminder
3. Tool: Google Tasks → create task "Call John" for tomorrow
4. Tool returns: task created
5. AI: "Done. I've added 'Call John' to your tasks for tomorrow."
6. Send response
7. Store in memory
```

**User:** [Voice message] "Summarize my unread emails"

```
1. Telegram receives voice
2. Download voice file
3. Whisper API → transcript: "Summarize my unread emails"
4. Classify intent: email_summary
5. Tool: Gmail → fetch unread (limit 10)
6. Tool returns: email list with subjects/senders
7. AI summarizes each briefly
8. Send text response
9. Store in memory
```

---

## Implementation Priority

### MVP (Week 1-2)
- [ ] Telegram bot setup
- [ ] Basic AI agent with memory
- [ ] Notes tool (local files)
- [ ] Time/weather tool
- [ ] Simple web search

### V1 (Week 3-4)
- [ ] Google Calendar integration
- [ ] Google Tasks integration
- [ ] Gmail read/summarize
- [ ] Voice input (Whisper)

### V2 (Month 2)
- [ ] Web interface
- [ ] Browser automation
- [ ] Local file search
- [ ] n8n integration
- [ ] Multi-user support

### V3 (Month 3)
- [ ] WhatsApp channel
- [ ] Slack channel
- [ ] Email response mode
- [ ] Custom tool creation
- [ ] Client deployment template

---

## Technical Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| **AI Model** | OpenRouter (primary) / Ollama (local backup) | Use qwen3.5 or similar for local |
| **Memory** | n8n Simple Memory / Redis / SQLite | Persistent across sessions |
| **Voice** | OpenAI Whisper API / Local Whisper | Cloud for accuracy, local for privacy |
| **Telegram** | n8n Telegram node | BotFather for token |
| **Google** | n8n Google nodes | OAuth2 required |
| **Web Search** | Perplexity API / DuckDuckGo | Perplexity for AI answers |
| **Browser** | n8n HTTP Request + Playwright | For complex interactions |
| **Storage** | SQLite / PostgreSQL | User data, memories, logs |
| **Hosting** | n8n self-hosted + OpenClaw | Already running |

---

## Systack Business Model

### Personal Agent as Product

**Target:** Busy professionals, small business owners
**Price:** $99/month (self-hosted) / $199/month (managed)
**Includes:**
- AI agent with all tools
- Google integration
- Voice + text
- 24/7 availability
- Custom tool development

**Value Proposition:**
- "Your AI executive assistant that never sleeps"
- "Handles email, scheduling, research, reminders"
- "Voice-first for hands-free productivity"
- "Privacy-focused with local option"

---

## Files

- Source template: https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/
- This spec: `~/systack-n8n-workflows/architecture/PERSONAL-AGENT-SPEC.md`
- Related: `~/utopia-deli-revamp/workflow-study/n8n-template-research.md`

---

## Next Steps

1. **Deploy Telegram bot** — Get token from BotFather
2. **Set up OpenRouter** — Get API key for AI
3. **Build core agent** — System prompt + memory + basic tools
4. **Add Google integration** — OAuth2 for Gmail/Calendar/Tasks
5. **Test voice input** — Whisper integration
6. **Document for clients** — Deployment guide

**Timeline:** MVP in 2 weeks, V1 in 1 month
