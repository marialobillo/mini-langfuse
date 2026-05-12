# ADR-003: How the decorator delivers traces to the backend

## Status

Accepted


## Context and Problem Statement

The `@trace` decorator captures data on every function invocation, including name, input, output, latency, and errors. This captured data must eventually reach the backend; that's the entire purpose of Mini-Langfuse.

However, the decorator itself should not know the details of how data is transported. Knowing the transport would violate the Single Responsibility Principle (SRP) and would make it impossible to change the transport mechanism, from HTTP to Kafka, to async batching, to multi-backend — without modifying the decorator itself.

The decision is not trivial because it directly affects:

- **Testability of the decorator**: if the wrapper speaks HTTP directly, every test needs to mock network calls.
- **Evolvability**: requirements like HTTP transport (F1.4), async batching (F1.8), and multi-tenancy (F2.7) will all live in or interact with this layer.
- **Architectural clarity**: future readers of the SDK need to understand where capture ends and transport begins.

We need to decide how to connect capture (the decorator) with delivery (the backend): what middleware sits in between, what each piece is responsible for, and how they couple to each other.

## Decision Drivers

- **Simple by default** — HTTP to a local endpoint should work out of the box. Complex transports are opt-in, not forced on everyone.

- **Testability** — The decorator must be testable without network calls or framework-level mocking. Simple in-memory test doubles are fine.

- **Separation of concerns** — Decorator captures; something else delivers. The decorator should never know about HTTP, Kafka, or batching.

- **Evolvability** — We will add async batching (F1.8) and multi-tenancy (F2.7) later. The design should support these without refactoring the decorator.


## Considered Options

### Option A: Direct HTTP from the decorator

The decorator builds the trace and calls an HTTP client inline within the wrapper. The wrapper knows the backend URL, handles failures, and is the sole owner of delivery.

**Trade-off:** Simplest to implement but couples capture to transport. Tests require HTTP mocks. Future async batching (F1.8) cannot be added without modifying every decorated function.

### Option B: Transport injected into the decorator

The decorator accepts a `transport` parameter (e.g., `@trace(transport=HTTPTransport())`). The wrapper holds a reference to the transport and calls it after capturing data. Transport is pluggable, but no intermediate layer exists.

**Trade-off:** Transport becomes swappable, which improves testability and evolvability for the decorator. But cross-cutting concerns like batching, sampling, and multi-tenancy still have no home — they would either leak into the decorator's parameters or be duplicated in every transport implementation.


### Option C: Tracer between decorator and transport

The decorator hands the captured data to a `Tracer` instance. The Tracer owns batching, sampling, multi-tenancy, and finally calls a `Transport` to deliver. The decorator knows nothing about HTTP, batching, or backends.

**Trade-off:** Maximum separation and evolvability, at the cost of one extra abstraction. Three pieces (decorator, tracer, transport) instead of one or two, but each has a clear responsibility.

## Decision Outcome

**Chosen option: Option C: Tracer between decorator and transport**, because it is the only option where the decorator truly knows nothing about delivery. The decorator hands data to a tracer and walks away.

For the MVP, the Tracer is the simplest possible implementation — an in-memory list of captured traces. HTTP delivery (F1.4) and async batching (F1.8) will be added later by composing transports into the Tracer, without touching the decorator.

Whether the Tracer is accessed as a module-level singleton or explicitly injected into the decorator is left for a separate ADR.

## Consequences

- **Good, because** the decorator becomes completely ignorant of delivery: it captures 
  data, builds a trace record, and hands it to the tracer. No HTTP, no batching, 
  no backends. Pure SRP.

- **Good, because** unit testing the decorator no longer requires mocks or network calls. 
  We can pass a fake tracer and assert that `capture()` was called with the right data.

- **Good, because** future requirements like batching (F1.8), sampling, retries, and 
  multi-tenancy (F2.7) have a natural home inside the tracer. They don't leak into 
  the decorator.

- **Bad, because** the design introduces an extra abstraction. Three pieces (decorator, 
  tracer, transport) where one or two would suffice for the simplest use case. 
  The learning curve is steeper for newcomers reading the SDK.

- **Neutral, because** the tracer adds indirection, but that indirection is exactly what 
  makes the design evolvable. We pay a small complexity tax now to avoid a much larger 
  refactor later.
  
## Follow-up ADRs

- How the Tracer instance is accessed by the decorator (singleton vs DI).
- Sync vs async capture call from decorator to tracer.
- Where the TraceRecord schema is constructed (decorator builds, or tracer builds).