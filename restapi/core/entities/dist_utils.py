"""
Created on Thu Dec  4 18:11:29 2014

Author: Jerónimo Arenas-García
Modified by Lorena Calvo-Bartolomé
Modification date: 08/05/2021
"""

import sys
from itertools import product

import numpy as np
from scipy import spatial
from sparse_dot_topn import awesome_cossim_topn

def dd_hellinger(theta1,theta2):
    
    """ Calcula la distancia de Hellinger entre distribuciones discretas. 
    
    Parametros de entrada:
        * theta1 :        Matriz de dimensiones (n1 x K)
        * theta2 :        Matriz de dimensiones (n2 x K)
        
    Devuelve: Una matriz de dimensiones (n1 x n2), donde cada componente
    se obtiene como la distancia de Hellinger entre las correspondientes filas
    de theta1 y theta2    
    """    
    _SQRT2 = np.sqrt(2)    
    
    (n1, col1) = theta1.shape
    (n2, col2) = theta2.shape
    if col1 != col2:
        sys.exit("Error en llamada a Hellinger: Las dimensiones no concuerdan")
    return spatial.distance.cdist(np.sqrt(theta1),np.sqrt(theta2),'euclidean') / _SQRT2
    
    
def dd_cosine(theta1,theta2):
    
    """ Calcula la distancia coseno entre distribuciones discretas. 
    
    Parametros de entrada:
        * theta1 :        Matriz de dimensiones (n1 x K)
        * theta2 :        Matriz de dimensiones (n2 x K)
        
    Devuelve: Una matriz de dimensiones (n1 x n2), donde cada componente
    se obtiene como la distancia coseno entre las correspondientes filas
    de theta1 y theta2    
    """
    (n1, col1) = theta1.shape
    (n2, col2) = theta2.shape
    if col1 != col2:
        sys.exit("Error en llamada a D. Coseno: Las dimensiones no concuerdan")
    #Normalize to get output between 0 and 1
    return spatial.distance.cdist(theta1,theta2,'cosine')/2


def kl(p, q):
    """Kullback-Leibler divergence D(P || Q) for discrete distributions
    (should only be used for the Jensen-Shannon divergence)
 
    Parameters
    ----------
    p, q : array-like, dtype=float, shape=n
        Discrete probability distributions.
    """
    p = np.asarray(p, dtype=np.float)
    q = np.asarray(q, dtype=np.float)
    #print np.all([p != 0,q!= 0],axis=0)
    #Notice standard practice would be that the p * log(p/q) = 0 for p = 0,
    #but p * log(p/q) = inf for q = 0. We could use smoothing, but since this
    #function will only be called to calculate the JS divergence, we can also
    #use p * log(p/q) = 0 for p = q = 0 (if q is 0, then p is also 0)
    return np.sum(np.where(np.all([p != 0,q!= 0],axis=0), p * np.log(p / q), 0))


def kl2(p, q):
    """Kullback-Leibler divergence D(P || Q) for discrete distributions
    (should only be used for the Jensen-Shannon divergence)

    *********USING BASE 2 FOR THE LOGARITHM*******
 
    Parameters
    ----------
    p, q : array-like, dtype=float, shape=n
        Discrete probability distributions.
    """
    p = np.squeeze(np.asarray(p.todense()))
    q = np.squeeze(np.asarray(q.todense()))
    #print np.all([p != 0,q!= 0],axis=0)
    #Notice standard practice would be that the p * log(p/q) = 0 for p = 0,
    #but p * log(p/q) = inf for q = 0. We could use smoothing, but since this
    #function will only be called to calculate the JS divergence, we can also
    #use p * log(p/q) = 0 for p = q = 0 (if q is 0, then p is also 0)
    return np.sum(np.where(np.all([p != 0,q!= 0],axis=0), p * np.log2(p / q), 0))


def dd_js(theta1,theta2):
    """ Calcula la distancia de Jensen-Shannon entre distribuciones discretas. 
    
    Parametros de entrada:
        * theta1 :        Matriz de dimensiones (n1 x K)
        * theta2 :        Matriz de dimensiones (n2 x K)
        
    Devuelve: Una matriz de dimensiones (n1 x n2), donde cada componente
    se obtiene como la distancia de J-S entre las correspondientes filas
    de theta1 y theta2    
    """
    (n1, col1) = theta1.shape
    (n2, col2) = theta2.shape
    if col1 != col2:
        sys.exit("Error en llamada a D. JS: Ambas matrices no tienen las mismas columnas")

    js_div = np.empty( (n1,n2) )
    for idx,pq in zip(product(range(n1),range(n2)),product(theta1,theta2)):
        av = (pq[0] + pq[1])/2
        js_div[idx[0],idx[1]] = 0.5 * (kl(pq[0],av) + kl(pq[1],av))
        
    return js_div


def js_similarity(theta1,theta2):
    """ Calcula la similitud basada en la divergencia de Jensen-Shannon
    
    Parametros de entrada:
        * theta1 :        Matriz de dimensiones (n1 x K)
        * theta2 :        Matriz de dimensiones (n2 x K)
        
    Devuelve: Una matriz de dimensiones (n1 x n2), donde cada componente
    se obtiene como la distancia de J-S entre las correspondientes filas
    de theta1 y theta2    
    """
    (n1, col1) = theta1.shape
    (n2, col2) = theta2.shape
    if col1 != col2:
        sys.exit("Error en llamada a D. JS: Ambas matrices no tienen las mismas columnas")

    js_sim = np.empty( (n1,n2) )
    for idx,pq in zip(product(range(n1),range(n2)),product(theta1,theta2)):
        av = (pq[0] + pq[1])/2
        js_sim[idx[0],idx[1]] = 1 - 0.5 * (kl2(pq[0],av) + kl2(pq[1],av))
        
    return js_sim

def bhatta(u, v):
    """Calculates the Bhattacharyya distance between two discrete distributions.
    
    Parameters
    ----------
    u: array-like, dtype=float, shape=n
        Discrete probability distribution.
    v: array-like, dtype=float, shape=n
        Discrete probability distribution.
        
    Returns: The Bhattacharyya distance between u and v.
    """
    return np.sum(np.sqrt(u*v))

def bhatta_mat(x, lb, N):
    """Calculates the Battacharyya distance between all pairs of rows in x.
    
    Parameters
    ----------
    x: csr_matrix, dtype=float, shape=(n, m)
        Matrix of n rows of m-dimensional discrete probability distributions.
    lb: float
        Lower bound for the similarity measure.
    N: int
        Number of top similar items to return.
        
    Returns
    -------
    W: csr_matrix, dtype=float, shape=(n, N)
        Matrix of n rows of N-dimensional vectors of the top N similar items.
    """
    x_sqrt = np.sqrt(x)
    x_col = x_sqrt.T
    W = awesome_cossim_topn(x_sqrt, x_col, N, lb)
   
    return W