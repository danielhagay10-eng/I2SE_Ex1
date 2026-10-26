import csv

def generate_interactive_csv():
    try:
        num_rows = int(input("Enter number of planes to generate: "))
        
        print("\nChoose cut type:")
        print("1. Axial (Horizontal) - Z axis is constant")
        print("2. Sagittal (Side view) - X axis is constant")
        print("3. Coronal (Front view) - Y axis is constant")
        cut_type = input("Enter 1, 2, or 3: ")
        
        start_val = int(input("Enter starting coordinate (e.g., 0 to 129 for Z, or 0 to 255 for X/Y): "))
        step = int(input("Enter step size between planes (e.g., 1): "))
        
        filename = f"custom_planes_{num_rows}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Number of Points", "x1", "y1", "z1", "x2", "y2", "z2", "x3", "y3", "z3", "x4", "y4", "z4"])
            
            for i in range(num_rows):
                current_val = start_val + (i * step)
                
                if cut_type == '1': # חיתוך אופקי - Z משתנה בין מישורים
                    z_val = current_val % 130 
                    x1, y1, z1 = 0, 0, z_val
                    x2, y2, z2 = 255, 0, z_val
                    x3, y3, z3 = 0, 255, z_val
                    x4, y4, z4 = 255, 255, z_val
                    
                elif cut_type == '2': # חיתוך צדדי - X משתנה בין מישורים
                    x_val = current_val % 256
                    x1, y1, z1 = x_val, 0, 0
                    x2, y2, z2 = x_val, 255, 0
                    x3, y3, z3 = x_val, 0, 129
                    x4, y4, z4 = x_val, 255, 129
                    
                elif cut_type == '3': # חיתוך חזיתי - Y משתנה בין מישורים
                    y_val = current_val % 256
                    x1, y1, z1 = 0, y_val, 0
                    x2, y2, z2 = 255, y_val, 0
                    x3, y3, z3 = 0, y_val, 129
                    x4, y4, z4 = 255, y_val, 129
                    
                else:
                    print("Invalid choice, defaulting to Axial.")
                    break
                    
                writer.writerow([4, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4])
                
        print(f"\nSuccess! Created {filename} with {num_rows} planes.")
        
    except ValueError:
        print("Error: Please enter numbers only.")

if __name__ == "__main__":
    generate_interactive_csv()