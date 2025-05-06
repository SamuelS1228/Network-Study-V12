import pydeck as pdk, pandas as pd, streamlit as st
_PAL=[[31,119,180],[255,127,14],[44,160,44],[214,39,40],[148,103,189],[140,86,75],[227,119,194],[127,127,127],[188,189,34],[23,190,207]]
def _color(i): return _PAL[i%len(_PAL)]
def plot_network(stores,centers):
    st.subheader("Network Map")
    cen_df=pd.DataFrame(centers,columns=['Longitude','Latitude'])
    edges=[{'f':[r.Longitude,r.Latitude],'t':[cen_df.iloc[int(r.Warehouse)].Longitude,cen_df.iloc[int(r.Warehouse)].Latitude],'color':_color(int(r.Warehouse))+[160]} for r in stores.itertuples()]
    edge_layer=pdk.Layer('LineLayer',data=edges,get_source_position='f',get_target_position='t',get_color='color',get_width=2)
    cen_df[['r','g','b']]=[_color(i) for i in range(len(cen_df))]
    wh_layer=pdk.Layer('ScatterplotLayer',data=cen_df,get_position='[Longitude,Latitude]',get_fill_color='[r,g,b]',get_radius=35000,opacity=0.9)
    store_layer=pdk.Layer('ScatterplotLayer',data=stores,get_position='[Longitude,Latitude]',get_fill_color='[0,128,255]',get_radius=12000,opacity=0.6)
    deck=pdk.Deck(layers=[edge_layer,store_layer,wh_layer],initial_view_state=pdk.ViewState(latitude=39,longitude=-98,zoom=3.5),map_style='mapbox://styles/mapbox/light-v10')
    st.pydeck_chart(deck)
def summary(stores,total,trans,wh,centers,demand,sqft_per_lb):
    import pandas as pd
    st.subheader("Cost Summary")
    col1,col2=st.columns(2)
    st.metric("Total Annual Cost",f"${total:,.0f}")
    col1.metric("Transportation",f"${trans:,.0f}")
    col2.metric("Warehousing",f"${wh:,.0f}")
    cen_df=pd.DataFrame(centers,columns=['Longitude','Latitude'])
    cen_df['DemandLbs']=demand
    cen_df['SqFt']=cen_df['DemandLbs']*sqft_per_lb
    st.subheader("Warehouse Demand & Size")
    st.dataframe(cen_df[['DemandLbs','SqFt','Latitude','Longitude']].style.format({'DemandLbs':'{:,}','SqFt':'{:,}'}))
    # distance buckets
    buckets=pd.cut(stores['DistMiles'],bins=[-1,350,500,700,1e9],labels=['Next Day 7am','Next Day 10am','End of Next Day','2 Days+'])
    st.subheader("Stores by Distance Bucket")
    st.bar_chart(buckets.value_counts().reindex(['Next Day 7am','Next Day 10am','End of Next Day','2 Days+']).fillna(0))
