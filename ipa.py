import numpy as np

# Rounding for each step to help normalize out floating point errors
DECIMAL_PLACES = 3


def to_prey_at_site(arr):
    arr[arr != -1] = 1
    arr[arr == -1] = 0
    return arr


def ipa(initial_proportionality, verbose=False):
    """
    Implementation of the Iterative Preference Averaging (IPA) algorithm
    specified by https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268520

    Author:
        Chase McManning <cmcmanning@gmail.com>

    Args:
        initial_proportionality (pd.DataFrame): Matrix of estimated within-site preferences
            for available prey. If a particular prey j is not present at site i, use `mat[i, j] = -1`
    """

    total_sites, total_prey = initial_proportionality.shape

    estimated_preference = np.zeros(
        [total_sites, total_prey]
    )

    prey_at_site = to_prey_at_site(initial_proportionality.copy())

    # def proportionality(prey, site):
    #     denom = 0
    #     for j in enumerate(prey):
    #         denom += eaten[j][site] / density[j][site]

    #     return (eaten[j][site] / density[j][site]) / denom

    # We're using a static dataset that is precomputed.
    # Otherwise, this comes from real data for the initial.
    # def initialize_preferences():
    #     for i in range(total_sites):
    #         for j in range(total_prey):
    #             if is_prey_in_site(prey, site):
    #                 estimated_preference[prey][site] = proportionality(prey, site)
    #             else:
    #                 estimated_preference[prey][site] = '-'

    if verbose:
        print('\nInitial proportionality')
        print(initial_proportionality)
        print('\nRow sums')
        print(initial_proportionality.sum(axis=1))
        print('\nPrey at site matrix')
        print(prey_at_site)

    prev_overall_preference = np.array([])

    # Compute initial overall preferences
    e = 1.0 / total_prey
    overall_preference = np.around(
        np.array([e] * total_prey),
        DECIMAL_PLACES
    )

    if verbose:
        print('\nOverall preference p_1')
        print(overall_preference)
        print('\nOverall preference row sum')
        print(overall_preference.sum())

    def scaling_constant(site):
        # Compute c_i for site i in current iteration k
        # Eq(3)
        sum = 0
        for j in range(total_prey):
            # M_j - prey *not* in site
            if prey_at_site[site][j] == 0:
                sum += overall_preference[j]

        return 1 - sum

    def next_mean_estimate(prey):
        # Compute next overall estimate
        # based on the means of the columns of the matrix
        # Returns: p_•j(k+1)
        sum = 0

        # This is the mean of the estimated preference column for the given prey
        for i in range(total_sites):
            sum += estimated_preference[i, prey]

        return sum / float(total_sites)

    def iteration(k):
        nonlocal prev_overall_preference, overall_preference, estimated_preference

        prev_overall_preference = overall_preference.copy()
        estimated_preference = np.around(
            initial_proportionality, DECIMAL_PLACES)

        # Step 3
        c = np.around(
            [scaling_constant(i) for i in range(total_sites)],
            DECIMAL_PLACES
        )

        # Steps 3 & 4
        for i in range(total_sites):
            for j in range(total_prey):
                # Step 3: Rescale by multiplying the constant
                if estimated_preference[i, j] != -1:
                    estimated_preference[i, j] *= c[i]
                else:
                    # Replace missing value with overall preference
                    estimated_preference[i, j] = overall_preference[j]

        estimated_preference = np.around(estimated_preference, DECIMAL_PLACES)

        # Step 5 - estimate new overall preferences
        overall_preference = np.around(
            [next_mean_estimate(j) for j in range(total_prey)],
            DECIMAL_PLACES
        )

        if verbose:
            print(f'\nScaling constant for k={k}')
            print(c)
            print(f'\nEstimated Preference P_{k}')
            print(estimated_preference)
            print('\nRow sums')
            print(estimated_preference.sum(axis=1))
            print(f'\nOverall Preference p_{k+1}')
            print(overall_preference)
            print('\nOverall preference row sum')
            print(overall_preference.sum())

    k = 1
    while True:
        iteration(k)

        diff = abs(prev_overall_preference - overall_preference)

        if verbose:
            print(f'\nDifference between overall preferences')
            print(diff)

        # If we've hit all zeros, stop iteration
        if not np.any(diff > 0.001):
            break

        k += 1

    if verbose:
        print(f'\nFinal Preference found at k={k}')

    return estimated_preference, overall_preference


# Test case - this is the same demonstrative test case as
# the "A method to predict overall food preferences" paper.
if __name__ == '__main__':
    # Going to do a mock initial preference
    # that's normalized to sum each row to 1
    # (this come from the paper). I can build
    # one from our dataset later.
    sample_initial_preferences = np.array([
        [0.27, 0.28, 0.36, 0.09, -1, -1],
        [0.29, 0.12, -1, 0.06, 0.29, 0.24],
        [0.20, 0.10, 0.20, 0.07, 0.23, 0.20],
        [-1, 0.20, 0.31, 0.06, 0.12, 0.31]
    ])

    print(ipa(sample_initial_preferences, verbose=True))

    # Expectation:
    #  Final Preference found at k=4
    # [[0.163 0.169 0.217 0.054 0.184 0.212]
    #  [0.226 0.093 0.222 0.047 0.226 0.187]
    #  [0.2   0.1   0.2   0.07  0.23  0.2  ]
    #  [0.196 0.161 0.249 0.048 0.096 0.249]]
