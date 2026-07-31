#/usr/bin/python

#Script used to add header to csv files from archideck import.

from pathlib import Path



# The header you want every CSV file to have
HEADER = "Quantity,Name,Set,SetCode,CollectorNumber,Category,SecondaryCategory,Label,Price,Collection,Modifier,Salt,Color,Manavalue,Rarity,ScryfallCode,Cardtypes"

LOG = open("LOG_editing_header.txt","a")

csv_files = Path(".").glob("*.csv")
#print(type(csv_files))
#print(("Found the following files:" , ";".join(csv_files)), file=LOG)
# Search all CSV files in the current directory
for csv_file in csv_files:
    print(f"Checking {csv_file.name}...", file=LOG)

    # Read the file
    with open(csv_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        #print(lines)
        print(lines[0], file=LOG)
        lines = [line.strip().strip('"') + "\n" for line in lines]
        print("Altering\n\n",file=LOG)
        print(lines[0], file=LOG)
    # Skip empty files
    if not lines:
        print("  File is empty. Adding header.")
        lines = [HEADER + "\n"]
    elif lines[0].strip() != HEADER:
        print("Header missing. Adding it.", file=LOG)
        lines.insert(0, HEADER + "\n")
    else:
        print("  Header already present.", file=LOG)
        continue

    # Write the modified file back
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)

print("Done.", file=LOG)
LOG.close()
