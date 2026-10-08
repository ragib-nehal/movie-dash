# MovieLens Dashboard Build Log

These are working notes from the actual build, kept for the follow-up dashboard review.

## Moment 1 — Turning the assignment into a plan

**Prompt I gave**

> Let's plan a movie dashboard using Streamlit that addresses the design requirements in this document.

**What the AI produced initially**

It inspected the CSV and proposed a single-page dashboard, explicit definitions for all four questions, Plotly charts, a genre multiselect, a 50/150 rating-floor control, tests, and Streamlit deployment steps.

**What I changed, or didn't**

I chose a course-first polished finish, chart-specific controls, and the modular pandas + Plotly approach. I also kept deployment for myself, so the implementation stops at a locally verified, deployment-ready repository.

## Moment 2 — Making the analysis testable

**Prompt I gave**

> Execute the plan.

**What the AI produced initially**

The first analysis test run failed because `analysis.py` did not exist. The tests defined the required behavior first: unique-movie genre counts, rating-weighted genre means, release-year grouping, multi-genre filtering without duplicates, and inclusive ranking floors.

**What I changed, or didn't**

I kept those analytical choices. The implementation also displays the source label `unknown` as `Unknown` and uses rating count plus title as deterministic ranking tie-breakers.

## Moment 3 — Reviewing the real interface

**Prompt I gave**

> Course-first polished; single-page story; modular pandas + Plotly.

**What the AI produced initially**

The desktop browser render was clear, but the first 390-pixel-wide screenshot showed the red archive kicker partly hidden beneath Streamlit's fixed toolbar. Its measured top position was about 45 pixels.

**What I changed, or didn't**

The mobile top padding increased from `1.8rem` to `4rem`. A second browser measurement placed the kicker at 80 pixels, fully below the toolbar, while preserving the desktop layout.
