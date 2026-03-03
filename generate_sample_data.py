import pandas as pd
import numpy as np
import os
import datetime

def generate_sample_data(base_path="data", num_equipments=2, days=3, rows_per_day=100):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    models = ["Model_A", "Model_B", "Model_C"]
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=days)

    for equip_idx in range(1, num_equipments + 1):
        equip_name = f"EQ_{equip_idx:03d}"
        equip_path = os.path.join(base_path, equip_name)
        if not os.path.exists(equip_path):
            os.makedirs(equip_path)

        for day in range(days):
            current_date = start_date + datetime.timedelta(days=day)
            date_str = current_date.strftime("%Y-%m-%d")
            
            data = []
            for i in range(rows_per_day):
                time = current_date + datetime.timedelta(minutes=i*15)
                model = np.random.choice(models)
                roll = f"R{np.random.randint(1000, 9999)}"
                bar_no = f"B{np.random.randint(100, 999)}"
                layer_no = np.random.randint(1, 10)
                total_layer = 10
                l_margin = np.random.uniform(0.5, 2.0)
                w_margin = np.random.uniform(0.5, 2.0)
                layer_pattern = f"P{np.random.randint(1, 5)}"
                ab_stack_x = np.random.uniform(10, 50)
                ab_stack_y = np.random.uniform(10, 50)
                
                row = {
                    "Time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Model": model,
                    "Roll": roll,
                    "Bar No": bar_no,
                    "Layer No": layer_no,
                    "Total Layer": total_layer,
                    "L Margin": l_margin,
                    "W Margin": w_margin,
                    "Layer Pattern": layer_pattern,
                    "AB Stack X": ab_stack_x,
                    "AB Stack Y": ab_stack_y,
                }
                
                for fp in range(1, 7):
                    row[f"FP{fp} X"] = np.random.normal(0, 1) + (fp * 10)
                    row[f"FP{fp} Y"] = np.random.normal(0, 1) + (fp * 10)
                    
                row["Bar Grade"] = np.random.choice(["A", "B", "C", "D"], p=[0.5, 0.3, 0.15, 0.05])
                
                data.append(row)
                
            df = pd.DataFrame(data)
            file_path = os.path.join(equip_path, f"{date_str}.csv")
            df.to_csv(file_path, index=False)
            print(f"Generated sample data: {file_path}")

if __name__ == "__main__":
    print("Generating sample data...")
    generate_sample_data()
    print("Done!")
