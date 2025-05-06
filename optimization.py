import numpy as np
from sklearn.cluster import KMeans
from utils import warehousing_cost

def _assign(df, centers):
    dists = np.linalg.norm(
        df[['Longitude', 'Latitude']].values[:, None, :] - centers[None, :, :],
        axis=2,
    )
    idx = dists.argmin(axis=1)
    return idx, dists.min(axis=1)

def evaluate(df, centers, rate, sqft_per_lb, cost_per_sqft, fixed_cost):
    idx, dist = _assign(df, centers)
    assigned = df.copy()
    assigned['Warehouse'] = idx
    assigned['DistMiles'] = dist

    trans = (assigned['DistMiles'] * assigned['DemandLbs'] * rate).sum()

    wh_cost = 0.0
    demand_list = []
    for i in range(len(centers)):
        demand = assigned.loc[assigned['Warehouse'] == i, 'DemandLbs'].sum()
        demand_list.append(demand)
        wh_cost += warehousing_cost(demand, sqft_per_lb, cost_per_sqft, fixed_cost)

    return trans + wh_cost, trans, wh_cost, assigned, demand_list

def optimize(
    df,
    k_vals,
    rate,
    sqft_per_lb,
    cost_per_sqft,
    fixed_cost,
    fixed_centers=None,
    seed=42,
):
    # Ensure fixed_centers becomes (n, 2) array even when empty
    if fixed_centers:
        fixed_centers = np.asarray(fixed_centers, dtype=float).reshape(-1, 2)
    else:
        fixed_centers = np.empty((0, 2))

    coords = df[['Longitude', 'Latitude']].values
    weights = df['DemandLbs'].values

    best = None
    for k in k_vals:
        if k < len(fixed_centers):
            continue  # can't have fewer centers than fixed

        k_rem = k - len(fixed_centers)
        if k_rem == 0:
            centers = fixed_centers
        else:
            km = KMeans(n_clusters=k_rem, n_init='auto', random_state=seed)
            km.fit(coords, sample_weight=weights)
            centers = np.vstack([fixed_centers, km.cluster_centers_])

        total, trans, wh, assigned, d_list = evaluate(
            df, centers, rate, sqft_per_lb, cost_per_sqft, fixed_cost
        )

        if best is None or total < best['total_cost']:
            best = {
                'k': k,
                'total_cost': total,
                'trans_cost': trans,
                'wh_cost': wh,
                'centers': centers,
                'assigned_df': assigned,
                'demand_per_wh': d_list,
            }

    return best
