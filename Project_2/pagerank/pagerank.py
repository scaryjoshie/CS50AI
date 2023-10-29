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

    # Gets a list of pages linked to the page in question and a list of all pages within the corpus
    linked_pages_list = corpus[page]
    all_pages_list = corpus.keys()

    # Calculates the probability for choosing a page that is linked to the current page
    if len(linked_pages_list) > 0:
        linked_probability = damping_factor/len(linked_pages_list)
    # Calculates the probability for choosing a page out of all pages randomly
    all_probability = (1-damping_factor)/len(all_pages_list)
    
    # Creates probability distribution. Initially only includes the probability from selecting all pages randomly, not directly from linked pages
    probability_distribution = {page: all_probability for page in all_pages_list}

    # For each page linked to the original page, adds the linked_probability to the probability distribution
    for linked_page in linked_pages_list:
        probability_distribution[linked_page] += linked_probability

    # Returns the final probability distribution
    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    # Dictionary that keeps track of how many times each page has been sampled
    counts = {page:0 for page in corpus.keys()}

    # Randomly selects a page to sample
    page = random.choice(list(corpus.keys()))
    counts[page] += 1

    # Samples pages n-1 times (because the first random sample counts as an iteration)
    for i in range(0, n-1):
        # Gets transition distribution
        transition_distribution = transition_model(corpus=corpus, page=page, damping_factor=damping_factor)
        
        # Uses the random.choices module to select a page given the probability distribution
        page = random.choices(population=list(transition_distribution.keys()),
                                weights=transition_distribution.values(),
                                k=1,)[0]
        
        # Increases count for specified page
        counts[page] += 1

    # Creates the pagerank dictionary based on the counts
    pageranks = {page:counts[page]/n for page in counts.keys()} 

    # Returns 
    return pageranks



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    change_threshold = 0.001
    N = len(corpus)

    # Creates starting pageranks
    pageranks = {page:1/N for page in corpus.keys()}
    
    # Iterates until no pagerank value changes by more than 0.001
    while True:
        
        threshold_broken = False

        # Repeats the pagerank formula for every page
        for p in corpus:

            # Calculates the summation portion of the equation
            summation = 0
            for i in corpus.keys():
                # Gets NumLinks(i). 
                # If i contains current page --> numlinks = number of links in i
                # If i contains no pages --> numlinks = length of corpus
                # If i contains pages but not the current page --> skips to the next page
                if p in corpus[i]:
                    numlinks = len(corpus[i])
                elif len(corpus[i]) == 0:
                    numlinks = len(corpus)
                else:
                    continue

                # Gets PR(i)
                PR_i = pageranks[i]

                # adds the current value to the summation
                summation += PR_i/numlinks

            
            # Calculates PR(p)
            PR_p = (1-damping_factor)/N + damping_factor*summation

            # Checks if the change is greater than the allowed threshold. If it is, sets "threshold_broken" to True, forcing the loop to repeat
            if abs(PR_p - pageranks[p]) > change_threshold:
                threshold_broken = True

            # Sets the pagerank value to the calculated value
            pageranks[p] = PR_p

        # If the threshold has not been broken, returns pageranks
        if threshold_broken == False:
            return pageranks


if __name__ == "__main__":
    main()
