import numpy as np
from sklearn.cluster import KMeans
from utils import warehousing_cost

def _assign(df,centers):
    d=np.linalg.norm(df[['Longitude','Latitude']].values[:,None,:]-centers[None,:,:],axis=2)
    idx=d.argmin(axis=1)
    return idx,d.min(axis=1)

def evaluate(df,centers,rate,sqft_per_lb,cost_per_sqft,fixed):
    idx,dist=_assign(df,centers)
    assigned=df.copy()
    assigned['Warehouse']=idx
    assigned['DistMiles']=dist
    trans=(assigned['DistMiles']*assigned['DemandLbs']*rate).sum()
    wh=0.0; demand_list=[]
    for i in range(len(centers)):
        demand=assigned.loc[assigned['Warehouse']==i,'DemandLbs'].sum()
        demand_list.append(demand)
        wh+=warehousing_cost(demand,sqft_per_lb,cost_per_sqft,fixed)
    return trans+wh,trans,wh,assigned,demand_list

def optimize(df,k_vals,rate,sqft_per_lb,cost_per_sqft,fixed,fixed_centers=None,seed=42):
    if fixed_centers is None: fixed_centers=[]
    fixed_centers=np.array(fixed_centers)
    coords=df[['Longitude','Latitude']].values
    weights=df['DemandLbs'].values
    best=None
    for k in k_vals:
        if k < len(fixed_centers): continue
        k_rem=k-len(fixed_centers)
        if k_rem==0:
            centers=fixed_centers
        else:
            km=KMeans(n_clusters=k_rem,n_init='auto',random_state=seed)
            km.fit(coords,sample_weight=weights)
            centers=np.vstack([fixed_centers,km.cluster_centers_])
        tot,trans,wh,assigned,d_list=evaluate(df,centers,rate,sqft_per_lb,cost_per_sqft,fixed)
        if best is None or tot<best['total_cost']:
            best=dict(k=k,total_cost=tot,trans_cost=trans,wh_cost=wh,
                      centers=centers,assigned_df=assigned,demand_per_wh=d_list)
    return best
