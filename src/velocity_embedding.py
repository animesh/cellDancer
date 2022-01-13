from sklearn.neighbors import NearestNeighbors
import numpy as np
import matplotlib.pyplot as plt
from sampling import *
import pandas as pd


def corr_coeff(ematrix, vmatrix, i):
    '''
    Calculate the correlation between the predict velocity (velocity_matrix[:,i])
    and the difference between a cell and every other (cell_matrix - cell_matrix[:, i])
    '''
    # ematrix = cell_matrix
    # vmatrix = velocity_matrix
    ematrix = ematrix.T
    vmatrix = vmatrix.T
    ematrix = ematrix - ematrix[i, :]
    vmatrix = vmatrix[i, :][None,:]
    ematrix_m = ematrix - ematrix.mean(1)[:, None]
    vmatrix_m = vmatrix - vmatrix.mean(1)[:, None]

    # Sum of squares across rows
    ematrix_ss = (ematrix_m**2).sum(1)
    vmatrix_ss = (vmatrix_m**2).sum(1)
    cor = np.dot(ematrix_m, vmatrix_m.T) / np.sqrt(np.dot(ematrix_ss[:, None],vmatrix_ss[None]))
    return cor.T

def velocity_correlation(cell_matrix, velocity_matrix):
    """Calculate the correlation between the predict velocity (velocity_matrix[:,i])
    and the difference between a cell and every other (cell_matrix - cell_matrix[:, i])
    
    Arguments
    ---------
    cell_matrix: np.ndarray (ngenes, ncells)
        gene expression matrix
    velocity_matrix: np.ndarray (ngenes, ncells)
    Return
    ---------
    c_matrix: np.ndarray (ncells, ncells)
    """
    c_matrix = np.zeros((cell_matrix.shape[1], velocity_matrix.shape[1]))
    for i in range(cell_matrix.shape[1]):
        c_matrix[i, :] = corr_coeff(cell_matrix, velocity_matrix, i)[0,:]
    np.fill_diagonal(c_matrix, 0)
    return c_matrix


def velocity_projection(cell_matrix, velocity_matrix, embedding, knn_embedding):
    '''
    cell_matrix: np.ndarray (ngenes, ncells)
        gene expression matrix
    velocity_matrix: np.ndarray (ngenes, ncells)
    '''
    # cell_matrix = np_s0[:,sampling_ixs]
    # velocity_matrix = np_dMatrix[:,sampling_ixs]
    sigma_corr = 0.05
    cell_matrix[np.isnan(cell_matrix)]=0
    velocity_matrix[np.isnan(velocity_matrix)]=0
    corrcoef = velocity_correlation(cell_matrix, velocity_matrix)
    probability_matrix = np.exp(corrcoef / sigma_corr)*knn_embedding.A
    probability_matrix /= probability_matrix.sum(1)[:, None]
    unitary_vectors = embedding.T[:, None, :] - embedding.T[:, :, None]
    with np.errstate(divide='ignore', invalid='ignore'):
        unitary_vectors /= np.linalg.norm(unitary_vectors, ord=2, axis=0)
        np.fill_diagonal(unitary_vectors[0, ...], 0)
        np.fill_diagonal(unitary_vectors[1, ...], 0)
    velocity_embedding = (probability_matrix * unitary_vectors).sum(2)
    velocity_embedding -= (knn_embedding.A * unitary_vectors).sum(2) / knn_embedding.sum(1).A.T  # embedding_knn.A * 
    velocity_embedding = velocity_embedding.T
    return velocity_embedding

def data_reshape(load_cellDancer):
    '''
    load detail file
    return expression matrix and velocity
    '''
    psc = 1
    gene_names = load_cellDancer['gene_name'].drop_duplicates().to_list()
    # cell_number = load_cellDancer[load_cellDancer['gene_name']==gene_names[0]].shape[0]
    # load_cellDancer['index'] = np.tile(range(cell_number),len(gene_names))
    load_cellDancer['index'] = 0
    for g in gene_names:
        load_cellDancer.loc[load_cellDancer['gene_name']==g, 'index'] = range(load_cellDancer[load_cellDancer['gene_name']==g].shape[0])
    s0_reshape = load_cellDancer.pivot(index='gene_name', values='s0', columns='index')
    s1_reshape = load_cellDancer.pivot(index='gene_name', values='s1', columns='index')
    dMatrix = s1_reshape-s0_reshape
    np_s0_reshape = np.array(s0_reshape)
    np_dMatrix = np.array(dMatrix)
    np_dMatrix2 = np.sqrt(np.abs(np_dMatrix) + psc) * np.sign(np_dMatrix) # (2159, 18140)
    return(np_s0_reshape, np_dMatrix2)


config = pd.read_csv('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/neighbor/config/inverse_SGD_costV2.csv', sep=';',header=None)
data_source = config.iloc[0][0]
platform = config.iloc[0][1]
epoches=[int(config.iloc[0][2])]
num_jobs=int(config.iloc[0][3])
learning_rate=float(config.iloc[0][4])
cost_version=int(config.iloc[0][5])
cost1_ratio=float(config.iloc[0][6])
cost2_cutoff=float(config.iloc[0][7])
downsample_method=config.iloc[0][8]
downsample_target_amount=int(config.iloc[0][9])
step_i=int(config.iloc[0][10])
step_j=int(config.iloc[0][11])
sampling_ratio=float(config.iloc[0][12])
n_neighbors=int(config.iloc[0][13])
optimizer=config.iloc[0][14] #["SGD","Adam"]

gene_choice=["Ntrk2","Tmem163"]

raw_data_path="/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/neighbor/denGyr_test_2.csv" 
load_raw_data=pd.read_csv(raw_data_path,names=['gene_list', 'u0','s0',"clusters",'cellID','embedding1','embedding2'])
data_df=load_raw_data[['gene_list', 'u0','s0','cellID','embedding1','embedding2']][load_raw_data.gene_list.isin(gene_choice)]
embedding_downsampling, sampling_ixs, knn_embedding = downsampling_embedding(data_df,
                    para=downsample_method,
                    target_amount=downsample_target_amount,
                    step_i=60,
                    step_j=60,
                    n_neighbors=100)




embedding = np.loadtxt(open("/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/loom/OneDrive_1_12-27-2021/vlm_embedding.csv", "rb"), delimiter=",")
hi_dim = np.loadtxt(open("/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/loom/OneDrive_1_12-27-2021/vlm_Sx_sz.csv", "rb"), delimiter=",")
delta_S = np.loadtxt(open("/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/loom/OneDrive_1_12-27-2021/vlm_delta_S.csv", "rb"), delimiter=",")
delta_embedding = np.loadtxt(open("/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/loom/OneDrive_1_12-27-2021/vlm_delta_embedding.csv", "rb"), delimiter=",")
delta_embedding_random = np.loadtxt(open("/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/loom/OneDrive_1_12-27-2021/vlm_delta_embedding_random.csv", "rb"), delimiter=",")
used_delta_t = float(0.5)
psc = 1

hi_dim_t = hi_dim + used_delta_t * delta_S  # [:, :ndims] [:, :ndims]
delta_hi_dim = hi_dim_t - hi_dim # (2159, 18140)
dmatrix = np.sqrt(np.abs(delta_hi_dim) + psc) * np.sign(delta_hi_dim) # (2159, 18140)
############################
### velocyto predict  ######
############################
A = hi_dim[:, sampling_ixs]
B = dmatrix[:, sampling_ixs]
velocity_embedding = velocity_projection(A, B, embedding[sampling_ixs,:], knn_embedding)

############################
### cellDancer predict  ####
############################

load_cellDancer=pd.read_csv('/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/detail_file/detail_e302.csv')
# load_cellDancer2 = load_cellDancer[load_cellDancer['gene_name'].isin(['1190002N15Rik','Atp1b1'])]
# load_cellDancer = load_cellDancer[load_cellDancer['gene_name'].isin(['Dcx','Elavl4'])]

np_s0, np_dMatrix = data_reshape(load_cellDancer)
velocity_embedding = velocity_projection(np_s0[:,sampling_ixs], np_dMatrix[:,sampling_ixs], embedding[sampling_ixs,:], knn_embedding)

# load_cellDancer['u1'].isnull().values.any()

plt.scatter(embedding[sampling_ixs, 0], embedding[sampling_ixs, 1],s=0.5)
plt.quiver(embedding[sampling_ixs, 0], embedding[sampling_ixs, 1],
           velocity_embedding[:, 0], velocity_embedding[:, 1] ,color='red')
plt.savefig('figure/test2_302.pdf')



delta_embedding2 = np.loadtxt(open("/Users/guangyuwang/OneDrive - Houston Methodist/Work/cellDancer/data/loom/OneDrive_1_12-27-2021/vlm_delta_embedding.csv", "rb"), delimiter=",")

plt.scatter(embedding[sampling_ixs, 0], embedding[sampling_ixs, 1],s=0.5)
plt.quiver(embedding[sampling_ixs, 0], embedding[sampling_ixs, 1],
           delta_embedding2[sampling_ixs, 0], delta_embedding2[sampling_ixs, 1] ,color='red')
plt.savefig('figure/test2_velocyto.pdf')







