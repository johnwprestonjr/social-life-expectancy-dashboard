# Social Conditions & Life Expectancy Explorer

This Streamlit dashboard explores how social and economic conditions relate to life expectancy and health outcomes across U.S. counties.

## Files

- `app.py` — Streamlit app
- `dashboard_data.csv` — cleaned county-level dataset for dashboard visuals
- `race_life_expectancy_long.csv` — race-specific life expectancy data in long format
- `requirements.txt` — packages needed for deployment

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `dashboard_data.csv`, `race_life_expectancy_long.csv`, and `requirements.txt`.
3. Go to Streamlit Community Cloud.
4. Select the repository and choose `app.py` as the main file.
5. Deploy and copy the dashboard link for submission.

## Dashboard interactions

- Sidebar filters for region and state.
- Dropdown to switch the social determinant used in the poor health scatterplot.
- Brush interaction in the child poverty scatterplot updates a regional summary chart.
- Brush interaction in the state chart updates the race comparison chart.
- Tooltips provide county, state, region, and health outcome details.
