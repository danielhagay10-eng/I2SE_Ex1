import os
import sys
import glob
import subprocess

def main():
    test_dir = "tests"
    
    if not os.path.exists(test_dir):
        print(f"Error: The '{test_dir}' folder does not exist.")
        sys.exit(1)

    # מציאת כל קבצי הטסטים בתיקייה
    test_files = glob.glob(os.path.join(test_dir, "test_*.py"))
    
    if not test_files:
        print(f"No tests found in '{test_dir}'.")
        sys.exit(1)

    print("--- Test Menu ---")
    print("0. Run ALL tests")
    for i, file_path in enumerate(test_files):
        print(f"{i+1}. Run {os.path.basename(file_path)}")

    try:
        choice = int(input("\nEnter number: "))
    except ValueError:
        print("Invalid input.")
        sys.exit(1)

    # הפעלת הפקודות דרך מודול subprocess כדי לדמות הקלדה בטרמינל
    if choice == 0:
        print("\nRunning ALL tests...\n" + "-"*30)
        subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", test_dir])
        
    elif 1 <= choice <= len(test_files):
        selected_test = test_files[choice-1]
        print(f"\nRunning {os.path.basename(selected_test)}...\n" + "-"*30)
        # המרת הנתיב לפורמט שמודול הטסטים של פייתון דורש
        test_module = selected_test.replace(".py", "").replace(os.sep, ".")
        subprocess.run([sys.executable, "-m", "unittest", selected_test])
        
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()