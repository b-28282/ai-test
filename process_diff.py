import sys

def process_diff(file_path):
    with open(file_path, 'r') as f:
        diff = f.read()
    
    print("Processing diff...")
    print(diff[:500])  # Print first 500 chars for preview

    # Example: Extract modified files
    modified_files = [line.split()[-1] for line in diff.splitlines() if line.startswith("diff --git")]
    
    print("Modified files:", modified_files)

if __name__ == "__main__":
    process_diff(sys.argv[1])
