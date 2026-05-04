# ADR-001: Database Selection for Mini-Langfuse

## Status

Accepted


## Context and Problem Statement

Mini-Langfuse is a lightweight LLM tracing tool that records traces, spans, observations, and events — a time-series-ish workload where queries need joins, filters, and aggregations (p95 latency, error rates by project, etc.).

We need to choose a database. The decision is not trivial because:

- Option A (PostgreSQL) is simple and everyone knows it, but row-based storage is not ideal for analytical queries at scale.
- Option B (ClickHouse) is blazing fast for aggregations, but operationally heavy and overkill for our current volume (~10k-40k events).
- Option C (MongoDB) is flexible, but lacks native joins and makes complex aggregations painful.

We're building this to learn Python, not to become database experts — but we also don't want to lock ourselves out of scaling later.


## Decision Drivers

- **Operational simplicity** — easy to install, run locally, understand without deep specialization
- **Educational focus** — the project goal is Python learning, not extreme scale
- **Low-to-medium volume** — designed for ~10k–40k events realistically
- **Query flexibility** — we need joins, filters, aggregations (SQL-style)
- **Future Scalability** — we should not lock ourselves out of scaling later if the project grows

## Considered Options

- **Option A: PostgreSQL only** (relational database)
- **Option B: ClickHouse** (OLAP database optimized for analytics)
- **Option C: MongoDB** (NoSQL document-based database)

## Decision

**We choose Option A: PostgreSQL.**

### Why PostgreSQL?

1. **Simplicity wins.** We can run it locally with Docker. Every backend dev knows SQL and basic Postgres. No new query language or ingestion patterns to learn.

2. **Good enough for 40k events.** Postgres handles this volume easily — including joins and aggregations — while staying responsive.

3. **No premature optimization.** ClickHouse is overkill for our volume. It would add complexity (sharding, partitioning, append-only constraints) without real benefit today.

4. **Scaling path exists.** If we later grow to hundreds of thousands or millions of events, we can:
   - Add proper indexing
   - Move time-series data to ClickHouse or TimescaleDB
   - Keep Postgres for relational metadata

   The decision is reversible. We are not locked in.

5. **Joins and aggregations are native.** This matches our trace/spans data model perfectly.

### Why not the others?

**Option B (ClickHouse):**  
Too heavy for our stage. Operationally complex to tune (partitions, ordering keys, compression). Designed for billions of events, not tens of thousands. Would distract from the Python learning goal.

**Option C (MongoDB):**  
No native joins across collections. We would end up re-implementing joins in application code (N+1 queries or denormalization hacks). Aggregations are possible but less expressive than SQL. Not worth the flexibility we don't need.

# Consequences

- Good, because we can spin up a full database with one Docker command — no complex setup, no specialized knowledge required.
- Good, because every backend dev already knows SQL and Postgres basics, so anyone can understand and modify the queries without learning new concepts.
- Good, because we stay focused on the real goal (learning Python and building tracing features) instead of fighting database quirks or tuning obscure parameters.
- Bad, because Postgres stores data by rows, not columns — so if we ever reach millions of events, some analytical queries (like aggregations across large time ranges) will become noticeably slower.
- Neutral, because we need to think about schema design upfront (normalization, indexes, data types), that's extra thinking now, but it's just standard engineering practice that we'd do anyway in a relational database.



## Option A: PostgreSQL only
- Good, because every backend dev knows SQL and relational modeling — no learning curve for the team.
- Good, because we can run it locally with a single docker run postgres command.
- Good, because joins, filters, and aggregations work natively without workarounds.
- Bad, because row-based storage means analytical queries over millions of rows will eventually get slow.
- Bad, because time-series data (traces, spans) is append-heavy, and Postgres lacks built-in optimizations for it, we'd need TimescaleDB or manual partitioning later.
- Neutral, because we need to design schema upfront — that's extra work now, but it's just standard practice.

## Option B: ClickHouse

- Good, because columnar storage makes aggregations blazing fast even on billions of rows.
- Good, because it compresses data heavily (up to 5-10x less storage than Postgres).
- Bad, because it's overkill for 40k events — like using a freight train to deliver a pizza.
- Bad, because operational complexity is high: partitioning, order keys, compression tuning, Zookeeper for clusters.
- Bad, because updates and deletes are clunky (designed for append-only workloads) — our tracing data might need occasional fixes.
- Neutral, because it speaks SQL-ish, so queries wouldn't be completely foreign — but many functions and patterns are different.

## Option C: MongoDB
- Good, because schema-less design means we can evolve the data model without migrations.
- Good, because it's easy to run locally and has good Python driver support.
- Bad, because no native joins — we'd need to do N+1 queries or denormalize heavily.
- Bad, because aggregations for stats (p95 latency, error rates by project) are less expressive than SQL and harder to debug.
- Bad, because our data model (traces → spans → observations) is inherently relational — forcing it into documents creates friction.
- Neutral, because it can handle 40k events easily, but so can Postgres without the join pain.

## Revisit triggers
- When we exceed ~500k events per month — Postgres will likely still handle it, but query performance for complex aggregations across long time windows may start to degrade noticeably. That's when we benchmark and consider ClickHouse or TimescaleDB.
- When we need real-time dashboards with sub-second refresh on historical data — Postgres can do it, but columnar storage would do it better. If a business requirement demands "instant" aggregations on months of data, we revisit.
- When we face operational pain with schema migrations on a growing table — if ALTER TABLE locks become a bottleneck and zero-downtime deploys get complicated, we evaluate alternatives like Citus or moving time-series data to a separate store.
- When the project unexpectedly goes viral (good problem to have) — if we jump from 40k to 10M+ events in a short period, we pause and reassess immediately. Not because Postgres would die, but because we'd want to make a conscious choice before scaling further.

