import csv
import itertools
import sys
import numpy

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # parents_gene_count = dict()
    # for parent in parents:
    #     parents_gene_count[parent] = random.choices(list(PROBS["gene"].keys()), list(PROBS["gene"].values()), k=1)[0]
    #
    # for parent in parents_gene_count:
    #     if parents_gene_count[parent] == 1:
    #         one_gene.add(parent)
    #     elif parents_gene_count[parent] == 2:
    #         two_genes.add(parent)

    parents = list()
    children = list()

    for person in people:
        if people[person]["mother"] is None:
            parents.append(person)
        else:
            children.append(person)

    any_gene = one_gene.union(two_genes)
    no_genes = people.keys() - any_gene

    probabilities = dict()

    for person in people:
        if person in parents:
            if person not in have_trait:
                if person in no_genes:
                    probabilities[person] = PROBS["gene"][0] * PROBS["trait"][0][False]
                elif person in one_gene:
                    probabilities[person] = PROBS["gene"][1] * PROBS["trait"][1][False]
                elif person in two_genes:
                    probabilities[person] = PROBS["gene"][2] * PROBS["trait"][2][False]
            elif person in have_trait:
                if person in no_genes:
                    probabilities[person] = PROBS["gene"][0] * PROBS["trait"][0][True]
                elif person in one_gene:
                    probabilities[person] = PROBS["gene"][1] * PROBS["trait"][1][True]
                elif person in two_genes:
                    probabilities[person] = PROBS["gene"][2] * PROBS["trait"][2][True]
        elif person in children:
            parent_probability = list()
            for parent in parents:
                if parent in no_genes:
                    parent_probability.append(PROBS["mutation"])
                elif parent in one_gene:
                    parent_probability.append(0.5)
                elif parent in two_genes:
                    parent_probability.append(1 - PROBS["mutation"])
            if person not in have_trait:
                if person in no_genes:
                    probabilities[person] = (1 - parent_probability[0]) * (1 - parent_probability[1]) * \
                                            PROBS["trait"][0][
                                                False]
                elif person in one_gene:
                    probabilities[person] = ((parent_probability[0] * (1 - parent_probability[1])) + (
                            (1 - parent_probability[0]) * parent_probability[1])) * PROBS["trait"][1][False]
                elif person in two_genes:
                    probabilities[person] = parent_probability[0] * parent_probability[1] * PROBS["trait"][2][False]
            elif person in have_trait:
                if person in no_genes:
                    probabilities[person] = (1 - parent_probability[0]) * (1 - parent_probability[1]) * \
                                            PROBS["trait"][0][
                                                True]
                elif person in one_gene:
                    probabilities[person] = ((parent_probability[0] * (1 - parent_probability[1])) + (
                            (1 - parent_probability[0]) * parent_probability[1])) * PROBS["trait"][1][True]
                elif person in two_genes:
                    probabilities[person] = parent_probability[0] * parent_probability[1] * PROBS["trait"][2][True]

    joint_p = 1

    for probability in probabilities.values():
        joint_p = joint_p * probability

    return joint_p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for person in probabilities:
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        elif person not in have_trait:
            probabilities[person]["trait"][False] += p
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    normalized_traits = list()
    normalized_genes = list()

    for person in probabilities:
        temporary_list = list()
        for has_trait in probabilities[person]["trait"]:
            temporary_list.append(probabilities[person]["trait"][has_trait])
        normalized_traits.append(temporary_list)
        temporary_list = list()
        for gene_count in probabilities[person]["gene"]:
            temporary_list.append(probabilities[person]["gene"][gene_count])
        normalized_genes.append(temporary_list)

    for index, person_traits in enumerate(normalized_traits):
        person_traits = numpy.array(person_traits)
        person_traits = person_traits / person_traits.sum()
        normalized_traits[index] = person_traits

    for index, person_genes in enumerate(normalized_genes):
        person_genes = numpy.array(person_genes)
        person_genes = person_genes / person_genes.sum()
        normalized_genes[index] = person_genes

    for index, person in enumerate(probabilities):
        for index2, has_trait in enumerate(probabilities[person]["trait"]):
            probabilities[person]["trait"][has_trait] = normalized_traits[index][index2]
        for index2, gene_count in enumerate(probabilities[person]["gene"]):
            probabilities[person]["gene"][gene_count] = normalized_genes[index][index2]


if __name__ == "__main__":
    main()
