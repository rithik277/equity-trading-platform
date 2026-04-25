# setup.py
# Runs automatically on Render to build the dataset
# before the dashboard starts

import subprocess
import os

def build():
    print("Building dataset...")
    subprocess.run(["python", "data_builder.py"], check=True)
    
    print("Building database...")
    subprocess.run(["python", "db_builder.py"], check=True)
    
    print("Setup complete!")

if __name__ == "__main__":
    build()