#/usr/bin/python

#Script used to add header to csv files from archideck import.

from pathlib import Path



# The header you want every CSV file to have
HEADER = "Quantity,Name,Set,SetCode;CollectorNumner,Category,SecondaryCategory,Label,Price;Collection,Modifier,Salt,Color,Manavalue,Rarity,ScryfallCode,Cardtypes,Cardtext"

csv_files = Path(".").glob("*.csv")

# Search all CSV files in the current directory
for csv_file in csv_files:
    print(f"Checking {csv_file.name}...")

    # Read the file
    with open(csv_file, "r", newline="") as f:
        lines = f.readlines()
        print(lines)

    # Skip empty files
    if not lines:
        print("  File is empty. Adding header.")
        lines = [HEADER + "\n"]
    elif lines[0].strip() != HEADER:
        print("Header missing. Adding it.")
        lines.insert(0, HEADER + "\n")
    else:
        print("  Header already present.")
        continue

    # Write the modified file back
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)

print("Done.")