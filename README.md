# CAS Case Study: Data Cleaning & Analysis

This repository demonstrates a complete workflow for cleaning insurance exposures data, combining historical hurricane data, and fulfilling two core **Management Requests** (1 & 2) to visualize and analyze potential hurricane risks.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Workflow Steps](#workflow-steps)
- [Scripts Explanation](#scripts-explanation)
  - [clean_exposures.py](#clean_exposurespy)
  - [hurr1_task1.py](#hurr1_task1py)
  - [hurr_task2.py](#hurr_task2py-or-hurr2)
  - [management_request_2_complete.py (Final)](#management_request_2_completepy-final)
- [How to Run](#how-to-run)
- [Results & Outputs](#results--outputs)
- [License](#license)

---

## Overview

This project addresses a **CAS Data Visualization Case Study**. Our aim is to:

1. **Clean and validate** an insurance “Exposures” dataset.
2. **Combine** two hurricane datasets (Historical Hurricane 1 & 2).
3. **Calculate** metrics such as Loss Ratio, TIV at risk, highest wind speed impacting each location, etc.
4. **Fulfill** specific Management Requests to produce charts, tables, and analysis for:
   - **Management Request 1:** Trends of Loss Ratio, TIV, Premium, Loss Cost over time.
   - **Management Request 2:** Concentration of TIV by geography, TIV at risk, top wind speeds for hurricanes that impacted the portfolio, and a final grouping of locations into probable maximum loss (PML) categories.

---

## Project Structure

A simplified layout of the repository (key files and folders):

```
CAS_Case/
├─ original_data/
│  └─ case_data.xlsx          # Original Excel file with Exposures & Hurricane sheets
├─ cleaned_data/
│  ├─ exposures_cleaned.csv   # Cleaned exposures data
│  ├─ hurr1_cleaned.csv       # Cleaned hurricane 1 data
│  ├─ hurr2_merged_with_h1_wind.csv
│  └─ ... (other output CSVs)
├─ pic/
│  └─ (Generated charts/plots saved here)
├─ clean_exposures.py         # Script to read & clean Exposures
├─ hurr1_task1.py             # Script to read & transform Historical Hurricane 1
├─ hurr_task2.py              # Script to process Historical Hurricane 2 (partial)
├─ data_validation.py         # Basic validation for each sheet
├─ management_request_2_complete.py  # Final integrated script for Mgmt Req 2
├─ requirements.txt 
└─ README.md                  # This file
```

---

## Setup & Installation

1. **Clone** this repository to your local machine:
   ```bash
   git clone https://github.com/GiveMeAjob-job/CAS_Case.git
   ```
2. **Open** the project in PyCharm (or your preferred IDE).
3. **Create** and activate a Python virtual environment (optional but recommended).
4. **Install** required libraries (e.g., `pandas`, `numpy`, `matplotlib`, `seaborn`, `openpyxl`):
   ```bash
   pip install -r requirements.txt
   ```
   or manually install them if `requirements.txt` is not provided:
   ```bash
   pip install pandas numpy matplotlib seaborn openpyxl
   ```

---

## Workflow Steps

1. **Data Validation** (`data_validation.py`): Basic removal of empty rows, duplicates, prints sample info.
2. **Clean Exposures** (`clean_exposures.py`): Reads the “Exposures” sheet from `case_data.xlsx`, fixes column names, ensures correct data types, and saves `exposures_cleaned.csv`.
3. **Hurricane 1** (`hurr1_task1.py`): Processes Historical Hurricane 1, renames columns, filters years (1985–2020), computes storm counts and maximum wind speed, finally saves `hurr1_cleaned.csv`.
4. **Hurricane 2** (`hurr_task2.py` or similar): Merges wind data from Hurr1 into Hurr2, calculates storm areas, wind speed comparisons, etc. The result is often `hurr2_merged_with_h1_wind.csv`.
5. **Management Request 1**: Typically calculates Loss Ratio, TIV, Premium, Premium per $100 TIV, and Loss Cost over time. Creates relevant charts and tables.
6. **Management Request 2**:
   - Concentration of TIV on a map (scatter plot).
   - TIV at risk (if within ±1° of hurricane paths).
   - Summaries of top wind speeds for hurricanes that impacted the portfolio.
   - A final grouping into High/Medium/Low probable maximum loss categories based on TIV, risk location, and recorded wind speed.

---

## Scripts Explanation

### clean_exposures.py

- **Goal**: Clean and standardize Exposures data from `case_data.xlsx`.
- **Main tasks**:
  - Remove empty/duplicate rows.
  - Rename columns to something consistent (e.g., `TotalInsuredValue`, `NonCatLoss`).
  - Convert data types (`float`, removing commas).
  - Save the result to `cleaned_data/exposures_cleaned.csv`.

### hurr1_task1.py

- **Goal**: Process Historical Hurricane 1.
- **Main tasks**:
  - Rename columns (removing placeholders like ` .1`, `degrees_north`, etc.).
  - Filter to 1985–2020.
  - Compute storm counts by year/type, maximum wind speeds.
  - Save the cleaned result (`hurr1_cleaned.csv`).

### hurr_task2.py (or hurr2)

- **Goal**: Process Historical Hurricane 2 data.
- **Main tasks**:
  - Potentially merges with `hurr1_cleaned.csv` wind info.
  - Calculates storm area (π × radius²).
  - Summarizes wind speed comparisons (Hurr1 vs Hurr2).
  - Saves merged data to `hurr2_merged_with_h1_wind.csv`.

### management_request_2_complete.py (Final)

- **Goal**: Integrate everything for **Management Request 2**.
- **Main tasks**:
  1. Read `exposures_cleaned.csv` + `hurr2_merged_with_h1_wind.csv`.
  2. Perform a cartesian join to see which exposures are within 1° of any hurricane’s (lat, lon) path → `is_at_risk`.
  3. Compute TIV at risk ratio.
  4. Summarize highest wind speeds actually impacting each location (`MaxWindAtLocation`).
  5. Merge that back into exposures → define PML categories (High/Medium/Low).
  6. Print or save final PML summary results.

---

## How to Run

Below is one example sequence that covers the entire pipeline:

1. **Clean Exposures**  
   ```bash
   python clean_exposures.py
   ```
   Generates `exposures_cleaned.csv`.

2. **Process Hurricane 1**  
   ```bash
   python hurr1_task1.py
   ```
   Outputs `hurr1_cleaned.csv`.

3. **Process Hurricane 2**  
   ```bash
   python hurr_task2.py
   ```
   Or there is a final integrated script that merges Hurr1 & Hurr2. This outputs `hurr2_merged_with_h1_wind.csv`.

4. **Management Request 2**  
   ```bash
   python management_request_2_complete.py
   ```
   This final script calculates at-risk TIV, impacted storms, merges location wind speeds, and groups exposures into PML categories.

In PyCharm, you can also right-click each script and select **“Run…”**. Make sure your **Working Directory** is set to the project’s root so that relative paths (e.g., `cleaned_data/filename.csv`) resolve correctly.

---

## Results & Outputs

1. **`cleaned_data/exposures_cleaned.csv`**: The fully cleaned Exposures table.  
2. **`cleaned_data/hurr1_cleaned.csv`**: The normalized Historical Hurricane 1 dataset.  
3. **`cleaned_data/hurr2_merged_with_h1_wind.csv`**: Hurr2 + integrated Hurr1 wind speeds.  
4. **`cleaned_data/exposures_risk.csv`**: Indicates which locations are within 1° of any hurricane path.  
5. **`cleaned_data/hurr_impact_summary.csv`** & `exposures_loc_storm_wind.csv`: Summaries of top wind speeds impacting the portfolio, per location/storm.  
6. **PML Summary**: A final grouping (High/Medium/Low) in `exposures_pml.csv` or similar.  
7. **Visualizations** in the `pic/` folder, such as:
   - **Concentration of TIV** (scatter plot).
   - **Loss Ratio Over Time** (line plot).
   - **Premium vs TIV** (line chart), etc.

---

## License
```
MIT License

Copyright (c) 2025 ...
Permission is hereby granted, free of charge, to any person obtaining a copy of this software...
```
---

```
