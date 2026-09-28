# India EV Charging Infrastructure Analytics — Generative AI-Assisted

An end-to-end **business analytics project** designed to understand the distribution and concentration of EV charging infrastructure across India using **Python, MySQL, and an interactive HTML dashboard**.


> **Generative AI-Assisted Project:** Generative AI was used as a development and analytical assistant for data-validation logic, SQL development/debugging, dashboard implementation, documentation, and iterative problem solving. Final datasets, SQL outputs, and business findings were validated against the underlying data.


## Business Problem

As EV adoption grows, charging infrastructure providers need to understand **where charging infrastructure is concentrated, which cities and states have stronger coverage, and where geographic gaps or concentration patterns may exist**.

A charging-network operator, EV mobility company, infrastructure investor, or market-entry team can use this analysis to answer questions such as:

- Which states have the largest charging-infrastructure footprint?
- Which cities act as major charging hubs?
- Is infrastructure broadly distributed across a state, or concentrated in a few cities?
- Which states have wide city-level coverage but relatively low station counts?
- Which locations contain unusually high numbers of station records?
- Where should deeper market research be performed before expanding the network?
- How geographically concentrated is the current charging infrastructure?

The project converts raw charging-station records into a **decision-support dataset and interactive analytical dashboard** that can be used for geographic benchmarking and infrastructure planning.

> **Important:** The current dataset describes charging infrastructure and locations. It does not contain customer activity, charging sessions, revenue, or retention data, so it supports infrastructure analysis rather than customer-churn analysis.

## Project Objective

The main objective is to **analyze India's EV charging-infrastructure landscape and identify geographic concentration, coverage patterns, and potential areas for further market investigation**.

### Analytical objectives

1. Measure charging-infrastructure coverage across states and cities.
2. Identify the states and cities with the highest concentration of station records.
3. Compare **depth of infrastructure** (station count) with **breadth of coverage** (number of cities).
4. Identify repeated station/site names and geographic clusters that require business interpretation.
5. Build an interactive dashboard that allows users to drill from **India → State → City → Station**.
6. Create a clean analytical foundation that can later be combined with EV registrations, population, highway traffic, utilization, or customer-session data.

## Business Questions

The project focuses on practical questions that a business or strategy team could ask:

### Market coverage
- How large is the current charging-station footprint?
- Which states have the strongest infrastructure presence?
- Which states have the widest city coverage?

### Market concentration
- What percentage of charging infrastructure is concentrated in the top five states?
- Which cities are the largest charging hubs?
- Are some states dependent on a small number of high-volume cities?

### Expansion planning
- Which states have many covered cities but relatively few station records?
- Which cities show strong infrastructure density within the dataset?
- Which geographic areas should be investigated further for potential infrastructure expansion?

### Data-driven decision support
- Which station-name values appear in multiple locations?
- Where do multiple station records share the same coordinates?
- Is the dataset reliable enough for downstream BI and geospatial analysis?

## Why This Project Matters

The value of the project is not simply counting charging stations. The analysis helps transform location-level infrastructure data into **business insights about market concentration and geographic coverage**.

For example:

```text
Charging-station data
        ↓
State / city coverage analysis
        ↓
Infrastructure concentration analysis
        ↓
Geographic comparison
        ↓
Market-expansion questions
        ↓
Decision-support dashboard
```

## How Generative AI Was Used

Generative AI was integrated into the project as a **co-pilot for analytics development**, while the underlying data and final analytical decisions remained data-driven and were validated independently.

### AI-assisted activities

- **Problem framing:** helped structure the EV infrastructure business problem and convert it into measurable analytical questions.
- **Data preparation:** assisted in developing and refining Python cleaning and validation logic for inconsistent state-city records, duplicates, and coordinate checks.
- **SQL analysis:** assisted with generating, debugging, and improving MySQL queries, including aggregations, CTEs, `HAVING`, `COUNT(DISTINCT)`, and window functions.
- **Dashboard development:** assisted with the HTML/CSS/JavaScript implementation of interactive KPIs, charts, filters, mapping, search, pagination, and CSV export.
- **Documentation:** assisted with the project report, README, business interpretation, and portfolio presentation.
- **Quality validation:** final outputs were checked against the underlying dataset rather than accepted solely from AI-generated output.

### AI workflow

```text
Business problem
      ↓
Generative AI-assisted planning
      ↓
Python data preparation
      ↓
Manual / data-based validation
      ↓
MySQL analysis
      ↓
AI-assisted query development & debugging
      ↓
Validated analytical findings
      ↓
AI-assisted dashboard implementation
      ↓
Final portfolio deliverables
```

The project should therefore be described as **Generative AI-assisted analytics**, not as an AI/ML prediction model.

## Supporting Data Preparation & Cleaning

```text
Raw EV charging data
        |
        v
Text normalization
        |
        v
State / city consistency checks
        |
        v
Address + geographic validation
        |
        v
Latitude / longitude validation
        |
        v
Duplicate / duplicate-like detection
        |
        v
Remove unresolved records
        |
        v
Final consistent master dataset
        |
        +------------------+
        |                  |
        v                  v
      MySQL            Dashboard
```

### Major cleaning steps

- Standardized text casing, whitespace, and geographic labels.
- Corrected high-confidence state-city mismatches using station name, address, and geographic evidence.
- Example: **Royal Global University -> Guwahati -> Assam**.
- Removed exact duplicates.
- Removed duplicate-like records after geographic corrections.
- Removed unresolved records where a reliable mapping could not be established.
- Validated latitude and longitude.
- Checked that no city maps to multiple states in the final dataset.
- Maintained a separate correction audit file.

## Technology Stack

| Area | Technology |
|---|---|
| Data cleaning | Python, Pandas, NumPy |
| Database analysis | MySQL 8.0+ |
| Visualization | Plotly |
| Dashboard | HTML, CSS, JavaScript |
| Generative AI | AI-assisted development, debugging, analytical structuring, documentation |
| Documentation | Microsoft Word, Markdown |
| Version control | Git / GitHub |

## SQL Analysis

The MySQL query file contains data-quality, geographic, concentration, station-name, and location-cluster analysis.

### Main SQL questions

1. Total charging-station records.
2. States and cities represented.
3. Missing-value checks.
4. Duplicate-like record checks.
5. City mapped to multiple states.
6. Coordinate validation.
7. Station records by state.
8. Top-five state concentration.
9. Top city-state combinations.
10. State city coverage.
11. Cities with more than 10 records.
12. Average station records per city.
13. Repeated station names.
14. Station-name frequency.
15. Exact coordinate clusters.
16. Unique-coordinate share.
17. Largest state.
18. Largest city.
19. States with at least 50 records.
20. Top city within each state using a window function.

## Key Findings

### Geographic concentration

The **top five states account for 56.06%** of all final station records.

### Largest state cluster

**Maharashtra** has the largest station-record count in the final master dataset.

### Largest city cluster

**Bengaluru, Karnataka** is the largest city-state cluster by station records.

### Station-name uniqueness

There are **1,128 distinct station-name values** across 1,222 records.

Therefore, `name` should not be treated as a unique station identifier. A future production model should use a stable `station_id` or physical-site ID.

### Geographic clustering

There are **1,191 unique latitude/longitude pairs** across 1,222 records.

Multiple records at the same coordinate may represent several chargers or several records belonging to the same physical site. They should not automatically be treated as data errors.

## Interactive Dashboard

The final HTML dashboard uses an EV-themed dark interface.

### Dashboard includes

- Total station records KPI.
- States covered KPI.
- Cities covered KPI.
- Unique station names KPI.
- Unique coordinate pairs KPI.
- Top-five concentration KPI.
- State distribution chart.
- State concentration chart.
- Top-city chart.
- City-coverage chart.
- Interactive India map.
- State filter.
- City filter.
- Station/address search.
- Paginated station-level table.
- Filtered CSV export.

### Dashboard drill-down

```text
India
  |
  +--> State
        |
        +--> City
              |
              +--> Station / Address
                    |
                    +--> Latitude / Longitude
```

## Project Files

```text
.
|-- final_ev_data_cleaning.py
|-- ev_charging_stations_india_final_consistent.csv
|-- ev_charging_state_city_corrections_final.csv
|-- final_ev_charging_mysql_analysis.sql
|-- EV_Charging_Final_SQL_Analysis_Report.docx
|-- EV_Charging_Final_Interactive_Dashboard.html
`-- README.md
```

### File purpose

| File | Purpose |
|---|---|
| `final_ev_data_cleaning.py` | Reproducible Python cleaning pipeline |
| `ev_charging_stations_india_final_consistent.csv` | Final master dataset |
| `ev_charging_state_city_corrections_final.csv` | Geographic correction audit |
| `final_ev_charging_mysql_analysis.sql` | MySQL table setup and analysis queries |
| `EV_Charging_Final_SQL_Analysis_Report.docx` | Professional SQL analysis report |
| `EV_Charging_Final_Interactive_Dashboard.html` | Interactive dashboard |
| `README.md` | Project documentation |

## How to Run

### 1. Python cleaning

Install dependencies:

```bash
pip install pandas numpy
```

Run:

```bash
python final_ev_data_cleaning.py
```

### 2. MySQL

Open:

```text
final_ev_charging_mysql_analysis.sql
```

Create the database/table, then update the `LOAD DATA LOCAL INFILE` path for your computer.

Example:

```sql
LOAD DATA LOCAL INFILE 'C:/path/to/ev_charging_stations_india_final_consistent.csv'
INTO TABLE ev_charging_stations
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(name, state, city, address, latitude, longitude);
```

Run the analysis queries in MySQL Workbench or another MySQL client.

### 3. Dashboard

Open:

```text
EV_Charging_Final_Interactive_Dashboard.html
```

It can be opened directly in a modern browser.

## Data Model

Current infrastructure layer:

```text
EV Charging Station
|
|-- name
|-- state
|-- city
|-- address
|-- latitude
`-- longitude
```

### Recommended future customer/session layer

```text
Customer
|
|-- customer_id
|-- vehicle_type
`-- signup_date
        |
        v
Charging Session
|
|-- session_id
|-- customer_id
|-- station_id
|-- session_datetime
|-- energy_kwh
|-- amount
|-- payment_status
`-- complaint_flag
```

Adding this layer would enable:

- Customer retention.
- Recency analysis.
- Repeat usage.
- Cohort analysis.
- Station utilization.
- Revenue analysis.
- Customer churn.
- Churn segmentation.
- Customer lifetime value.

## Important Limitation

The current dataset does not contain:

- Customer IDs
- Charging session history
- Session timestamps
- Revenue / spend
- Energy consumption
- Complaint history
- Last activity dates
- Retention status

Therefore, customer churn cannot be calculated from this dataset alone.

The correct project positioning is:

**EV Charging Infrastructure Analytics**

rather than claiming:

**EV Customer Churn Analytics**

until a customer/session transaction layer is added.

## Portfolio / Resume Description

**India EV Charging Infrastructure Analytics | Python, MySQL, HTML, JavaScript, Plotly**

> Built an end-to-end EV charging infrastructure analytics project using Python and MySQL, cleaning and standardizing 1,222 charging-station records across 28 states and 283 cities. Performed geographic concentration, city coverage, station-name duplication, and coordinate-cluster analysis using 20 SQL queries, and developed an interactive EV-themed HTML dashboard with KPIs, filters, charts, geographic mapping, station-level search, and CSV export.

## Future Enhancements

- Add charging operator / CPO analysis.
- Add charger type and connector analysis.
- Add station utilization and energy-consumption data.
- Add historical installation dates.
- Add district and PIN-code hierarchy.
- Calculate station density against population or EV registrations.
- Add highway / travel-corridor analysis.
- Add nearest-station distance analysis.
- Add customer/session data for churn and retention modeling.
- Deploy the dashboard using GitHub Pages or another static host.

## Author

**Rishu Rundla**  
B.Tech Mechanical Engineering, NSUT Delhi

Areas of interest:

- Data Analytics
- Business Analytics
- SQL
- Power BI
- Python
- Data Visualization
- EV / Mobility Analytics
- Mechanical Engineering & CAE
