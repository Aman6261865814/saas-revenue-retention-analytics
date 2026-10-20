
from pathlib import Path
import json, sqlite3, hashlib
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261011
sns.set_theme(style='whitegrid', palette=['#2563eb','#e87924','#0f766e'])

def write(df, name, folder='processed'):
    p = ROOT/'data'/folder
    p.mkdir(parents=True, exist_ok=True)
    df.to_csv(p/f'{name}.csv', index=False)

def load_clean(raw, keys):
    # In this generator, repeated keys are exact retry duplicates. Conflicting
    # versions fail closed; blindly keeping the last row would be unsafe.
    out = raw.drop_duplicates()
    if out.duplicated(keys).any():
        raise ValueError('Conflicting duplicate business keys')
    assert not out[keys].isna().any().any()
    return out.copy(), len(raw)-len(out)

def bootstrap_mean_diff(a,b,seed=SEED,repeats=1500):
    # Independent users/tickets; not event-level resampling.
    rng=np.random.default_rng(seed)
    diffs=np.array([rng.choice(b,len(b),True).mean()-rng.choice(a,len(a),True).mean()
                    for _ in range(repeats)])
    return np.quantile(diffs,[.025,.975]).tolist()

def finish(tables, metrics, summary, title, chart_fn):
    for d in ['reports','powerbi','excel','sql','tests']:
        (ROOT/d).mkdir(exist_ok=True)
    db=ROOT/'data'/'analytics.sqlite'
    if db.exists(): db.unlink()
    with sqlite3.connect(db) as con:
        for name,df in tables.items():
            write(df,name)
            df.to_sql(name,con,index=False)
        sql=(ROOT/'sql'/'analysis.sqlite.sql').read_text()
        result=pd.read_sql_query(sql,con)
        result.to_csv(ROOT/'reports'/'sql_result.csv',index=False)
    (ROOT/'reports'/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf8')
    (ROOT/'reports'/'executive_brief.md').write_text(f'# {title}\n\nSYNTHETIC PORTFOLIO CASE STUDY — not actual company results.\n\n'+summary,encoding='utf8')
    dictionary=[]
    for name,df in tables.items():
        for col in df:
            dictionary.append({'table':name,'column':col,'dtype':str(df[col].dtype),'nulls':int(df[col].isna().sum()),'unique':int(df[col].nunique())})
    pd.DataFrame(dictionary).to_csv(ROOT/'reports'/'data_profile.csv',index=False)
    chart_fn()
    # SHA256 manifest helps detect changed inputs and supports reproducibility.
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((ROOT/'data'/'raw').glob('*.csv'))}
    (ROOT/'reports'/'input_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(metrics,indent=2))
