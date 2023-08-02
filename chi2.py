import numpy as np
import pandas as pd
from datetime import datetime
import csv
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import f_oneway
from scipy.stats import chi2_contingency

import pandas as pd

# Define a function to map a date to a season based on specific date ranges


def get_season(date):
    # Spring 21:  21 May - 14 June 2021
    # Summer 21:  21 June - 20 Sept 2021
    # Fall 21:    4 Oct - 4 Nov 2021
    # Spring 22   25 Mar - 12 May 2022
    if pd.Timestamp('2021-05-21') <= date <= pd.Timestamp('2021-06-14'):
        return 'Spring 2021'
    elif pd.Timestamp('2021-06-21') <= date <= pd.Timestamp('2021-09-20'):
        return 'Summer 2021'
    elif pd.Timestamp('2021-10-04') <= date <= pd.Timestamp('2021-11-04'):
        return 'Fall 2021'
    elif pd.Timestamp('2022-03-25') <= date <= pd.Timestamp('2022-05-12'):
        return 'Spring 2022'

    raise ValueError(f'Unhandled date {date}')


# Map the 'Day of the year' column to a new 'Season' column using the custom function
CSV = 'data/collection_species_host.csv'

data = pd.read_csv(CSV)

data['Collection_Date'] = pd.to_datetime(
    data['Collection_Date'], format="%m/%d/%y")
data['Month'] = data['Collection_Date'].dt.month

# Create a new column for the season
data['Season'] = data['Collection_Date'].apply(get_season)

print('TRANSFORMED DATA')
print(data)

# Get a list of unique mosquito species in the data
species = data['Species'].unique()

# Set the significance level for the chi-squared test
alpha = 0.05

# Perform a chi-squared test for each mosquito species
for s in species:
    # Create a contingency table for this species
    contingency_table = pd.crosstab(
        data[data['Species'] == s]['Host'],
        data[data['Species'] == s]['Season']
    )

    # Perform the chi-squared test
    chi2, p, dof, expected = chi2_contingency(contingency_table)

    print(f'\n---------------------- {s} -------------------------')

    print('\nCONTINGENCY TABLE')
    print(contingency_table)

    # Check if the p-value is below the significance level
    if p < alpha:
        print(
            f'\nThere is a significant association between the season and host bitten for {s} (p={p:.5f})')

        # Find the host with the highest proportion of bites for each season
        for season in seasons.values():
            season_data = data[(data['Species'] == s) &
                               (data['Season'] == season)]
            print('\nSEASON DATA')
            print(season_data)
            host_counts = season_data['Host'].value_counts(normalize=True)
            print('\nHOST COUNTS')
            print(host_counts)
            if not host_counts.empty:
                most_common_host = host_counts.idxmax()
                print(most_common_host)

                proportion = host_counts.max()
                print(
                    f'\nIn {season}, {s} bit {most_common_host} the most ({proportion:.2%} of bites)')
            else:
                print('Empty host counts')
    else:
        print(
            f'\nThere is no significant association between the season and host bitten for {s} (p={p:.5f})')
