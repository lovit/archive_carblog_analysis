from collections import defaultdict
import numpy as np
from carblog_dataset import load_text, load_category_index
from ..tokenizer import SubwordTokenizer

def compute_document_frequency(documents, subword_to_idx):
    """
    Arguments
    ---------
    documents : list of set
        Document set. Each document formed as str
    subword_to_idx : {str:int}
        Mapper subword to index

    Returns
    -------
    df_ratio : numpy.ndarray
        Array of document frequency ratio, shape is (num_subwords,)
    """
    n_docs = len(documents)
    n_subwords = len(subword_to_idx)
    tokenizer = SubwordTokenizer(subword_to_idx)

    # count subwords
    df = defaultdict(int)
    for doc in documents:
        subword_set = set(tokenizer.tokenize(doc))
        for subword in subword_set:
            df[subword] += 1
    df = {sub:df_s/n_docs for sub, df_s in df.items()}

    # convert dict to as numpy.ndarray
    df_ratio = np.zeros(n_subwords)
    for sub, ratio in df.items():
        df_ratio[subword_to_idx[sub]] = ratio
    return df_ratio

def train_subword_df_distribution(subword_to_idx, verbose=False):
    """
    Arguments
    ---------
    subword_to_idx : {str:int}
        Mapper subword to index
    verbose : Boolean
        If True, it shows progress

    Returns
    -------
    df_ratios : numpy.ndarray
        Array of document frequency ratio, shape is (num_categories, num_subwords)
    """
    idx_to_category = load_category_index()
    num_categories = len(idx_to_category)

    df_ratios = []
    for c in range(num_categories):
        texts = load_text(category=c)
        df_ratios.append(compute_document_frequency(texts, subword_to_idx))

        if verbose:
            print('Train DF from [{}] category'.format(idx_to_category[c]))
    df_ratios = np.vstack(df_ratios)
    return df_ratios

def show_df_distribution(subword, subword_to_idx, df_ratios, idx_to_category):
    """
    It shows distribution of document frequency ratio by categories

    Arguments
    ---------
    subword : str
        Input subword
    subword_to_idx : {str:int}
        Mapper, subword to index
    df_ratios : numpy.ndarray
        Shape is (num_categories, num_subwords)
    idx_to_category : list of str
        List of category names

    Usage
    -----
        >>> show_df_distribution('터미네이터', subword_to_idx, df_ratios, idx_to_category)

        $ Subword = 터미네이터
          [--------------------]: (0.022 %)	 A6
          [--------------------]: (0.051 %)	 BMW5
          [--------------------]: (0.038 %)	 BMW
          [--------------------]: (0.013 %)	 K3
          [--------------------]: (0.015 %)	 K5
          [--------------------]: (0.012 %)	 K7
          [--------------------]: (0.008 %)	 QM3
          [--------------------]: (0.011 %)	 그랜저
          [--------------------]: (0.039 %)	 벤츠E
          [--------------------]: (0.028 %)	 산타페
          [--------------------]: (0.027 %)	 소나타
          [--------------------]: (0.012 %)	 스포티지
          [--------------------]: (0.011 %)	 싼타페
          [--------------------]: (0.009 %)	 쏘나타
          [--------------------]: (0.010 %)	 쏘렌토
          [--------------------]: (0.011 %)	 아반떼
          [--------------------]: (0.000 %)	 아반테
          [####################]: (1.775 %)	 제네시스
          [--------------------]: (0.008 %)	 코란도C
          [--------------------]: (0.011 %)	 투싼
          [--------------------]: (0.015 %)	 티구안
          [--------------------]: (0.018 %)	 티볼리
          [--------------------]: (0.000 %)	 파사트
          [--------------------]: (0.008 %)	 폭스바겐골프
          [--------------------]: (0.067 %)	 현기차
          [--------------------]: (0.017 %)	 현대자동차
          [--------------------]: (0.027 %)	 현대차
    """
    def bar_str(df_i):
        bar_len = int(20 * df_i)
        return '#' * bar_len + '-' * (20 - bar_len)

    subword_idx = subword_to_idx.get(subword, -1)
    if subword_idx == -1:
        return
    df = df_ratios[:,subword_idx].reshape(-1)
    bars = df / df.max()

    print('Subword = {}'.format(subword))
    for i, (df_i, bar_i) in enumerate(zip(df, bars)):
        category = idx_to_category[i]
        perc = '%.3f' % (100 * df_i)
        bar = bar_str(bar_i)
        print('[{}]: ({} %)\t {}'.format(bar, perc, category))
