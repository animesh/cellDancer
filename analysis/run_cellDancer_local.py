import sys
sys.path.append('../src')

#from utilities import *

import warnings
import os
import argparse
warnings.filterwarnings("ignore")
import time

import pandas as pd

if __name__ == "__main__":
    sys.path.append('.')
    from constant import *
    from sampling import *
    from sampling import *
    from velocity_estimation import *
    from utilities import set_rcParams
    from velocity_plot import velocity_plot as vpl
else:
    from .constant import *
    from .sampling import *
    from .sampling import *
    from .velocity_estimation import *
    from .utilities import set_rcParams
    from .velocity_plot import velocity_plot as vpl

set_rcParams()

time_start=time.time()

print('\nvelocity_estimate.py version 1.0.0')
print('python velocity_estimate.py')
print('time_start'+str(time_start))
print('')

use_all_gene=True
plot_trigger=False

model_dir = {"Sulf2": '/Users/shengyuli/OneDrive - Houston Methodist/work/Velocity/veloNN/cellDancer-development_20220128/src/model/Sulf2/Sulf2.pt', 
            "Ntrk2_e500": "/Users/shengyuli/OneDrive - Houston Methodist/work/Velocity/veloNN/cellDancer-development/src/model/Ntrk2_e500/Ntrk2_e500.pt"}
# config = pd.read_csv('/Users/shengyuli/OneDrive - Houston Methodist/work/Velocity/data/velocyto/neuro/config/config_test20220128.txt', sep=';',header=None)
config = pd.read_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/velocity_result/config.txt', sep=';',header=None)
task_id=config.iloc[0][0]
data_source = config.iloc[0][1]
platform = config.iloc[0][2]
epoch=int(config.iloc[0][3])
num_jobs=int(config.iloc[0][4])
learning_rate=float(config.iloc[0][5])
cost2_cutoff=float(config.iloc[0][6])
downsample_method=config.iloc[0][7]
downsample_target_amount=int(config.iloc[0][8])
step_i=int(config.iloc[0][9])
step_j=int(config.iloc[0][10])
sampling_ratio=float(config.iloc[0][11])
n_neighbors=int(config.iloc[0][12])
optimizer=config.iloc[0][13] #["SGD","Adam"]  # set to Adam
trace_cost_ratio=config.iloc[0][14]
corrcoef_cost_ratio=config.iloc[0][15]
raw_path=config.iloc[0][16]
out_path=config.iloc[0][17]



#### mkdir for output_path with parameters(naming)
folder_name=(data_source+
    "Lr"+str(learning_rate)+
    "traceR"+str(trace_cost_ratio)+
    "corrcoefR"+str(corrcoef_cost_ratio)+
    "C2cf"+str(cost2_cutoff)+
    "Down"+downsample_method+str(downsample_target_amount)+"_"+str(step_i)+"_"+str(step_j)+
    "Ratio"+str(sampling_ratio)+
    "N"+str(n_neighbors)+
    "O"+optimizer)

output_path=(out_path+folder_name+"/")
if os.path.isdir(output_path):pass
else:os.mkdir(output_path)


######################################################
############             Guangyu          ############
######################################################
#raw_data_path='/Users/shengyuli/OneDrive - Houston Methodist/work/Velocity/veloNN/cellDancer-development/data/simulation_data/one_gene.csv'

# load_raw_data=pd.read_csv(raw_path)
# load_raw_data=pd.read_csv(raw_path,names=['gene_list', 'u0','s0',"clusters",'cellID','embedding1','embedding2'])
load_raw_data=pd.read_csv(raw_path)


if use_all_gene: 
    gene_choice=list(set(load_raw_data.gene_list))
    # gene_choice.sort()
    gene_choice=gene_choice
    print('---gene_choice---')
    print(gene_choice)
else:
    gene_choice = select_gene_set(data_source)

data_df=load_raw_data[['gene_list', 'u0','s0','embedding1','embedding2']][load_raw_data.gene_list.isin(gene_choice)]

# data_df=load_raw_data[['gene_list', 'u0','s0','cellID','embedding1','embedding2']][load_raw_data.gene_list.isin(gene_choice)]

embedding_downsampling, sampling_ixs, neighbor_ixs = downsampling_embedding(data_df,
                    para=downsample_method,
                    target_amount=downsample_target_amount,
                    step_i=step_i,
                    step_j=step_j,
                    n_neighbors=n_neighbors)
gene_downsampling = downsampling(data_df=data_df, gene_choice=gene_choice, downsampling_ixs=sampling_ixs)

_, sampling_ixs_select_model, _ = downsampling_embedding(data_df,
                    para=downsample_method,
                    target_amount=downsample_target_amount,
                    step_i=20,
                    step_j=20,
                    n_neighbors=n_neighbors)
gene_downsampling_select_model = downsampling(data_df=data_df, gene_choice=gene_choice, downsampling_ixs=sampling_ixs_select_model)


# set fitting data, data to be predicted, and sampling ratio in fitting data
feed_data = feedData(data_fit = gene_downsampling, data_predict=data_df, sampling_ratio=sampling_ratio) # default sampling_ratio=0.5

model_save_path=None
#model_dir=None

#############################################
###########  Fitting and Predict ############
#############################################
print('-------epoch----------------')
print(epoch)
# cost_version=1
brief, detail = train(feed_data,
                        max_epoches=epoch, 
                        model_save_path=model_save_path,
                        result_path=output_path,
                        n_jobs=num_jobs,
                        learning_rate=learning_rate,
                        cost2_cutoff=cost2_cutoff,
                        n_neighbors=n_neighbors,
                        optimizer=optimizer,
                        trace_cost_ratio=trace_cost_ratio,
                        corrcoef_cost_ratio=corrcoef_cost_ratio)
detailfinfo="e"+str(epoch)
##########################################
###########       Plot        ############
##########################################
if plot_trigger:
    for i in gene_choice:
        save_path=output_path+i+"_"+"e"+str(epoch)+".pdf"# notice: changed
        vpl.velocity_gene(i,detail,save_path=save_path) # from cell dancer # from cell dancer
        save_path_validation=output_path+i+"_validation_"+"e"+str(epoch)+".pdf"
        if epoch>0:vpl.vaildation_plot(gene=i,validation_result=brief[brief["gene_name"]==i],save_path_validation=save_path_validation)

time_end=time.time()
print('time spent: ',(time_end-time_start)/60,' min')   