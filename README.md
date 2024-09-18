
# CV compilation

Currently this only compiles the number of publications using the csv from google scholar. 


# STEP 1: 
1. Go to your google scholar
2. Import the csv with all your publications
3. Remove all items that are not publications (e.g. conference proceedings)
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
python cv_compilation.py --names 'Letourneau' 'Létourneau' 'Guillon' # names to check for authorship
```

