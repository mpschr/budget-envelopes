from datetime import datetime
import pandas 

import matplotlib.pyplot as plt

def plot_month(envelopes: pandas.DataFrame, output_file: str):
    envelopes = envelopes.fillna(0)

    #print(envelopes)

    plt.style.use('dark_background')

    envelopes['state_pct'] = envelopes.apply(lambda r: max(min(r.state/(r.budget+abs(r.carryover)),1),0)*100, axis=1)
    envelopes['budget_pct'] = envelopes.apply(lambda r: (r.budget /(r.budget+abs(r.carryover)))*100 if r.budget + r.carryover > 0  else 0, axis=1)
    envelopes['carryover_pos_pct'] = envelopes.apply(lambda r: (abs(r.carryover)/(r.budget+abs(r.carryover)))*100 if r.carryover > 0 else None , axis=1)
    envelopes['carryover_neg_pct'] = envelopes.apply(lambda r: (abs(r.carryover)/(r.budget+abs(r.carryover)))*100 if r.carryover < 0 else None, axis=1)
    envelopes['total_budget_string'] = envelopes.apply(lambda r: f"{round(r.budget)} {'+' if r.carryover > 0 else '-'} {abs(round(r.carryover))} CHF", axis=1)
    envelopes = envelopes.fillna(0)

    fig = plt.figure(figsize=(10, 20))
    ax = fig.add_subplot(111)
    contextbar_width = 0.05
    ax.barh(y=envelopes.envelope, width=envelopes.state_pct, height=0.35, align='edge', color='grey')
    ax.barh(y=envelopes.envelope, width=envelopes.budget_pct, height=contextbar_width, align='center', color='grey')
    ax.barh(y=envelopes.envelope, width=envelopes.carryover_pos_pct, left=envelopes.budget_pct, height=contextbar_width, align='center', color='yellow')
    ax.barh(y=envelopes.envelope, width=envelopes.carryover_neg_pct, left=envelopes.budget_pct, height=contextbar_width, align='center', color='red')


    #ax = envelopes.sort_values('envelope',ascending=False).plot.barh('envelope','state_pct',figsize=(10, 16), legend=False, color='grey')
    for p,state in zip(ax.patches,envelopes.sort_values('envelope',ascending=False).state.tolist()):
        ax.annotate(str(f" {state} CHF"), (0 ,p.get_y()+0.1),  weight='bold',color='w')
    for p,total_budget in zip(ax.patches,envelopes.sort_values('envelope',ascending=False).total_budget_string.tolist()):
        ax.annotate(str(total_budget.replace(' - 0','')), (80 ,p.get_y()+0.1), color='w')        
        #ax.annotate(str(f" {total_budget} CHF"), (85 ,p.get_y()+0.1), color='w')        

    ax.text(1.01, .97, f'updated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ha='left', va='top', transform=ax.transAxes, rotation='vertical')
    plt.tight_layout()
    #plt.show()
    fig.savefig(output_file, format='png', transparent=True, bbox_inches='tight')