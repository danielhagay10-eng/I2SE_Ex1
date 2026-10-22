import csv

def generate_large_csv(filename, num_planes=100):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        # ניצור 100 מישורים שמתקדמים בציר ה-Z כדי "לסרוק" את המוח
        for z in range(10, 10 + num_planes):
            # נקודה a, נקודה b, נקודה c (מרחקים של 150 אחד מהשני)
            row = [50, 50, z, 200, 50, z, 50, 200, z]
            writer.writerow(row)
    print(f"Created {filename} with {num_planes} planes.")

if __name__ == "__main__":
    generate_large_csv("big_planes.csv", 100)