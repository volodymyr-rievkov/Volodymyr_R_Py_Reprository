import os

FILE_PATH = "DP/Lab_2/utils"
FILES_DIR = os.path.join(FILE_PATH, "files")

os.makedirs(FILES_DIR, exist_ok=True)


def generate_file(size_mb: int, folder_path: str = FILES_DIR):
    filename = os.path.join(folder_path, f"test_{size_mb}mb.txt")
    with open(filename, "wb") as f:
        f.write(b"0" * size_mb * 1024 * 1024)
    print(f"✅ Created {filename} ({size_mb} MB)")


if __name__ == "__main__":
    generate_file(1)
    generate_file(10)
    generate_file(100)
    generate_file(1000)
