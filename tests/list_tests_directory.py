import os

print("Contents of the 'tests' directory:")
for root, dirs, files in os.walk("tests"):
    for name in files:
        print(os.path.join(root, name))
