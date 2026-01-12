import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 

BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

print(SCRIPT_DIR)
print(BASE_DIR)
print(OUTPUT_DIR)