import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    links_count = len(corpus[page])
    pages_count = len(corpus)
    probability_of_each_page = (1 - damping_factor) / pages_count

    a_transition_model = dict()

    for page2 in corpus:

        if links_count == 0:

            a_transition_model[page2] = 1 / pages_count

        else:

            if page2 in corpus[page]:

                probability_of_each_link = (damping_factor / links_count) + probability_of_each_page
                a_transition_model[page2] = probability_of_each_link

            else:

                a_transition_model[page2] = probability_of_each_page

    return a_transition_model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    random_surfer = random
    pageranks = dict()
    first_page = list(corpus)[random_surfer.randrange(len(corpus))]
    visited_pages = list()
    visited_pages.append(first_page)

    for i in range(n - 1):
        a_transition_model = transition_model(corpus, visited_pages[-1], damping_factor)
        pages = list(a_transition_model.keys())
        probabilities = list(a_transition_model.values())
        chosen_page = random_surfer.choices(pages, probabilities, k=1)[0]
        visited_pages.append(chosen_page)

    for page in corpus:
        pageranks[page] = visited_pages.count(page) / n

    return pageranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    pageranks = dict()
    page_count = len(corpus)

    for page in corpus:
        pageranks[page] = 1 / page_count

    too_rough = True

    while too_rough:

        too_rough = False

        for page in pageranks:

            previous_pagerank = pageranks[page]

            sum = 0

            for linking_page in pageranks:

                if page in corpus[linking_page]:

                    sum += (pageranks[linking_page] / len(corpus[linking_page]))

                elif len(corpus[linking_page]) == 0:

                    sum += (pageranks[linking_page] / page_count)

            pageranks[page] = ((1 - damping_factor) / page_count) + damping_factor * sum

            if (previous_pagerank - pageranks[page]) > 0.001:
                too_rough = True

    return pageranks


if __name__ == "__main__":
    main()
