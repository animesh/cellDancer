from analysis_SIM_compare_fun import *
###############################################
########## cosin similarity analysis ##########
###############################################
# path: server
analysis_result_path='/Users/wanglab/Documents/ShengyuLi/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/'
detail_input_path='/Users/wanglab/Documents/ShengyuLi/Velocity/data/simulation/data/multi_path/multi_path/velocity_result/celldancer/'
raw_input_path='/Users/wanglab/Documents/ShengyuLi/Velocity/data/simulation/data/multi_path/multi_path/raw/'
scv_result_input_path='/Users/wanglab/Documents/ShengyuLi/Velocity/data/simulation/data/multi_path/multi_path/velocity_result/scv/'
foldername_para='_all_geneLr0.001traceR0corrcoefR0C2cf0.3Downneighbors0_200_200Ratio0.125N30OAdam'

# path - hpc
analysis_result_path='/condo/wanglab/tmhsxl98/Velocity/simulation_velocity_analysis/simulation_data/analysis_result/'
detail_input_path='/condo/wanglab/tmhsxl98/Velocity/simulation_velocity_analysis/simulation_data/velocity_result/celldancer/'
raw_input_path='/condo/wanglab/tmhsxl98/Velocity/simulation_velocity_analysis/simulation_data/raw/multipath/'
scv_result_input_path='/condo/wanglab/tmhsxl98/Velocity/simulation_velocity_analysis/simulation_data/velocity_result/scv/'

# path - shengyu
detail_input_path='/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/velocity_result/celldancer/'
raw_input_path='/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/raw/'
scv_result_input_path='/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/velocity_result/scv/'
analysis_result_path='/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result'

########## scv
# path: server
print('running scv analysis')

for ratio in [1,0.2,0.4,0.6,0.8]:
    print(ratio)
    scVelo = get_similarity_scVelo(ratio,scv_result_input_path,raw_input_path,type='multi',path='Path1Upper')
    scVelo.to_csv(analysis_result_path+'scvelo_similarity_eachCell'+str(ratio)+'.csv')
    sns.boxplot(x="ratio", y="similarity", hue='method', data=scVelo)

########## celldancer
print('running celldancer analysis')

for ratio in [0.2,0.4,0.6,1]:
    print(ratio)
    cellDancer = get_similarity_cellDancer(ratio,detail_input_path,raw_input_path,type='multi',foldername_para=foldername_para,path='Path1Upper')
    cellDancer.to_csv(analysis_result_path+'celldancer_similarity_eachCell'+str(ratio)+'.csv')
    sns.boxplot(x="ratio", y="similarity", hue='method', data=cellDancer)

########## scv correct col name
ratio_list=[1,0.8,0.6,0.4,0.2]
for ratio in ratio_list:
    scv_cell=pd.read_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/scvelo_similarity_eachCell'+str(ratio)+'.csv')
    scv_cell=scv_cell.rename(columns={"Unnamed: 0": "cellID", "cell": "gene"})
    scv_cell.to_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/scvelo_similarity_eachCell'+str(ratio)+'.csv',index=False)

########## celldancer correct col name
ratio_list=[0.6,0.4,0.2]
for ratio in ratio_list:
    scv_cell=pd.read_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/celldancer_similarity_eachCell'+str(ratio)+'.csv')
    scv_cell=scv_cell.rename(columns={"Unnamed: 0": "cellID", "cell": "gene"})
    scv_cell.to_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/celldancer_similarity_eachCell'+str(ratio)+'.csv',index=False)
###############################################
########## END - cosin similarity analysis ####
###############################################

###################################################
########## scv and celldancer error rate ##########
###################################################

ratio_list=[0.4]
ratio_list=[1,0.8,0.6,0.4,0.2]
sim_cutoff_list=[0.5,0.6,0.7,0.8,0.9]


for sim_cutoff in [0.7]:
    celldancer_error_df_all=pd.DataFrame()
    scv_error_df_all=pd.DataFrame()
    combined_error_df=pd.DataFrame()
    for ratio in ratio_list:
        print(ratio)

        #celldancer
        print('celldancer')
        celldancer_cell=pd.read_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/celldancer_similarity_eachCell'+str(ratio)+'.csv')
        celldancer_cell.loc[celldancer_cell.similarity<=sim_cutoff,'cutoff_count']=1
        celldancer_cell.loc[celldancer_cell.similarity>sim_cutoff,'cutoff_count']=0

        error_calc_celldancer=celldancer_cell[['gene','cutoff_count']].groupby('gene').sum().reset_index()
        error_calc_celldancer['error_rate']=error_calc_celldancer.cutoff_count/len(set(celldancer_cell.cellID))
        error_calc_celldancer['method']='celldancer'
        error_calc_celldancer['ratio']=ratio

        celldancer_error_df_all=celldancer_error_df_all.append(error_calc_celldancer)

        #scv
        print('scv')
        scv_cell=pd.read_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/scvelo_similarity_eachCell'+str(ratio)+'.csv')
        scv_cell.loc[scv_cell.similarity<=sim_cutoff,'cutoff_count']=1
        scv_cell.loc[scv_cell.similarity>sim_cutoff,'cutoff_count']=0

        error_calc_dynamic=scv_cell[scv_cell['method']=='dynamic'][['gene','cutoff_count']].groupby('gene').sum().reset_index()
        error_calc_dynamic['error_rate']=error_calc_dynamic.cutoff_count/len(set(scv_cell.cellID))
        error_calc_dynamic['method']='dynamic'
        error_calc_dynamic['ratio']=ratio

        error_calc_static=scv_cell[scv_cell['method']=='static'][['gene','cutoff_count']].groupby('gene').sum().reset_index()
        error_calc_static['error_rate']=error_calc_static.cutoff_count/len(set(scv_cell.cellID))
        error_calc_static['method']='static'
        error_calc_static['ratio']=ratio

        scv_error_df=pd.concat([error_calc_dynamic,error_calc_static])
        scv_error_df_all=scv_error_df_all.append(scv_error_df)
        
        # combine celldancer and scv
    combined_error_df=pd.concat([celldancer_error_df_all,scv_error_df_all])
    combined_error_df.to_csv(('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/'+'error_sim'+str(sim_cutoff)+'.csv'),index=False)
    plt.figure()
    plt.title('sim_cutoff '+str(sim_cutoff))
    sns.color_palette("flare", as_cmap=True)

    sns.boxplot(x="ratio", y="error_rate", hue='method', data=combined_error_df)
    plt.savefig('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/'+'error_sim'+str(sim_cutoff)+'.pdf')

combined_error_df_filtered_dot8=combined_error_df[combined_error_df.error_rate<=0.8]

plt.figure()

plt.rcParams["figure.figsize"] = (3.5,3)

plt.title('sim_cutoff '+str(sim_cutoff))
sns.color_palette("flare", as_cmap=True)
ax = sns.boxplot(x="ratio", y="error_rate", hue='method', data=combined_error_df_filtered_dot8,linewidth=0.3,showfliers = False)
ax = sns.stripplot(x="ratio", y="error_rate", hue='method', data=combined_error_df_filtered_dot8, jitter=True, split=True, linewidth=0.5,size=0.3,alpha=.5)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.savefig('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/analysis_result/'+'error_sim'+str(sim_cutoff)+'.pdf')

###################################################
#######End scv and celldancer error rate ##########
###################################################

###################################################
#### several samples for multipath  ###############
###################################################

import pandas as pd
from velocity_plot import velocity_plot as vpl
scv_result=pd.read_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/velocity_result/scv/scvelo_result_multi_path__s0_u0_s1_u1_dynamic_and_steady_df_1.csv')
celldancer_result=pd.read_csv('/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/velocity_result/celldancer/ratio1_all_geneLr0.001traceR0corrcoefR0C2cf0.3Downneighbors0_200_200Ratio0.125N30OAdam/detail_e200.csv')
scv_dynamic_result=scv_result[['gene_list','dynamic_s0','dynamic_u0','dynamic_s1','dynamic_u1']]
scv_static_result=scv_result[['gene_list','static_s0','static_u0','static_s1','static_u1']]
scv_dynamic_result=scv_dynamic_result.rename(columns={"gene_list": "gene_name", "dynamic_s0": "s0", "dynamic_u0": "u0","dynamic_s1": "s1", "dynamic_u1": "u1"})
scv_static_result=scv_static_result.rename(columns={"gene_list": "gene_name", "static_s0": "s0", "static_u0": "u0","static_s1": "s1", "static_u1": "u1"})
scv_dynamic_result['s1']=scv_dynamic_result.s0+scv_dynamic_result.s1
scv_dynamic_result['u1']=scv_dynamic_result.u0+scv_dynamic_result.u1

scv_static_result['u1']=scv_static_result.u0+scv_static_result.u1
scv_static_result['s1']=scv_static_result.s0+scv_static_result.s1

path='/Users/shengyuli/Library/CloudStorage/OneDrive-HoustonMethodist/work/Velocity/data/simulation/data/multi_path/multi_path/velocity_result/compare_gene_velocity_figures/'
for i in [2,38,50,60,58,59]:
    gene='simulation'+str(i)
    vpl.velocity_gene(gene,celldancer_result,alpha_inside=0.1,point_size=150,color_scatter='green',save_path=path+'celldancer_'+gene+'.pdf')
    vpl.velocity_gene(gene,scv_dynamic_result,alpha_inside=0.1,point_size=150,color_scatter='green',save_path=path+'dynamic_'+gene+'.pdf')
    vpl.velocity_gene(gene,scv_static_result,alpha_inside=0.1,point_size=150,color_scatter='green',save_path=path+'static_'+gene+'.pdf')
###################################################
#### end - several samples for multipath  #########
###################################################

