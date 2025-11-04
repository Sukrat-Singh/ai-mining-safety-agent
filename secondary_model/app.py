"""
DGMS Mining Safety AI Dashboard
Built for AI Hackathon 2025 @ IIT (ISM) Dhanbad
Author: Sukrat

Combines:
✅ 2015 DGMS PDF Extraction (NLP)
✅ AI-Powered Accident Analysis
✅ Live Report Upload & Visualization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pdfplumber, re
import io

# ======================================================
# PAGE CONFIGURATION
# ======================================================
st.set_page_config(
    page_title="DGMS Mining Safety AI Dashboard",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# CUSTOM STYLING
# ======================================================
st.markdown("""
<style>
.main-header {
    font-size: 48px;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    padding: 20px;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
.alert-critical {
    background-color: #ffebee;
    padding: 15px;
    border-left: 5px solid #f44336;
    margin: 10px 0;
}
.alert-warning {
    background-color: #fff3e0;
    padding: 15px;
    border-left: 5px solid #ff9800;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# PDF PARSER (for 2015 report and uploads)
# ======================================================
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                text += txt + "\n"
    return text

def parse_accidents(text, default_year=2015):
    entries = re.split(r"\bCode\s*[:\-]", text)
    data = []
    for entry in entries[1:]:
        code_match = re.search(r"([0-9]{3,4}\s*[A-Za-z].*?)(?:\n|$)", entry)
        code_text = code_match.group(1).strip().replace("\n", " ") if code_match else None

        date_match = re.search(r"Date\s*[:\-]\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", entry)
        date_obj = None
        if date_match:
            for fmt in ("%d.%m.%y", "%d-%m-%y", "%d/%m/%y", "%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    date_obj = datetime.strptime(date_match.group(1), fmt)
                    break
                except:
                    continue

        mine = re.search(r"Mine\s*[:\-]\s*(.*)", entry)
        owner = re.search(r"Owner\s*[:\-]\s*(.*)", entry)
        district = re.search(r"District\s*[:\-]\s*(.*)", entry)
        state = re.search(r"State\s*[:\-]\s*(.*)", entry)
        persons = re.search(r"Persons\s*Killed\s*[:\-]\s*(.*)", entry)
        desc = re.search(r"Description\s*[:\-]\s*(.*)", entry)

        fatalities = len(re.findall(r"\b(killed|died)\b", entry, re.IGNORECASE))
        injuries = len(re.findall(r"\b(injured)\b", entry, re.IGNORECASE))
        severity = "Fatal" if fatalities > 0 else "Serious" if injuries > 0 else "Minor"

        if not code_text and not mine and not date_obj:
            continue

        data.append({
            "accident_code": code_text,
            "date": date_obj.strftime("%Y-%m-%d") if date_obj else None,
            "year": date_obj.year if date_obj else default_year,
            "state": state.group(1).strip() if state else None,
            "district": district.group(1).strip() if district else None,
            "mine_name": mine.group(1).strip() if mine else None,
            "mine_type": "Opencast" if "Opencast" in entry else "Underground",
            "owner": owner.group(1).strip() if owner else None,
            "severity": severity,
            "fatalities": fatalities,
            "injuries": injuries,
            "persons_killed": persons.group(1).strip() if persons else None,
            "description": desc.group(1).strip() if desc else None,
        })
    return pd.DataFrame(data)

def enrich_accident_data(df):
    df[["code_number", "accident_type"]] = df["accident_code"].str.extract(r"(\d+)\s*(.*)")
    df["code_number"] = df["code_number"].astype(str).str.zfill(4)

    def map_cause(acc_type):
        if pd.isna(acc_type): return "Other"
        acc_type = acc_type.lower()
        if "roof" in acc_type or "side" in acc_type:
            return "Ground Control Failure"
        if any(w in acc_type for w in ["wagon", "truck", "conveyor", "tanker", "transport", "movement", "dumper"]):
            return "Transportation Accident"
        if any(w in acc_type for w in ["electric", "power", "cable"]):
            return "Electrical Hazard"
        if any(w in acc_type for w in ["explosion", "fire", "blowout"]):
            return "Explosion / Fire"
        if "fall of person" in acc_type or "height" in acc_type:
            return "Fall from Height"
        if "drown" in acc_type or "water" in acc_type:
            return "Drowning / Flooding"
        if "machine" in acc_type or "machinery" in acc_type:
            return "Machinery Failure"
        return "Other"

    df["cause"] = df["accident_type"].apply(map_cause)
    for col in ["state", "district", "mine_name", "owner", "accident_type", "cause"]:
        df[col] = df[col].astype(str).str.strip().str.title().replace("Nan", "")
    df["accident_id"] = range(1, len(df) + 1)
    return df


# ======================================================
# LOAD BASE DATA
# ======================================================
@st.cache_data
def load_base_data():
    df1 = pd.read_csv('dgms_accidents_2016_2022.csv')
    df1['date'] = pd.to_datetime(df1['date'], errors='coerce')
    return df1

try:
    df = load_base_data()
except:
    st.error("⚠️ Data file not found. Please ensure 'dgms_accidents_2016_2022.csv' is in the same directory.")
    st.stop()

# ======================================================
# SIDEBAR CONTROLS
# ======================================================
st.sidebar.header("📁 Data Integration")
uploaded_pdf = st.sidebar.file_uploader("Upload DGMS Accident Report (PDF)", type=["pdf"])
if uploaded_pdf:
    with st.spinner("Extracting accident records from uploaded PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_pdf)
        df_new = parse_accidents(pdf_text, default_year=2015)
        df_new = enrich_accident_data(df_new)
        df = pd.concat([df, df_new], ignore_index=True)
    st.sidebar.success(f"✅ Extracted {len(df_new)} new accident records from PDF.")
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Filters
st.sidebar.header("🔍 Filters")
selected_years = st.sidebar.multiselect("Select Years", sorted(df['year'].dropna().unique()), default=sorted(df['year'].dropna().unique()))
selected_states = st.sidebar.multiselect("Select States", sorted(df['state'].dropna().unique()), default=sorted(df['state'].dropna().unique()))
selected_severity = st.sidebar.multiselect("Select Severity", ['Fatal', 'Serious', 'Minor'], default=['Fatal', 'Serious', 'Minor'])

filtered_df = df[
    (df['year'].isin(selected_years)) &
    (df['state'].isin(selected_states)) &
    (df['severity'].isin(selected_severity))
]

st.sidebar.info(f"📊 Showing {len(filtered_df)} of {len(df)} accident records")

# ======================================================
# MAIN TITLE
# ======================================================
st.markdown('<h1 class="main-header">⛏️ AI-Powered DGMS Mining Safety Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### Mining Accident Intelligence & Predictive Risk Insights (2015–2022)")
st.markdown("---")

# ======================================================
# IMPORT YOUR EXISTING 4 TAB UI HERE
# ======================================================
# (paste your existing tab1, tab2, tab3, tab4 logic directly below)
# I kept your dashboard logic fully compatible.

# 👇 Paste your 4-tab logic starting from:
# tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🤖 AI Agent", "🚨 Alerts", "📄 Reports"])
# (All your existing visualizations will work automatically on `filtered_df`.)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🤖 AI Agent", "🚨 Alerts", "📄 Reports"])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Accidents",
            len(filtered_df),
            delta=f"{len(filtered_df) - len(df[df['year'] == 2021])}" if 2021 in selected_years else None
        )
    
    with col2:
        total_fatalities = filtered_df['fatalities'].sum()
        st.metric("Total Fatalities", total_fatalities)
    
    with col3:
        total_injuries = filtered_df['injuries'].sum()
        st.metric("Total Injuries", total_injuries)
    
    with col4:
        high_risk_states = filtered_df[filtered_df['severity'] == 'Fatal']['state'].nunique()
        st.metric("High-Risk States", high_risk_states)
    
    st.markdown("---")
    
    # Trend over time
    st.subheader("📈 Accident Trends Over Time")
    monthly = filtered_df.groupby(filtered_df['date'].dt.to_period('M')).size().reset_index()
    monthly['date'] = monthly['date'].dt.to_timestamp()
    monthly.columns = ['date', 'count']
    
    fig_trend = px.line(
        monthly, 
        x='date', 
        y='count',
        labels={'count': 'Number of Accidents', 'date': 'Date'},
        title='Monthly Accident Frequency'
    )
    fig_trend.update_traces(line_color='#1f77b4', line_width=3)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Two columns for charts
    col1, col2 = st.columns(2)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    with col1:
        st.subheader("🏭 Accidents by Type")
        type_counts = filtered_df['accident_type'].value_counts().reset_index()
        type_counts.columns = ['Accident Type', 'Count']
        
        fig_type = px.bar(
            type_counts.head(10),
            x='Count',
            y='Accident Type',
            orientation='h',
            color='Count',
            color_continuous_scale='Reds'
        )
        fig_type.update_layout(showlegend=False)
        st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        st.subheader("🗺️ Geographic Distribution")
        state_counts = filtered_df['state'].value_counts()
        
        fig_state = px.pie(
            values=state_counts.values,
            names=state_counts.index,
            hole=0.4
        )
        st.plotly_chart(fig_state, use_container_width=True)
    
    # Severity analysis
    st.subheader("⚠️ Severity Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        severity_counts = filtered_df['severity'].value_counts()
        fig_severity = px.bar(
            x=severity_counts.index,
            y=severity_counts.values,
            labels={'x': 'Severity', 'y': 'Count'},
            color=severity_counts.index,
            color_discrete_map={'Fatal': '#d32f2f', 'Serious': '#f57c00', 'Minor': '#fbc02d'}
        )
        fig_severity.update_layout(showlegend=False)
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        # Heatmap of accidents by state and year
        heatmap_data = filtered_df.groupby(['state', 'year']).size().reset_index(name='count')
        fig_heat = px.density_heatmap(
            heatmap_data,
            x='year',
            y='state',
            z='count',
            color_continuous_scale='Reds',
            labels={'count': 'Accidents'}
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    
    # Top causes
    st.subheader("🔍 Root Cause Analysis")
    cause_counts = filtered_df['cause'].value_counts().head(10)
    fig_cause = px.bar(
        x=cause_counts.values,
        y=cause_counts.index,
        orientation='h',
        labels={'x': 'Number of Incidents', 'y': 'Cause'},
        color=cause_counts.values,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_cause, use_container_width=True)

# ==================== TAB 2: AI AGENT ====================
with tab2:
    st.subheader("🤖 Digital Mine Safety Officer")
    st.markdown("""
    Ask questions about mining accidents using natural language!
    This AI agent can search through accident records, identify patterns, and provide safety recommendations.
    """)
    
    # Example queries
    st.markdown("#### 💡 Try these queries:")
    example_queries = [
        "Show me all methane-related accidents in Jharkhand",
        "What are the most dangerous states for underground coal mining?",
        "How many fatal accidents involved roof falls in 2021?",
        "Give me safety recommendations for preventing explosions",
        "Which mine type has the highest fatality rate?",
        "Show me accidents in Opencast Coal mines with more than 5 injuries"
    ]
    
    selected_example = st.selectbox("Quick queries:", ["Select an example..."] + example_queries)
    
    user_query = st.text_input("Or type your own question:", value="" if selected_example == "Select an example..." else selected_example)
    
    if st.button("🔍 Analyze", type="primary") or user_query:
        if user_query and user_query != "Select an example...":
            with st.spinner("🔍 Analyzing accident records..."):
                # Simple rule-based response system (can be replaced with LangChain)
                query_lower = user_query.lower()
                response = ""
                results = filtered_df.copy()
                
                # Filter based on keywords
                if 'methane' in query_lower:
                    results = results[results['cause'].str.contains('Methane', case=False, na=False)]
                    response += f"Found {len(results)} methane-related accidents.\n\n"
                
                if 'roof fall' in query_lower or 'roof/side fall' in query_lower:
                    results = results[results['accident_type'].str.contains('Roof', case=False, na=False)]
                    response += f"Found {len(results)} roof fall incidents.\n\n"
                
                if 'explosion' in query_lower:
                    results = results[results['accident_type'].str.contains('Explosion', case=False, na=False)]
                    response += f"Found {len(results)} explosion incidents.\n\n"
                
                if 'jharkhand' in query_lower:
                    results = results[results['state'].str.contains('Jharkhand', case=False, na=False)]
                    response += f"Filtered to Jharkhand: {len(results)} accidents.\n\n"
                
                if 'fatal' in query_lower:
                    results = results[results['severity'] == 'Fatal']
                    response += f"Fatal accidents: {len(results)}.\n\n"
                
                if 'underground coal' in query_lower:
                    results = results[results['mine_type'].str.contains('Underground Coal', case=False, na=False)]
                    response += f"Underground coal mine accidents: {len(results)}.\n\n"
                
                if 'opencast coal' in query_lower:
                    results = results[results['mine_type'].str.contains('Opencast Coal', case=False, na=False)]
                    response += f"Opencast coal mine accidents: {len(results)}.\n\n"
                
                # Year filtering
                for year in range(2016, 2023):
                    if str(year) in query_lower:
                        results = results[results['year'] == year]
                        response += f"Year {year}: {len(results)} accidents.\n\n"
                
                # Statistics
                if len(results) > 0:
                    response += f"**Statistics:**\n"
                    response += f"- Total Fatalities: {results['fatalities'].sum()}\n"
                    response += f"- Total Injuries: {results['injuries'].sum()}\n"
                    response += f"- Most common type: {results['accident_type'].value_counts().index[0]}\n"
                    response += f"- Most affected state: {results['state'].value_counts().index[0]}\n\n"
                
                # Recommendations
                if 'recommendation' in query_lower or 'prevent' in query_lower:
                    response += "**Safety Recommendations:**\n\n"
                    
                    if 'roof fall' in query_lower:
                        response += "- Conduct immediate slope stability inspections\n"
                        response += "- Review and upgrade ground support systems\n"
                        response += "- Implement real-time ground movement monitoring\n"
                        response += "- Provide additional training on rock mechanics\n"
                    
                    elif 'methane' in query_lower or 'explosion' in query_lower:
                        response += "- Inspect all ventilation systems immediately\n"
                        response += "- Upgrade gas detection equipment\n"
                        response += "- Conduct mandatory methane testing before each shift\n"
                        response += "- Review explosion-proof electrical installations\n"
                    
                    elif 'fire' in query_lower:
                        response += "- Inspect fire suppression systems\n"
                        response += "- Conduct fire safety drills\n"
                        response += "- Review combustible material storage procedures\n"
                        response += "- Check emergency evacuation routes\n"
                    
                    else:
                        response += "- Schedule comprehensive safety audit\n"
                        response += "- Review and update all safety protocols\n"
                        response += "- Conduct mandatory safety training for all personnel\n"
                        response += "- Implement stricter compliance monitoring\n"
                
                # Display response
                st.success(response if response else "No specific patterns found for this query. Try refining your search.")
                
                # Show sample records
                if len(results) > 0 and len(results) <= 10:
                    st.markdown("#### 📋 Matching Records:")
                    st.dataframe(results[['accident_id', 'date', 'state', 'accident_type', 'severity', 'fatalities', 'injuries']])
                elif len(results) > 10:
                    st.markdown(f"#### 📋 Sample Records (showing 10 of {len(results)}):")
                    st.dataframe(results.head(10)[['accident_id', 'date', 'state', 'accident_type', 'severity', 'fatalities', 'injuries']])
        else:
            st.warning("Please enter a question or select an example query.")

# ==================== TAB 3: ALERTS ====================
with tab3:
    st.subheader("🚨 Automated Safety Alerts")
    st.markdown("Real-time pattern detection and risk assessment")
    
    # Analyze recent trends (last 90 days in the dataset)
    max_date = filtered_df['date'].max()
    recent_3months = filtered_df[filtered_df['date'] >= max_date - timedelta(days=90)]
    
    alerts = []
    
    # Alert 1: High accident rate in specific location
    location_counts = recent_3months['state'].value_counts()
    if len(location_counts) > 0 and location_counts.iloc[0] > 8:
        alerts.append({
            'severity': 'Critical',
            'icon': '🔴',
            'message': f"High accident concentration in {location_counts.index[0]}",
            'details': f"{location_counts.iloc[0]} incidents in last 90 days",
            'recommendation': f"Schedule immediate comprehensive inspection of all mines in {location_counts.index[0]}"
        })
    
    # Alert 2: Increase in specific accident type
    type_counts = recent_3months['accident_type'].value_counts()
    if len(type_counts) > 0 and type_counts.iloc[0] > 6:
        alerts.append({
            'severity': 'Warning',
            'icon': '⚠️',
            'message': f"Spike in {type_counts.index[0]} accidents",
            'details': f"{type_counts.iloc[0]} cases in recent months",
            'recommendation': "Review safety protocols and conduct targeted training"
        })
    
    # Alert 3: Fatal accident rate
    fatal_recent = recent_3months[recent_3months['severity'] == 'Fatal']
    if len(fatal_recent) > 5:
        alerts.append({
            'severity': 'Critical',
            'icon': '🔴',
            'message': "Elevated fatal accident rate",
            'details': f"{len(fatal_recent)} fatal accidents in last 90 days",
            'recommendation': "Emergency safety review required for all high-risk operations"
        })
    
    # Alert 4: Specific cause pattern
    cause_counts = recent_3months['cause'].value_counts()
    if len(cause_counts) > 0 and cause_counts.iloc[0] > 7:
        alerts.append({
            'severity': 'Warning',
            'icon': '⚠️',
            'message': f"Recurring issue: {cause_counts.index[0]}",
            'details': f"{cause_counts.iloc[0]} incidents with same root cause",
            'recommendation': f"Implement corrective measures to address {cause_counts.index[0].lower()}"
        })
    
    # Display alerts
    if alerts:
        for alert in alerts:
            if alert['severity'] == 'Critical':
                st.markdown(f"""
                <div class="alert-critical">
                    <h3>{alert['icon']} {alert['severity']}: {alert['message']}</h3>
                    <p><strong>Details:</strong> {alert['details']}</p>
                    <p><strong>Recommended Action:</strong> {alert['recommendation']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                    <h3>{alert['icon']} {alert['severity']}: {alert['message']}</h3>
                    <p><strong>Details:</strong> {alert['details']}</p>
                    <p><strong>Recommended Action:</strong> {alert['recommendation']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ No critical alerts. Safety metrics within acceptable range.")
    
    st.markdown("---")
    
    # Pattern detection
    st.subheader("🔍 Pattern Detection")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📅 Temporal Patterns")

        # Ensure 'date' is datetime-safe
        filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')

        # Extract months safely
        filtered_df['month'] = filtered_df['date'].dt.month
        monthly_pattern = (
            filtered_df.groupby('month')
            .size()
            .sort_values(ascending=False)
        )

        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Convert valid month indexes to names
        valid_months = [int(m) for m in monthly_pattern.head(3).index.tolist() if pd.notnull(m)]
        if valid_months:
            peak_months = [month_names[m - 1] for m in valid_months if 1 <= m <= 12]
            st.write(f"**Peak accident months:** {', '.join(peak_months)}")
        else:
            st.write("No valid month data available.")

        # Yearly trend
        yearly_trend = filtered_df.groupby('year').size().sort_values()
        if len(yearly_trend) > 1:
            trend_direction = (
                "increasing 📈" if yearly_trend.iloc[-1] > yearly_trend.iloc[0]
                else "decreasing 📉"
            )
            st.write(f"**Overall trend:** {trend_direction}")
        else:
            st.write("Not enough yearly data to detect trend.")

    with col2:
        st.markdown("##### ⚠️ High-Risk Combinations")

        # Most dangerous accident type (Fatal only)
        fatal_df = filtered_df[filtered_df['severity'] == 'Fatal']

        if not fatal_df.empty:
            type_severity = fatal_df.groupby('accident_type').size().sort_values(ascending=False)
            if len(type_severity) > 0:
                st.write(f"**Most lethal accident type:** {type_severity.index[0]}")

            cause_severity = fatal_df.groupby('cause').size().sort_values(ascending=False)
            if len(cause_severity) > 0:
                st.write(f"**Most common fatal cause:** {cause_severity.index[0]}")
        else:
            st.write("No fatal accident data available for pattern analysis.")

# ==================== TAB 4: REPORTS ====================
with tab4:
    st.subheader("📄 Automated Safety Audit Report")
    st.markdown("Generate comprehensive safety reports based on accident data analysis")
    
    report_type = st.selectbox(
        "Select Report Type:",
        ["Executive Summary", "Detailed Analysis", "State-wise Report", "Trend Analysis"]
    )
    
    if st.button("📥 Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            st.markdown("---")
            
            if report_type == "Executive Summary":
                st.markdown("### Executive Summary Report")
                st.markdown(f"**Report Period:** {filtered_df['date'].min().strftime('%Y-%m-%d')} to {filtered_df['date'].max().strftime('%Y-%m-%d')}")
                st.markdown(f"**Generated On:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                st.markdown("#### Key Findings:")
                st.write(f"- Total accidents analyzed: **{len(filtered_df)}**")
                st.write(f"- Total fatalities: **{filtered_df['fatalities'].sum()}**")
                st.write(f"- Total injuries: **{filtered_df['injuries'].sum()}**")
                st.write(f"- Most affected state: **{filtered_df['state'].value_counts().index[0]}** ({filtered_df['state'].value_counts().iloc[0]} accidents)")
                st.write(f"- Most common accident type: **{filtered_df['accident_type'].value_counts().index[0]}** ({filtered_df['accident_type'].value_counts().iloc[0]} incidents)")
                st.write(f"- Primary root cause: **{filtered_df['cause'].value_counts().index[0]}** ({filtered_df['cause'].value_counts().iloc[0]} cases)")
                
                st.markdown("#### Critical Recommendations:")
                st.write("1. Implement enhanced monitoring in high-risk states")
                st.write("2. Mandatory safety training for accident-prone operations")
                st.write("3. Upgrade safety equipment and detection systems")
                st.write("4. Strengthen regulatory compliance enforcement")
                st.write("5. Establish rapid response protocols for emergencies")
            
            elif report_type == "Detailed Analysis":
                st.markdown("### Detailed Analysis Report")
                
                # Severity breakdown
                st.markdown("#### Severity Breakdown")
                severity_df = filtered_df['severity'].value_counts().reset_index()
                severity_df.columns = ['Severity', 'Count']
                st.dataframe(severity_df, use_container_width=True)
                
                # Top 10 accident types
                st.markdown("#### Top 10 Accident Types")
                type_df = filtered_df['accident_type'].value_counts().head(10).reset_index()
                type_df.columns = ['Accident Type', 'Count']
                st.dataframe(type_df, use_container_width=True)
                
                # State-wise statistics
                st.markdown("#### State-wise Statistics")
                state_stats = filtered_df.groupby('state').agg({
                    'accident_id': 'count',
                    'fatalities': 'sum',
                    'injuries': 'sum'
                }).reset_index()
                state_stats.columns = ['State', 'Total Accidents', 'Fatalities', 'Injuries']
                st.dataframe(state_stats.sort_values('Total Accidents', ascending=False), use_container_width=True)
            
            elif report_type == "State-wise Report":
                st.markdown("### State-wise Safety Report")
                
                for state in filtered_df['state'].unique():
                    state_data = filtered_df[filtered_df['state'] == state]
                    
                    with st.expander(f"📍 {state}"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Accidents", len(state_data))
                        col2.metric("Fatalities", state_data['fatalities'].sum())
                        col3.metric("Injuries", state_data['injuries'].sum())
                        
                        st.write(f"**Most common accident type:** {state_data['accident_type'].value_counts().index[0]}")
                        st.write(f"**Primary cause:** {state_data['cause'].value_counts().index[0]}")
                        st.write(f"**High-risk mine type:** {state_data['mine_type'].value_counts().index[0]}")
            
            elif report_type == "Trend Analysis":
                st.markdown("### Trend Analysis Report")
                
                yearly_stats = filtered_df.groupby('year').agg({
                    'accident_id': 'count',
                    'fatalities': 'sum',
                    'injuries': 'sum'
                }).reset_index()
                yearly_stats.columns = ['Year', 'Accidents', 'Fatalities', 'Injuries']
                
                st.markdown("#### Year-over-Year Trends")
                st.dataframe(yearly_stats, use_container_width=True)
                
                # Trend interpretation
                if len(yearly_stats) > 1:
                    accident_change = yearly_stats['Accidents'].iloc[-1] - yearly_stats['Accidents'].iloc[0]
                    fatality_change = yearly_stats['Fatalities'].iloc[-1] - yearly_stats['Fatalities'].iloc[0]
                    
                    st.markdown("#### Interpretation:")
                    if accident_change > 0:
                        st.warning(f"⚠️ Accident rate has increased by {accident_change} incidents")
                    else:
                        st.success(f"✅ Accident rate has decreased by {abs(accident_change)} incidents")
                    
                    if fatality_change > 0:
                        st.error(f"🔴 Fatality rate has increased by {fatality_change}")
                    else:
                        st.success(f"✅ Fatality rate has decreased by {abs(fatality_change)}")
            
            st.success("✅ Report generated successfully!")
            st.download_button(
                label="📥 Download Report (CSV)",
                data=filtered_df.to_csv(index=False),
                file_name=f"dgms_safety_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏆 DGMS Mining Safety AI System | AI Hackathon 2025 | IIT ISM Dhanbad</p>
    <p>Powered by AI & NLP | Data Source: DGMS India (2016-2022)</p>
</div>
""", unsafe_allow_html=True)