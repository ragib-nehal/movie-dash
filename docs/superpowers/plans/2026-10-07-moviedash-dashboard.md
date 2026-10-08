# MovieDash Streamlit Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and locally verify a polished, single-page Streamlit dashboard that answers all four required MovieDash questions.

**Architecture:** Keep statistical transformations in a small, pure `analysis.py` module and presentation in `app.py`. Use pandas for aggregation, Plotly Express for charts, Streamlit for the interface, and pytest for behavior-focused verification.

**Tech Stack:** Python 3, pandas, Plotly Express, Streamlit, pytest

**Spec:** Approved in chat on 2026-10-07; deployment is explicitly excluded from implementation.

## Global Constraints

- Work in the current `main` checkout with the user's explicit approval.
- Use `data/movie_ratings.csv` as the only data source.
- Keep the four required answers visible in their default states.
- Controls are chart-specific: genre selection affects only the release-year trend; the 50/150 floor affects only movie rankings.
- Do not add the later notebook-style audit or report to the app.
- Prepare deployment instructions, but do not push or deploy.

## Review Focus

- Multi-genre movies must count once per genre without inflating unique-movie counts.
- Selecting several genres for the trend must not duplicate ratings for films matching more than one selection.
- Missing release years must be excluded and disclosed rather than converted to a bogus year.
- The rating floor is inclusive, and ranking tie-breaks are deterministic.
- Missing or malformed input must produce a useful on-page error rather than a traceback-only experience.

---

### Task 1: Analysis layer

**Files:** `tests/test_analysis.py`, `analysis.py`

**Interfaces:**
- Produces `load_ratings`, `genre_distribution`, `genre_satisfaction`, `release_year_trend`, and `top_movies`.
- Each aggregation returns a DataFrame with stable, documented output columns for the Streamlit layer.

- [ ] Write synthetic-fixture tests for validation, multi-genre behavior, weighted means, missing years, genre filtering, inclusive floors, and deterministic sorting.
- [ ] Run the tests and confirm they fail because `analysis.py` does not exist.
- [ ] Implement the smallest analysis module that satisfies the tests.
- [ ] Run the complete test suite and commit the analysis task.

### Task 2: Streamlit dashboard

**Files:** `tests/test_app.py`, `app.py`, `.streamlit/config.toml`

**Interfaces:**
- Consumes the Task 1 aggregation functions and their stable DataFrame schemas.
- Produces the four-section Streamlit page and two isolated interactive controls.

- [ ] Write an AppTest smoke test for the real dataset, required headings, widgets, and error-free initial render.
- [ ] Run the test and confirm it fails because the app does not exist.
- [ ] Implement the single-page dashboard and Plotly visualizations.
- [ ] Add the approved film-catalog visual system and responsive CSS.
- [ ] Run the complete test suite and commit the dashboard task.

### Task 3: Project packaging and documentation

**Files:** `requirements.txt`, `.gitignore`, `README.md`, `docs/build_log.md`

**Interfaces:**
- Documents local setup, analytical definitions, project structure, and user-owned deployment steps.

- [ ] Add reproducible runtime/test dependencies and ignore generated files.
- [ ] Write local run and Streamlit Community Cloud handoff instructions.
- [ ] Record 2–3 genuine prompt/result/revision moments from this implementation.
- [ ] Run all tests and a local headless Streamlit health check, then commit the documentation task.

### Task 4: Final verification and review

- [ ] Verify the real-data top-five results at floors 50 and 150.
- [ ] Run the full pytest suite, compile check, and headless Streamlit smoke check.
- [ ] Inspect the rendered dashboard at desktop and narrow viewport widths.
- [ ] Run a fresh whole-branch review and address Critical or Important findings through RED→GREEN tests.
- [ ] Leave the repository ready for the user to commit/push/deploy, without performing deployment.

## Acceptance Criteria

- All four assignment questions are visibly answered.
- The genre multiselect and 50/150 floor control work and affect only their intended charts.
- The floor-50 results begin with *A Close Shave*, *Schindler's List*, and *The Wrong Trousers*.
- The floor-150 results begin with *Schindler's List*, *Casablanca*, and *The Shawshank Redemption*.
- Tests and a headless Streamlit launch pass locally.
- README deployment instructions require no additional code changes.
