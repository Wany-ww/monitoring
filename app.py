import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import glob
import os
import datetime

st.set_page_config(page_title="Custom Dashboard App", layout="wide")

@st.cache_data(ttl=60)
def load_data(data_dir="data"):
    calc_files = glob.glob(os.path.join(data_dir, "**", "calc", "*.csv"), recursive=True)
    data_files = glob.glob(os.path.join(data_dir, "**", "data", "*.csv"), recursive=True)
    
    df_calc_list = []
    for f in calc_files:
        try:
            df = pd.read_csv(f)
            p = os.path.normpath(f).split(os.sep)
            if len(p) >= 6:
                df['지역'] = p[-6]
                df['분야'] = p[-5]
                df['설비종류'] = p[-4]
            df_calc_list.append(df)
        except:
            pass
            
    df_data_list = []
    for f in data_files:
        try:
            df = pd.read_csv(f)
            p = os.path.normpath(f).split(os.sep)
            if len(p) >= 6:
                df['지역'] = p[-6]
                df['분야'] = p[-5]
                df['설비종류'] = p[-4]
            df_data_list.append(df)
        except:
            pass
            
    df_calc = pd.concat(df_calc_list, ignore_index=True) if df_calc_list else pd.DataFrame()
    df_data = pd.concat(df_data_list, ignore_index=True) if df_data_list else pd.DataFrame()
    
    if not df_calc.empty:
        df_calc['날짜'] = pd.to_datetime(df_calc['날짜'])
    if not df_data.empty:
        df_data['DATE'] = pd.to_datetime(df_data['DATE'])
        # Time column to datetime
        df_data['DATETIME'] = pd.to_datetime(df_data['DATE'].dt.strftime('%Y-%m-%d') + ' ' + df_data['TIME'])

    return df_calc, df_data

st.title("Equipment Monitoring Dashboard")

df_calc, df_data = load_data()

if df_calc.empty or df_data.empty:
    st.warning("No data found. Please run the generation script.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

# Date Filter
min_date = df_calc['날짜'].min()
max_date = df_calc['날짜'].max()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter DataFrames by Date
df_c = df_calc[(df_calc['날짜'] >= start_date) & (df_calc['날짜'] <= end_date)]
df_d = df_data[(df_data['DATE'] >= start_date) & (df_data['DATE'] <= end_date)]

if '지역' in df_c.columns:
    regions = df_c['지역'].unique()
    selected_region = st.sidebar.multiselect("Select Region", regions, default=regions)
    if selected_region:
        df_c = df_c[df_c['지역'].isin(selected_region)]
        df_d = df_d[df_d['지역'].isin(selected_region)]

if '분야' in df_c.columns:
    fields = df_c['분야'].unique()
    selected_field = st.sidebar.multiselect("Select Field", fields, default=fields)
    if selected_field:
        df_c = df_c[df_c['분야'].isin(selected_field)]
        df_d = df_d[df_d['분야'].isin(selected_field)]

if '설비종류' in df_c.columns:
    types = df_c['설비종류'].unique()
    selected_type = st.sidebar.multiselect("Select Equip Type", types, default=types)
    if selected_type:
        df_c = df_c[df_c['설비종류'].isin(selected_type)]
        df_d = df_d[df_d['설비종류'].isin(selected_type)]

equipments = df_c['설비 이름'].unique()
selected_equip = st.sidebar.multiselect("Select Equipment", equipments, default=equipments)
if selected_equip:
    df_c = df_c[df_c['설비 이름'].isin(selected_equip)]
    df_d = df_d[df_d['EQUIP_NAME'].isin(selected_equip)]

models = df_c['모델'].unique()
selected_model = st.sidebar.multiselect("Select Model", models, default=models)
if selected_model:
    df_c = df_c[df_c['모델'].isin(selected_model)]
    df_d = df_d[df_d['MODEL'].isin(selected_model)]

rolls = df_c['ROLL'].unique()
selected_roll = st.sidebar.multiselect("Select Roll", rolls, default=rolls)
if selected_roll:
    df_c = df_c[df_c['ROLL'].isin(selected_roll)]
    df_d = df_d[df_d['ROLL'].isin(selected_roll)]

bars = df_c['Bar 번호'].unique()
selected_bar = st.sidebar.multiselect("Select Bar No", bars, default=bars)
if selected_bar:
    df_c = df_c[df_c['Bar 번호'].isin(selected_bar)]
    df_d = df_d[df_d['BAR_NO'].isin(selected_bar)]


# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["3D Coordinates (Bar Level)", "Max Deviation Table", "Trend: Deviation & Tilt", "Grade D Frequency"])

# --- TAB 1: 3D Plot & Raw Data ---
with tab1:
    st.subheader("Data Analysis - 3D Coordinates")
    st.write("Displays FP1 ~ FP6 (x, y) coordinates for each Layer (z) based on the filtered Bar.")
    
    if len(selected_bar) != 1 or len(selected_roll) != 1:
        st.info("Please select exactly one Roll and one Bar No to view the 3D plot and raw data.")
    else:
        # We need a specific Bar for this
        bar_data = df_d.copy()
        
        if not bar_data.empty:
            # Prepare data for 3D plot
            plot_data = []
            for fp in range(1, 7):
                temp = bar_data[['LAYER_NO', f'FP{fp}_DX', f'FP{fp}_DY']].copy()
                temp.columns = ['Z', 'X', 'Y']
                temp['FP'] = f'FP{fp}'
                plot_data.append(temp)
                
            plot_df = pd.concat(plot_data)
            
            plot_df['FP_num'] = plot_df['FP'].str.extract(r'(\d+)').astype(int)
            plot_df = plot_df.sort_values(['Z', 'FP_num'])
            
            fig_3d = go.Figure()
            
            # Add line connecting FPs per layer based on spatial angle to form a polygon/rectangle
            for layer in plot_df['Z'].unique():
                layer_data = plot_df[plot_df['Z'] == layer].copy()
                if not layer_data.empty:
                    # Calculate centroid for angular sorting
                    cx = layer_data['X'].mean()
                    cy = layer_data['Y'].mean()
                    # Calculate angle
                    layer_data['angle'] = np.arctan2(layer_data['Y'] - cy, layer_data['X'] - cx)
                    # Sort points to form an ordered boundary
                    layer_data = layer_data.sort_values('angle')
                    
                    # To make a closed polygon, append the first point at the end
                    layer_data = pd.concat([layer_data, layer_data.iloc[[0]]])
                    
                    fig_3d.add_trace(go.Scatter3d(
                        x=layer_data['X'],
                        y=layer_data['Y'],
                        z=layer_data['Z'],
                        mode='lines',
                        line=dict(color='gray', width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
            
            # Add Scatter points colored by FP
            for fp in plot_df['FP'].unique():
                fp_data = plot_df[plot_df['FP'] == fp]
                fig_3d.add_trace(go.Scatter3d(
                    x=fp_data['X'],
                    y=fp_data['Y'],
                    z=fp_data['Z'],
                    mode='markers',
                    name=fp,
                    marker=dict(size=4) # Reduced marker size
                ))
                
            fig_3d.update_layout(
                title=f"3D Scatter: Roll {selected_roll[0]}, Bar {selected_bar[0]}",
                margin=dict(l=0, r=0, b=0, t=40)
            )
            st.plotly_chart(fig_3d, use_container_width=True)            
            st.markdown("---")
            st.subheader("Raw Data Table")
            st.dataframe(bar_data, use_container_width=True)
        else:
            st.warning("No data found for the selected Bar.")

# --- TAB 2: Max Deviation Table ---
with tab2:
    st.subheader("Max Deviation per Equipment")
    st.write("Finding the row with the maximum '최대이탈값' within the selected date range for each equipment.")
    
    if not df_c.empty:
        idx = df_c.groupby("설비 이름")["최대이탈값"].idxmax()
        max_dev_df = df_c.loc[idx, ["날짜", "설비 이름", "모델", "ROLL", "Bar 번호", "최대이탈값", "Bar 등급"]]
        max_dev_df = max_dev_df.sort_values(by="최대이탈값", ascending=False).reset_index(drop=True)
        max_dev_df['날짜'] = max_dev_df['날짜'].dt.strftime('%Y-%m-%d')
        st.dataframe(max_dev_df, use_container_width=True)
    else:
        st.warning("No Calc Data available.")

# --- TAB 3: Deviation & Tilt Trend ---
with tab3:
    st.subheader("Trend over Time: Max Deviation and TILT")
    st.write("D Grade points are highlighted with large red markers.")
    
    if not df_d.empty and not df_c.empty:
        # We need to merge df_d and df_c to get '최대이탈값' (from calc) and 'TILT', 'DATETIME' (from data)
        # However, data has layer-level info. We probably want Bar-level aggregation or just taking the first row of each bar.
        df_d_bar = df_d.drop_duplicates(subset=["DATE", "EQUIP_NAME", "MODEL", "ROLL", "BAR_NO"], keep="first")
        
        # Merge
        merged = pd.merge(df_c, df_d_bar, left_on=["날짜", "설비 이름", "모델", "ROLL", "Bar 번호"], right_on=["DATE", "EQUIP_NAME", "MODEL", "ROLL", "BAR_NO"], how="inner")
        
        if not merged.empty:
            merged = merged.sort_values("DATETIME")
            
            # Map Grade integer to string if needed, calc 'Bar 등급' already has A, B, C, D
            color_map = {"A": "blue", "B": "green", "C": "orange", "D": "red"}
            merged['TILT_Num'] = pd.to_numeric(merged['TILT'], errors='coerce')
            
            for equip in merged["설비 이름"].unique():
                st.markdown(f"### 설비: {equip}")
                merged_equip = merged[merged["설비 이름"] == equip]
                
                # We will use Plotly Graph Objects to have fine control over marker sizes
                fig_trend = go.Figure()
                
                for grade in ["A", "B", "C", "D"]:
                    subset = merged_equip[merged_equip["Bar 등급"] == grade]
                    if subset.empty: continue
                    
                    size = 15 if grade == "D" else 6
                    marker_symbol = "diamond" if grade == "D" else "circle"
                    
                    fig_trend.add_trace(go.Scatter(
                        x=subset["DATETIME"],
                        y=subset["최대이탈값"],
                        mode="markers+text",
                        name=f"Max Dev (Grade {grade})",
                        marker=dict(color=color_map[grade], size=size, symbol=marker_symbol),
                        text=subset["Bar 등급"] if grade == "D" else "",
                        textposition="top center"
                    ))
                
                # Optionally add TILT on secondary Y axis
                fig_trend.update_layout(title=f"Max Deviation Over Time - {equip}", xaxis_title="Time", yaxis_title="Max Deviation (최대이탈값)")
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # TILT Over Time
                fig_tilt = px.scatter(merged_equip, x="DATETIME", y="TILT_Num", color="Bar 등급", color_discrete_map=color_map, title=f"TILT Value Over Time - {equip}")
                
                # Emphasize D
                fig_tilt.update_traces(marker=dict(size=6))
                for i, trace in enumerate(fig_tilt.data):
                    if trace.name == 'D':
                        trace.marker.size = 15
                        trace.marker.symbol = 'diamond'
                
                st.plotly_chart(fig_tilt, use_container_width=True)
                st.markdown("---")
            
        else:
            st.warning("Could not merge Calc and Data tables for Trend analysis.")
    else:
        st.warning("Insufficient data for Trend analysis.")

# --- TAB 4: Grade D Frequency ---
with tab4:
    st.subheader("Grade D Frequency")
    st.write("Frequency of Grade D occurrences per Equipment and Bar.")
    
    if not df_c.empty:
        # Filter only Grade D
        grade_d = df_c[df_c["Bar 등급"] == "D"]
        if not grade_d.empty:
            for equip in grade_d["설비 이름"].unique():
                st.markdown(f"### 설비: {equip}")
                grade_d_equip = grade_d[grade_d["설비 이름"] == equip]
                
                # Group by Equipment and Date
                freq_df = grade_d_equip.groupby(["날짜"]).size().reset_index(name="D Grade Count")
                freq_df["날짜"] = freq_df["날짜"].dt.strftime('%Y-%m-%d') if pd.api.types.is_datetime64_any_dtype(freq_df["날짜"]) else freq_df["날짜"].astype(str)
                
                fig_freq = px.bar(freq_df, x="날짜", y="D Grade Count", title=f"Frequency of D Grade per Date - {equip}")
                fig_freq.update_xaxes(type='category')
                st.plotly_chart(fig_freq, use_container_width=True)
                st.markdown("---")
        else:
            st.info("No Grade D occurrences found in the selected specific filters.")
    else:
        st.warning("No Calc Data available.")
