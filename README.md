# Delhi daily climate: cleaning, aggregation and seasonality analysis

**MSc coursework (independent project, topic 11).** A pandas analysis of four years of daily weather in Delhi:
- data-quality checks and outlier correction,
- time-based features,
- group-by and pivot-table aggregation,
- seasonality and heat-wave analysis.

![Monthly mean temperature](outputs/figures/srednia_miesieczna_temp.png)

## Context & motivation

Real measurement series are never clean. Sensors log impossible values, files overlap, and seasonal structure hides inside daily noise. Before any modelling, the data have to be validated, corrected in a documented way and summarised at the right time scale.

This was the final project of the *Python Language* course. It practised that workflow with pandas, plus readable, testable code:
- loading and merging files,
- validation with assertions,
- feature engineering,
- aggregation and visualisation.

## Key results

- **Merged series:** the Kaggle *train* and *test* files form one continuous series, **2013-01-01 → 2017-04-24 (1 575 days)**, after removing the duplicated boundary day.
- **Corrected pressure values:** **8 unrealistic `meanpressure` values** (e.g. 59 hPa, negative values, values in the thousands) were set to NaN and filled by time interpolation.
- **Heat waves:** **90 days** had a mean temperature above 35 °C, mostly in May–June, peaking at ≈ 38.7 °C.
- **Seasonality:** a clear, repeatable annual temperature cycle, shown in the year × month pivot table and the monthly box plots.

## Method

| Step | What was done |
|---|---|
| Load | `read_csv(parse_dates=["date"])`, train and test files merged, sorted, duplicate day removed |
| Inspect | `shape`, `info`, `describe`, date range, missing values, outliers |
| Clean | unrealistic pressure → NaN → time interpolation; `assert` checks (e.g. humidity 0–100 %) |
| Transform | `year`, `month`, `season` and a derived column |
| Aggregate | `groupby` by month and season; `pivot_table` year × month |
| Visualise | monthly mean line plot, monthly box plots |

## How to run

```bash
pip install -r requirements.txt
python scripts/build_notebook.py          # optional: regenerate the notebook from code
cd notebooks && jupyter nbconvert --to notebook --execute --inplace projekt_pogoda.ipynb
```

## Repository structure

```
data/        DailyDelhiClimateTrain.csv, DailyDelhiClimateTest.csv
notebooks/   projekt_pogoda.ipynb (main notebook, sections 1–7 with outputs, Polish)
outputs/     figures
scripts/     build_notebook.py (regenerates the notebook from code)
```

## Data

[Daily Climate Time Series Data](https://www.kaggle.com/datasets/sumanthvrao/daily-climate-time-series-data) (Kaggle, CC0 Public Domain), included in `data/`.

## Scope

- **Set by the course:** the topic (historical weather data), the dataset and the required techniques:
  - loading with date parsing,
  - inspection,
  - cleaning with validation,
  - transformations,
  - `groupby` and `pivot_table`,
  - a heat-wave filter and two plots.
- **My decisions:**
  - merging train and test into one series,
  - how to detect and correct the pressure outliers,
  - the season definition,
  - generating the notebook from a script for reproducibility.

## AI usage

AI-assisted development was used for implementation and documentation. Method choice, validation strategy, data-handling decisions, result verification and interpretation were reviewed and owned by me.

## License

Code: MIT (see [LICENSE](LICENSE)). Data: CC0 (see *Data*).

---

## 🇵🇱 Opis po polsku

Samodzielny projekt zaliczeniowy z przedmiotu *Język Python* (temat 11; kierunek InfoBioChem, studia II stopnia, Politechnika Gdańska, 2026). To analiza historycznych danych pogodowych Delhi:
- połączenie plików z Kaggle,
- korekta 8 błędnych wartości ciśnienia z interpolacją,
- asserty walidacyjne,
- kolumny pochodne (rok, miesiąc, pora roku),
- `groupby` i `pivot_table`,
- fale upałów (90 dni > 35 °C) i wykresy sezonowości.

Notebook z wynikami: `notebooks/projekt_pogoda.ipynb`.

**Wsparcie AI:** kod i dokumentacja powstały z pomocą narzędzi AI. Wybór metod, decyzje dotyczące danych, weryfikacja i interpretacja wyników należały do mnie.
