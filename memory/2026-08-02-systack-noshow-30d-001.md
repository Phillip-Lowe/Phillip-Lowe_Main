# SyStack No-Show Reduction 30-Day Mission

## Mission Control

- Mission ID: SYSTACK-NOSHOW-30D-001
- Mission Name: SyStack Appointment Recovery Pilot
- Status: EVIDENCE_COLLECTION
- Start Date: 2026-08-02
- Decision Deadline: 2026-09-01
- Principal: GREEN
- Execution Owner: SOL
- Architecture Owner: ORACLE
- Commercial Target: One paid pilot
- Primary Metric: Preventable no-show rate
- Existing Components Authorization: READ-ONLY AUDIT_AND_DISCOVERY_DEMO
- New Build Authorization: BLOCKED_PENDING_EVIDENCE
- Production Change Authorization: BLOCKED_PENDING_GREEN_APPROVAL

## Mission

Prove that SyStack can measurably reduce preventable appointment no-shows for one narrowly defined service-business segment through automated confirmation, reminder, and exception-recovery workflows.

## Existing Infrastructure

The following infrastructure is known to exist at mission initiation:

- PostgreSQL database: systack_noshow
- Bookings table
- n8n booking-creation workflow
- n8n booking-confirmation workflow
- n8n T-24-hour reminder workflow
- n8n T-2-hour reminder workflow
- Booking dashboard on port 8772
- Auto-release capability queued but not authorized for implementation
- Smart-rebooking capability queued but not authorized for implementation

The existence of an asset does not establish that it is active, healthy, secure, correctly connected, or pilot-ready.

## Initial Buyer Hypothesis

Owner-operated appointment businesses where one missed appointment creates meaningful lost revenue and staff downtime.

Candidate subsegments:

- Barbershops
- Salons
- Independent beauty professionals
- Nonregulated consultants
- Other owner-operated scheduled-service businesses

Regulated healthcare is excluded from the initial mission because it introduces additional privacy, integration, consent, and compliance obligations.

## Problem Boundary

The pilot addresses appointments lost because customers:

- Forget the appointment
- Do not receive an effective reminder
- Cannot easily confirm, cancel, or reschedule
- Ignore generic reminders
- Fail to respond without staff follow-up
- Give the business too little time to refill the opening

The pilot does not initially attempt to solve:

- Service dissatisfaction
- Pricing objections
- Transportation barriers
- Deposit enforcement
- Broad lead generation
- Reputation management
- General CRM requirements
- General customer-support automation

## Core Thesis

Appointment businesses do not merely need more reminders. They need an operational recovery system that identifies appointment risk early enough to confirm attendance, capture timely cancellations, support rescheduling, escalate exceptions, and protect otherwise lost revenue.

## Primary Metric

Preventable No-Show Rate:

Preventable no-shows divided by eligible scheduled appointments.

## Supporting Metrics

- Baseline no-show rate
- Pilot-period no-show rate
- Confirmation rate
- Timely cancellation rate
- Rescheduling rate
- Unresponsive booking rate
- Appointments recovered
- Openings successfully refilled
- Estimated revenue protected
- Staff follow-up minutes avoided
- Reminder delivery failures
- Customer opt-outs
- Customer complaints
- Workflow exception count
- Manual interventions required

Message opens, clicks, and delivery events are diagnostic metrics. They are not the primary business outcome.

## Evidence Threshold

Before substantial new architecture or implementation, the mission requires:

- 10 completed customer interviews
- At least 5 businesses with measurable no-show exposure
- At least 3 businesses reporting that the problem is recurring and economically meaningful
- At least 1 business willing to provide baseline data or enter a controlled pilot

At least one canonical Evidence Gate condition must also be satisfied:

1. Three independent users demonstrate the same costly problem.
2. One customer pays for resolution.
3. The system solves a documented internal bottleneck with measurable cost.
4. The work is explicitly authorized as a bounded research experiment.

## Pilot Offer Hypothesis

SyStack Appointment Recovery Pilot:

A 30-day managed service that confirms appointments, identifies unresponsive customers, facilitates cancellation or rescheduling, escalates defined exceptions, and helps the business recover openings before they become lost revenue.

The offer remains a hypothesis until customer evidence supports its language, scope, channel, and pricing.

## Initial Pilot Scope

Potentially included after evidence authorization:

1. Booking intake from one supported source
2. Initial booking confirmation
3. Scheduled reminder sequence
4. Confirm, cancel, and reschedule actions
5. Unresponsive-customer classification
6. Staff escalation for defined exceptions
7. Appointment outcome recording
8. Weekly outcome report
9. End-of-pilot comparison against baseline

## Explicit Exclusions

The initial pilot will not include:

- A general-purpose CRM
- A new platform
- A new fleet agent
- A major dashboard expansion
- AI voice calling
- Complex multichannel campaigns
- Deposit or payment enforcement
- Reputation management
- Lead nurturing
- Broad customer-support automation
- Unsupported custom integrations
- Auto-release without separate evidence and approval
- Smart rebooking without separate evidence and approval

## Existing Infrastructure Audit

A read-only audit is authorized during evidence collection.

The audit must determine:

- Whether the systack_noshow database is reachable
- Whether the bookings table exists and matches documented expectations
- Whether test and production environments remain separated
- Whether the known n8n workflows exist
- Whether each workflow is active or inactive
- Whether workflow triggers and dependencies are configured
- Whether the dashboard responds on port 8772
- Whether dashboard access controls are functioning
- Whether booking statuses reconcile across database and workflows
- Whether reminder schedules use the correct timezone
- Whether webhook protections are present
- Whether credentials are referenced safely
- Whether logs reveal unresolved failures
- Whether a discovery demonstration can be run without modifying production state

The audit must not:

- Modify records
- Change schemas
- Activate workflows
- Execute live customer communications
- Rotate credentials
- Repair workflows
- Start queued features
- Deploy code
- Alter dashboard configuration
- Touch production without explicit approval

All findings must be classified as:

- VERIFIED_RUNNING
- VERIFIED_PRESENT_INACTIVE
- PRESENT_STATUS_UNKNOWN
- DEGRADED
- FAILED
- NOT_FOUND
- NOT_TESTED_AUTHORIZATION_REQUIRED

## Success Criteria

### Commercial Proof

- At least one paid pilot

### Operational Proof

- Live booking-to-outcome execution
- Reconciled appointment-status records
- No cross-customer data leakage
- Defined exception and recovery path
- Reliable measurement of eligible appointments and outcomes

### Outcome Proof

At least one of the following:

- Demonstrated reduction in preventable no-shows
- Documented recovered revenue exceeding pilot cost
- Strong leading evidence, when sample size is limited, through confirmed attendance, timely cancellations, rescheduled appointments, or recovered openings

### Replication Proof

- One evidence-backed case study
- One reusable deployment checklist
- Documented implementation time
- Documented maintenance burden
- Clearly bounded second-customer implementation path

## Test Target

The initial outcome target is a 20 percent relative reduction in preventable no-shows.

This is an internal test target and must not be represented as a guaranteed customer result.

Example:

- Baseline no-show rate: 10 percent
- Pilot no-show rate: 8 percent
- Absolute reduction: 2 percentage points
- Relative reduction: 20 percent

## Stop Rules

Pause, modify, or retire the mission if:

- No-show loss is too small to motivate payment
- Businesses cannot provide reliable booking outcomes
- Existing booking platforms already solve the problem adequately
- Integration cost exceeds realistic customer value
- Prospects consistently prioritize lead generation over appointment recovery
- The operational burden cannot support the current SyStack economics
- A credible baseline cannot be established
- The chosen segment introduces disproportionate compliance obligations
- Customer evidence contradicts the initial problem definition
- The fleet begins expanding infrastructure without evidence authorization

Rejection by one subsegment does not invalidate the broader thesis. It may indicate that another appointment category has stronger economics.

## Thirty-Day Sequence

### Days 1–5: Evidence

- Identify 25 qualified interview targets
- Conduct the first 10 interviews
- Preserve exact customer language
- Quantify missed appointments
- Quantify average appointment value
- Document reminder and recovery practices
- Identify booking platforms
- Identify integration constraints
- Rank subsegments by pain, accessibility, data quality, and willingness to pay

### Days 6–10: Offer

Only after sufficient signal:

- Select one subsegment
- Establish the baseline measurement method
- Finalize the fixed pilot scope
- Produce a concise demonstration
- Prepare pilot materials
- Define data-handling responsibilities
- Begin direct pilot acquisition

### Days 11–15: Controlled Implementation

Only after evidence authorization and pilot approval:

- Connect one supported booking source
- Configure confirmation and reminder timing
- Configure booking-response states
- Configure cancellation, rescheduling, and escalation
- Validate customer isolation
- Validate webhook protection
- Run deterministic test appointments
- Obtain approval before live activation

### Days 16–27: Live Operation

- Monitor delivery and response events
- Reconcile scheduled appointments against outcomes
- Record exceptions
- Run weekly outcome comparisons
- Prevent uncontrolled scope expansion
- Capture staff and customer feedback

### Days 28–30: Decision

- Calculate operational results
- Calculate commercial results
- Produce the case study
- Document implementation and maintenance costs
- Decide SCALE, MODIFY, CHANGE_SEGMENT, or RETIRE
- Consider lead follow-up only after this decision

## Fleet Assignments

### GREEN

- Select the initial market
- Participate in decisive customer interviews
- Approve pilot terms
- Approve production activation
- Make the final scale-or-retire decision

### SOL

- Maintain the mission board
- Sequence execution
- Enforce scope and authorization boundaries
- Coordinate live operations
- Preserve evidence and mission state

### ORACLE

- Formalize the initiative packet
- Maintain the thesis
- Design the bounded pilot
- Evaluate strategic evidence
- Recommend scale, modification, or retirement

### ATLAS

- Build the prospect set
- Prepare account context
- Organize interview evidence
- Separate researched assumptions from direct customer evidence

### CHATTY

- Draft interview outreach
- Draft interview scripts
- Prepare follow-up messaging
- Prepare pilot messaging only after evidence supports the offer
- Produce the case study after validation

### CLAUDE

- Implement only evidence-authorized pilot requirements
- Avoid general-platform expansion
- Produce complete implementation artifacts after authorization

### CODY

- Review booking-state architecture
- Review integration correctness
- Review customer-data boundaries
- Review proposed implementation changes

### VALI

- Validate infrastructure findings
- Validate technical execution
- Validate metric calculations
- Validate the business outcome
- Issue commercial validation status separately from technical status

### PESSI

- Review webhook security
- Review customer isolation
- Review failure handling
- Review maintenance burden
- Review opportunity cost
- Challenge premature scope expansion

### JURIS

- Review pilot terms
- Review consent and messaging obligations
- Review data-processing exposure
- Review regulated-data implications when applicable

### ASSEMBLY

- Prepare controlled test procedures
- Prepare production deployment procedures
- Deploy only after approval

## Binding Constraints

- No new agent
- No new general platform
- No major dashboard expansion
- No unrequested subsystem
- No auto-release implementation during evidence collection
- No smart-rebooking implementation during evidence collection
- No production activation without approval
- No customer communication without authorized messaging and execution
- No architecture expansion merely because existing components are incomplete
- No silent repairs during the read-only audit

Exception:

A missing capability may be considered only when it directly blocks a qualified live pilot and has passed the Evidence Gate.

## Decision Outputs

On or before 2026-09-01, the mission must conclude with exactly one primary decision:

- SCALE
- MODIFY
- CHANGE_SEGMENT
- RETIRE

The decision must cite customer evidence, operational evidence, commercial evidence, and opportunity cost.
