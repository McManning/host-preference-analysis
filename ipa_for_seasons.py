
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ipa import ipa
from ipa_bootstrap import ipa_bootstrap


# Rows for collection instances we skipped in the run_season()
# because there wasn't enough eBird density data to do math things.
skipped_collections = []

# Feature flag to change what data gets passed off to IPA
OMIT_PREY_NEVER_FED_ON = True

# Should it be ran with bootstrapping to get confidence intervals
# If false, results will be quicker but no extra data will be generated
WITH_BOOTSTRAP = True

EXPORTS_PATH = 'exports'
RESULTS_PATH = 'results'


def load_dataset(season, export_tag):
    """
    Load source files and generate an initial proportionality matrix for IPA,
    as well as a listing of sites and applicable prey for mapping back
    indices to human-readable values
    """
    sites = set()
    prey = set()

    # Dict[site, Dict[prey, count]]
    density = dict()

    # Dict[site, Dict[prey, count]]
    eaten = dict()

    # Pull in observation / eaten rows and aggregate distinct birds & sites

    # Generate a matrix of initial_preference and prey_at_site from data exports
    with open(f'{EXPORTS_PATH}/observed_birds_near_collection_site.csv', 'r', encoding='utf8') as f:
        # site_name, location, season, common_name, total_observed
        reader = csv.reader(f)
        for row in reader:
            if row[2] != season:
                continue

            site = row[0]
            common_name = row[3]

            # Aggregate into the density map
            if not density.get(site):
                density[site] = dict()

            if not density[site].get(common_name):
                density[site][common_name] = 0

            density[site][common_name] += int(row[4])
            prey.add(common_name)

    with open(f'{EXPORTS_PATH}/{export_tag}_eaten_birds_at_collection_site.csv', 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        # site_name, location, season, common_name, total_eaten
        for row in reader:
            if row[2] != season:
                continue

            site = row[0]
            common_name = row[3]

            # Aggregate into the eaten map
            # CAVEAT: If the bird is missing from the eBird density map
            # we DO NOT add the entry to the eaten table. The proportionality
            # equation cannot work if we can't get sufficient density info
            # for that particular bird (divides by zero)
            if not density.get(site) or not density[site].get(common_name):
                skipped_collections.append(row)
                print(
                    f'Skip collection for {common_name} at {site} - missing from density map')
                continue

            if not eaten.get(site):
                eaten[site] = dict()

            if not eaten[site].get(common_name):
                eaten[site][common_name] = 0

            eaten[site][common_name] += int(row[4])

            sites.add(site)
            prey.add(common_name)

    # Scrub out prey columns we don't need to care about
    if OMIT_PREY_NEVER_FED_ON:
        prey = set()
        for site in eaten:
            for p in eaten[site]:
                prey.add(p)

    # ['American Crow', 'American Goldfinch', ... 'Yellow-rumped Warbler']
    prey = sorted(list(prey))

    # ['Storage Site', ... 'Walcutt Run']
    sites = sorted(list(sites))

    # Matrix of prey present at each site
    # prey_at_site = np.zeros((len(sites), len(prey)))
    # for i in range(len(sites)):
    #     for j in range(len(prey)):
    #         site = sites[i]
    #         common_name = prey[j]
    #         if density[site].get(common_name):
    #             prey_at_site[i, j] = 1
    #         else:
    #             prey_at_site[i, j] = 0

    # Compute initial preference s.t. each row is normalized to 1.
    # This uses the proportionality equation where density is the
    # number of birds observed at that site and eaten is the
    # number bit from the sequencing results.
    initial_proportionality = np.zeros((len(sites), len(prey)))
    for i in range(len(sites)):
        denom = 0
        for j in range(len(prey)):
            site = sites[i]
            common_name = prey[j]

            # If prey type wasn't eaten, nothing to add to the denominator
            if not eaten[site].get(common_name):
                continue

            denom += eaten[site][common_name] / density[site][common_name]

        # print(f'Site {sites[i]}')
        # print(denom)

        for j in range(len(prey)):
            site = sites[i]
            common_name = prey[j]

            if not eaten[site].get(common_name):
                initial_proportionality[i, j] = -1  # Placeholder for IPA
            else:
                initial_proportionality[i, j] = (
                    eaten[site][common_name] / density[site][common_name]
                ) / denom

    return initial_proportionality, sites, prey


def run_season(season, export_tag):
    """
    Perform IPA for the given season data.
    """
    print(f'------------------------------------------------------------------------')
    print(
        f'------------------------------- {season} -------------------------------')

    initial_proportionality, sites, prey = load_dataset(season, export_tag)

    df = pd.DataFrame(initial_proportionality, columns=prey, index=sites)
    print('\nInitial proportionality')
    print(df)

    df.to_excel(
        f'{RESULTS_PATH}/{export_tag}/{export_tag} - {season} - Initial proportionality.xlsx')

    if WITH_BOOTSTRAP:
        try:
            ipa_matrix, preferences, ax = ipa_bootstrap(
                initial_proportionality, verbose=False)

            ax.set_label(f'{season} - {export_tag}')
            ax.set_xticklabels(prey, rotation=90)
            # plt.tight_layout()
            # plt.show()
            plt.savefig(
                f'{RESULTS_PATH}/boxplots/{season} - {export_tag} boxplot.png',
                bbox_inches='tight')
        except ValueError:
            print(f'SKIP: {export_tag} - {season}')
            return
    else:
        ipa_matrix, preferences = ipa(initial_proportionality, verbose=True)

    df = pd.DataFrame(preferences, index=prey)
    df = df.transpose()
    df.to_excel(
        f'{RESULTS_PATH}/{export_tag}/{export_tag} - {season} - IPA Overall Preference.xlsx')

    df = pd.DataFrame(ipa_matrix, columns=prey, index=sites)
    df.to_excel(
        f'{RESULTS_PATH}/{export_tag}/{export_tag} - {season} - IPA Matrix.xlsx')


# Just Cx. pipiens
run_season('Spring 2021', 'pipiens')
run_season('Summer 2021', 'pipiens')
run_season('Fall 2021', 'pipiens')
run_season('Spring 2022', 'pipiens')

# Just Cx. restuans
run_season('Spring 2021', 'restuans')
run_season('Summer 2021', 'restuans')
run_season('Fall 2021', 'restuans')
run_season('Spring 2022', 'restuans')

# Both
run_season('Spring 2021', 'combined')
run_season('Summer 2021', 'combined')
run_season('Fall 2021', 'combined')
run_season('Spring 2022', 'combined')

# Report on collections that were skipped
# over because of omissions from the density map
with open('results/skips.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(skipped_collections)
