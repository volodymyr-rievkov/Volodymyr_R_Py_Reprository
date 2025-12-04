import os

FILE_PATH = "DP/Lab_2/utils"
FILES_DIR = os.path.join(FILE_PATH, "files")

SIZES = [1, 10, 100, 1000]

os.makedirs(FILES_DIR, exist_ok=True)


def generate_file(size_mb: int, folder_path: str = FILES_DIR):
    filename = os.path.join(folder_path, f"test_{size_mb}mb.txt")
    with open(filename, "wb") as f:
        f.write(b"0" * size_mb * 1024 * 1024)
    print(f"✅ Created {filename} ({size_mb} MB)")

def main():
    for size_mb in SIZES:
        generate_file(size_mb)

if __name__ == "__main__":
    main()
