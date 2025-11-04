
# First, let's create a complete working demo with sample data generation
# This will be a full working project you can use

# 1. Generate sample DGMS mining accident data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# Define realistic data
states = ['Jharkhand', 'Odisha', 'Chhattisgarh', 'West Bengal', 'Madhya Pradesh', 'Assam']
districts = ['Dhanbad', 'Ranchi', 'Sundergarh', 'Korba', 'Asansol', 'Singrauli', 'Talcher']
mine_types = ['Underground Coal', 'Opencast Coal', 'Iron Ore', 'Limestone', 'Manganese']
accident_types = ['Roof/Side Fall', 'Inundation', 'Explosion', 'Fire', 'Transport/Haulage', 
                  'Machinery', 'Fall of Person', 'Electrical', 'Gas Emission', 'Collapse']
causes = ['Methane buildup', 'Inadequate support', 'Equipment failure', 'Human error', 
          'Poor ventilation', 'Structural weakness', 'Safety protocol violation', 
          'Inadequate training', 'Weather conditions', 'Equipment malfunction']
severity_levels = ['Fatal', 'Serious', 'Minor']

# Generate 300 accident records
data = []
start_date = datetime(2016, 1, 1)
end_date = datetime(2022, 12, 31)
days_range = (end_date - start_date).days

for i in range(300):
    # Random date between 2016-2022
    random_days = np.random.randint(0, days_range)
    date = start_date + timedelta(days=random_days)
    
    # Severity with realistic distribution
    severity = np.random.choice(severity_levels, p=[0.15, 0.35, 0.5])
    
    # Fatalities based on severity
    if severity == 'Fatal':
        fatalities = np.random.choice([1, 2, 3, 4, 5], p=[0.5, 0.25, 0.15, 0.07, 0.03])
        injuries = np.random.randint(0, 8)
    elif severity == 'Serious':
        fatalities = 0
        injuries = np.random.randint(1, 15)
    else:
        fatalities = 0
        injuries = np.random.randint(0, 3)
    
    state = np.random.choice(states)
    accident_type = np.random.choice(accident_types)
    cause = np.random.choice(causes)
    
    # Create descriptive text
    description = f"{accident_type} incident at {mine_types[np.random.randint(0, len(mine_types))]} mine. "
    description += f"Cause: {cause}. "
    description += f"Location: {state}, {np.random.choice(districts)}. "
    if fatalities > 0:
        description += f"{fatalities} fatalities reported. "
    if injuries > 0:
        description += f"{injuries} injuries reported. "
    description += "Investigation ongoing by DGMS authorities."
    
    data.append({
        'accident_id': f'DGMS-{date.year}-{i%100:03d}',
        'date': date.strftime('%Y-%m-%d'),
        'year': date.year,
        'month': date.month,
        'state': state,
        'district': np.random.choice(districts),
        'mine_name': f'{state[:3].upper()}-Mine-{np.random.randint(1, 100):02d}',
        'mine_type': np.random.choice(mine_types),
        'accident_type': accident_type,
        'cause': cause,
        'severity': severity,
        'fatalities': fatalities,
        'injuries': injuries,
        'description': description
    })

# Create DataFrame
df = pd.DataFrame(data)

# Sort by date
df = df.sort_values('date')

# Save to CSV
df.to_csv('dgms_accidents_2016_2022.csv', index=False)

print(f"✅ Created {len(df)} accident records")
print(f"\nData Preview:")
print(df.head(10))
print(f"\nData Summary:")
print(f"Total Fatalities: {df['fatalities'].sum()}")
print(f"Total Injuries: {df['injuries'].sum()}")
print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
print(f"\nAccidents by Type:")
print(df['accident_type'].value_counts())
