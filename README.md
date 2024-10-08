
# CV compilation

Currently this only compiles the number of publications using the csv from google scholar. 


# STEP 1: 
1. Go to your google scholar
2. Import the csv with all your publications
3. Remove all items that are not publications (e.g. conference proceedings)
4. Check the .csv named citations_core_do_not_erase  - these are the citations that are already cleaned. Makes sure there is no overlap and remove citations from the new csv.
> Note the code checks for duplicate anyway but it is better to remove them before running the code
4. save the csv in the `1_data` folder
This will be concatenated with the 'citations_core_do_not_erase '
5. A message will ask to double check if all entries are ok in the file citations_core_do_not_erase.csv that will be overwritten

## Usage:

Clone this repository
```bash
git clone laurentletg/cv_compilation.git
```
Create a virtual environment
```bash
python3 -m venv cv_compilation
source cv_compilation/bin/activate
```
Install requireqments
```bash
pip install -r requirements.txt
```
Run the script
```bash
python cv_compilation.py --names 'Letourneau' 'Létourneau' 'Guillon' 
# names to check for authorship
```
By default the code expects the following structure and will check for csv file in the `1_data` folder and save the output in the `3_output` folder.

```bash
├── 1_data
│   ├── citations-2.csv
│   └── citations_core_do_not_erase.csv
├── 3_output
```
the `1_data` directory is where csvs should be saved
