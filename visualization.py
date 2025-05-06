import pydeck as pdk
import pandas as pd
import streamlit as st

_PALETTE = [
    [31,119,180], [255,127,14], [44,160,44], [214,39,40],
    [148,103,189], [140,86,75], [227,119,194], [127,127,127],
    [188,189,34], [23,190,207]
]

def _rgb(idx):
    return _PALETTE[idx % len(_PALETTE)]

def plot_network(stores_df, centers):
    st.subheader("Network Map")
    center_df = pd.DataFrame(centers, columns=['Longitude','Latitude'])

    # Build edges with RGBA colors
    edges = []
    for _, row in stores_df.iterrows():
        idx = int(row['Warehouse'])
        wh = center_df.iloc[idx]
        r,g,b = _rgb(idx)
        edges.append({
            'from_lon': row['Longitude'], 'from_lat': row['Latitude'],
            'to_lon': wh['Longitude'], 'to_lat': wh['Latitude'],
            'color': [r, g, b, 160]
        })
    edges_df = pd.DataFrame(edges)

    edge_layer = pdk.Layer(
        'LineLayer',
        data=edges_df,
        get_source_position='[from_lon, from_lat]',
        get_target_position='[to_lon, to_lat]',
        get_color='color',
        get_width=2
    )

    # Warehouses with matching colors
    center_df[['r','g','b']] = [_rgb(i) for i in range(len(center_df))]
    wh_layer = pdk.Layer(
        'ScatterplotLayer',
        data=center_df,
        get_position='[Longitude, Latitude]',
        get_fill_color='[r, g, b]',
        get_radius=35000,
        opacity=0.9
    )

    store_layer = pdk.Layer(
        'ScatterplotLayer',
        data=stores_df,
        get_position='[Longitude, Latitude]',
        get_fill_color='[0, 128, 255]',
        get_radius=12000,
        opacity=0.6
    )

    view_state = pdk.ViewState(latitude=39, longitude=-98, zoom=3.5)
    deck = pdk.Deck(layers=[edge_layer, store_layer, wh_layer],
                    initial_view_state=view_state,
                    map_style='mapbox://styles/mapbox/light-v10')
    st.pydeck_chart(deck)

def summary(stores_df, total_cost, trans_cost, wh_cost, centers, demand_per_wh, sqft_per_lb):
    st.subheader("Cost Summary")
    st.metric("Total Annual Cost", f"${total_cost:,.0f}")
    col1, col2 = st.columns(2)
    col1.metric("Transportation", f"${trans_cost:,.0f}")
    col2.metric("Warehousing", f"${wh_cost:,.0f}")

    # Warehouse table
    center_df = pd.DataFrame(centers, columns=['Longitude','Latitude'])
    center_df['DemandLbs'] = demand_per_wh
    center_df['SqFt'] = center_df['DemandLbs'] * sqft_per_lb
    center_df.index.name = 'Warehouse'
    st.subheader("Warehouse Demand & Size")
    st.dataframe(center_df[['DemandLbs','SqFt','Latitude','Longitude']].style.format({'DemandLbs':'{:,}','SqFt':'{:,}'}))

    st.subheader("Stores per Warehouse")
    st.bar_chart(stores_df['Warehouse'].value_counts().sort_index())
        # Distance bucket chart
        buckets = pd.cut(stores_df['DistMiles'], bins=[-1,350,500,700,99999], labels=['Next Day 7am','Next Day 10am','End of Next Day','2 Days+'])
        bucket_counts = buckets.value_counts().reindex(['Next Day 7am','Next Day 10am','End of Next Day','2 Days+']).fillna(0)
        st.subheader('Distance Buckets')
        st.bar_chart(bucket_counts)