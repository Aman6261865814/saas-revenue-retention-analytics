
from pathlib import Path
import json, sqlite3, time, statistics
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'project.json').read_text())
kind=CONFIG['kind']; title=CONFIG['title']
metrics=json.loads((ROOT/'reports/metrics.json').read_text())
if kind=='saas':
    fact=pd.read_csv(ROOT/'data/processed/fact_subscription.csv').merge(pd.read_csv(ROOT/'data/processed/dim_account.csv'),validate='many_to_one')
    source=fact.groupby(['month','segment'],as_index=False).agg(numerator=('mrr','sum'),denominator=('active','sum'))
    source.columns=['period','category','numerator','denominator']
    lookup=[['SMB','Small business'],['Mid-market','Mid-market'],['Enterprise','Enterprise']]
    metric_label='MRR per active account (USD)'; chart_label='MRR (USD)'
    dates=sorted(fact.month.unique()); dimension='segment'; period='month'; numerator='mrr';denominator='active'
elif kind=='experiment':
    fact=pd.read_csv(ROOT/'data/processed/fact_experiment.csv')
    source=fact.groupby(['assigned_date','variant'],as_index=False).agg(numerator=('converted','sum'),denominator=('user_id','count'))
    source.columns=['period','category','numerator','denominator'];lookup=[['control','Original onboarding'],['treatment','New onboarding']]
    metric_label='Seven-day conversion rate';chart_label='Conversion rate'
    dates=sorted(fact.assigned_date.unique());dimension='variant';period='assigned_date';numerator='converted';denominator=None
else:
    fact=pd.read_csv(ROOT/'data/processed/fact_ticket.csv')
    source=fact.groupby(['opened_day','queue'],as_index=False).agg(numerator=('sla_breach','sum'),denominator=('sla_eligible','sum'))
    source.columns=['period','category','numerator','denominator'];lookup=[[x,x+' support'] for x in sorted(fact.queue.unique())]
    metric_label='Eligible-ticket SLA breach rate';chart_label='Breach rate'
    dates=sorted(fact.opened_day.unique());dimension='queue';period='opened_day';numerator='sla_breach';denominator='sla_eligible'
source.to_csv(ROOT/'excel/source_metrics.csv',index=False)
(ROOT/'excel/workbook_input.json').write_text(json.dumps({'title':title,'kind':kind,'metric_label':metric_label,'lookup':lookup,'source':source.values.tolist(),'headers':source.columns.tolist()},indent=2))
regional=fact.groupby(['region',period,dimension],as_index=False).agg(numerator=(numerator,'sum'),denominator=(denominator or 'user_id','sum' if denominator else 'count'))
regional.columns=['region','period','category','numerator','denominator']
records=regional.to_dict('records')
body=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title><style>
body{margin:0;background:#f4f7fb;color:#132238;font:16px/1.6 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:40px 24px}small,.eyebrow{color:#52657d}h1{font-size:38px;line-height:1.15;max-width:900px}h2{font-size:22px}section,.card{background:white;border:1px solid #dce4ef;border-radius:14px;padding:24px;margin:20px 0}label{display:inline-block;margin:8px 20px 8px 0}select{padding:9px;border-radius:7px;border:1px solid #b8c6d8}#cards{display:flex;gap:16px;flex-wrap:wrap}.card{flex:1;min-width:180px;margin:0}.big{font-size:32px;font-weight:700;color:#174ba4}table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:10px;border-bottom:1px solid #e1e8f0}th{background:#edf3fb}svg{width:100%;height:auto}.pill{display:inline-block;background:#fff2cf;padding:4px 12px;border-radius:20px;font-size:13px}.notes{max-width:900px}a{color:#1d4ed8}button{padding:10px 15px;background:#164eb1;color:white;border:0;border-radius:7px;cursor:pointer}@media(max-width:650px){h1{font-size:28px}main{padding:20px 14px}section{padding:16px}}
</style></head><body><main><div class="eyebrow">AMAN KUMAR MISHRA / ANALYTICS CASE STUDY</div><h1>__TITLE__</h1><span class="pill">Synthetic data · Independent portfolio project</span><p class="notes">__CONTEXT__</p><section><label>Region <select id="region"><option>All regions</option><option>Americas</option><option>EMEA</option><option>APAC</option></select></label><label>Period <select id="period"></select></label><button id="export">Export current view</button><p><small>Filters change descriptive results only. This browser file contains all synthetic regions; it is not a security boundary.</small></p></section><div id="cards"></div><section><h2>__CHART__ by category</h2><svg id="chart" viewBox="0 0 1000 280" role="img" aria-label="Category comparison"></svg><table><thead><tr><th>Category</th><th>Numerator</th><th>Denominator</th><th>__METRIC__</th></tr></thead><tbody id="rows"></tbody></table></section><section><h2>Decision and limitations</h2><div id="decision"></div><p>See <a href="executive_brief.md">executive brief</a>, <a href="metrics.json">metric evidence</a>, and <a href="../README.md">reproduction guide</a>.</p></section></main><script>
const data=__DATA__,kind=__KIND__,metrics=__METRICS__;
const periods=[...new Set(data.map(r=>r.period))].sort();const sel=document.querySelector('#period');
sel.innerHTML=(kind==='saas'?'':'<option>All periods</option>')+periods.map(p=>`<option>${p}</option>`).join('');if(kind==='saas')sel.value=periods.at(-1);
let current=[];const fmt=x=>x.toLocaleString('en-US',{maximumFractionDigits:2});
function update(){let region=document.querySelector('#region').value,period=sel.value;let groups={};data.filter(r=>(region==='All regions'||r.region===region)&&(period==='All periods'||r.period===period)).forEach(r=>{groups[r.category]??={category:r.category,n:0,d:0};groups[r.category].n+=r.numerator;groups[r.category].d+=r.denominator});current=Object.values(groups);let n=current.reduce((s,r)=>s+r.n,0),d=current.reduce((s,r)=>s+r.d,0);let val=d?n/d:null;document.querySelector('#cards').innerHTML=`<div class="card"><small>${kind==='saas'?'Ending MRR (USD)':'Numerator'}</small><div class="big">${fmt(n)}</div></div><div class="card"><small>${kind==='saas'?'Active accounts':kind==='experiment'?'Assigned users':'Eligible tickets'}</small><div class="big">${fmt(d)}</div></div><div class="card"><small>__METRIC__</small><div class="big">${val===null?'N/A':kind==='saas'?'$'+fmt(val):(100*val).toFixed(2)+'%'}</div></div>`;
document.querySelector('#rows').innerHTML=current.map(r=>`<tr><td>${r.category}</td><td>${fmt(r.n)}</td><td>${fmt(r.d)}</td><td>${!r.d?'N/A':kind==='saas'?'$'+fmt(r.n/r.d):(100*r.n/r.d).toFixed(2)+'%'}</td></tr>`).join('');
let max=Math.max(...current.map(r=>kind==='saas'?r.n:r.d?r.n/r.d:0),.01);document.querySelector('#chart').innerHTML=current.map((r,i)=>{let v=kind==='saas'?r.n:r.d?r.n/r.d:0,y=20+i*75;return `<text x="0" y="${y+25}" fill="#132238" font-size="16">${r.category}</text><rect x="170" y="${y}" width="${v/max*640}" height="40" rx="4" fill="#2563eb"/><text x="${180+v/max*640}" y="${y+26}" fill="#132238" font-size="16">${kind==='saas'?'$'+fmt(v):(v*100).toFixed(2)+'%'}</text>`}).join('');}
document.querySelector('#decision').textContent=__DECISION__;
document.querySelector('#region').addEventListener('change',update);sel.addEventListener('change',update);document.querySelector('#export').onclick=()=>{const csv='category,numerator,denominator\n'+current.map(r=>[r.category,r.n,r.d].join(',')).join('\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='filtered-metrics.csv';a.click();URL.revokeObjectURL(a.href)};update();
</script></body></html>'''
context={'saas':'Monthly subscription snapshots; choose one month to avoid summing MRR across time. Compare customer segments and inspect the separate revenue bridge and cohort report.', 'experiment':'Randomized onboarding test, May 2026. Filtered conversion rates are descriptive; the prespecified full-experiment decision is reported separately in the executive brief.', 'support':'First-response SLA monitoring as of July 1, 2026 UTC. Unanswered overdue tickets count as breaches; not-yet-due unanswered tickets are excluded.'}[kind]
decision={'saas':'Use the revenue bridge and cohort chart to separate acquisition from retained revenue. MRR is not recognized revenue. Segment differences are descriptive.', 'experiment':'Launch decision is intentionally not recalculated for these filters. Use the full-experiment brief for SRM, confidence intervals and guardrails; post-hoc slice comparisons are exploratory.', 'support':'Investigate queue case mix before making staffing decisions. Resolved-only turnaround excludes censored open tickets. CSAT has voluntary-response bias.'}[kind]
for k,v in {'TITLE':title,'CONTEXT':context,'CHART':chart_label,'METRIC':metric_label,'DATA':json.dumps(records),'KIND':json.dumps(kind),'METRICS':json.dumps(metrics),'DECISION':json.dumps(decision)}.items():body=body.replace('__'+k+'__',v)
(ROOT/'reports/dashboard.html').write_text(body,encoding='utf8')
# Server schemas explicitly constrain the business grain. Load into an empty database.
for dialect in ['sqlserver','mysql']:
    statements=[]
    for path in sorted((ROOT/'data/processed').glob('*.csv')):
        df=pd.read_csv(path);cols=[]
        for c in df:
            typ='BIGINT' if pd.api.types.is_integer_dtype(df[c]) else 'DOUBLE' if pd.api.types.is_float_dtype(df[c]) else 'VARCHAR(255)'
            if dialect=='sqlserver' and typ=='DOUBLE':typ='FLOAT'
            if 'mrr' in c or c=='revenue_usd':typ='DECIMAL(19,4)'
            if c in ['month','assigned_date','opened_day','date']:typ='DATE'
            if c in ['opened_at','first_response_at','closed_at']:typ='DATETIME2' if dialect=='sqlserver' else 'DATETIME'
            cols.append(f'    {c} {typ} NULL')
        key={'fact_subscription':['account_id','month'],'dim_account':['account_id'],'fact_experiment':['user_id'],'fact_ticket':['ticket_id'],'qa_sample':['ticket_id']}.get(path.stem)
        if key:
            cols=[s.replace(' NULL',' NOT NULL') if s.strip().split()[0] in key else s for s in cols]
            cols.append('    PRIMARY KEY ('+', '.join(key)+')')
        statements.append('CREATE TABLE '+path.stem+' (\n'+',\n'.join(cols)+'\n);')
    (ROOT/f'sql/schema.{dialect}.sql').write_text('-- Run once in a new empty database. Never run against production without review.\n'+'\n\n'.join(statements))
# Meaningful local index evidence, with warm repetitions; no production performance claim.
factname={'saas':'fact_subscription','experiment':'fact_experiment','support':'fact_ticket'}[kind]
datecol={'saas':'month','experiment':'assigned_date','support':'opened_day'}[kind]
with sqlite3.connect(ROOT/'data/analytics.sqlite') as con:
    q=f'SELECT COUNT(*) FROM {factname} WHERE {datecol}>=? AND {datecol}<?';args=('2026-05-01','2026-05-03')
    con.execute(f'DROP INDEX IF EXISTS ix_{factname}_date')
    def measure():
        plan=con.execute('EXPLAIN QUERY PLAN '+q,args).fetchall();samples=[]
        for _ in range(30):
            t=time.perf_counter();result=con.execute(q,args).fetchone()[0];samples.append((time.perf_counter()-t)*1000)
        return {'median_ms':statistics.median(samples),'plan':plan,'matching_rows':result}
    before=measure();con.execute(f'CREATE INDEX ix_{factname}_date ON {factname}({datecol})');after=measure()
(ROOT/'reports/query_plan_evidence.json').write_text(json.dumps({'engine':'SQLite','repetitions':30,'warm_cache':True,'before':before,'after':after,'limitation':'Small local synthetic data. No production speedup claim.'},indent=2))
# Descriptive and bivariate EDA exports; numeric IDs deliberately excluded.
numeric=fact.select_dtypes(include='number').drop(columns=[c for c in fact if c.endswith('_id') or c in ['signup_month','age_month']],errors='ignore')
numeric.describe(percentiles=[.5,.9,.95]).to_csv(ROOT/'reports/descriptive_statistics.csv')
numeric.corr().to_csv(ROOT/'reports/exploratory_correlations.csv')
print('Published',title)
