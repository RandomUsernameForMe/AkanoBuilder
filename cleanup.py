import os
import shutil

def cleanup():
    # Define paths relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'output')
    inputs_dir = os.path.join(base_dir, 'inputs')

    # 1. Clean output directory (remove everything)
    if os.path.exists(output_dir):
        print(f"Cleaning directory: {output_dir}")
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        print(f"Directory not found: {output_dir}")

    # 2. Clean inputs directory (remove everything except characters.csv)
    if os.path.exists(inputs_dir):
        print(f"Cleaning directory: {inputs_dir}")
        for filename in os.listdir(inputs_dir):
            if filename.lower() == 'characters.csv':
                print(f"Skipping: {filename}")
                continue
            
            file_path = os.path.join(inputs_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

if __name__ == "__main__":
    cleanup()
    print("Cleanup finished.")