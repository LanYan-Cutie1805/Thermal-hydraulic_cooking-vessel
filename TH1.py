import numpy as np
import matplotlib.pyplot as plt

# Constants
Cp_water = 4.18  # kJ/kg°C (specific heat capacity of water)
Cp_food = 3.7    # kJ/kg°C (approximate for generic food)
Lv = 2260        # kJ/kg (latent heat of vaporization)
P_atm = 101325   # Pa (atmospheric pressure)
R = 461.5        # J/kg·K (specific gas constant for steam)
g = 9.81         # m/s^2 (gravitational acceleration)
m_lid = 0.05     # kg (lid mass, 50 grams)
A_lid = 0.01     # m^2 (approximate venting area under lid)
V_vessel = 0.01  # m³ (approximate vessel volume)

# User inputs
T_end = float(input("Enter simulation time in minutes: ")) * 60  # Convert to seconds
dt = float(input("Enter time step in seconds: "))

# Initial conditions
T_water = 20     # °C (initial water temperature)
T_food = 10      # °C (initial food temperature)
m_water = 100    # kg (initial water mass)
m_food = 0.5     # kg (food mass)
Q_gas = 30      # W (power input from gas stove)

time = np.arange(0, T_end, dt)  # Simulation time array

# Arrays to store results
T_water_arr, T_food_arr, P_vessel_arr, m_steam_arr = [], [], [], []
m_steam = 0

for t in time:
    # Heat input only for the first 20 minutes
    if t < 1200:
        Q_input = Q_gas
    else:
        Q_input = 0
    
    # Heat transfer to water
    if m_water > 0:
        dT_water_dt = Q_input / (m_water * Cp_water)
        T_water += dT_water_dt * dt
    
    # Boiling and steam generation
    if T_water >= 100 and m_water > 0:
        dM_steam_dt = Q_input / Lv  # kg/s of water turning into steam
        m_evaporated = dM_steam_dt * dt
        m_water = max(0, m_water - m_evaporated)  # Ensure non-negative water mass
        m_steam += m_evaporated
    
    # Pressure inside the vessel (Ideal Gas Law)
    T_vessel_K = T_water + 273.15  # Convert to Kelvin
    if m_steam > 0:
        P_vessel = (m_steam * R * T_vessel_K) / V_vessel
    else:
        P_vessel = P_atm  # Default to atmospheric pressure if no steam
    
    # Steam escape condition (lid needs pressure to lift)
    P_lift = m_lid * g / A_lid  # Pressure needed to lift the lid
    if P_vessel > P_atm + P_lift:
        m_out = (P_vessel - (P_atm + P_lift)) / 100000  # Proportional release
        m_steam = max(0, m_steam - m_out)
    
    # Heat transfer to food (simple conduction model)
    dT_food_dt = (T_water - T_food) / 30  # Assume slow heating rate
    T_food += dT_food_dt * dt
    
    # Store results
    T_water_arr.append(T_water)
    T_food_arr.append(T_food)
    P_vessel_arr.append(P_vessel / 1000)  # Convert to kPa
    m_steam_arr.append(m_steam)

# Plot results
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(time / 60, T_water_arr, label="Water Temperature (°C)")
plt.plot(time / 60, T_food_arr, label="Food Temperature (°C)")
plt.xlabel("Time (minutes)")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.grid()

plt.subplot(2, 1, 2)
plt.plot(time / 60, P_vessel_arr, label="Vessel Pressure (kPa)")
plt.plot(time / 60, m_steam_arr, label="Steam Mass (kg)")
plt.xlabel("Time (minutes)")
plt.ylabel("Pressure / Steam Mass")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
