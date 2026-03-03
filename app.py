import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import glob
import os
import datetime

st.set_page_config(page_title="Equipment Data Pattern Analyzer", layout="wide")

@st.cache_data(ttl=60)
def load_data(data_dir="data"):
    all_files = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
    if not all_files:
        return pd.DataFrame()
    
    df_list = []
    for file in all_files:
        try:
            temp_df = pd.read_csv(file)
            
            # Extract metadata
            path_parts = os.path.split(file)
            file_name = path_parts[1]
            equipment_name = os.path.split(path_parts[0])[1]
            date_str = file_name.replace('.csv', '')
            
            temp_df['Equipment'] = equipment_name
            temp_df['Date'] = date_str
            df_list.append(temp_df)
        except Exception as e:
            st.warning(f"Error loading {file}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    df = pd.concat(df_list, ignore_index=True)
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    return df

st.title("Equipment Data Pattern Analyzer (EDPA)")

df = load_data()

if df.empty:
    st.warning("No Data: Please ensure CSV files exist in the 'data/{Equipment_Name}/' directory.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filters")

# Time Range
min_time = df['Time'].min()
max_time = df['Time'].max()
if pd.notna(min_time) and pd.notna(max_time):
    start_time, end_time = st.sidebar.slider(
        "Select Time Range",
        min_value=min_time.to_pydatetime(),
        max_value=max_time.to_pydatetime(),
        value=(min_time.to_pydatetime(), max_time.to_pydatetime())
    )
    df_filtered = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)]
else:
    df_filtered = df.copy()

# Equipment Selection
equipments = df_filtered['Equipment'].unique()
selected_equip = st.sidebar.multiselect("Select Equipment", equipments, default=equipments)

# Model Selection
if 'Model' in df_filtered.columns:
    models = df_filtered['Model'].unique()
    selected_model = st.sidebar.multiselect("Select Model", models, default=models)
else:
    selected_model = []

# Search
search_roll = st.sidebar.text_input("Search Roll No")
search_bar = st.sidebar.text_input("Search Bar No")

# Apply Filters
if selected_equip:
    df_filtered = df_filtered[df_filtered['Equipment'].isin(selected_equip)]
if selected_model:
    df_filtered = df_filtered[df_filtered['Model'].isin(selected_model)]
if search_roll and 'Roll' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['Roll'].astype(str).str.contains(search_roll)]
if search_bar and 'Bar No' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['Bar No'].astype(str).str.contains(search_bar)]

if df_filtered.empty:
    st.info("No Data matches the given filters.")
    st.stop()

# Main Dashboard
tab1, tab2, tab3, tab4 = st.tabs(["FP Coordinates", "Time Series", "Quality Analysis", "Correlation"])

with tab1:
    st.subheader("FP Coordinates Distribution")
    fp_choices = [f"FP{i}" for i in range(1, 7)]
    selected_fp = st.selectbox("Select FP Point", fp_choices)
    
    fp_x_col = f"{selected_fp} X"
    fp_y_col = f"{selected_fp} Y"
    
    if fp_x_col in df_filtered.columns and fp_y_col in df_filtered.columns:
        color_by = st.radio("Color By (FP)", ["Equipment", "Model"], horizontal=True)
        fig_fp = px.scatter(df_filtered, x=fp_x_col, y=fp_y_col, color=color_by, title=f"{selected_fp} Coordinates")
        st.plotly_chart(fig_fp, use_container_width=True)
    else:
        st.warning(f"Columns {fp_x_col} and/or {fp_y_col} not found in data.")

with tab2:
    st.subheader("Time Series Trend")
    if 'Time' in df_filtered.columns:
        y_axis_options = [col for col in df_filtered.columns if 'FP' in col and ('X' in col or 'Y' in col)]
        if y_axis_options:
            selected_y = st.selectbox("Select Metric for Trend", y_axis_options)
            color_by_trend = st.radio("Color By (Trend)", ["Equipment", "Model"], horizontal=True)
            fig_trend = px.line(df_filtered.sort_values("Time"), x="Time", y=selected_y, color=color_by_trend, markers=True, title=f"{selected_y} over Time")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("No numerical metrics available for Time Series.")
    else:
        st.warning("'Time' column is missing.")

with tab3:
    st.subheader("Quality Analysis (Bar Grade)")
    if 'Bar Grade' in df_filtered.columns:
        color_by_qual = st.radio("Group By (Quality)", ["Equipment", "Model"], horizontal=True)
        fig_box = px.box(df_filtered, x=color_by_qual, y="Bar Grade", color=color_by_qual, title="Bar Grade Distribution")
        st.plotly_chart(fig_box, use_container_width=True)
        
        fig_hist = px.histogram(df_filtered, x="Bar Grade", color=color_by_qual, barmode="group", title="Bar Grade Counts")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("'Bar Grade' column not found.")

with tab4:
    st.subheader("Correlation: Layer No vs Bar Grade")
    if 'Layer No' in df_filtered.columns and 'Bar Grade' in df_filtered.columns:
        fig_corr = px.scatter(df_filtered, x="Layer No", y="Bar Grade", color="Equipment", trendline="ols", title="Layer No vs Bar Grade")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("Required columns ('Layer No', 'Bar Grade') are missing.")
