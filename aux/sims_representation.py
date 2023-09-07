import encodings
import pathlib
import scipy.sparse as sparse
from typing import List
import time
import tqdm

def get_doc_by_doc_sims(W, ids_corpus) -> List[str]:
    """
    Calculates the similarity between each pair of documents in the corpus collection based on the document-topic distribution provided by the model being indexed.

    Parameters
    ----------
    W: scipy.sparse.csr_matrix
        Sparse matrix with the similarities between each pair of documents in the corpus collection.
    ids_corpus: List[str]
        List of ids of the documents in the corpus collection.

    Returns:
    --------
    sims: List[str]
        List of string represenation of the top similarities between each pair of documents in the corpus collection.
    """

    # Get the non-zero elements indices
    non_zero_indices = W.nonzero()

    # Convert to a string
    sim_str = \
        [' '.join([f"{ids_corpus[col]}|{W[row, col]}" for col in non_zero_indices[1]
                    [non_zero_indices[0] == row]][1:]) for row in range(W.shape[0])]

    return sim_str



dir = pathlib.Path("/export/usuarios_ml4ds/amendoza/Intelcomp/EWB/data/source/Mallet-20/")

sims = sparse.load_npz(dir.joinpath("TMmodel").joinpath("distances.npz"))
print(f"Sims obtained")

def process_line(line):
    id_ = line.rsplit(' 0 ')[0].strip()
    id_ = int(id_.strip('"'))
    return id_

with open(dir.joinpath("corpus.txt"), encoding="utf-8") as file:
    ids_corpus = [process_line(line) for line in file]
print(f"Ids obtained")
print(f"Starting similarities representation...")
time_start = time.perf_counter()
sim_rpr = get_doc_by_doc_sims(sims, ids_corpus)
time_end = time.perf_counter()
print(f"Similarities representation finished in {time_end - time_start:0.4f} seconds")
print(f"Writing similarities representation to txt file...")

# Escribir en el archivo
with open(dir.joinpath("TMmodel").joinpath('distances.txt'), 'w') as f:
    for item in sim_rpr:
        f.write("%s\n" % item)

"""
# Leer el archivo
with open('distances.txt', 'r') as f:
    mi_lista = [line.strip() for line in f]
"""