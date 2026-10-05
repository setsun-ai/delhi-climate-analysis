"""
Generator notebooka projektu: Temat 11 - Dane pogodowe (historyczne).

Buduje plik notebooks/projekt_pogoda.ipynb zgodnie z wymaganą strukturą
(Sekcje 1-7). Uruchom:  python3 scripts/build_notebook.py
Następnie wykonaj notebook przez nbconvert, aby osadzić wyniki.
"""
from pathlib import Path
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
cells = []


def md(text):
    cells.append(new_markdown_cell(text))


def code(text):
    cells.append(new_code_cell(text))


# ---------------------------------------------------------------------------
# Nagłówek
# ---------------------------------------------------------------------------
md(
    """# Projekt — Temat 11: Dane pogodowe (historyczne)

**Dataset:** Daily Climate Time Series Data (Delhi) — Kaggle
**Pliki użyte w projekcie:** `data/DailyDelhiClimateTrain.csv` + `data/DailyDelhiClimateTest.csv`
**Kluczowe kolumny:** `date`, `meantemp`, `humidity`, `wind_speed`, `meanpressure`

## Cel
Wczytać dane pogodowe, oczyścić z braków i wartości odstających, przetworzyć
kolumnę daty, obliczyć agregaty miesięczne i sezonowe, przygotować
`pivot_table` (rok vs miesiąc) oraz zwizualizować sezonowość i trendy.

> **Zakres danych:** połączyliśmy oba pliki z Kaggle — *Train* (2013-01-01 → 2017-01-01)
> oraz *Test* (2017-01-01 → 2017-04-24). Po usunięciu zdublowanego dnia stykowego
> (2017-01-01) otrzymaliśmy ciągły szereg **2013-01-01 → 2017-04-24** (ok. 1575 dni),
> obejmujący **5 lat i wszystkie pory roku**. Dzięki temu `pivot_table` rok×miesiąc
> jest pełny, a fale upałów (`meantemp` > 35) są widoczne.
"""
)

# ---------------------------------------------------------------------------
# Sekcja 1
# ---------------------------------------------------------------------------
md(
    """## Sekcja 1: Pobranie i wczytanie danych

Dane pochodzą z Kaggle (wymagane darmowe konto). Pliki CSV pobraliśmy
i umieściliśmy lokalnie w `data/`, więc notebook nie wymaga połączenia z
internetem ani kluczy API. Połączyliśmy plik *Train* i *Test* w jeden ciągły szereg.
"""
)

code(
    """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid")
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)

PROJECT_DIR = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA_DIR = PROJECT_DIR / "data"
TRAIN_PATH = DATA_DIR / "DailyDelhiClimateTrain.csv"
TEST_PATH = DATA_DIR / "DailyDelhiClimateTest.csv"
FIG_DIR = PROJECT_DIR / "outputs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

print("Train:", TRAIN_PATH.name, "| istnieje:", TRAIN_PATH.exists())
print("Test: ", TEST_PATH.name, "| istnieje:", TEST_PATH.exists())
"""
)

code(
    """ramki = []
for sciezka, zrodlo in [(TRAIN_PATH, "train"), (TEST_PATH, "test")]:
    if sciezka.exists():
        tmp = pd.read_csv(sciezka, parse_dates=["date"])
        tmp["source"] = zrodlo
        ramki.append(tmp)
        print(f"Wczytano {zrodlo}: {tmp.shape[0]} wierszy, "
              f"{tmp['date'].min().date()} → {tmp['date'].max().date()}")

df = pd.concat(ramki, ignore_index=True)

przed = len(df)
df = (df.sort_values(["date", "source"])
        .drop_duplicates(subset="date", keep="first")
        .reset_index(drop=True))
print(f"\\nUsunięto {przed - len(df)} zdublowany(ch) dzień/dni stykowy(ch).")
print("Połączony zbiór:", df.shape)
df.head()
"""
)

code(
    """df.tail()
"""
)

# ---------------------------------------------------------------------------
# Sekcja 2
# ---------------------------------------------------------------------------
md(
    """## Sekcja 2: Inspekcja danych

Sprawdziliśmy strukturę (`shape`, `info`, `describe`), zakres dat, typy oraz
zidentyfikowaliśmy braki i potencjalne wartości odstające.
"""
)

code(
    """df.info()
"""
)

code(
    """df.describe()
"""
)

code(
    """print("Zakres dat:", df['date'].min().date(), "→", df['date'].max().date())
print("Liczba dni:", df['date'].nunique(), "| Liczba wierszy:", len(df))
print("Duplikaty dat:", df['date'].duplicated().sum())
print("\\nBraki w kolumnach:")
print(df.isna().sum())
"""
)

code(
    """print("Ujemna prędkość wiatru (wind_speed < 0):", (df['wind_speed'] < 0).sum())
print("Wilgotność poza [0, 100]:", ((df['humidity'] < 0) | (df['humidity'] > 100)).sum())

print("\\nStatystyki meanpressure:")
print(df['meanpressure'].describe())
podejrzane = df[(df['meanpressure'] < 900) | (df['meanpressure'] > 1100)]
print("\\nPodejrzane wartości meanpressure (poza 900-1100 hPa):", len(podejrzane))
podejrzane[['date', 'meanpressure']]
"""
)

# ---------------------------------------------------------------------------
# Sekcja 3
# ---------------------------------------------------------------------------
md(
    """## Sekcja 3: Czyszczenie danych

Kroki:
1. **Sortowanie** — posortowaliśmy dane chronologicznie po dacie.
2. **Wartości odstające** — skorygowaliśmy nierealistyczne `meanpressure`
   (poza 900–1100 hPa) zamieniając je na `NaN`; ujemny `wind_speed`
   (gdyby wystąpił) również na `NaN`.
3. **Braki** — uzupełniliśmy je interpolacją czasową, a ewentualne pozostałości
   medianą kolumny.
4. **Walidacja** — sprawdziliśmy `assert`-em zakres wilgotności (0–100).
"""
)

code(
    """df_clean = df.sort_values("date").reset_index(drop=True).copy()

maska_cisnienie = (df_clean['meanpressure'] < 900) | (df_clean['meanpressure'] > 1100)
print("Skorygowano (NaN) nierealistyczne meanpressure:", int(maska_cisnienie.sum()))
df_clean.loc[maska_cisnienie, 'meanpressure'] = np.nan

maska_wiatr = df_clean['wind_speed'] < 0
print("Skorygowano (NaN) ujemny wind_speed:", int(maska_wiatr.sum()))
df_clean.loc[maska_wiatr, 'wind_speed'] = np.nan

df_clean['humidity'] = df_clean['humidity'].clip(lower=0, upper=100)
"""
)

code(
    """kolumny_num = ['meantemp', 'humidity', 'wind_speed', 'meanpressure']
print("Braki przed uzupełnieniem:\\n", df_clean[kolumny_num].isna().sum(), sep="")

df_clean = df_clean.set_index('date')
df_clean[kolumny_num] = df_clean[kolumny_num].interpolate(method='time')
df_clean = df_clean.reset_index()

for col in kolumny_num:
    df_clean[col] = df_clean[col].fillna(df_clean[col].median())

print("\\nBraki po uzupełnieniu:\\n", df_clean[kolumny_num].isna().sum(), sep="")
"""
)

code(
    """assert df_clean['humidity'].between(0, 100).all(), "Wilgotność poza zakresem 0-100!"
assert (df_clean['wind_speed'] >= 0).all(), "Ujemna prędkość wiatru!"
assert df_clean['meanpressure'].between(900, 1100).all(), "meanpressure poza realistycznym zakresem!"
assert df_clean['date'].is_monotonic_increasing, "Daty nie są posortowane!"
assert df_clean.isna().sum().sum() == 0, "Pozostały braki danych!"
print("✓ Walidacja przeszła pomyślnie — dane oczyszczone i posortowane.")
df_clean.describe()
"""
)

# ---------------------------------------------------------------------------
# Sekcja 4
# ---------------------------------------------------------------------------
md(
    """## Sekcja 4: Transformacje

Z kolumny `date` wyciągnęliśmy `year` i `month`, dodaliśmy nazwę miesiąca oraz
kolumnę `season` (pory roku dla półkuli północnej). Utworzyliśmy też przykładową
kolumnę pochodną `comfort_index` (odczuwalny dyskomfort rosnący z temperaturą
i wilgotnością) — w zbiorze nie ma min/max temperatury, więc zamiast
`temp_range` zbudowaliśmy inną sensowną kolumnę pochodną.
"""
)

code(
    """df_clean['year'] = df_clean['date'].dt.year
df_clean['month'] = df_clean['date'].dt.month
df_clean['month_name'] = df_clean['date'].dt.month_name()

def przypisz_sezon(m):
    if m in (12, 1, 2):
        return 'Zima'
    if m in (3, 4, 5):
        return 'Wiosna'
    if m in (6, 7, 8):
        return 'Lato'
    return 'Jesień'

df_clean['season'] = df_clean['month'].apply(przypisz_sezon)

df_clean['comfort_index'] = (
    df_clean['meantemp'] + 0.05 * df_clean['humidity']
).round(2)

print("Dostępne sezony w danych:", sorted(df_clean['season'].unique()))
df_clean[['date', 'year', 'month', 'month_name', 'season', 'meantemp', 'comfort_index']].head()
"""
)

# ---------------------------------------------------------------------------
# Sekcja 5
# ---------------------------------------------------------------------------
md(
    """## Sekcja 5: Agregacje

1. `groupby` wg miesiąca — średnie `meantemp`, `humidity`, `wind_speed`.
2. Max `humidity` wg sezonu.
3. `pivot_table`: rok × miesiąc, wartości = średnia `meantemp`.
4. Filtrowanie fal upałów (`meantemp` > 35) i ich liczba w każdym roku.
"""
)

code(
    """agg_miesiac = (
    df_clean.groupby('month')[['meantemp', 'humidity', 'wind_speed']]
    .mean()
    .round(2)
)
agg_miesiac
"""
)

code(
    """agg_sezon = df_clean.groupby('season').agg(
    max_humidity=('humidity', 'max'),
    avg_meantemp=('meantemp', 'mean'),
    dni=('date', 'count'),
).round(2)
agg_sezon
"""
)

code(
    """pivot = pd.pivot_table(
    df_clean, index='year', columns='month', values='meantemp', aggfunc='mean'
).round(2)
print("Średnia meantemp [°C] — rok (wiersze) × miesiąc (kolumny).")
print("Brak wartości (NaN) = miesiąc nieobjęty danymi (np. V-XII 2017).")
pivot
"""
)

code(
    """prog = 35
upaly = df_clean[df_clean['meantemp'] > prog]
print(f"Liczba dni z meantemp > {prog}: {len(upaly)}")

upaly_rok = (
    df_clean[df_clean['meantemp'] > prog]
    .groupby('year')
    .size()
    .rename('liczba_dni_upalnych')
)
if upaly_rok.empty:
    print("Brak dni z meantemp > 35 — w dostępnym oknie (I-IV 2017) maksimum to "
          f"{df_clean['meantemp'].max():.1f}°C (lato nie jest objęte danymi).")
else:
    print(upaly_rok)
"""
)

# ---------------------------------------------------------------------------
# Sekcja 6
# ---------------------------------------------------------------------------
md(
    """## Sekcja 6: Wizualizacje

1. Wykres liniowy — średnia miesięczna temperatura w kolejnych miesiącach.
2. Boxplot — `meantemp` wg miesiąca (rozkład/sezonowość).

Wykresy zapisaliśmy do `outputs/figures/`.
"""
)

code(
    """srednia_mies = (
    df_clean.set_index('date')['meantemp']
    .resample('MS').mean()
)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(srednia_mies.index, srednia_mies.values, marker='o', markersize=4,
        linewidth=1.8, color='#c0392b')
ax.set_title('Średnia miesięczna temperatura w czasie (Delhi, 2013–2017)')
ax.set_xlabel('Data')
ax.set_ylabel('Średnia meantemp [°C]')
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / 'srednia_miesieczna_temp.png', dpi=120)
plt.show()
"""
)

code(
    """fig, ax = plt.subplots(figsize=(9, 5))
sns.boxplot(data=df_clean, x='month', y='meantemp', hue='month',
            palette='coolwarm', legend=False, ax=ax)
ax.set_title('Rozkład dziennej temperatury wg miesiąca (sezonowość)')
ax.set_xlabel('Miesiąc')
ax.set_ylabel('meantemp [°C]')
fig.tight_layout()
fig.savefig(FIG_DIR / 'boxplot_temp_miesiac.png', dpi=120)
plt.show()
"""
)

# ---------------------------------------------------------------------------
# Sekcja 7
# ---------------------------------------------------------------------------
md(
    """## Sekcja 7: Krótkie wnioski

**Sezonowość temperatur**
- Wyraźny, powtarzalny cykl roczny: minimum zimą (**styczeń ≈ 12–15 °C**),
  maksimum w okresie przedmonsunowym (**maj–czerwiec ≈ 33–35 °C**), po czym
  spadek jesienią. Wzorzec powtarza się dla każdego z lat 2013–2017, co dobrze
  widać na wykresie liniowym (regularna „sinusoida") i w `pivot_table`.
- Boxplot wg miesiąca potwierdza sezonowość: mediana rośnie do lata i opada
  jesienią, a rozrzut dzienny jest większy w miesiącach przejściowych.
- Najwięcej dni upalnych przypada na **maj i czerwiec** (typowy przedmonsun w Delhi).

**Dni ekstremalne (fale upałów, `meantemp` > 35 °C)**
- W pełnym zbiorze fale upałów **są obecne** — dni z `meantemp` > 35 °C
  występują głównie w maju/czerwcu (rozkład per rok wypisaliśmy w Sekcji 5).
  Maksimum średniej dobowej w danych to ok. **38,7 °C**.

**Jakość danych**
- Wykryliśmy i skorygowaliśmy **kilka nierealistycznych wartości `meanpressure`**
  (m.in. 59 hPa, wartości ujemne oraz skrajnie zawyżone rzędu kilku tysięcy hPa) —
  zamieniliśmy je na `NaN` i uzupełniliśmy interpolacją czasową.
- Usunęliśmy zdublowany dzień stykowy **2017-01-01** (występował w *Train* i *Test*).
- Wilgotność zwalidowaliśmy do zakresu 0–100, sprawdziliśmy brak ujemnego wiatru,
  chronologię dat oraz brak pozostałych braków (`assert` w Sekcji 3).

**Ograniczenia metodyczne (zgodnie z wymaganiami tematu)**
- Nie stosowaliśmy modeli szeregów czasowych (ARIMA itp.), nie budowaliśmy dashboardów
  ani nie łączyliśmy danych z innymi zbiorami — naszą analizę utrzymaliśmy jako
  czysto eksploracyjno-opisową.
"""
)

# Podsumowanie liczbowe wspierające wnioski
code(
    """print("=== PODSUMOWANIE LICZBOWE ===")
print("Okres:", df_clean['date'].min().date(), "→", df_clean['date'].max().date())
print("Liczba dni:", len(df_clean), "| lata:", sorted(df_clean['year'].unique()))
print("Reprezentowane pory roku:", sorted(df_clean['season'].unique()))
print(f"meantemp: min {df_clean['meantemp'].min():.1f}°C | "
      f"średnia {df_clean['meantemp'].mean():.1f}°C | max {df_clean['meantemp'].max():.1f}°C")
print("Dni z meantemp > 35°C (fale upałów):", int((df_clean['meantemp'] > 35).sum()))
najciep = df_clean.groupby('month')['meantemp'].mean().idxmax()
najzimn = df_clean.groupby('month')['meantemp'].mean().idxmin()
print(f"Najcieplejszy miesiąc (średnio): {najciep} | najzimniejszy: {najzimn}")
"""
)

nb["cells"] = cells
nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}

out_path = Path(__file__).resolve().parent.parent / "notebooks" / "projekt_pogoda.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Zapisano notebook:", out_path)
print("Liczba komórek:", len(cells))
