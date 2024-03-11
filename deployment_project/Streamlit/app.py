import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots

### Config
st.set_page_config(
    page_title="GetAround Analysis",
    page_icon= "🚗",
    layout="wide"
)

DATA_URL = ("https://jedha-deployment.s3.amazonaws.com/get_around_delay_analysis.xlsx")

st.title("GetAround Delay Analysis Web Dashboard 🚗")

st.markdown("""
    Welcome to the Streamlit Dashboard of Getaround app! 👋

""")

@st.cache_data
def load_data():
    data = pd.read_excel(DATA_URL, sheet_name='rentals_data')
    return data

st.header("Load and showcase data", divider="red")

data_load_state = st.text('Loading data ...')
data = load_data()
data_load_state.text("")

col1, col2 = st.columns(2)
with col1:
    st.write("Here's the 50 first rows of the dataset")
    st.write(data.head(50))
    
with col2:
    if st.checkbox('Show metadata'):
        st.subheader("Meaning of each column")
        metadata = pd.read_excel(DATA_URL, sheet_name='Documentation')
        pd.set_option('display.max_colwidth', None)
        st.write(metadata)

# Graph showing the late checkouts proportions
st.header("How often are drivers late for checkout?")
delay_perc = (data["delay_at_checkout_in_minutes"]>=0).value_counts(normalize=True)
fig = go.Figure(data=[go.Pie(labels=delay_perc.rename(index={True:'Late',False:'In advance or in time'}).index, values=delay_perc.values, textinfo='percent', hole=.5)])
fig.update_traces(marker=dict(colors=['#D13838','#FF9F9F']))
st.plotly_chart(fig)


st.header("Time Intervals and Delays")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Time Intervals between anticipated check-outs and next-check-in**")
    fig = px.histogram(data, x="time_delta_with_previous_rental_in_minutes",color_discrete_sequence=["indianred"])
    fig.update_layout(bargap=0.01)
    st.plotly_chart(fig,height = 400, use_container_width=True)
with col2:
    st.markdown("**Delays in minutes**")
    #Removing outliers for delay_at_checkout_in_minutes
    lower_bound = data['delay_at_checkout_in_minutes'].mean() - 3*data['delay_at_checkout_in_minutes'].std()
    upper_bound = data['delay_at_checkout_in_minutes'].mean() + 3*data['delay_at_checkout_in_minutes'].std()

    df = data[(data['delay_at_checkout_in_minutes'] > lower_bound) & (data['delay_at_checkout_in_minutes'] < upper_bound)]
    fig = px.histogram(df, x="delay_at_checkout_in_minutes", color_discrete_sequence=["indianred"])
    fig.update_layout(bargap=0.01)
    st.plotly_chart(fig, height = 400 , use_container_width=True)

st.subheader("Some data insights")

#Plotting 3 pies
pie = make_subplots(
    rows=1,
    cols=3,
    specs=[[{"type": "domain"}, {"type": "domain"},{"type": "domain"}]],
    shared_yaxes=True,
    subplot_titles=["State of rentals", "Checkin type","Proportion of cancellation by checkin type"],
)

state_perc = data["state"].value_counts() / len(data) * 100
checkin_perc = data["checkin_type"].value_counts() / len(data) * 100
canceled = (data[data['state']=='canceled']['checkin_type'].value_counts() / len(data[data['state']=='canceled'])) * 100

pie.add_trace(
    go.Pie(
        values=state_perc,
        labels=state_perc.index,
        marker_colors=["#E73636","#FF9F9F"],
    ),
    row=1,
    col=1,
)

pie.add_trace(
    go.Pie(
        values=checkin_perc,
        labels=checkin_perc.index,
        marker_colors=["#202EBD", "#13E7E3"],
    ),
    row=1,
    col=2,
)

pie.add_trace(
    go.Pie(
        values=canceled,
        labels=canceled.index,
        marker_colors=["#202EBD", "#13E7E3"],
    ),
    row=1,
    col=3,
)

pie.update_traces(hole=0.4, textinfo="label+percent")

pie.update_layout(width=1200, showlegend=True)

st.plotly_chart(pie)

st.subheader("Quick analysis")
st.markdown(""" * 80% of rentals are made via connect checkin type.  
* Around 15% of the overall rentals end up with cancellation.  
* However, although connect checkin type only represents 20% of the rentals, we can underline that 25% of the cancellations come from connect checkin type. 
* That highlights a bigger impact from this kind on rental flow over the cancellations.""")

st.write("")

# Difference between delay at checkout and the delta with previous rental
data['minutes_passed_checkin_time'] = data['delay_at_checkout_in_minutes'] - data['time_delta_with_previous_rental_in_minutes']

impacted_df = data[~data["time_delta_with_previous_rental_in_minutes"].isna()]

st.header("How many impacted and solved rentals cases depending on threshold and scope ?")

threshold_range = np.arange(0, 60*12, step=15) # 15min intervals for 12 hours
impacted_list_mobile = []
impacted_list_connect = []
impacted_list_total = []
solved_list_mobile = []
solved_list_connect = []
solved_list_total = []

solved_list = []
for t in range(721):
    connect_impact = impacted_df[impacted_df['checkin_type'] == 'connect']
    mobile_impact = impacted_df[impacted_df['checkin_type'] == 'mobile']
    connect_impact = connect_impact[connect_impact['time_delta_with_previous_rental_in_minutes'] < t]
    mobile_impact = mobile_impact[mobile_impact['time_delta_with_previous_rental_in_minutes'] < t]
    impacted = impacted_df[impacted_df['time_delta_with_previous_rental_in_minutes'] < t]
    impacted_list_connect.append(len(connect_impact))
    impacted_list_mobile.append(len(mobile_impact))
    impacted_list_total.append(len(impacted))

    solved = impacted_df[data['minutes_passed_checkin_time'] > 0]
    connect_solved = solved[solved['checkin_type'] == 'connect']
    mobile_solved = solved[solved['checkin_type'] == 'mobile']
    connect_solved = connect_solved[connect_solved['delay_at_checkout_in_minutes'] < t]
    mobile_solved = mobile_solved[mobile_solved['delay_at_checkout_in_minutes'] < t]
    solved = solved[solved['delay_at_checkout_in_minutes'] < t]
    solved_list_connect.append(len(connect_solved))
    solved_list_mobile.append(len(mobile_solved))
    solved_list_total.append(len(solved))


# Convert range to a list for 'x' argument
x_values = list(range(721))

col1, col2 = st.columns(2)
with col1:

    # Creation of the 3 traces
    total_impacted_cars = go.Scatter(x=x_values, y=impacted_list_total, name='All cars')
    impacted_connect_cars = go.Scatter(x=x_values, y=impacted_list_connect, name='Connect cars')
    impacted_mobile_cars = go.Scatter(x=x_values, y=impacted_list_mobile, name='Mobile cars')

    # Create layout for the plot
    layout = go.Layout(
        title='Number of impacted cases by threshold',
        xaxis=dict(title='Threshold in minutes'),
        yaxis=dict(title='Number of impacted cases'),
        xaxis_tickvals=list(range(0, 721, 60)),# 60 minutes step from 0 to 12h
        legend=dict(orientation='h', yanchor='bottom', xanchor='right',y=1.02, x=1)
    )

    # Create figure and add traces to it
    fig = go.Figure(data=[total_impacted_cars, impacted_connect_cars, impacted_mobile_cars], layout=layout)
    st.plotly_chart(fig, width = 800, height = 600, use_container_width=True)

with col2:

    # Creation of the 3 traces
    total_solved_cars = go.Scatter(x=x_values, y=solved_list_total, name='All cars')
    connect_solved_cars = go.Scatter(x=x_values, y=solved_list_connect, name='Connect cars')
    mobile_solved_cars = go.Scatter(x=x_values, y=solved_list_mobile, name='Mobile cars')

    # Create layout for the plot
    layout = go.Layout(
        title='Number of solved cases by threshold',
        xaxis=dict(title='Threshold in minutes'),
        yaxis=dict(title='Number of cases solved'),
        xaxis_tickvals=list(range(0, 721, 60)),# 60 minutes step from 0 to 12h
        legend=dict(orientation='h', yanchor='bottom', xanchor='right',y=1.02, x=1)
    )

    # Create figure and add traces to it
    fig = go.Figure(data=[total_solved_cars, connect_solved_cars, mobile_solved_cars], layout=layout)
    st.plotly_chart(fig, width = 800, height = 600, use_container_width=True)

st.subheader("Graph analysis")
st.markdown("""* The curve of solved cases tends to noticeably flatten out at around **120 minutes**, or even up to 180 minutes. * We might be tempted to implement a much higher threshold in order to solve as many problem cases as possible.
* But we're faced with a twofold problem : the higher the threshold, the greater the impact on the number of cars available and obviously on our revenue.  
* So we need to find the right balance between the number of problem cases solved and the proportion of revenue impacted.   
* With this in mind, :red[**120 minutes**] threshold seems to be a good compromise for our business.""")

st.write("")
st.header("Dynamic playground of threshold and scope effects")
st.markdown("You can here adjust the threshold and scope you desire to see the effects on data")
    ## Threshold and scope form
with st.form("threshold_testing"):
    threshold = st.slider("Choose the threshold in minutes", 0,720,0)
    checkin_type = st.radio("Choose the desired checkin type", ["All", "Connect", "Mobile"])
    submit = st.form_submit_button("Let's check it out")

    if submit:
        # Focus only on the selected checkin type
        st.markdown(f"With a threshold of **{threshold}** and for **{checkin_type}** scope")
        if checkin_type == "All":
            st.metric(f"The number of cases impacted is :",impacted_list_total[threshold])
            st.metric("The number of cases solved is :",solved_list_total[threshold])
        elif checkin_type == "Connect":
            st.metric(f"The number of cases impacted is :",impacted_list_connect[threshold])
            st.metric("The number of cases solved is :",solved_list_connect[threshold])
        else :
            st.metric(f"The number of cases impacted is :",impacted_list_mobile[threshold])
            st.metric("The number of cases solved is :",solved_list_mobile[threshold])


