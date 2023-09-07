import numpy as np
import scipy.sparse as sparse
from sparse_dot_topn import awesome_cossim_topn
import time
import pandas as pd
import pathlib


dir = "/export/usuarios_ml4ds/amendoza/Intelcomp/EWB/data/source/Mallet-20/TMmodel"

t_start = time.perf_counter()
TMfolder = pathlib.Path(dir)
thetas = sparse.load_npz(TMfolder.joinpath('thetas.npz'))
print(f"Shape of thetas: {np.shape(thetas)} ")
thetas_sqrt = np.sqrt(thetas)
thetas_col = thetas_sqrt.T
#topn=np.shape(thetas)[0]
#topn=numero_filas
#print(f"Topn: {topn}")
"""Duda: si le pongo topn igual al tamaño del dataset me da el siguiente error:
Traceback (most recent call last):
  File "/export/usuarios_ml4ds/amendoza/top-comp/automatic_scripts/similarities.py", line 42, in <module>
    sims = awesome_cossim_topn(thetas_sqrt, thetas_col, topn, lb)
  File "/export/usuarios_ml4ds/amendoza/top-comp/.venv/lib/python3.10/site-packages/sparse_dot_topn/awesome_cossim_topn.py", line 102, in awesome_cossim_topn
    alt_indices, alt_data = ct.sparse_dot_topn_extd(
  File "sparse_dot_topn/sparse_dot_topn.pyx", line 149, in sparse_dot_topn.sparse_dot_topn.__pyx_fuse_0sparse_dot_topn_extd
  File "sparse_dot_topn/sparse_dot_topn.pyx", line 219, in sparse_dot_topn.sparse_dot_topn.sparse_dot_topn_extd
OverflowError: value too large to convert to int

Sin embargo, lo he ejecutado con topn=40000 y el shape de sims es tamaño del dataset x tamaño del dataset
Tiempo de ejecución: 28 min"""
topn = 300
print(f"Topn: {topn}")
lb=0
sims = awesome_cossim_topn(thetas_sqrt, thetas_col, topn, lb)
sparse.save_npz(TMfolder.joinpath('distances.npz'), sims)

t_end = time.perf_counter()
t_total = (t_end - t_start)/60
print(f"Total computation time: {t_total}")
"""
TMfolder_sims = TMfolder.joinpath('distances.npz')
sims = sparse.load_npz(TMfolder_sims).toarray()
size = np.size(sims)
num_nonzeros = np.count_nonzero(sims)
percentage = ((size-num_nonzeros)/size)*100
print(f"Percentage of zeros is: {percentage}")

matriz_sin_ceros = np.ma.masked_where(sims == 0, sims)

# Encuentra el valor mínimo y máximo de los elementos que no son cero
valor_minimo = np.min(matriz_sin_ceros)
valor_maximo = np.max(matriz_sin_ceros)

print("Valor mínimo de los elementos que no son cero:", valor_minimo)
print("Valor máximo de los elementos que no son cero:", valor_maximo)

sims_list = []
print(f"Shape of sims: {np.shape(sims)} ")

for i in range(0, len(sims)):
    sims_list.append(np.count_nonzero(sims[i]))

print(f"Length of sims_list: {len(sims_list)}")
maximo_elemento = max(sims_list)

print(f"Num of non zero elements in the document with more similarities computed {maximo_elemento}")

print(f"Non zero elements in one row of sims: {np.count_nonzero(sims[1])}")
print(f"Size of one row of sims: {np.size(sims[1])}")
"""
