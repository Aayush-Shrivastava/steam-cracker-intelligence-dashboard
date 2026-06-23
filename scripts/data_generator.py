import pandas as pd
import numpy as np

np.random.seed(42)
n_points = 8760  # one full year of hourly data

time = pd.date_range('2023-01-01', periods=n_points, freq='H')

# Run length — resets every 720 hours (30 day runs)
run_length = np.tile(np.linspace(0, 720, 720), 13)[:n_points]

# ── FEEDSTOCK ──────────────────────────────────────────────
feed_rate_tph = 25 + np.random.normal(0, 0.5, n_points)
naphtha_fraction = 0.72 + np.random.normal(0, 0.01, n_points)   # fraction of naphtha in feed
ethane_recycle_tph = 2.1 + np.random.normal(0, 0.1, n_points)   # ethane recycle stream

# ── FURNACE OPERATING CONDITIONS ───────────────────────────
steam_hc_ratio = 0.45 + np.random.normal(0, 0.02, n_points)
COT = 820 + run_length * 0.05 + np.random.normal(0, 1.5, n_points)  # coil outlet temp C
CIT = 560 + np.random.normal(0, 3, n_points)                         # coil inlet temp C
furnace_bridge_wall_temp = 1080 + run_length*0.02 + np.random.normal(0, 5, n_points)
TMT = 950 + run_length * 0.04 + np.random.normal(0, 2, n_points)     # tube metal temp C
residence_time_ms = 180 + np.random.normal(0, 5, n_points)           # milliseconds

# ── COIL HEALTH ─────────────────────────────────────────────
pressure_drop_bar = 0.8 + run_length*0.003 + np.random.normal(0, 0.05, n_points)
coke_thickness_mm = 0 + run_length*0.004 + np.random.normal(0, 0.1, n_points)
coil_skin_temp = 870 + run_length*0.06 + np.random.normal(0, 3, n_points)

# ── PRODUCT YIELDS ──────────────────────────────────────────
ethylene_selectivity = 0.32 + (COT-820)*0.001 - run_length*0.00005 + np.random.normal(0, 0.005, n_points)
propylene_selectivity = 0.16 - (COT-820)*0.0005 - run_length*0.00003 + np.random.normal(0, 0.003, n_points)
butadiene_selectivity = 0.045 + (COT-820)*0.0001 + np.random.normal(0, 0.002, n_points)
pygas_selectivity = 0.12 + run_length*0.00002 + np.random.normal(0, 0.003, n_points)
methane_selectivity = 0.13 + (COT-820)*0.0003 + np.random.normal(0, 0.004, n_points)
hydrogen_selectivity = 0.018 + (COT-820)*0.0001 + np.random.normal(0, 0.001, n_points)

# ── ENERGY ──────────────────────────────────────────────────
fuel_consumption_GJ_hr = 45 + run_length*0.02 + np.random.normal(0, 1, n_points)
dilution_steam_consumption = feed_rate_tph * steam_hc_ratio * 1000  # kg/hr
quench_oil_temp = 180 + np.random.normal(0, 5, n_points)             # C
transfer_line_temp = 820 + np.random.normal(0, 8, n_points)          # C, TLE inlet

# ── DERIVED PRODUCTION METRICS ──────────────────────────────
ethylene_production_tph = feed_rate_tph * ethylene_selectivity
propylene_production_tph = feed_rate_tph * propylene_selectivity
specific_energy_GJ_t = fuel_consumption_GJ_hr * 3.6 / ethylene_production_tph
furnace_thermal_efficiency = (ethylene_production_tph * 47.2) / (fuel_consumption_GJ_hr) * 100

# ── UTILITIES ───────────────────────────────────────────────
hp_steam_production_tph = 18 + np.random.normal(0, 0.5, n_points)    # high pressure steam
cooling_water_flow = 320 + np.random.normal(0, 10, n_points)          # m3/hr
instrument_air_pressure = 6.5 + np.random.normal(0, 0.1, n_points)   # bar

df = pd.DataFrame({
    'timestamp': time,
    'run_length_hours': run_length,
    # Feedstock
    'feed_rate_tph': feed_rate_tph,
    'naphtha_fraction': naphtha_fraction,
    'ethane_recycle_tph': ethane_recycle_tph,
    # Furnace conditions
    'steam_hc_ratio': steam_hc_ratio,
    'coil_inlet_temp_C': CIT,
    'coil_outlet_temp_C': COT,
    'tube_metal_temp_C': TMT,
    'furnace_bridge_wall_temp_C': furnace_bridge_wall_temp,
    'residence_time_ms': residence_time_ms,
    # Coil health
    'pressure_drop_bar': pressure_drop_bar,
    'coke_thickness_mm': coke_thickness_mm,
    'coil_skin_temp_C': coil_skin_temp,
    # Product yields
    'ethylene_selectivity': ethylene_selectivity,
    'propylene_selectivity': propylene_selectivity,
    'butadiene_selectivity': butadiene_selectivity,
    'pygas_selectivity': pygas_selectivity,
    'methane_selectivity': methane_selectivity,
    'hydrogen_selectivity': hydrogen_selectivity,
    # Production
    'ethylene_production_tph': ethylene_production_tph,
    'propylene_production_tph': propylene_production_tph,
    'specific_energy_GJ_t': specific_energy_GJ_t,
    'furnace_thermal_efficiency': furnace_thermal_efficiency,
    # Energy and utilities
    'fuel_consumption_GJ_hr': fuel_consumption_GJ_hr,
    'dilution_steam_kg_hr': dilution_steam_consumption,
    'hp_steam_production_tph': hp_steam_production_tph,
    'cooling_water_flow_m3hr': cooling_water_flow,
    'quench_oil_temp_C': quench_oil_temp,
    'transfer_line_temp_C': transfer_line_temp,
})

# Clip physically impossible values
df['ethylene_selectivity'] = df['ethylene_selectivity'].clip(0.28, 0.38)
df['propylene_selectivity'] = df['propylene_selectivity'].clip(0.12, 0.20)
df['coke_thickness_mm'] = df['coke_thickness_mm'].clip(0, None)
df['pressure_drop_bar'] = df['pressure_drop_bar'].clip(0.5, None)

df.to_csv('steam_cracker_data.csv', index=False)
print(f"Dataset created: {len(df)} rows, {len(df.columns)} columns")
print(f"\nColumn list:")
for col in df.columns:
    print(f"  {col}")