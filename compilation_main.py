import pandas as pd
import os
import argparse
import logging
import glob
import pprint
from datetime import datetime
from functools import reduce

PATH = os.path.dirname(os.path.abspath(__file__))

DATA = os.path.join(PATH, '1_data')
OUTPUT= os.path.join(PATH, '3_output')

def get_logger(level = logging.INFO):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def get_parser():
    parser = argparse.ArgumentParser(description="Data Exploration")
    parser.add_argument("--data_dir", type=str, default= DATA)
    parser.add_argument("--output_dir", type=str, default= OUTPUT)
    parser.add_argument("--date_cutoff", type=int, default= None,
                        help='Date cutoff for the data')
    parser.add_argument('--names', nargs='+', default=['Letourneau', 'Létourneau','Guillon'],
                        help='List of author names to check')

    return parser

def write_csv_for_each_year_cutoffs(output_dir, df_list, years):
    for i, j in zip(df_list, years):
        i.to_csv(os.path.join(output_dir, 'Publications since {}.csv'.format(j)))


def get_df_list_per_year(df_core, years):
    df_list = []
    for year in years:
        is_year = df_core['Year'] >= year
        df_year = df_core[is_year]
        df_list.append(df_year)
    return df_list


def get_author_list(df_list):
    author_list = []
    for i in df_list:
        b = i['Authors'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        a = b.to_list()
        author_list.append(a)
    return author_list

def process_author_list(author_list):
    processed_list = []
    for entry in author_list:
        # Split the entry into individual authors
        authors = entry.split(';')
        # Remove the last author if it's empty or just whitespace
        if authors and not authors[-1].strip():
            authors.pop()
        # Join the authors back together and add to the processed list
        processed_list.append('; '.join(authors))
    return processed_list

def get_authorship_numbers(years,author_list, output_dir, names, logger):
    df_list_authors = []
    for a, j in zip(years, author_list):
        list_first_author = []
        list_senior_author = []
        list_potential_senior_to_check =[]
        list_co_author = []

        print(j)
        # remove trailing empty string (often present in the data)
        processed_list = process_author_list(j)
        print('first author: {}'.format(processed_list[0]))
        for i in processed_list:
            str(i)
            i.strip()
            b = i.split(';')
            if b[0].strip().startswith(tuple(names)):
                print('yes this paper contains first author {}'.format(b))
                list_first_author.append(b)

            elif b[-1].strip().startswith(tuple(names)):
                print('Senior authorship: {}'.format(b))
                list_senior_author.append(b)
            # add the b[-2] IF CO-SENIOR AUTHORSHIP
            # If co-senior....
            # elif b[-2].strip().startswith(tuple(names)):
            #     print('potential_senior: {}'.format(b))
            #     list_potential_senior_to_check.append(b)

            else:
                print('co_author!')
                list_co_author.append(b)
            # In inner loop count the number of each publications
        fa = len(list_first_author)
        sa = len(list_senior_author)
        # potential_sa = len(list_potential_senior_to_check)
        ca = len(list_co_author)
        tot = len(list_senior_author) + len(list_first_author) + len(list_co_author)

        logger.info(f'First author {fa}')
        logger.info(f'Senior author {sa}')
        # logger.info(f'Potential senior author {potential_sa}')
        logger.info(f'Co-author {ca}')
        logger.info(f'Total {tot}')

        # put in a list
        lst_num_papers = [fa, sa, ca,  tot]

        df_summary = pd.DataFrame({'Catégorie': ['Premier auteur', 'Auteur sénior',  'Co-auteur', 'Total'],
                                   'Nombre depuis {}'.format(a): lst_num_papers})
        df_list_authors.append(df_summary)
        df_summary.to_csv(os.path.join(output_dir, 'Nombre de publications depuis {}.csv'.format(a)))

    return df_list_authors


def merge_authorship(df_list_authors, output_dir, logger):
    df_merged = reduce(lambda left, right: pd.merge(left, right, on=['Catégorie'],
                                                    how='outer'), df_list_authors)

    df_merged.to_csv(os.path.join(output_dir, 'summary_of_publications.csv'))
    df_merged.to_excel(os.path.join(output_dir, 'summary_of_publications.xlsx'))

    logger.info(f'Wrote csv and excel files here: {output_dir}')



def main():
    logger = get_logger(logging.DEBUG)


    logger.info('Initializing data extraction')

    parser = get_parser()
    args = parser.parse_args()

    logger.debug(f'data: {args.data_dir}')
    logger.debug(f'output: {args.output_dir}')

    # Get the core cleaned .csv before updating with new entries
    core_filename = os.path.join(args.data_dir, 'citations_core_do_not_erase.csv')
    logger.debug(f'Core filename: {core_filename}')
    df_core = pd.read_csv(os.path.join(args.data_dir, core_filename),
                          encoding='utf-8-sig')
    logger.debug(f'Core shape: {df_core.shape}')
    #get latest csv in DATA
    csvs = glob.glob(os.path.join(args.data_dir, '*.csv'))
    csvs = [i for i in csvs if 'citations_core_do_not_erase' not in i]
    if not csvs:
        logger.error(f'No new csv files found in {args.data_dir}')
    pprint.pp(csvs)
    logger.debug(csvs)

    latest_csv = max([f for f in csvs], key=os.path.getctime)
    logging.info(f'Found this latest csv: {latest_csv}')
    df_updated = pd.read_csv(os.path.join(args.data_dir, latest_csv),
                             encoding='utf-8-sig')

    logger.debug(f'Updated shape: {df_updated.shape}')

    # Append with updated dataframe
    df_core = df_core.append(df_updated, ignore_index=True)

    df_core.sort_values(by=['Year'], inplace=True, ascending=False)
    logger.info(df_core.head())

    logger.info(f'Checking the number of row prior to removing duplicates {df_core.shape[0]}')
    df_core = df_core.drop_duplicates()
    logger.info(f'Checking the number of row after removing duplicates {df_core.shape[0]}')


    df_core.to_csv(os.path.join(args.data_dir, 'citations_core_do_not_erase.csv'), index=False)
    check = input('Check the data before proceeding,\n'
                  'MAKE SURE ALL LINES ARE PUBLICATIONS,\n'
                  '***The current script does not consider co-senior authorship***,\n'
                  'You can put your name at the last position of the author list to be counted as senior authorship\n'
                  'Else the co-senior authorship will be counted as co-authorship\n'
                  '--> interrupt by pressing ctrl+c, press n to exit, press any key to continue')
    if check == 'n':
        logger.CRITICAL('Exiting')
        exit()

    current_year = datetime.now().year
    logger.info(f'Current year: {current_year}')

    years = [current_year - 20, current_year - 10, current_year - 5, current_year - 3, current_year - 2,
             current_year - 1]

    df_list = get_df_list_per_year(df_core, years)

    logger.info(f'Five entry for last year {df_list[-1].head().to_markdown()}')

    write_csv_for_each_year_cutoffs(args.output_dir, df_list, years)

    df_list = get_df_list_per_year(df_core, years)
    # logger.debug(f'df_list: {df_list}')

    authors_list = get_author_list(df_list)
    logger.info(f' authors list : {len(authors_list)}')

    df_list_authors = get_authorship_numbers(years, authors_list, args.output_dir, args.names,logger)
    # logger.info(f'len of df_list_authors: {len(df_list_authors)}')
    # logger.info(f'Number of papers: {df_list_authors}')

    merge_authorship(df_list_authors,args.output_dir,logger)

if __name__ == '__main__':
    main()