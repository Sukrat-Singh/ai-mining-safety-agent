"""
Quick Setup Script for DGMS Mining Safety AI
Run this first to set up everything
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def check_data_file():
    """Check if data file exists"""
    print("\n📊 Checking for data file...")
    if os.path.exists('dgms_accidents_2016_2022.csv'):
        print("✅ Data file found!")
        return True
    else:
        print("⚠️  Data file not found. Generating sample data...")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample DGMS data if not exists"""
    try:
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
            random_days = np.random.randint(0, days_range)
            date = start_date + timedelta(days=random_days)
            
            severity = np.random.choice(severity_levels, p=[0.15, 0.35, 0.5])
            
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
        
        df = pd.DataFrame(data)
        df = df.sort_values('date')
        df.to_csv('dgms_accidents_2016_2022.csv', index=False)
        
        print(f"✅ Generated {len(df)} sample accident records!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating data: {e}")
        return False

def run_app():
    """Run the Streamlit app"""
    print("\n🚀 Starting the application...")
    print("\n" + "="*50)
    print("🎯 DGMS Mining Safety AI System")
    print("="*50)
    print("\n📝 Instructions:")
    print("  1. The app will open in your browser")
    print("  2. Use the sidebar to filter data")
    print("  3. Try the AI Agent with example queries")
    print("  4. Check the Alerts tab for patterns")
    print("  5. Generate reports in the Reports tab")
    print("\n💡 Tip: Press Ctrl+C to stop the app")
    print("="*50 + "\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped.")
    except Exception as e:
        print(f"\n❌ Error running app: {e}")

def main():
    """Main setup function"""
    print("="*50)
    print("🎯 DGMS Mining Safety AI - Setup")
    print("="*50 + "\n")
    
    # Step 1: Install packages
    if not install_packages():
        print("\n❌ Setup failed. Please install packages manually.")
        return
    
    # Step 2: Check/generate data
    if not check_data_file():
        print("\n❌ Setup failed. Data file issue.")
        return
    
    print("\n✅ Setup complete!")
    print("\n" + "="*50)
    
    # Step 3: Ask to run app
    response = input("\n🚀 Ready to run the app? (y/n): ").lower()
    if response == 'y':
        run_app()
    else:
        print("\n📝 To run the app later, use: streamlit run app.py")

if __name__ == "__main__":
    main()
