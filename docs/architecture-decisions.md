# Architecture Decisions

## ADR-001 UUID

We use UUID primary keys for all core entities.

Reasoning:
- They are safe for distributed creation without coordination.
- They avoid predictable sequential identifiers.
- They align with future horizontal scaling and external integration.

## ADR-002 KnowledgeSource separado

Knowledge sources are modeled as a separate table instead of embedding them in Tutor.

Reasoning:
- A tutor can have multiple sources with independent lifecycle.
- Source configuration is heterogeneous and grows better as a separate row.
- Separation keeps Tutor focused on prompt and execution metadata.

## ADR-003 Provider desacoplado

Provider details are represented as data through `provider_type` and `configuration`, not as application logic in persistence.

Reasoning:
- The persistence layer should not know provider implementation details.
- This keeps the domain stable when integrations change.
- It allows future provider implementations without schema redesign.

## ADR-004 Estratégia sem banco vetorial

The first version does not introduce a vector database.

Reasoning:
- Sprint 1.3 is about persistence and application structure, not retrieval infrastructure.
- It avoids premature coupling to a search or embedding strategy.
- This keeps the architecture simpler until a real retrieval requirement exists.

## ADR-005 Knowledge Layer isolada

The knowledge layer is modeled as its own package, separate from services, repositories and persistence models.

Reasoning:
- It keeps provider-specific concerns outside the application core.
- It makes new providers additive instead of invasive.
- It gives the future agent a stable contract through `KnowledgeProvider` and `KnowledgeResult`.

## ADR-006 Factory por enum

Provider instantiation is handled by a direct enum-to-class factory mapping.

Reasoning:
- It keeps construction explicit and readable.
- It avoids reflection and dynamic imports.
- It makes provider registration a single, predictable extension point.

## ADR-007 Erros tipados

The layer uses specific exceptions for provider lookup, unimplemented providers and invalid sources.

Reasoning:
- Callers can handle errors deterministically.
- It avoids leaking generic exceptions across the application.
- It makes failure modes clearer for future orchestration logic.

## ADR-008 HTTP como MVP

The first implementation uses HTTP clients directly for URL and JSON sources.

Reasoning:
- It is enough for the current sprint objective.
- It avoids overengineering parser and cache layers.
- It leaves the contract intact for later integration with Tavily or other sources.

## ADR-009 KnowledgeTool como orquestrador

The knowledge layer is consumed through a tool that maps a `KnowledgeSource` to the appropriate provider and normalizes the result.

Reasoning:
- It keeps the future agent decoupled from provider selection logic.
- It concentrates error handling and logging in one orchestration point.
- It enables bulk retrieval with partial failure tolerance.

## ADR-010 TutorAgent desacoplado do LLM

The agent orchestrates knowledge retrieval, prompt building and LLM generation through injected abstractions.

Reasoning:
- It keeps the agent independent from any specific LLM vendor.
- It makes testing possible with simple stubs or fakes.
- It leaves room for future tool calling and LangGraph adoption without rewriting the core flow.

## ADR-011 LangChain como cliente infraestrutural

The platform uses a thin LangChain-backed LLM client instead of exposing LangChain directly to higher layers.

Reasoning:
- It keeps the current application shape stable if the LLM backend changes later.
- It prevents the rest of the codebase from depending on LangChain message types.
- It makes the LLM boundary easy to stub in tests.

## ADR-012 .env carregado no bootstrap

The application loads the root `.env` file during configuration bootstrap so third-party libraries can read the same values as Pydantic Settings.

Reasoning:
- It mirrors the reference project pattern.
- It allows LangChain and LangSmith to observe tracing and API variables without duplicate wiring.
- It keeps environment handling centralized in one place.

## ADR-013 Chat persistence separada

Conversation and Message are modeled as first-class persistence entities.

Reasoning:
- It allows persistent chat history without coupling to the Agent.
- It gives the application a stable history substrate for future prompt assembly.
- It keeps conversation lifecycle independent from knowledge retrieval.

## ADR-014 ChatService como coordenador

ChatService coordinates tutor lookup, conversation lookup/creation and message persistence, but does not generate responses.

Reasoning:
- It preserves a clean boundary between persistence orchestration and response generation.
- It prepares the next sprint where TutorAgent will be invoked with history.
- It keeps the service reusable even if the response generation strategy changes.