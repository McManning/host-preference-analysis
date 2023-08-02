import numpy as np
import matplotlib.pyplot as plt

from ipa import ipa

RANDOM_ROW_SIZE = 2

BOOTSTRAP_SAMPLES = 1_001


def ipa_bootstrap(initial_proportionality, verbose: bool = False):
    """
    Implementation of the Iterative Preference Averaging (IPA) algorithm
    with a bootstrapping step to measure error.

    specified by https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268520

    Author:
        Chase McManning <cmcmanning@gmail.com>

    Args:
        initial_proportionality (pd.DataFrame): Matrix of estimated within-site preferences
            for available prey. If a particular prey j is not present at site i, use `mat[i, j] = -1`
    """

    # Number of bootstrap samples
    bootstrap_estimates = []

    ipa_matrix, estimated_preferences = ipa(
        initial_proportionality, verbose=verbose)

    if verbose:
        print(f'\nSampling {BOOTSTRAP_SAMPLES} times')

    row_count, col_count = initial_proportionality.shape

    for i in range(BOOTSTRAP_SAMPLES):
        copy = np.around(initial_proportionality, 3)

        # take a random sample of m rows from the matrix with replacement
        sample_size = row_count  # // 2
        choice = np.random.choice(
            row_count,
            size=sample_size,
            replace=True
        )
        sample = copy[choice]

        # print('\nSAMPLE')
        # print(sample)
        # break

        ipa_matrix, preferences = ipa(sample, verbose=False)

        if np.any(preferences < 0):
            raise ValueError('Unexpected negative preference')
            # print('\nSAMPLE IN ERROR')
            # print(sample)
            # print('\nPREFERENCES IN ERROR')
            # print(preferences)
            # continue

        # transform the preferences and add to the bootstrap estimates
        # transformed_preferences = np.arcsin(2 * preferences - 1)
        # bootstrap_estimates.append(transformed_preferences)
        bootstrap_estimates.append(preferences)

        if i % 1000 == 0:
            print(f'Sample {i}...')

    # # Calculate the mean and standard deviation of the bootstrap estimates
    # bootstrap_mean = np.mean(bootstrap_estimates, axis=0)
    # bootstrap_std = np.std(bootstrap_estimates, axis=0)

    # # Calculate the confidence intervals of the bootstrap estimates
    # alpha = 0.05  # 95% confidence interval
    # lower_bound = np.quantile(bootstrap_estimates, alpha/2, axis=0)
    # upper_bound = np.quantile(bootstrap_estimates, 1-alpha/2, axis=0)

    # # Back-transform the means and confidence intervals
    # back_transformed_mean = (np.sin(bootstrap_mean) + 1) / 2
    # back_transformed_lower_bound = (np.sin(lower_bound) + 1) / 2
    # back_transformed_upper_bound = (np.sin(upper_bound) + 1) / 2

    # # x = animal identifier
    # # y = preferences
    # x = np.arange(initial_proportionality.shape[1])
    # y = estimated_preferences
    # e = back_transformed_mean  # np.zeros(initial_proportionality.shape[1])

    return ipa_matrix, estimated_preferences, bootstrap_estimates

    # plt.savefig('foo.png')

    # Create data frame of results
    # return [bootstrap_mean, bootstrap_std, back_transformed_mean]


# Test case - this is the same demonstrative test case as
# the "A method to predict overall food preferences" paper.
if __name__ == '__main__':

    sample_initial_preferences = np.array([
        [0.27, 0.28, 0.36, 0.09, -1, -1],
        [0.29, 0.12, -1, 0.06, 0.29, 0.24],
        [0.20, 0.10, 0.20, 0.07, 0.23, 0.20],
        [-1, 0.20, 0.31, 0.06, 0.12, 0.31]
    ])

    ipa_matrix, estimated_preferences, bootstrap_estimates = ipa_bootstrap(
        sample_initial_preferences, verbose=True)

    print(estimated_preferences)
