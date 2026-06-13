
---

# 🔗 2. INTEGRATION TESTS PROMPT (`tests/integration`)

```text id="integration_test_prompt_v2"
Act as a senior Python QA engineer specializing in integration testing of backend systems (FastAPI / Django / service-oriented architectures).

Your task is to generate a complete pytest INTEGRATION test suite for ONLY the specified modules, focusing on real interaction between components.

---

# 🔴 SCOPE (STRICT)

You MUST generate integration tests ONLY for:

{LIST_OF_PATHS_TO_TEST}

Do NOT include any other modules.

---

# 📁 OUTPUT STRUCTURE RULE (CRITICAL)

You MUST place all generated tests under:

tests/integration/

AND fully mirror the original project structure inside it.

Example:

Source:
- app/api/v1/auth.py

Output:
- tests/integration/app/api/v1/test_auth.py

Rules:
- Preserve full directory hierarchy under tests/integration/
- Prefix test files with `test_`
- Do NOT flatten structure
- Do NOT place files outside tests/integration/

---

# 🔗 INTEGRATION TESTING RULES

1. Test interaction between components (NOT isolated functions).
2. Use real application wiring where possible.
3. Allow real database usage (test DB / sqlite if applicable).
4. Use API test clients (e.g. FastAPI TestClient) if relevant.
5. Mock ONLY external services:
   - third-party APIs
   - external HTTP calls
   - email/SMS providers
6. Do NOT mock internal modules unless strictly necessary.

---

# 🎯 COVERAGE REQUIREMENTS

- Cover full request → response lifecycle
- Include:
  - end-to-end happy paths
  - validation errors
  - authentication/authorization flows
  - DB persistence checks
  - transaction behavior
- Use pytest fixtures for:
  - test DB setup/teardown
  - API client setup
  - dependency overrides

---

# ⚠️ STRICT CONSTRAINTS

- Do NOT isolate single functions
- Do NOT over-mock internal architecture
- Do NOT skip DB or routing layers
- Do NOT leave placeholders or TODOs
- Tests must be deterministic

---

# 📦 OUTPUT FORMAT

- Only Python code
- Each file must be runnable independently
- Include fixtures or conftest usage if needed
- Use clear naming:
  test_<flow>_<scenario>

---

# 📌 CODEBASE INPUT

```python
{PASTE_CODEBASE_HERE}