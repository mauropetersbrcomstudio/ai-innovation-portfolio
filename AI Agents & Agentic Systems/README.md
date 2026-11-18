# AI Agents & Agentic Systems

This category contains demonstrators for agents that plan bounded tasks, use explicitly defined tools, and return traceable outputs.

## Initial demonstration specification: SME Operations Assistant
**Goal:** classify an incoming operational request, select from a small allowlisted set of actions, and produce an auditable action plan.

**Safety boundaries:** no external side effects in the baseline demo; tool calls are simulated; inputs are treated as untrusted; uncertain requests are escalated rather than guessed.

**Acceptance checks:** valid request classification, rejection of unknown actions, structured output, and traceable execution steps.

**Status:** DEMO specification documented; executable implementation pending.
