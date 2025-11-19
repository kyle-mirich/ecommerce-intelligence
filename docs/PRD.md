# Metadata Vision Agent System (MVAS)

A LangChain / LangGraph Agentic System for Product Metadata Extraction

---

## 1. Problem

Product metadata is often inconsistent, incomplete, and unreliable. Teams spend time manually verifying product attributes across images, webpages, and inconsistent data feeds. This results in poor search performance, messy catalogs, and slow onboarding.

MVAS solves this by using a fully agentic, LangChain-powered pipeline to autonomously extract, validate, and structure metadata from product inputs.

---

## 2. Goal

Build an autonomous multi-agent system using LangChain and LangGraph that can:

* Accept product images, URLs, or copied text
* Extract metadata automatically
* Validate it using a critic agent
* Produce stable structured output (JSON)
* Minimize human intervention

---

## 3. System Overview

MVAS uses a LangGraph agent created with `create_agent`. The agent runs a ReAct loop, calling tools and reasoning step by step until it reaches a validated final answer.

**Core behaviors:**

* Model node performs reasoning
* Tools node handles extraction actions
* Critic middleware verifies correctness
* Graph runtime ensures iteration until completion

---

## 4. Tools

**HTML Scraper**
Extracts visible text and metadata from product pages.

**Vision Extractor**
LLM vision tool for reading labels, colors, and visual product cues.

**Schema Validator**
Ensures that attributes fit a defined schema.

**Cleaner Tool**
Normalizes malformed data (sizes, colors, materials).

---

## 5. Agent Flow

1. User provides input (image or URL).
2. Agent analyzes input through the model node.
3. Agent decides which tool to use.
4. Tools return observations.
5. Critic checks for hallucinations, missing fields, or inconsistencies.
6. Agent retries or fixes values.
7. Final structured output JSON is returned.

---

## 6. Output Format

Final output must be strict JSON with fields like:

* title
* brand
* category
* color
* material
* dimensions
* description

This uses LangChain Structured Output via ToolStrategy or ProviderStrategy.

---

## 7. Success Metrics

* Reduced Human Intervention Rate (HIR)
* High attribute accuracy
* Repeatable deterministic outputs
* Fast processing time

---

## 8. Future Extensions

* Multi-image fusion
* Competitor comparison
* Price extraction and validation
* Integration with commerce knowledge graphs
