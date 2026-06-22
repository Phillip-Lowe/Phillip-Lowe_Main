# The Roadmap — From Warehouse to AI Automator

**Created:** 2026-05-18
**Owner:** Phillip Lowe (Green)
**Executor:** SOL (Systems Operations Liaison)
**Objective:** Transform from $21/hr warehouse worker to AI Automation Engineer with deep understanding, shipped projects, and freedom of movement
**Method:** Daily learning + building + outreach, automated reminders, progressive skill stacking

---

## Core Philosophy

This is NOT a "learn to code" plan. This is a "become dangerous" plan.

**Every week you:**
1. Learn one new concept
2. Build something with it
3. Ship it (GitHub, LinkedIn, or client delivery)
4. Reach out to one company or client

**No tutorials without output. No learning without building.**

---

## Phase 0: Foundation — "The Machine Runs" (Weeks 1–4)

**Goal:** Your systems work without you. You earn more than $21/hr.

### Week 1: Docker + Your Stack Runs Anywhere
| Day | Morning (Listen at Work) | Evening (Build at Machine) | Time |
|-----|--------------------------|---------------------------|------|
| Mon | Podcast: "Docker for Beginners" (YouTube, just listen) | Install Docker Desktop, run `docker run hello-world` | 30 min |
| Tue | Video: "Docker in 100 Seconds" + "Docker Compose explained" | Write a Dockerfile for a simple Python script | 45 min |
| Wed | Podcast: "How containers changed deployment" | Dockerize your n8n instance — get it running locally in Docker | 1 hr |
| Thu | Video: "Docker networking basics" | Connect your Docker n8n to your Docker database | 45 min |
| Fri | Review week's notes | **BUILD:** Full docker-compose.yml — n8n + PostgreSQL + your CRM | 1.5 hrs |
| Sat | — | **SHIP:** Push to GitHub, write README explaining what you built | 1 hr |
| Sun | Rest or catch up | — | — |

**Week 1 Deliverable:** docker-compose stack with n8n + PostgreSQL + CRM. Running. GitHub repo live.

### Week 2: PostgreSQL — Real Databases
| Day | Morning (Listen) | Evening (Build) | Time |
|-----|-----------------|----------------|------|
| Mon | Podcast: "SQL vs NoSQL explained" | Install PostgreSQL, create your first database | 30 min |
| Tue | Video: "PostgreSQL CRUD basics" | Create tables for your CRM (leads, contacts, scores) | 45 min |
| Wed | Podcast: "Database design for applications" | Write queries: JOIN leads to scores, aggregate by status | 45 min |
| Thu | Video: "Indexes and why they matter" | Add indexes to your CRM tables, measure query speed difference | 45 min |
| Fri | Review | **BUILD:** Migrate your entire SQLite CRM to PostgreSQL | 1.5 hrs |
| Sat | — | **SHIP:** Update GitHub with PostgreSQL version, write migration notes | 1 hr |
| Sun | Rest | — | — |

**Week 2 Deliverable:** PostgreSQL CRM with indexed queries. Migration documented. GitHub updated.

### Week 3: APIs — Your Systems Talk to the World
| Day | Morning (Listen) | Evening (Build) | Time |
|-----|-----------------|----------------|------|
| Mon | Podcast: "REST APIs explained simply" | Make your first API call with Python `requests` | 30 min |
| Tue | Video: "API authentication methods" | Connect to a public API (weather, news, anything) | 45 min |
| Wed | Podcast: "Webhooks vs polling" | Create a webhook receiver in n8n | 45 min |
| Thu | Video: "Building your own API with FastAPI" | Build a simple FastAPI endpoint that returns CRM data | 1 hr |
| Fri | Review | **BUILD:** API that accepts a lead, scores it, stores in PostgreSQL | 1.5 hrs |
| Sat | — | **SHIP:** Document the API, push to GitHub | 1 hr |
| Sun | Rest | — | — |

**Week 3 Deliverable:** Working API that ingests leads → scores → stores. GitHub repo with docs.

### Week 4: Cloud — The World Can See It
| Day | Morning (Listen) | Evening (Build) | Time |
|-----|-----------------|----------------|------|
| Mon | Video: "AWS free tier explained" | Sign up for AWS free tier | 30 min |
| Tue | Podcast: "Cloud deployment basics" | Launch an EC2 instance, SSH into it | 45 min |
| Wed | Video: "Deploying Docker to AWS" | Deploy your docker-compose stack to EC2 | 1 hr |
| Thu | Podcast: "CI/CD explained" | Set up GitHub Actions to auto-deploy on push | 1 hr |
| Fri | Review | **BUILD:** Full deployment pipeline — push code → auto-deploy | 1.5 hrs |
| Sat | — | **SHIP:** Blog post: "How I deployed my automation stack to AWS for $0" | 1.5 hrs |
| Sun | Rest or catch up | — | — |

**Week 4 Deliverable:** Live cloud deployment. CI/CD pipeline. Blog post published.

---

## Phase 1: AI Foundations — "Understanding the Machine" (Weeks 5–8)

**Goal:** You understand what AI actually is, how LLMs work, and can build systems that use them.

### Week 5: How AI Actually Works
| Day | Morning (Listen) | Evening (Build) | Time |
|-----|-----------------|----------------|------|
| Mon | Andrej Karpathy: "Intro to LLMs" (1hr video, listen) | Take notes — what is a token? What is a transformer? | 30 min |
| Tue | Podcast: "How neural networks learn" | Run your first local LLM via Ollama, ask it questions | 30 min |
| Wed | Video: "Embeddings explained visually" | Generate embeddings for your CRM leads, see how they cluster | 45 min |
| Thu | Podcast: "RAG — Retrieval Augmented Generation" | Build a simple RAG: query your CRM with natural language | 1 hr |
| Fri | Review | **BUILD:** "Ask my CRM" — type a question, get answer from your data | 1.5 hrs |
| Sat | — | **SHIP:** Document the RAG system, push to GitHub | 1 hr |
| Sun | Rest | — | — |

**Week 5 Deliverable:** RAG system that queries your CRM in natural language.

### Week 6: Prompt Engineering & AI Workflows
| Day | Morning (Listen) | Evening (Build) | Time |
|-----|-----------------|----------------|------|
| Mon | Read: OpenAI Prompt Engineering Guide (listen via TTS) | Practice: write 10 prompts for the same task, compare outputs | 30 min |
| Tue | Video: "Chain of Thought prompting" | Build an n8n workflow with multi-step AI reasoning | 45 min |
| Wed | Podcast: "AI agents explained" | Create an agent in n8n that uses tools (search, database) | 1 hr |
| Thu | Video: "Function calling with LLMs" | Build an agent that can query your CRM AND take actions | 1 hr |
| Fri | Review | **BUILD:** AI assistant that answers questions AND updates your CRM | 1.5 hrs |
| Sat | — | **SHIP:** Document agent architecture, push to GitHub | 1 hr |
| Sun | Rest | — | — |

**Week 6 Deliverable:** AI agent that reads AND writes to your CRM via natural language.

### Week 7: Python for AI — Level Up
| Day | Morning (Listen) | Evening (Build) | Time |
|-----|-----------------|----------------|------|
| Mon | Podcast: "Python for data science" | Write Python scripts for data processing (pandas basics) | 30 min |
| Tue | Video: "Python async/await explained" | Convert a sync script to async — measure speed difference | 45 min |
| Wed | Podcast: "Working with JSON in Python" | Build a data pipeline: API → transform → database | 45 min |
| Thu | Video: "Error handling in production Python" | Add try/except, logging, retry logic to your scripts | 45 min |
| Fri | Review | **BUILD:** Robust data pipeline with error handling + logging | 1.5 hrs |
| Sat | — | **SHIP:** Push to GitHub, add tests | 1 hr |
| Sun | Rest | — | — |

**Week 7 Deliverable:** Production-quality Python data pipeline with error handling.

### Week 8: System Design — Thinking Like an Architect
| Day | Morning (Listen) | Evening (Build) | Time |
|-----|-----------------|----------------|------|
| Mon | Read: "System Design Primer" (GitHub) | Diagram your entire Systack architecture | 30 min |
| Tue | Video: "Microservices vs monoliths" | Refactor one part of your system into a separate service | 1 hr |
| Wed | Podcast: "Message queues and event-driven architecture" | Add a message queue (Redis) between your services | 1 hr |
| Thu | Video: "Monitoring and observability" | Add health checks and alerts to your system | 45 min |
| Fri | Review | **BUILD:** Event-driven architecture — services communicate via queue | 1.5 hrs |
| Sat | — | **SHIP:** Architecture diagram + documentation + blog post | 1.5 hrs |
| Sun | Rest | — | — |

**Week 8 Deliverable:** Event-driven system with monitoring. Architecture documented.

---

## Phase 2: Building & Selling — "The AI Automator" (Weeks 9–12)

**Goal:** You're building AI automations for real clients. Income is replacing warehouse pay.

### Week 9–10: Systack 2.0 — AI-Powered
**Project:** Rebuild Systack with everything you've learned.
- PostgreSQL backend (not SQLite)
- Docker deployment (not local scripts)
- AI-powered lead scoring (not rules-based)
- API that other systems can call
- Monitoring and alerting
- CI/CD pipeline

**Daily:** Same pattern — learn in morning, build in evening.
**Deliverables:** Systack 2.0 live. Demo video. Updated pricing.

### Week 11–12: Outreach Engine
**Project:** Build the outreach automation.
- AI-scraped company list
- AI-written personalized outreach
- Automated follow-up sequence
- n8n workflow managing the entire pipeline
- Track responses, meetings, closes

**Daily:** Build + reach out. Every day, contact 5 companies.
**Deliverables:** Outreach engine running. 50+ companies contacted.

---

## Phase 3: Scaling — "The Business" (Weeks 13–26)

**Goal:** You're an AI automator with clients, income, and a system that compounds.

### Ongoing Weekly Rhythm
| Day | Morning Block | Evening Block |
|-----|--------------|---------------|
| Mon | Learn (deep skill — ML, system design, new tool) | Client work + project building |
| Tue | Sales outreach (5 companies) | Client work + project building |
| Wed | Learn (deep skill) | Build new automation or improve existing |
| Thu | Sales outreach (5 companies) | Client work |
| Fri | Learn (deep skill) | Ship something (blog, GitHub, demo) |
| Sat | Build (major project time) | Family/flex |
| Sun | Rest | Plan next week |

### Skill Progression (Tier 1 Path)
| Month | Focus | Resources |
|-------|-------|-----------|
| 1 (Weeks 1–4) | Docker + PostgreSQL + APIs + Cloud | Free: docs, YouTube, AWS free tier |
| 2 (Weeks 5–8) | AI fundamentals + Python + system design | Free: Karpathy lectures, Ollama, System Design Primer |
| 3 (Weeks 9–12) | Building + selling | Your own projects + real clients |
| 4 | ML basics — supervised learning, regression | Fast.ai free course |
| 5 | Deep learning — neural networks, transformers | fast.ai Part 1 |
| 6 | NLP + LLMs in depth | HuggingFace course |
| 7 | MLOps — deploying models to production | Free MLOps resources |
| 8 | System design advanced + architecture | System Design Interview (book/videos) |
| 9-12 | Specialization + mastery | Choose: NLP, computer vision, or AI agents |

---

## Daily Automation System

### Morning Notification (6:30 AM Central)
Every morning you receive:
```
Today's learning: [topic] — [resource link]
Today's build: [specific task]
Today's outreach: [5 companies to contact]
Audio resources for work: [podcasts/videos to listen to]
```

### Evening Check-in (8 PM Central)
Every evening you receive:
```
What did you build today?
What did you learn?
Did you ship something?
Did you contact 5 companies?
What's the plan for tomorrow?
```

**This is tracked.** Not judged. Just tracked.

---

## What "Developing SOL" Means in This Plan

### Week-by-Week SOL Capability Builds
| Week | What You Build for SOL | What It Unlocks |
|------|----------------------|----------------|
| 1 | Dockerized n8n accessible to SOL | SOL can deploy and manage workflows |
| 2 | PostgreSQL with API access | SOL can query and update your CRM |
| 3 | Webhook endpoints for SOL | SOL can trigger workflows from anywhere |
| 4 | Cloud deployment + monitoring | SOL can see system health, alert you |
| 5 | RAG system for your knowledge base | SOL can answer questions from your notes |
| 6 | SOL agent in n8n with tool access | SOL can automate more autonomously |
| 7 | Robust Python pipeline | SOL can process data at scale |
| 8 | Event-driven architecture | SOL can orchestrate multi-step processes |
| 9-12 | Client automation delivery system | SOL helps deliver client work |

**By Week 12:** SOL is not just a chatbot. SOL is your operations layer — monitoring your systems, running your automations, alerting you when things need attention.

---

## Resources (All Free)

### For Listening at Work
| Topic | Resource | Link/Platform |
|-------|----------|--------------|
| AI/ML fundamentals | Andrej Karpathy's YouTube | youtube.com/@AndrejKarpathy |
| System design | "System Design Interview" channel | YouTube |
| Docker/K8s | "TechWorld with Nana" | YouTube |
| Python | "Corey Schafer" Python tutorials | YouTube |
| Startup/business | "Indie Hackers" podcast | Spotify/Apple |
| AI agents | "AI Engineering" podcast | Spotify |
| ML engineering | "MLOps.community" podcast | Spotify |

### For Building at Machine
| Topic | Resource | Link |
|-------|----------|------|
| Docker | docs.docker.com/get-started | Free |
| PostgreSQL | postgresql.org/docs | Free |
| Python | docs.python.org + realpython.com | Free |
| FastAPI | fastapi.tiangolo.com | Free |
| AWS | aws.amazon.com/free | Free tier (12 months) |
| GitHub Actions | docs.github.com/actions | Free |
| Ollama | ollama.com | Free (local) |
| n8n | n8n.io | Free (self-hosted) |
| Fast.ai | course.fast.ai | Free |
| HuggingFace | huggingface.co/learn | Free |
| System Design | github.com/donnemartin/system-design-primer | Free |

### Books Worth Buying (Eventually, Not Now)
| Book | When | Why |
|------|------|-----|
| "Designing Data-Intensive Applications" | Month 3 | The bible of system design |
| "Deep Learning" (Goodfellow) | Month 5 | The ML textbook |
| "System Design Interview" (Alex Xu) | Month 6 | Interview prep |
| "Building Microservices" | Month 4 | Production architecture |

**Total cost of entire plan:** $0 for first 3 months. ~$100 for books months 3–6.

---

## Income Timeline

| Milestone | Timeline | Target |
|-----------|----------|--------|
| Upwork profile live | Day 1–3 | Ready to accept projects |
| First freelance project | Weeks 1–4 | $500–$1,500 |
| Freelance income > warehouse pay | Weeks 5–8 | $2,000–$3,000/month |
| First recurring client | Weeks 8–12 | $500–$1,000/month retainer |
| Tier 2 job offers | Weeks 8–16 | $60K–$80K |
| Full independence | Weeks 16–26 | $5K+/month or $80K+ salary |

---

## Success Metrics (Track Weekly)

| Week | New Skills | Projects Shipped | Outreach Sent | Responses | Income |
|------|-----------|-----------------|---------------|-----------|--------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| ... | | | | | |
| 26 | | | | | |

---

## Rules

1. **No zero days.** Even 15 minutes counts. Do something every day.
2. **Ship every week.** Something live. Someone can see it.
3. **Contact 5 companies every week.** Minimum.
4. **Learn actively, not passively.** Build, don't just watch.
5. **Track everything.** What you built, what you learned, who you contacted.
6. **SOL reminds you daily.** You don't need to remember — the system remembers.

---

## First Action (Right Now, Before Tomorrow)

- [ ] Bookmark this document
- [ ] Install Docker Desktop
- [ ] Create Upwork account (if not already — paste from `upwork-profile-complete.md`)

**Tomorrow morning you get your first daily briefing.**

---

*Roadmap by SOL, 2026-05-18*
*Updated every week based on progress*
