# MovieLens, frame by frame

A Streamlit dashboard that turns 100,000 MovieLens ratings into four focused answers:

1. Which genres appear among the movies that were rated?
2. Which genres have the highest and lowest average ratings?
3. How does mean rating change across movie release years?
4. Which five movies lead after requiring at least 50 or 150 ratings?

The app includes a genre multiselect for the release-year trend and a 50/150 audience-floor control for the movie ranking.

## Run locally

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL printed by Streamlit, normally `http://localhost:8501`.

Run the automated checks with:

```bash
python -m pytest -q
```

## How the analysis works

- **Genre breakdown:** one movie is counted once in every pipe-separated genre assigned to it. Repeated rating rows do not inflate movie counts.
- **Genre satisfaction:** every rating event contributes to each genre assigned to its movie, so the average is weighted by ratings rather than by movies.
- **Ratings over time:** ratings are grouped by the movie's release year, not by the rating timestamp. Records without a release year are excluded and disclosed in the app.
- **Top movies:** the rating floor is inclusive (`rating_count >= floor`). Movies are ranked by their unrounded average, then rating count, then title.

## Project structure

```text
app.py                         Streamlit page and Plotly figures
analysis.py                    Validated data loading and aggregations
data/movie_ratings.csv         MovieLens source data
tests/                         Analysis and Streamlit smoke tests
.streamlit/config.toml         Dashboard theme
docs/build_log.md              Prompt and revision record
docs/superpowers/plans/        Approved implementation plan
```

## Deploy on Streamlit Community Cloud

Deployment is intentionally left to the project owner. The repository is ready for these steps:

1. Commit any final local changes and push the `main` branch to the public GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Choose **Create app**, select this repository and the `main` branch, and set the entrypoint to `app.py`.
4. Deploy without adding secrets; this project reads only the committed CSV.
5. Open the public URL and verify all four charts plus both controls.

Streamlit Community Cloud installs the pinned packages from `requirements.txt` automatically.
