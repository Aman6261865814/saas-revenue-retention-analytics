
from common import *

def run():
    rng=np.random.default_rng(SEED)
    n=2400
    accounts=pd.DataFrame({'account_id':np.arange(1,n+1),'region':rng.choice(['Americas','EMEA','APAC'],n,p=[.45,.30,.25]),
         'segment':rng.choice(['SMB','Mid-market','Enterprise'],n,p=[.6,.3,.1]),'signup_month':rng.integers(0,15,n)})
    rows=[]
    months=pd.date_range('2025-01-01',periods=18,freq='MS')
    for a in accounts.itertuples():
        base={'SMB':49,'Mid-market':249,'Enterprise':1499}[a.segment]
        mrr=0.; ever=False; lost=False
        for i,date in enumerate(months):
            prev=mrr
            if i<a.signup_month: mrr=0.
            elif i==a.signup_month: mrr=float(base);ever=True
            elif mrr>0:
                u=rng.random()
                if u<.032: mrr=0.;lost=True
                elif u<.11: mrr=round(mrr*1.2,2)
                elif u<.15: mrr=round(mrr*.85,2)
            elif lost and rng.random()<.045: mrr=float(base);lost=False
            kind=('new' if prev==0 and mrr>0 and i==a.signup_month else
                  'reactivation' if prev==0 and mrr>0 else
                  'churn' if prev>0 and mrr==0 else
                  'expansion' if mrr>prev else 'contraction' if mrr<prev else 'unchanged')
            rows.append([a.account_id,date.strftime('%Y-%m-%d'),prev,mrr,kind])
    raw=pd.DataFrame(rows,columns=['account_id','month','previous_mrr','mrr','movement'])
    raw=pd.concat([raw,raw.sample(200,random_state=SEED)],ignore_index=True)
    write(raw,'subscription_snapshots','raw');write(accounts,'accounts','raw')
    fact,removed=load_clean(raw,['account_id','month'])
    fact=fact.merge(accounts[['account_id','region','segment','signup_month']],validate='many_to_one')
    fact['delta']=fact.mrr-fact.previous_mrr
    for name in ['new','reactivation','expansion','contraction','churn']:
        fact[name+'_mrr']=np.where(fact.movement==name,fact.delta,0.)
    fact['active']=(fact.mrr>0).astype(int)
    fact['starting_active']=(fact.previous_mrr>0).astype(int)
    fact['churned']=(fact.movement=='churn').astype(int)
    fact['retained_mrr']=np.where(fact.previous_mrr>0,fact.mrr,0.)
    monthly=fact.groupby('month',as_index=False).agg(start_mrr=('previous_mrr','sum'),end_mrr=('mrr','sum'),
      new_mrr=('new_mrr','sum'),reactivation_mrr=('reactivation_mrr','sum'),expansion_mrr=('expansion_mrr','sum'),
      contraction_mrr=('contraction_mrr','sum'),churn_mrr=('churn_mrr','sum'),retained_mrr=('retained_mrr','sum'),
      active_accounts=('active','sum'),starting_accounts=('starting_active','sum'),churned_accounts=('churned','sum'))
    monthly['nrr']=monthly.retained_mrr/monthly.start_mrr.replace(0,np.nan)
    monthly['logo_churn_rate']=monthly.churned_accounts/monthly.starting_accounts.replace(0,np.nan)
    monthly['bridge_residual']=monthly.end_mrr-monthly[['start_mrr','new_mrr','reactivation_mrr','expansion_mrr','contraction_mrr','churn_mrr']].sum(axis=1)
    assert np.allclose(monthly.bridge_residual,0,atol=1e-7)
    fact['age_month']=pd.to_datetime(fact.month).dt.month+12*(pd.to_datetime(fact.month).dt.year-2025)-1-fact.signup_month
    cohorts=fact[fact.age_month>=0].groupby(['signup_month','age_month'],as_index=False).agg(active=('active','sum'),cohort_size=('account_id','count'))
    cohorts['retention']=cohorts.active/cohorts.cohort_size
    last=monthly.iloc[-1]
    metrics={'accounts':n,'snapshots':len(fact),'duplicate_retries_removed':removed,'ending_mrr_usd':round(last.end_mrr,2),
       'latest_nrr':float(last.nrr),'latest_logo_churn_rate':float(last.logo_churn_rate),'max_bridge_residual':float(monthly.bridge_residual.abs().max())}
    summary=f"""## Decision\nEnding MRR is ${last.end_mrr:,.2f}; latest-month NRR is {last.nrr:.1%}. Inspect churn and contraction by segment before funding acquisition.\n\n## Evidence\n{len(fact):,} account-month snapshots; {removed} exact retry duplicates removed. All 18 revenue bridges reconcile to floating-point tolerance. NRR follows accounts paying at the start of each month; new and reactivated accounts are excluded.\n\n## Limits and next action\nMRR is normalized subscription value, not recognized revenue or cash collected. Retention includes reactivation, so cohort curves may rise. The final cohorts have shorter observation windows, not zero retention in future months. Segment comparisons are descriptive, not causal. Validate billing adjustments and constant-currency rules before a production rollout.\n"""
    def charts():
        fig,ax=plt.subplots(figsize=(11,4));ax.plot(monthly.month,monthly.end_mrr,marker='o');ax.set(title='Monthly recurring revenue | synthetic USD',ylabel='MRR (USD)');ax.tick_params(axis='x',rotation=45);fig.tight_layout();fig.savefig(ROOT/'reports'/'revenue.png',dpi=160);plt.close(fig)
        fig,ax=plt.subplots(figsize=(11,6));sns.heatmap(cohorts.pivot(index='signup_month',columns='age_month',values='retention'),vmin=0,vmax=1,cmap='Blues',ax=ax);ax.set(title='Cohort retention | blanks are unobserved',ylabel='Signup month index (0 = Jan 2025)',xlabel='Months since signup');fig.tight_layout();fig.savefig(ROOT/'reports'/'cohorts.png',dpi=160);plt.close(fig)
    dims=accounts[['account_id','region','segment']]
    finish({'fact_subscription':fact.drop(columns=['region','segment','signup_month']), 'dim_account':dims,'monthly_metrics':monthly,'cohort_retention':cohorts},metrics,summary,'SaaS Revenue & Retention Observatory',charts)

if __name__=='__main__':run()
