"""Print concise diagnostics from the project's latest build artifacts."""
from pathlib import Path
B = Path(__file__).resolve().parent
for name in ['embswBuildTranscript.txt', 'embswManual.log']:
    p = B / name
    print('\n' + name + ':')
    print(p.read_text(errors='replace')[-2200:] if p.exists() else 'not yet generated')
