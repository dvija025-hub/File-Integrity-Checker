import os
import hashlib
import json

HASH_FILE = "file_hashes.json"


# -----------------------------------------
# Task 1: Select and check the file
# -----------------------------------------
def select_file():
    file_path = input("Enter the file path: ").strip()

    if os.path.isfile(file_path):
        print("\nFile found successfully!")
        print("Selected file:", file_path)
        return file_path
    else:
        print("\nFile not found. Please check the file path.")
        return None


# -----------------------------------------
# Task 2: Generate SHA-256 hash
# -----------------------------------------
def generate_hash(file_path):
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            while True:
                data = file.read(4096)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()

    except Exception as e:
        print("Error while generating hash:", e)
        return None


# -----------------------------------------
# Task 3: Store the original hash
# -----------------------------------------
def save_hash(file_path, file_hash):

    # Load existing hashes
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, "r") as file:
                hashes = json.load(file)
        except:
            hashes = {}
    else:
        hashes = {}

    # Store file path and hash
    hashes[file_path] = file_hash

    # Save the updated data
    with open(HASH_FILE, "w") as file:
        json.dump(hashes, file, indent=4)

    print("\nOriginal hash saved successfully!")


# -----------------------------------------
# Task 4 & 5: Verify file integrity
# -----------------------------------------
def verify_file(file_path):

    # Check whether hash database exists
    if not os.path.exists(HASH_FILE):
        print("\nNo original hash found.")
        print("Please register the file first.")
        return

    # Read stored hashes
    with open(HASH_FILE, "r") as file:
        hashes = json.load(file)

    if file_path not in hashes:
        print("\nThis file is not registered yet.")
        return

    original_hash = hashes[file_path]

    # Generate current hash
    current_hash = generate_hash(file_path)

    if current_hash is None:
        return

    print("\nOriginal Hash:")
    print(original_hash)

    print("\nCurrent Hash:")
    print(current_hash)

    # Compare hashes
    if original_hash == current_hash:
        print("\n✓ FILE INTEGRITY VERIFIED")
        print("The file has NOT been modified.")
    else:
        print("\n⚠ FILE INTEGRITY COMPROMISED")
        print("The file has been modified!")


# -----------------------------------------
# Main Program
# -----------------------------------------
def main():

    while True:

        print("\n================================")
        print("      FILE INTEGRITY CHECKER")
        print("================================")

        print("1. Register a file")
        print("2. Verify a file")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()

        # Register file
        if choice == "1":

            file_path = select_file()

            if file_path:
                file_hash = generate_hash(file_path)

                if file_hash:
                    print("\nSHA-256 Hash:")
                    print(file_hash)

                    save_hash(file_path, file_hash)

        # Verify file
        elif choice == "2":

            file_path = select_file()

            if file_path:
                verify_file(file_path)

        # Exit
        elif choice == "3":
            print("\nThank you for using File Integrity Checker!")
            break

        else:
            print("\nInvalid choice. Please try again.")


# Start program
if __name__ == "__main__":
    main()