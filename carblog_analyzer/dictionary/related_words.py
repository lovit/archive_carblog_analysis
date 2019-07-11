import math
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse import vstack
from sklearn.utils.extmath import safe_sparse_dot


def tf_to_prop_graph(X, min_score=0.75, min_cooccurrence=1,
    verbose=True, include_self=True, topk=-1):
    """
    Arguments
    ---------
    X: scipy.sparse
        Shape = (n_docs, n_terms)
    min_score: float
        Minimum co-occurrence score; pos_prop / (pos_prop + neg_prop)
        Default is 0.75
    min_cooccurrence: int
        Mininum co-occurrence count. Default is 1
    verbose: Boolean
        If True, it shows progress status for each 100 words
    include_self: Boolean
        If True, (w0, w0) is included in graph with score 1.0.

    Returns
    ----------
    g_prop : scipy.sparse.csr_matrix
        Co-occurrence score matrix. Shape = (n_terms, n_terms)
    g_count : scipy.sparse.csr_matrix
        Co-occurrence count matrix. Shape = (n_terms, n_terms)
    """

    to_count = lambda X:np.asarray(X.sum(axis=0)).reshape(-1)
    to_prop = lambda X: X / X.sum()

    total_count = to_count(X)
    n_vocabs = X.shape[1]

    rows = []
    cols = []
    props = []
    counts = []

    for base_idx in range(n_vocabs):
        pos_docs = X[:,base_idx].nonzero()[0]
        pos_count = to_count(X[pos_docs])
        ref_count = total_count - pos_count
        pos_prop = to_prop(pos_count)
        ref_prop = to_prop(ref_count)
        prop = pos_prop / (pos_prop + ref_prop)

        if min_cooccurrence > 1:
            idx_mc = np.where(pos_count >= min_cooccurrence)[0]
            idx_ms = np.where(prop >= min_score)[0]
            rel_idxs = np.intersect1d(idx_mc, idx_ms)
        else:
            rel_idxs = np.where(prop >= min_score)[0]

        for idx in rel_idxs:
            if not include_self and idx == base_idx:
                continue
            rows.append(base_idx)
            cols.append(idx)
            props.append(prop[idx])
            counts.append(pos_count[idx])

        if verbose and base_idx % 100 == 0:
            print('\rcreate graph %d / %d ...' % (base_idx , n_vocabs), end='')

    if verbose:
        print('\rcreate graph from %d words was done' % n_vocabs)

    g_prop = csr_matrix((props, (rows, cols)), shape=(n_vocabs, n_vocabs))
    g_count = csr_matrix((counts, (rows, cols)), shape=(n_vocabs, n_vocabs))

    return g_prop, g_count

def tf_to_cooccurrence(X, min_count=1, batch_size=10000):
    """
    Arguments
    ---------
    X: scipy.sparse
        Shape = (n_docs, n_terms)
    min_count: int
        Mininum co-occurrence count. Default is 1
    batch_size: int
        The number of words in a batch. Default is 10000

    Returns
    ----------
    C : scipy.sparse.csr_matrix
        Co-occurrence matrix
    """

    XT = X.T
    n_terms = X.shape[1]
    if batch_size == -1:
        C = safe_sparse_dot(XT, X)
        if min_count > 1:
            C = larger_than(C, min_count)
    else:
        stacks = []
        n_batch = math.ceil(n_terms / batch_size)
        for i in range(n_batch):
            b = i * batch_size
            e = min(n_terms, (i+1) * batch_size)
            C = safe_sparse_dot(XT[b:e], X)
            if min_count > 1:
                C = larger_than(C, min_count)
            stacks.append(C)
        C = vstack(stacks)

    if not isinstance(C, csr_matrix):
        C = C.tocsr()

    return C

def larger_than(X, min_count):
    rows_, cols_ = X.nonzero()
    data_ = X.data
    rows, cols, data = [], [], []
    for r, c, d in zip(rows_, cols_, data_):
        if d < min_count:
            continue
        rows.append(r)
        cols.append(c)
        data.append(d)
    return csr_matrix((data, (rows, cols)), shape=X.shape)
