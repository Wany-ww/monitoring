import pandas as pd
import numpy as np
import os
import datetime
import shutil

def generate_sample_data(base_path="data", num_equipments=2, days=3, rolls_per_day=2, bars_per_roll=3):
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)

    models = ["CL05B103KB54PCM", "CL10A106MQ8NNNC", "CL21A476MQYNNNE"]
    grades = ["A", "B", "C", "D"]
    grade_probs = [0.6, 0.25, 0.1, 0.05]
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=days-1)

    for equip_idx in range(1, num_equipments + 1):
        equip_name = f"5C{68 + equip_idx - 1}" # e.g., 5C68, 5C69
        
        region = np.random.choice(["천안", "기흥"])
        field = np.random.choice(["반도체", "배터리"])
        equip_type = np.random.choice(["세정기", "증착기", "식각기"])

        calc_path = os.path.join(base_path, region, field, equip_type, equip_name, "calc")
        data_path = os.path.join(base_path, region, field, equip_type, equip_name, "data")
        os.makedirs(calc_path)
        os.makedirs(data_path)

        for day in range(days):
            current_date = start_date + datetime.timedelta(days=day)
            date_str = current_date.strftime("%Y-%m-%d")
            
            for _ in range(rolls_per_day):
                model = np.random.choice(models)
                roll = f"ALC{np.random.randint(1000, 9999)}BAP"
                
                calc_rows = []
                data_rows = []
                
                time_offset_seconds = 0
                
                for bar_no in range(bars_per_roll):
                    bar_grade = np.random.choice(grades, p=grade_probs)
                    margin_pct = round(np.random.uniform(70.0, 95.0), 1)
                    
                    # calc data specific to this bar
                    # For simulating max deviation, D grade gets higher deviation
                    if bar_grade == 'D':
                        max_dev = round(np.random.uniform(50.0, 80.0), 1)
                    elif bar_grade == 'C':
                        max_dev = round(np.random.uniform(30.0, 50.0), 1)
                    else:
                        max_dev = round(np.random.uniform(5.0, 30.0), 1)
                        
                    calc_row = {
                        "날짜": date_str,
                        "설비 이름": equip_name,
                        "모델": model,
                        "ROLL": roll,
                        "Bar 번호": bar_no,
                        "Bar 등급": bar_grade,
                        "마진율 (%)": margin_pct,
                        "최대이탈값": max_dev
                    }
                    
                    for fp in range(1, 7):
                        calc_row[f"FP{fp} 최소 W 마진율 (%)"] = round(np.random.uniform(85.0, 98.0), 1) if np.random.random() > 0.1 else ""
                        calc_row[f"FP{fp} 최소 L 마진율 (%)"] = round(np.random.uniform(85.0, 98.0), 1) if np.random.random() > 0.1 else ""
                    
                    calc_rows.append(calc_row)
                    
                    # Data rows (layer by layer)
                    total_layer = np.random.randint(15, 30)
                    for layer in range(1, total_layer + 1):
                        bar_time = current_date + datetime.timedelta(seconds=time_offset_seconds)
                        time_offset_seconds += 1
                        
                        data_row = {
                            "DATE": date_str,
                            "TIME": bar_time.strftime("%H:%M:%S"),
                            "EQUIP_NAME": equip_name,
                            "MODEL": model,
                            "ROLL": roll,
                            "FIRST_LAYER": "TRUE" if layer == 1 else "FALSE",
                            "SAME_LAYER": "TRUE",
                            "LAYER_NO": layer,
                            "LAYER_NAME": "",
                        }
                        
                        # FP DX DY
                        for fp in range(1, 7):
                            dx = np.random.randint(-800, -200)
                            dy = np.random.randint(50, 500)
                            data_row[f"FP{fp}_DX"] = dx
                            data_row[f"FP{fp}_DY"] = dy
                            data_row[f"FP{fp}_ENABLE"] = 1
                            
                        data_row.update({
                            "AB_STACK_X": 1080,
                            "AB_STACK_Y": 0,
                            "TOTAL_LAYER": total_layer,
                            "W_MARGIN": 230,
                            "L_MARGIN": 260,
                            "BAR_NO": bar_no,
                            "MARGIN": margin_pct,
                            "GRADE": dict(zip(["A","B","C","D"], [1,2,3,4]))[bar_grade],
                            "TILT": round(np.random.uniform(0.0, 5.0), 2) if np.random.random() > 0.2 else "-",
                        })
                        
                        for fp in range(1, 7):
                            data_row[f"L_MARGIN{fp}"] = 90
                            data_row[f"W_MARGIN{fp}"] = 90
                            
                        data_rows.append(data_row)
                
                # Save files
                file_name = f"{date_str}_{roll}_{model}.csv"
                pd.DataFrame(calc_rows).to_csv(os.path.join(calc_path, file_name), index=False)
                pd.DataFrame(data_rows).to_csv(os.path.join(data_path, file_name), index=False)
                print(f"Generated {equip_name}/{calc_path}/{file_name}")

if __name__ == "__main__":
    print("Generating sample data with calc and data folders...")
    generate_sample_data()
    print("Done!")
