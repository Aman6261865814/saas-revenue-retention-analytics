"""One-command report refresh and validation. Run from any working directory."""
from pathlib import Path
import subprocess, sys
root=Path(__file__).resolve().parent
for script in ['pipeline.py','publish_report.py','ai_reporting.py']:
    subprocess.run([sys.executable,str(root/'src'/script)],check=True,cwd=root)
subprocess.run([sys.executable,'-m','unittest','discover','-s',str(root/'tests'),'-v'],check=True,cwd=root)
print('Reports refreshed; Excel snapshot refresh is documented in excel/README.md.')
