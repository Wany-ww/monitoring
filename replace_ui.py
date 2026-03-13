import sys
import pandas as pd

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_ui = """
st.markdown("## Dashboard Overview")
col1, col2 = st.columns([1, 1])

# --- Row 1: Max Deviation & 3D Coordinates
with col1:
    st.subheader("Max Deviation per Equipment")
    if not df_c.empty:
        idx = df_c.groupby("설비 이름")["최대이탈값"].idxmax()
        max_dev_df = df_c.loc[idx, ["날짜", "설비 이름", "모델", "ROLL", "Bar 번호", "최대이탈값", "Bar 등급"]]
        max_dev_df = max_dev_df.sort_values(by="최대이탈값", ascending=False).reset_index(drop=True)
        max_dev_df['날짜'] = max_dev_df['날짜'].dt.strftime('%Y-%m-%d')
        st.dataframe(max_dev_df, use_container_width=True)
    else:
        st.warning("No Calc Data available.")

with col2:
    st.subheader("Data Analysis - 3D Coordinates")
    if len(selected_bar) != 1 or len(selected_roll) != 1:
        st.info("Select exactly one Roll and one Bar No to view the 3D plot and raw data.")
    else:
        bar_data = df_d.copy()
        if not bar_data.empty:
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
            for layer in plot_df['Z'].unique():
                layer_data = plot_df[plot_df['Z'] == layer].copy()
                if not layer_data.empty:
                    cx = layer_data['X'].mean()
                    cy = layer_data['Y'].mean()
                    layer_data['angle'] = np.arctan2(layer_data['Y'] - cy, layer_data['X'] - cx)
                    layer_data = layer_data.sort_values('angle')
                    layer_data = pd.concat([layer_data, layer_data.iloc[[0]]])
                    fig_3d.add_trace(go.Scatter3d(x=layer_data['X'], y=layer_data['Y'], z=layer_data['Z'], mode='lines', line=dict(color='gray', width=2), showlegend=False, hoverinfo='skip'))
            for fp in plot_df['FP'].unique():
                fp_data = plot_df[plot_df['FP'] == fp]
                fig_3d.add_trace(go.Scatter3d(x=fp_data['X'], y=fp_data['Y'], z=fp_data['Z'], mode='markers', name=fp, marker=dict(size=4)))
            fig_3d.update_layout(title=f"3D Scatter: Roll {selected_roll[0]}, Bar {selected_bar[0]}", margin=dict(l=0, r=0, b=0, t=40), height=400)
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            st.warning("No data found for the selected Bar.")

st.markdown("---")
st.markdown("## Equipment Analysis")

if not df_d.empty and not df_c.empty:
    df_d_bar = df_d.drop_duplicates(subset=["DATE", "EQUIP_NAME", "MODEL", "ROLL", "BAR_NO"], keep="first")
    merged = pd.merge(df_c, df_d_bar, left_on=["날짜", "설비 이름", "모델", "ROLL", "Bar 번호"], right_on=["DATE", "EQUIP_NAME", "MODEL", "ROLL", "BAR_NO"], how="inner")
    
    if not merged.empty:
        merged = merged.sort_values("DATETIME")
        color_map = {"A": "blue", "B": "green", "C": "orange", "D": "red"}
        merged['TILT_Num'] = pd.to_numeric(merged['TILT'], errors='coerce')
        grade_d = df_c[df_c["Bar 등급"] == "D"]
        
        for equip in merged["설비 이름"].unique():
            st.markdown(f"### 설비: {equip}")
            col3, col4 = st.columns(2)
            
            merged_equip = merged[merged["설비 이름"] == equip]
            
            with col3:
                # Grade D Frequency
                if not grade_d.empty:
                    grade_d_equip = grade_d[grade_d["설비 이름"] == equip]
                    if not grade_d_equip.empty:
                        freq_df = grade_d_equip.groupby(["날짜"]).size().reset_index(name="D Grade Count")
                        freq_df["날짜"] = freq_df["날짜"].dt.strftime('%Y-%m-%d') if pd.api.types.is_datetime64_any_dtype(freq_df["날짜"]) else freq_df["날짜"].astype(str)
                        fig_freq = px.bar(freq_df, x="날짜", y="D Grade Count", title=f"Frequency of D Grade per Date - {equip}")
                        fig_freq.update_xaxes(type='category')
                        st.plotly_chart(fig_freq, use_container_width=True)
                    else:
                        st.info("No Grade D occurrences found.")
                else:
                    st.info("No Grade D occurrences found.")
                
                # TILT Value Over Time
                fig_tilt = px.scatter(merged_equip, x="DATETIME", y="TILT_Num", color="Bar 등급", color_discrete_map=color_map, title=f"TILT Value Over Time - {equip}")
                fig_tilt.update_traces(marker=dict(size=6))
                for i, trace in enumerate(fig_tilt.data):
                    if trace.name == 'D':
                        trace.marker.size = 15
                        trace.marker.symbol = 'diamond'
                st.plotly_chart(fig_tilt, use_container_width=True)
                
            with col4:
                # Max Deviation Trend
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
                fig_trend.update_layout(title=f"Max Deviation Over Time - {equip}", xaxis_title="Time", yaxis_title="Max Deviation (최대이탈값)")
                st.plotly_chart(fig_trend, use_container_width=True)

            st.markdown("---")
else:
    st.warning("Insufficient data for Equipment Analysis.")
"""

out = []
for line in lines:
    if line.startswith("# --- TABS ---") or line.startswith("tab1,"):
        break
    out.append(line)

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(out)
    f.write(new_ui)
