# Project Conventions

## Structure
- Keep data loading and pure aggregations in `analysis.py`; keep Streamlit and Plotly presentation in `app.py`.
- Use `data/movie_ratings.csv` as the source. Do not mutate source data in place.
- Reuse named theme tokens for page CSS and charts; light and dark modes must stay behaviorally identical.

## Analytics
- Genre distribution counts each movie once per listed genre.
- Genre satisfaction is weighted by rating events.
- Trends use movie release year, exclude missing years, and OR-match selected genres without duplicating ratings.
- Rating floors are inclusive; break ranking ties by rating count, then title.
- Reject malformed, non-finite, or out-of-range numeric input at the loading boundary.

## Quality
- Use TDD for behavior changes and run `.venv/bin/python -m pytest -q` before completion.
- Verify UI changes in both desktop and narrow browser viewports.
- Keep controls local to the chart they affect and preserve accessible contrast/focus states.
- Do not push or deploy unless the user explicitly asks.

## Avoid Repeats
- `AppTest.from_file()` resolves relative paths from the test file; pass an absolute app path.
- Never explode selected genres before trend aggregation; that double-counts multi-genre movies.
- Leave enough mobile top padding for Streamlit's fixed toolbar.
