import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import date
import json
import requests

# --- import data from CovidTracking.com
url_main = 'https://covidtracking.com/'

r_hist_data = requests.get(url_main+'api/v1/states/daily.json')
r_state_data = requests.get(url_main+'api/v1/states/current.json')

# --- historical data
USdf = pd.read_json(r_hist_data.text)
USdf['date'] = pd.to_datetime(USdf.date, format='%Y%m%d')
USdf = USdf.fillna(0)
USdf = USdf.sort_values(by=['date']).reset_index()
US_tot = USdf.groupby('date').sum().reset_index()

# --- state total current data
Sdf = pd.read_json(r_state_data.text)

# --- drop US territories and DC
Sdf = Sdf[:-5]
Sdf = Sdf[Sdf.state!='DC']
#----
Spop = pd.read_csv("E:\\Personal\\PythonScripts\\Coronavirus\\StatePop.csv")
Spop = Spop.sort_values(by=["State"],ascending=True).reset_index()
Sdf = Sdf.sort_values(by=["state"],ascending=True).reset_index()

S_testp = Sdf.totalTestResults.div(Spop.PopEstimate)*100

# --- state plot

f, axs = plt.subplots(figsize=(10,10))
axs.set_title("Covid Testing by State")
sns.set(style="whitegrid")
axs.grid(which="minor",color="gray",linestyle='--', alpha=0.25)
axs.grid(which="major",color="gray",linestyle='--', alpha=0.4)
sns.barplot(x=S_testp, y=Spop.State,palette='deep',alpha=0.75)
axs.set_xlabel('Percent of 2019 Population Tested')
sns.despine(bottom=True,left=True)

rects = axs.patches

for rect in rects:
    x_val = rect.get_width()
    y_val = rect.get_y() + rect.get_height() / 1.75
    space = 10.0
    ha = 'left'
    label = "{:.2f}".format(x_val)+str('%')
    axs.annotate(
        label,
        xy=(x_val,y_val),
        xytext=(space,0),
        textcoords="offset points",
        va='center',
        ha=ha,
        fontsize=10
    )
plt.tight_layout()
plt.savefig("Ouput\\CovidTesting_"+str(date.today())+".pdf",dpi=300)

#
def summary(state):
    f, axs = plt.subplots(nrows=3,ncols=2,figsize=(12,9))
    sns.set_style("ticks")

    f.suptitle('CoVid Summary for '+str(state),
               fontsize=24)

    date_form = DateFormatter('%m/%d')

    # TOP LEFT
    # --- total daily tests
    sns.lineplot(x=USdf.loc[USdf.state==state].date, y=USdf.loc[USdf.state==state].totalTestResults,ax=axs[0,0])

    # TOP RIGHT
    # --- percentage of infected relative to tests
    axs[0,1].yaxis.tick_right()
    pos = USdf.loc[USdf.state==state].positive.div(USdf.loc[USdf.state==state].totalTestResults)*100
    hosp = USdf.loc[USdf.state==state].hospitalized.div(USdf.loc[USdf.state==state].totalTestResults)*100
    sns.lineplot(x=USdf.loc[USdf.state==state].date, y=pos,ax=axs[0,1],label='Positive')
    sns.lineplot(x=USdf.loc[USdf.state==state].date, y=hosp,ax=axs[0,1],label='Hospitalized')

    # MID LEFT
    # --- total daily deaths
    sns.lineplot(x=USdf.loc[USdf.state==state].date, y=USdf.loc[USdf.state==state].death,
                ax=axs[1,0],color='b')

    # MID RIGHT
    # daily increases of cases
    axs[1,1].yaxis.tick_right()
    sns.lineplot(x=USdf.loc[USdf.state==state].date, y=USdf.loc[USdf.state==state].positive,
                 ax=axs[1,1],color='b')

    # BOT RIGHT
    # Percentage increases
    axs[2,1].yaxis.tick_right()
    sns.lineplot(x=USdf.loc[USdf.state==state].date,y=USdf.loc[USdf.state==state].positive.pct_change()*100,
                 ax=axs[2,1], label='State')
    sns.lineplot(x=US_tot.date, y=US_tot.positive.pct_change()*100,
                 ax=axs[2,1], label="US", dashes=[4, 1])
    #sns.lineplot(x=USdf.loc[USdf.state==state].date,y=USdf.loc[USdf.state==state].positive.pct_change(periods=7)*100,
    #             ax=axs[2,1],
    #             label='WoW (7-day)')

    # BOT LEFT
    # Percentage increases
    axs[2,1].yaxis.tick_right()
    sns.lineplot(x=USdf.loc[USdf.state==state].date,y=USdf.loc[USdf.state==state].death.pct_change()*100,
                 ax=axs[2,0], label='State')
    sns.lineplot(x=US_tot.date, y=US_tot.death.pct_change()*100,
                 ax=axs[2,0], label='US', dashes=[(4, 1), (1, 1)])

    for ax in axs.reshape(-1):
        if ax == axs[0,1]:
            ax.legend(loc='best')
        ax.set_xlabel('')
        ax.set_ylabel('')
        if ax!=axs[1,1]:
            ax.xaxis.set_major_formatter(date_form)
            ax.grid(which="major",color="gray",linestyle='--', alpha=0.4)
        else:
            ax.xaxis.set_visible(False)

    #--- set titles
    axs[0,0].set_ylabel('Total Tests Administered')
    axs[0,1].set_ylabel('Percentage of\nTested Outcomes')
    axs[1,0].set_ylabel('Total Deaths')
    axs[1,1].set_ylabel('Positive Test\n Daily Increases')
    axs[2,1].set_ylabel('Positive\nDay-over-Day %-Change')
    axs[2,0].set_ylabel('Death Rate\nDay-over-Day %-Change')

    return f, axs

def summarytotal():
    f, axs = plt.subplots(3,2,figsize=(12,9))
    sns.set_style("ticks")

    f.suptitle('CoVid Summary for United States',
               fontsize=24)

    # TOP LEFT
    # --- total daily tests
    sns.lineplot(x=US_tot.date, y=US_tot.totalTestResults,ax=axs[0,0])

    # TOP RIGHT
    # --- percentage of infected relative to tests
    axs[0,1].yaxis.tick_right()
    pos = US_tot.positive.div(US_tot.totalTestResults)*100
    hosp = US_tot.hospitalized.div(US_tot.totalTestResults)*100
    sns.lineplot(x=US_tot.date, y=pos,ax=axs[0,1],label='Positive')
    sns.lineplot(x=US_tot.date, y=hosp,ax=axs[0,1],label='Hospitalized')

    # MID LEFT
    # --- total daily deaths
    sns.lineplot(x=US_tot.date, y=US_tot.death,ax=axs[1,0], color='b')

    # MID RIGHT
    # daily increases of cases
    axs[1,1].yaxis.tick_right()
    sns.lineplot(x=US_tot.date, y=US_tot.positiveIncrease,ax=axs[1,1], color='b')

    # BOT RIGHT
    # Percentage increases
    axs[2,1].yaxis.tick_right()
    sns.lineplot(x=US_tot.date, y=US_tot.positive.pct_change()*100,
                 ax=axs[2,1])

    # BOT LEFT
    # Percentage increases
    axs[2,1].yaxis.tick_right()
    sns.lineplot(x=US_tot.date, y=US_tot.death.pct_change()*100,
                 ax=axs[2,0])

    date_form = DateFormatter('%m/%d')

    for ax in axs.reshape(-1):
        if ax == axs[0,1]:
            ax.legend(loc='best')
        ax.set_xlabel('')
        ax.set_ylabel('')
        if ax!=axs[1,1]:
            ax.xaxis.set_major_formatter(date_form)
            ax.grid(which="major",color="gray",linestyle='--', alpha=0.4)
        else:
            ax.xaxis.set_visible(False)

    #--- set titles
    axs[0,0].set_ylabel('Total Tests Administered')
    axs[0,1].set_ylabel('Percentage of\nTested Outcomes')
    axs[1,0].set_ylabel('Total Deaths')
    axs[1,1].set_ylabel('Positive Test\n Daily Increases')
    axs[2,1].set_ylabel('Positive Test\nDay-over-Day %-Change')
    axs[2,0].set_ylabel('Death Rate\nDay-over-Day %-Change')

    return f, axs

# --- generate plots
states = ['NY', 'CA','LA','MI','MA']

for s in states:
    summary(s)
    plt.savefig(str(s)+str(date.today())+'.png',dpi=300)

summarytotal()
plt.savefig('US_'+str(date.today())+'.png',dpi=300)


# -- facet grid of all 50 states --
#g = sns.FacetGrid(data=USdf, col='state', col_wrap=5)
#g = g.map(plt.plot,"date","positive",marker=".")
#plt.show()
print('************ Plotting & Saving Complete ************')
