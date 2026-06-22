# Green's 60–90 Day Plan
**Version:** 2026-05-21 (revised from 26-week roadmap)
**Status:** ACTIVE — Day 1 begins now

---

## Current Situation (Truthful)

| What | Status |
|------|--------|
| Warehouse job | Still active (~$21/hr) |
| Docker Desktop | ✅ Installed |
| Docker Compose | Not found (use `docker compose` instead) |
| PostgreSQL | Not installed |
| n8n | Running in Docker on port 5679 (duplicate instance from training) |
| Active learning | Minimal — plan created but not executed |
| Income from automation | $0 |
| Systack client work | 1 client (Utopia Deli) |

**Reality:** You have the tools. You have the plan. You haven't started the skill build yet.

---

## Actual Progress Log

| Day | Date | What Happened | Status |
|-----|------|---------------|--------|
| 0 | 2026-05-20 | Docker Desktop launched from external drive. `docker run hello-world` worked. | ✅ Done |
| 1 | 2026-05-20 | Built Dockerfile + Node.js image (`my-node-image`) | ✅ Done |
| 2 | 2026-05-20 | Started n8n in Docker with docker-compose.yml on port 5679. sqlite3 works in Code node. | ✅ Done |
| 3 | 2026-05-21 | **PICKING UP HERE** — Day 1 of 60-90 plan: Create `docker-compose.yml` with n8n + PostgreSQL + Adminer | 🔄 Current |

**Current state:**
- `~/docker-practice/day2/docker-compose.yml` has ONLY n8n service
- No PostgreSQL, no Adminer
- No `~/dev/systack-stack/` folder
- No `.env` file
- No README

---

## What This Plan Actually Is

Not a 26-week everything plan. A **60–90 day focused sprint** with one goal:

> **Ship enough proof that someone will pay you $50–$75/hr for automation work.**

That's it. Everything else is noise until that happens.

---

## The 3-Phase Sprint

### Phase 1: Foundation — Days 1–30
**Goal:** Your systems are production-grade and documented. You have a portfolio that beats most junior applicants.

#### Week 1: Docker + Compose (This Week — Starting Now)

| Day | Plan Day | Action | Time | Output |
|-----|----------|--------|------|--------|
| 1 (May 20) | — | Docker Desktop + hello-world | 15 min | Docker running |
| 2 (May 20) | — | Built Dockerfile + Node.js image | 30 min | `my-node-image` built |
| 3 (May 20) | — | n8n in Docker with docker-compose | 30 min | n8n on port 5679 |
| 4 (May 21) | **Day 1** | Create `docker-compose.yml` with n8n + PostgreSQL + Adminer. `docker compose up -d`. Verify all 3 containers start. | 1 hr | `docker-compose.yml` in repo |
| 5 (May 22) | Day 2 | Add volume persistence. Add `.env` file for secrets. Document in README. | 45 min | `.env.example`, README section |
| 6 (May 23) | Day 3 | Add health checks to each service. Test restart behavior. | 45 min | Health check configs |
| 7 (May 24) | Day 4 | Add a 4th service — your own FastAPI app in Docker. | 1 hr | FastAPI container running |
| 8 (May 25) | Day 5 | Connect FastAPI to PostgreSQL. Test read/write. | 1 hr | Working API + DB connection |
| 9 (May 26) | Day 6 | **SHIP:** Push to GitHub. Write README with architecture diagram (text-based). | 1.5 hr | Live repo |
| 10 (May 27) | Day 7 | Rest or catch up | — | — |

**Week 1 Deliverable:** `docker-compose.yml` with 4 services (n8n, PostgreSQL, Adminer, FastAPI). GitHub repo live with README.

#### Week 2: PostgreSQL + Migration
| Day | Action | Time | Output |
|-----|--------|------|--------|
| 8 | Connect to PostgreSQL via Adminer. Create `leads` table schema. | 30 min | Table created |
| 9 | Write Python script to read from SQLite CRM, write to PostgreSQL. | 1 hr | Migration script |
| 10 | Run migration. Verify data integrity. | 45 min | Data in PostgreSQL |
| 11 | Add indexes. Write 3 complex queries (JOIN, aggregate, filter). | 1 hr | Query file |
| 12 | Build n8n workflow that reads from PostgreSQL, processes data. | 1 hr | n8n workflow JSON |
| 13 | **SHIP:** Update GitHub. Write blog post: "Migrating from SQLite to PostgreSQL in 1 day." | 1.5 hr | Blog post published |
| 14 | Rest | — | — |

**Week 2 Deliverable:** PostgreSQL CRM with migrated data. 3 complex queries. n8n integration. Blog post.

#### Week 3: API + Webhooks
| Day | Action | Time | Output |
|-----|--------|------|--------|
| 15 | Build FastAPI endpoint: `POST /leads` — accept lead JSON, store in PostgreSQL. | 1 hr | API endpoint working |
| 16 | Add input validation (Pydantic). Add error handling. | 45 min | Robust endpoint |
| 17 | Build n8n webhook that calls your API. Test end-to-end. | 1 hr | Working webhook flow |
| 18 | Add authentication (API key). Document the API. | 1 hr | API docs |
| 19 | Build a second endpoint: `GET /leads/scored` — return leads with score > threshold. | 1 hr | Scored leads endpoint |
| 20 | **SHIP:** Update GitHub. Record 2-minute demo video (screen recording). Post to LinkedIn. | 1.5 hr | LinkedIn post |
| 21 | Rest | — | — |

**Week 3 Deliverable:** Working API with 2 endpoints. n8n webhook integration. Demo video. LinkedIn post.

#### Week 4: Cloud Deploy
| Day | Action | Time | Output |
|-----|--------|------|--------|
| 22 | Sign up AWS free tier. Launch t2.micro EC2. | 30 min | EC2 instance running |
| 23 | SSH into EC2. Install Docker. Clone your repo. | 45 min | Docker on EC2 |
| 24 | Run `docker compose up -d` on EC2. Verify all services. | 1 hr | Live cloud deployment |
| 25 | Set up GitHub Actions: push to main → auto-deploy to EC2. | 1.5 hr | CI/CD pipeline |
| 26 | Add health check endpoint. Test auto-deploy. | 1 hr | Verified pipeline |
| 27 | **SHIP:** Blog post: "I deployed my automation stack to AWS for $0." | 1.5 hr | Published post |
| 28 | Rest + plan Phase 2 | — | — |

**Week 4 Deliverable:** Live AWS deployment. CI/CD pipeline. Blog post. Portfolio is now Tier 2 competitive.

---

### Phase 2: AI + Sell — Days 31–60
**Goal:** You have AI-powered automations. You're selling to clients. First freelance income.

#### Week 5: AI Fundamentals
| Day | Action | Time | Output |
|-----|--------|------|--------|
| 29 | Watch Andrej Karpathy "Intro to LLMs" (1 hr). Take notes. | 1 hr | Notes file |
| 30 | Build RAG: ingest your CRM data into Ollama embeddings. | 1.5 hr | RAG system working |
| 31 | Build n8n workflow: ask question → RAG → answer from your data. | 1 hr | "Ask my CRM" feature |
| 32 | Test 10 questions. Document accuracy. | 1 hr | Test results |
| 33 | Build second RAG: ingest Systack documentation. | 1 hr | Systack knowledge base |
| 34 | **SHIP:** Demo video. LinkedIn post: "I built an AI that knows my CRM." | 1.5 hr | Social proof |
| 35 | Rest | — | — |

**Week 5 Deliverable:** RAG system over your CRM. Demo video. LinkedIn engagement.

#### Week 6: Prompt Engineering + Agent
| Day | Action | Time | Output |
|-----|--------|------|--------|
| 36 | Read OpenAI Prompt Engineering Guide. Practice 10 prompts for same task. | 1 hr | Prompt comparison file |
| 37 | Build n8n agent with tool access: search web, query CRM, take notes. | 1.5 hr | Agent workflow |
| 38 | Add function calling: agent can update CRM status. | 1 hr | Agent with write access |
| 39 | Test agent with 5 real scenarios. Log results. | 1 hr | Test log |
| 40 | Refine agent based on failures. | 1 hr | Improved agent |
| 41 | **SHIP:** Agent demo. GitHub update. | 1 hr | Portfolio updated |
| 42 | Rest | — | — |

**Week 6 Deliverable:** AI agent that reads AND writes to your CRM. Tested. Documented.

#### Week 7: Outreach Engine
| Day | Action | Time | Output |
|-----|--------|------|--------|
| 43 | Build n8n workflow: scrape 50 company websites → extract email. | 1.5 hr | Scraper workflow |
| 44 | Add AI personalization: generate custom outreach message per company. | 1 hr | Personalization node |
| 45 | Add email send via n8n. Test with 5 real companies. | 1 hr | 5 emails sent |
| 46 | Add follow-up sequence: day 3, day 7, day 14. | 1 hr | Follow-up workflow |
| 47 | Build tracker: log responses, meetings, closes in PostgreSQL. | 1 hr | CRM integration |
| 48 | **SHIP:** Document the outreach engine. LinkedIn post. | 1 hr | Content + engagement |
| 49 | Rest | — | — |

**Week 7 Deliverable:** Automated outreach engine. 5+ real companies contacted. Response tracker.

#### Week 8: First Client Sprint
| Day | Action | Time | Output |
|-----|--------|------|--------|
| 50 | Reach out to 10 companies manually (not automated). | 1 hr | 10 personalized emails |
| 51 | Follow up on Week 7 contacts. | 30 min | Follow-ups sent |
| 52 | Build a specific automation for one prospect's pain point. | 2 hr | Custom demo |
| 53 | Send demo to prospect. Request meeting. | 30 min | Demo delivered |
| 54 | Respond to any inbound. Refine pitch. | 1 hr | Pitch refined |
| 55 | **SHIP:** Case study: "How I built [specific thing] for [prospect]." | 1 hr | Case study published |
| 56 | Rest + plan Phase 3 | — | — |

**Week 8 Deliverable:** 10+ companies contacted. Custom demo built. First meeting potential.

---

### Phase 3: Income + Scale — Days 61–90
**Goal:** First paid project or job offer. Systems that compound.

#### Week 9–10: Client Delivery
- Take on 1–2 small freelance projects ($500–$1,500)
- Build with everything you've learned
- Document process, create templates
- Ask for testimonial

#### Week 11–12: Position for Tier 2
- Update resume with new skills + projects
- Apply to 5 Tier 2 roles ($60K–$80K)
- Leverage freelance income as safety net
- Continue outreach: 5 companies/week minimum

**Week 12 Deliverable:** First freelance income OR interview scheduled. Portfolio is undeniable.

---

## Daily Schedule Template

| Time | Activity | Where |
|------|----------|-------|
| 6:30 AM | Morning briefing (SOL reminder) | Phone |
| Work (5–7 hrs) | Listen to audio content | Phone + earbuds |
| 5:00 PM | Home, decompress | Home |
| 6:00–8:00 PM | Build time (2 hrs) | Computer |
| 8:00 PM | Evening check-in (SOL reminder) | Phone |
| Before bed | Plan tomorrow | Phone |

**Rule:** 2 hours of building minimum. Every day. No zero days.

---

## Audio Content for Work (Passive Learning)

| Topic | Resource | When |
|-------|----------|------|
| Docker | "TechWorld with Nana" Docker playlist | Week 1 |
| PostgreSQL | "Database Design" by Fireship | Week 2 |
| APIs | "FastAPI" by TechWorld with Nana | Week 3 |
| Cloud/AWS | "AWS for Beginners" freeCodeCamp | Week 4 |
| AI/LLMs | Andrej Karpathy YouTube | Week 5 |
| Agents | "AI Engineering" podcast | Week 6 |
| Sales | "Indie Hackers" podcast | Week 7+ |

---

## Success Tracker (Update Weekly)

| Week | New Skills | Hours Built | Projects Shipped | Companies Contacted | Income | Status |
|------|-----------|-------------|------------------|---------------------|--------|--------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |
| 8 | | | | | | |
| 9 | | | | | | |
| 10 | | | | | | |
| 11 | | | | | | |
| 12 | | | | | | |

---

## What SOL Will Do

| Frequency | Action |
|-----------|--------|
| Daily 6:30 AM | Send morning briefing: today's task + audio resource |
| Daily 8:00 PM | Ask: What did you build? Learn? Ship? |
| Weekly (Sun 10 AM) | Review progress, update tracker, adjust plan |
| On demand | Answer questions, debug code, review work |

---

## First Action (Right Now)

1. **Verify Docker Desktop is running** → `docker ps`
2. **Create a new folder** → `mkdir ~/dev/systack-stack`
3. **Create `docker-compose.yml`** → copy from example below
4. **Run `docker compose up -d`** → verify 3 containers start
5. **Message SOL** → "Day 1 done" or "stuck on [step]"

### Minimal `docker-compose.yml` to start:

```yaml
version: "3.8"

services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=systack
      - POSTGRES_PASSWORD=changeme
      - POSTGRES_DB=crm
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  adminer:
    image: adminer
    ports:
      - "8080:8080"
    restart: unless-stopped

volumes:
  n8n_data:
  postgres_data:
```

---

## Bottom Line

**Old plan:** 26 weeks of everything. Overwhelming. Never started.
**This plan:** 12 weeks of focused sprints. Specific tasks. Daily actions. Ship every week.

You have the tools. You have the time. You have SOL.

**Start today. Day 1 is now.**

---

*Plan by SOL, 2026-05-21*
*Revised from 26-week roadmap based on: tools already installed, need for faster feedback loops, focus on shipping over learning*
