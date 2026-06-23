import sys
from pathlib import Path
import pandas as pd
sys.path.append(str(Path(__file__).parent/'src'))
import streamlit as st 
from data_loader import load
from coking_analyzer import calculate_statistics,analyze_all_cycles,calculate_coking_rates
from cycle_detector import detect_cycles
from visualizations import plot_rate_comparison,plot_single_cycle,multiple_plot_comparison

# ─────────────────────────────────────── PAGE CONFIG ───────────────────────────────────────────────── 

st.set_page_config(page_title='Steam Cracker Intelligence Dashboard',layout='wide',page_icon='⚗️')
st.markdown("""<div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h1 style='color: #1f77b4; margin-bottom: 5px;'>
                🏭 Intelligent Steam Cracking Dashboard
                </h1>
                <h3 style='color: #666; font-weight: normal; margin-top: 0;'>
                Decoking Analysis Module
                </h3>
                <p style='font-size: 12px; color: #888; margin-top: 10px;'>
                Developed by <b style='color: #1f77b4;'>Aayush Shrivastava</b> • Summer 2026 Project
                </p>
                </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────── LOAD DATA ──────────────────────────────────────────────────

DATA_PATH=Path(__file__).parent/'data'/'steam_cracker_data.csv'

@st.cache_data
def load_all():
    df=load(DATA_PATH)
    cycles=detect_cycles(df)
    results=analyze_all_cycles(df,cycles)
    stats=calculate_statistics(results)

    return df,cycles,results,stats

# ────────────────────────────────────────SIDEBAR─────────────────────────────────────────────────────

with st.sidebar:
    # Logo/Header
    st.markdown("""
        <div style='text-align: center; padding: 20px 0 10px 0;'>
            <h2 style='color: #1f77b4; margin: 0; font-weight: 700;'>🏭 SCID</h2>
            <p style='font-size: 12px; color: #666; margin: 5px 0 0 0;'>Steam Cracker Intelligence Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    # About Section
    st.markdown("### 📋 About This Dashboard")
    st.markdown("""<div style='background-color: #e8f4f8; padding: 12px; border-radius: 8px; 
                    border-left: 3px solid #1f77b4; margin-bottom: 20px;'>
            <p style='margin: 0; font-size: 13px; line-height: 1.7; color: #1e1e1e;'>
                Intelligent analysis of <strong>pressure drop (ΔP)</strong> trends in 
                steam cracking furnaces for optimized decoking schedules and 
                maximum operational efficiency.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    # Data Upload Section
    st.markdown("### 📂 Data Source")
    data_source = st.radio("Choose data source:",["Use Default Dataset", "Upload Your Own CSV"],index=0)
    if data_source == "Upload Your Own CSV":
        uploaded_file = st.file_uploader("Upload CSV file",type=['csv'],help="CSV must contain 'run_length_hours' and 'pressure_drop_bar' columns")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} rows")
            
            # Show column check
            required_cols = ['run_length_hours', 'pressure_drop_bar']
            missing_cols = [c for c in required_cols if c not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
                st.info(f"Your columns: {', '.join(df.columns)}")
                st.stop()
        else:
            st.info("⬆️ Upload a CSV to begin analysis")
            st.stop()
    else:
        df,cycles,results,stats=load_all()

    if data_source == "Upload Your Own CSV" or 'cycles' not in locals():
        with st.spinner("Analyzing uploaded data..."):
            cycles = detect_cycles(df)                    
            results = analyze_all_cycles(df, cycles)
            stats = calculate_statistics(results)
    
    st.markdown("---")
    # Dynamic Key Parameters - ALL CALCULATED FROM DATA
    st.markdown("### ⚙️ Key Parameters")
    
    # Calculate metrics dynamically
    total_data_points = len(df)
    max_pressure_drop = df['pressure_drop_bar'].max()
    min_pressure_drop = df['pressure_drop_bar'].min()
    avg_pressure_drop = df['pressure_drop_bar'].mean()
    
    # Calculate total cycles from your cycles list
    total_cycles = len(cycles)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Cycles",value=total_cycles,help="Number of cycles detected in dataset")
    with col2:
        st.metric(label="Data Points",value=f"{total_data_points:,}",help="Total measurements recorded")
    
    col3, col4 = st.columns(2)
    with col3:
        st.metric(label="Max ΔP",value=f"{max_pressure_drop:.2f} bar",help="Maximum pressure drop observed")
    with col4:
        st.metric(label="Avg ΔP", value=f"{avg_pressure_drop:.2f} bar",help="Average pressure drop across all data")
    st.markdown("---")
    
    # Dynamic Analysis Results
    st.markdown("### 📈 Analysis Results")
    
    col5, col6 = st.columns(2)
    with col5:
        st.metric(label="Mean Rate",value=f"{stats['Mean Rate']:.4f}",help="Average coking rate (bar/day)")
    with col6:
        st.metric(label="Std Dev",value=f"{stats['Standard Rate']:.4f}",help="Standard deviation of rates")
    col7, col8 = st.columns(2)
    with col7:
        st.metric(label="Min Rate",value=f"{stats['Minimum Rate']:.4f}",help="Lowest coking rate (bar/day)")
    with col8:
        st.metric(label="Max Rate",value=f"{stats['Maximum Rate']:.4f}",help="Highest coking rate (bar/day)")
    col9, col10 = st.columns(2)
    with col9:
        st.metric(label="Variance",value=f"{stats['Variance']:.2e}".replace("e-0", "e-"),help="Variance of Coking rate (bar/day)")
    with col10:
        st.metric(label="Coeff. of Variance",value=f"{stats['Coefficient of variance(%)']:.4f}",help="Coefficient of Variance of coking rate expressed in percerntage")
    # Cycle status breakdown
    cycles_above = sum(1 for r in results if r[1] >= stats['Mean Rate'])
    cycles_below = total_cycles - cycles_above
    
    st.markdown("**Cycle Breakdown:**")
    st.markdown(f"""<div style='font-size: 13px; line-height: 1.8;'>
            🔴 Above Average: <strong>{cycles_above}</strong> cycles<br>
            🟢 Below Average: <strong>{cycles_below}</strong> cycles
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Technologies Used
    st.markdown("### 🛠️ Technologies")
    st.markdown("""
        <div style='font-size: 13px; line-height: 2.2; color: #FFFFFF;'>
            <strong>Backend:</strong><br>
            • Python 3.11<br>
            • Pandas & NumPy<br>
            <br>
            <strong>Frontend:</strong><br>
            • Streamlit<br>
            • Plotly<br>
            <br>
            <strong>Analysis:</strong><br>
            • Linear Regression<br>
            • Statistical Modeling
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Project Info
    st.markdown("### 📚 Project Info")
    
    with st.expander("ℹ️ Methodology"):
        st.markdown("""
            **Analysis Steps:**
            1. Data preprocessing
            2. Cycle segmentation
            3. Linear regression fitting
            4. Coking rate calculation
            5. Statistical comparison
        """)
    
    with st.expander("📊 Expected CSV Format"):
        st.markdown("""
            Your CSV must have these columns:
            - `run_length_hours` (numeric)
            - `pressure_drop_bar` (numeric)
            
            **Optional columns:**
            - `cycle` (cycle number)
            - `temperature` (°C)
            - `flow_rate` (kg/h)
        """)
        st.code("run_length_hours,pressure_drop_bar\n12.5,0.45\n13.0,0.47", language="csv")
    
    st.markdown("---")
    
    st.markdown("### 📞 Connect")
    st.markdown("""
        <div style='font-size: 13px; line-height: 2.2;'>
            <a href='mailto:aayushshrivastava015@gmail.com' 
               style='text-decoration: none; color: #1f77b4; display: block;'>
                📧 Email Me
            </a>
            <a href='https://www.linkedin.com/in/aayush-shrivastava-a5568b346/?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3B6mDgA4BgRnqM%2BxgUlfPYbA%3D%3D' 
               style='text-decoration: none; color: #1f77b4; display: block;'>
                💼 LinkedIn Profile
            </a>
            <a href='https://github.com/Aayush-Shrivastava/steam-cracker-intelligence-dashboard' 
               style='text-decoration: none; color: #1f77b4; display: block;'>
                🔗 GitHub Repository
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer 
    st.markdown("""
        <div style='text-align: center; padding-top: 10px;'>
            <p style='font-size: 11px; color: #999; margin: 5px 0;'>
                <strong>Version 1.0</strong> • Decoking Module
            </p>
            <p style='font-size: 10px; color: #999; margin: 5px 0;'>
                © 2026 AAYUSH SHRIVASTAVA<br>
                2nd Year Chemical Engineering Student<br>
                BIT Mesra
            </p>
        </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────── HEADER ────────────────────────────────────────────────────

st.title('Steam Cracker Coking Analysis')
st.markdown('Pressure drop and coking rate intelligence across all run cycles.')
st.markdown('---')

# ────────────────────────────────── GLOBAL DECOKING THRESHOLD ─────────────────────────────────────────────────────

threshold = st.number_input("🎯 Set Decoking Threshold (bar) - applies to all graphs:",min_value=1.0,max_value=6.0,value=2.9,step=0.1,help="This threshold will be displayed on all relevant graphs")
st.markdown('---')

# ────────────────────────────────────────── CHARTS ─────────────────────────────────────────────────────

st.subheader('ΔP(bar) v/s Run Length(hr) for the last cycle')
fig1=plot_single_cycle(df,len(cycles),cycles,threshold)
st.plotly_chart(fig1, use_container_width=True)

st.subheader('Comparison of coking rates across all available cycles')
fig2=plot_rate_comparison(results,stats)
st.plotly_chart(fig2, use_container_width=True)

st.header('📊 Multi-Cycle Comparison')

total_cycles = len(cycles)
selected_cycles = st.multiselect("Select cycles to compare:",options=list(range(1, total_cycles + 1)),default=[1, 2], help=f"Choose 2-4 cycles for best visualization (Total available: {total_cycles})")

if len(selected_cycles) == 0:
    st.warning("⚠️ Please select at least one cycle to display")
elif len(selected_cycles) > 4:
    st.warning("⚠️ Too many cycles selected. Please choose 4 or fewer for clarity")
else:
    fig3 = multiple_plot_comparison(df, selected_cycles, cycles, threshold)
    st.plotly_chart(fig3, use_container_width=True)
    col_a, col_b = st.columns(2)
    with col_a:
        html_buffer = fig3.to_html()
        st.download_button(label="📥 Download as HTML",data=html_buffer,file_name="cycle_comparison.html",mime="text/html")

    with st.expander("📈 View Cycle Statistics"):
        for cycle_num in selected_cycles:
            cycle_index = cycle_num - 1
            start_idx, end_idx = cycles[cycle_index]
            cycle_data = df.loc[start_idx:end_idx].copy()
            slope, intercept = calculate_coking_rates(cycle_data)
            rate_bar_per_day = slope * 24
            final_dp = cycle_data['pressure_drop_bar'].iloc[-1]
            cycle_length = cycle_data['run_length_hours'].max()
            delta_dp = final_dp - intercept
            deviation = rate_bar_per_day - stats['Mean Rate']
            deviation_pct = (deviation / stats['Mean Rate']) * 100
            
            st.write(f"**Cycle {cycle_num}:**")
            st.write(f"- Coking Rate: {rate_bar_per_day:.4f} bar/day")
            st.write(f"- Initial ΔP: {intercept:.3f} bar")
            st.write(f"- Final ΔP: {final_dp:.3f} bar")
            st.write(f"- Total ΔP Change: {delta_dp:.3f} bar")
            st.write(f"- Cycle Length: {cycle_length:.1f} hours")
            st.write(f"- Data Points: {len(cycle_data)}")
            st.write(f"- Deviation from Mean: {deviation:+.4f} bar/day ({deviation_pct:+.1f}%)")
            st.write(f"- Performance: {'🔴 Above Average' if rate_bar_per_day >= stats['Mean Rate'] else '🟢 Below Average'}")
            st.write("---")