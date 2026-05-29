# ADR-004: Decorator Uses a Default Tracer with Optional Injection

## Status

Accepted

## Context and Problem Statement
ADR-003 established that the @trace decorator uses an intermediate Tracer (not direct HTTP). However, that decision left a follow-up open: how does the decorator actually access the Tracer instance?

We now need to resolve that follow-up.

The decision is not trivial because:

A global singleton is simple but makes testing failures hard (requires monkeypatch)

Mandatory dependency injection makes the common case (@trace) too verbose

We are early in the project (~1.5 features), so refactoring is still cheap

## Decision Drivers
Testability — We must be able to inject fakes or broken tracers in tests without touching globals or monkeypatching.

Simplicity of use — The common case (@trace) must remain trivial, no boilerplate.

Cost of change — We are early (1.5 features). Refactoring is cheap now and becomes progressively more expensive as the surface area of the SDK grows.

## Considered Options
### Option A: Singleton global (what we had)
The decorator always uses a default_tracer from a global module variable. Simple, no extra parameters.

- **Good, because** the decorator has zero arguments. @trace just works.

- **Bad, because** testing failure scenarios (e.g., network error, broken tracer) requires monkeypatching the global — brittle and leaks between tests.

- **Bad, because** concurrent tests cannot use different tracers.

### Option B: Mandatory dependency injection
The decorator requires a tracer parameter: @trace(tracer=my_tracer).

- **Good, because** fully explicit. No magic. Tests can inject anything easily.

- **Bad, because** the common case becomes verbose: `@trace(tracer=default_tracer)` everywhere.

- **Bad, because** every user needs to know what a tracer is, even for "just trace this function".

### Option C: Hybrid — default + injectable
The decorator uses a default tracer when called without arguments, but accepts an explicit tracer parameter when needed.

- **Good, because** the common case (@trace) stays trivial.

- **Good, because** tests can inject fakes or failing tracers directly, no monkeypatch.

- **Good, because** advanced users (multi-tenant, custom backends) can inject their own tracers.

- **Bad, because** implementation requires a decorator with optional keyword-only arguments and `functools.partial`, which is a less common pattern that future maintainers will need to understand.

- **Bad, because** the signature now supports three calling patterns: `@trace`, `@trace(tracer=...)`, and direct call.

- **Neutral, because** end users almost never need injection. It's primarily for tests and advanced scenarios.

## Decision Outcome
Chosen option: Option C — Hybrid (default tracer + injectable).

## Why:

Testability is a hard requirement. We need to test what happens when the tracer fails (F1.3, and future features). Option A makes that painful (monkeypatch). Option B fixes testability but ruins the simple case.

The hybrid approach gives us both: simple default for real code, explicit injection for tests.

We are early enough (1.5 features) that the extra implementation complexity is acceptable. Doing this later would require a breaking change.

## Consequences
- **Good, because** tests can inject `BrokenTracer`, `FakeTracer`, or `SlowTracer` directly. No monkeypatch, no test pollution.

- **Good, because** the common case (`@trace`) remains a one-liner. Users don't need to know what a tracer is.

- **Good, because** future features (multi-tenancy F2.7, custom exporters) can use injection without changing the decorator.

- **Bad, because** the implementation is more complex — we need a double-layer decorator with `functools.partial` or a factory function. Three calling patterns to support.

- **Bad, because** there's now "magic" (a global default). Some developers prefer full explicitness.

- **Neutral, because** the end user SDK almost never uses injection. It's there for tests and advanced cases. Most users will write `@trace` and never know about the hybrid design.

## Revisit Triggers
When the partial-based implementation feels confusing or fragile — if we find ourselves explaining it too often, we reconsider a simpler design (a Tracer.configure() global setup instead).

When we need global configuration (e.g., langfuse.configure(tracer=...)) — the hybrid default could become part of a larger configuration system. That's fine, but we should revisit if the default tracer becomes stateful in problematic ways.

If we switch to an async-only architecture — the hybrid approach still works, but the implementation details (e.g., contextvars for default tracer) might need revisiting.