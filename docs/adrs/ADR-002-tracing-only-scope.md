# ADR-0002: Scope is tracing only, no full observability platform

## Status

Acepted

## Considered Options

* Option A: Tracing only 
* Option B: Tracing + Prompt Management 
* Option C: Full Langfuse clone 


## Decision Drivers

- **Learn Python fundamentals** - The main goal is Python mastery. Every extra feature is time not spent writing Python.

- **Working demo early** - We need a functional tracer we can actually use. Prompts and evals can come later.

- **Complexity budget** - Each feature adds tables, API endpoints, and edge cases. Start small, do one thing well.

- **Iterate incrementally** - We can add prompts and evals in ADR-003 and ADR-004. No need to build everything now.

## Decision Outcome

**Chosen option: Option A: Tracing only**, because it's the smallest useful thing we can build. It will actually help debug LLM calls. Prompts and evals are "nice to have", we build them only if we miss them.

## Consequences

- **Good, because** we can focus all our energy on making tracing rock solid — proper spans, accurate durations, clean filtering, reliable storage. One thing done well beats three things done halfway.

- **Good, because** the project is actually finishable in 6-8 weeks. A full Langfuse clone would take months and risk burnout or abandonment. This scope keeps momentum.

- **Good, because** Mini-Langfuse will be genuinely better at tracing than a half-baked full platform. Users who need tracing (the core use case) get a great tool, not a mediocre all-in-one.

- **Bad, because** some potential users might want prompt management or evals out of the box. They'll look at our tool, see missing features, and choose Langfuse instead.

- **Bad, because** without prompt management, we can't easily answer "which prompt version caused this trace?" that's a legitimate debugging question that will require manual workarounds.

- **Neutral, because** we're leaving value on the table today, but we're also leaving room to grow tomorrow. Adding prompts and evals later will be easier once the tracing foundation is stable.


## Pros and Cons of the Options

## Option A: Tracing only
- Good, because we can focus entirely on making tracing rock solid — accurate durations, clean spans, reliable storage. One thing done well beats three things done halfway.

- Good, because the project is actually finishable in 6-8 weeks. A full clone would take months and risk abandonment.

- Good, because the codebase stays small and focused, which is perfect for learning Python without distractions.

- Bad, because some users might want prompt management or evals out of the box — they'll see missing features and choose Langfuse instead.

- Bad, because we miss hands-on exposure to evals — a fast-growing area in LLM observability that would deepen our understanding of the full Langfuse stack.

- Neutral, because we're leaving value on the table today, but leaving room to grow tomorrow. Adding features later is easier once the foundation is solid.

## Option B: Tracing + Prompt Management

- Good, because prompt management adds immediate value, you can see exactly which prompt version caused a given trace without manual bookkeeping.

- Good, because two patas make the tool more competitive against Langfuse for real-world use.

- Good, because it demonstrates versioning and template handling skills, which are relevant for backend engineering.

- Bad, because it roughly doubles the scope, more tables, more API endpoints, more edge cases to handle.

- Bad, because prompt management is a rabbit hole (versioning, variable injection, diffs, rollbacks). We could easily spend 4 extra weeks just on prompts.

- Bad, because it delays our core goal (learning Python fundamentals) by adding non-essential complexity.

- Neutral, because we could build prompts after tracing is done, it doesn't have to be now or never. But the temptation to do it "properly" might slow us down.

## Option C: Full Langfuse clone (all 3 patas)
- Good, because the finished product would be genuinely useful and competitive with Langfuse for small projects.

- Good, because demonstrates breadth across all three areas of LLM observability (tracing, prompt management, evals) — strong technical signal.

- Good, because it's the most complete learning experience (though also the most painful).

- Bad, because it's a massive scope. Realistically, this could take 3-6 months, not weeks. High risk of never finishing.

- Bad, because doing three things mediocre is worse than doing one thing well. A full clone with weak tracing, basic prompts, and shallow evals helps no one.

- Bad, because the cognitive load is enormous — we'd be learning Python + building a complex distributed-like system + managing three feature areas simultaneously.

- Bad, because we'd likely cut corners on testing, documentation, and code quality just to "finish" — defeating the learning goal.

- Neutral, because we could start with tracing and add prompts/evals incrementally. The option isn't "never build them" — it's "not now".

## Revisit Triggers
- When we have real users asking for prompts or evals — right now we have zero users. But if we open-source this or share it with friends/colleagues, and multiple people request the same feature, that's a signal to reconsider.

- When our own frustration debugging becomes painful — if we find ourselves manually copying prompts into traces, or manually scoring responses without structure, and it hurts enough to interrupt flow, that's a trigger to add the missing feature.

- When tracing is rock solid and we're bored — after 6-8 weeks, if tracing works perfectly, tests pass, documentation is clean, and we still have energy and motivation, we can add the next feature without risk.

- When the AI Engineering market shifts — if in 6-12 months, prompt management or evals become table stakes for any LLM tool (not just "nice to have"), we revisit to stay relevant.


