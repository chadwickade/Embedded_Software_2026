"""Recheck source preservation, naming, PDF links and layout review artifacts."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pypdf import PdfReader
from PIL import Image, ImageDraw

B = Path(__file__).resolve().parent
A = B.parent / 'ArchitectureDesignTemplate-2.33'
baseline = json.loads((B / 'embswTemplateManifest.json').read_text(encoding='utf-8'))
actual = {str(p.relative_to(A)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in A.rglob('*') if p.is_file()}
unchanged = baseline == actual
exceptions = {'AGENTS.md', 'SKILL.md', '.gitignore', 'cornell.cls', 'IEEEtran.bst'}
bad_names = [str(p.relative_to(B)) for p in B.rglob('*')
             if p.is_file() and not p.name.startswith('embsw') and p.name not in exceptions]
sources = list(B.glob('*.tex')) + list((B / 'TikZ').rglob('*.tex'))
missing_inputs, tikz_paths = [], []
labels, refs = set(), set()
for source in sources:
    content = source.read_text(encoding='utf-8')
    # Skip comments and literal example blocks for the actual input closure.
    content = re.sub(r'\\begin\{verbatim\}.*?\\end\{verbatim\}', '', content, flags=re.S)
    content = '\n'.join(line.split('%', 1)[0] for line in content.splitlines())
    labels.update(re.findall(r'\\label\{([^}#]+)\}', content))
    labels.update('Chapter:' + x for x in re.findall(r'\\ChapterLabel\{([^}#]+)\}', content))
    refs.update(re.findall(r'\\hyperref\[([^\]#]+)\]', content))
    refs.update(re.findall(r'\\ref\*?\{([^}#]+)\}', content))
    refs.update('Chapter:' + x for x in re.findall(r'\\ChapterRef\{([^}#]+)\}', content))
    for rel in re.findall(r'\\(?:input|include)\{([^}]+)\}', content):
        target = B / rel
        if not target.suffix: target = target.with_suffix('.tex')
        if not target.exists(): missing_inputs.append((source.name, rel))
        if rel.startswith('TikZ/'):
            tikz_paths.append((source.name, rel, Path(rel).parent.name == source.stem))

if '--sources' in sys.argv:
    print(json.dumps({'template_unchanged': unchanged, 'template_files': len(baseline),
        'bad_names': bad_names, 'missing_inputs': missing_inputs, 'tikz_paths': tikz_paths,
        'missing_explicit_labels': sorted(refs - labels)}, indent=2))
    raise SystemExit(0)

pdf = B / 'embswManual.pdf'
review = B / 'embswReview' / ('embsw' + hashlib.sha256(pdf.read_bytes()).hexdigest()[:12])
reader = PdfReader(pdf)
destinations = reader.named_destinations
dest_errors, links = [], 0
for i, page in enumerate(reader.pages):
    for ref in page.get('/Annots', []):
        ann = ref.get_object()
        action = ann.get('/A', {})
        if action and action.get('/S') == '/GoTo':
            links += 1
            dest = action.get('/D')
            if isinstance(dest, str) and dest not in destinations:
                dest_errors.append((i + 1, dest))
log = (B / 'embswManual.log').read_text(encoding='utf-8', errors='replace')
issues = [line for line in log.splitlines() if re.search(
    r'(^!|undefined|multiply defined|duplicate|Overfull|Underfull|LaTeX Warning|Package .* Warning)', line)]
texts = [p.extract_text() or '' for p in reader.pages]
question_targets = [f'Question:Q-{i:02}' for i in range(1, 13)]
aux = (B / 'embswManual.aux').read_text(encoding='utf-8', errors='replace')
all_aux = '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in B.glob('*.aux'))
missing_questions = [q for q in question_targets if '\\newlabel{' + q + '}' not in all_aux]
summary = {
    'template_files_hashed': len(baseline), 'template_unchanged': unchanged,
    'namespace_violations': bad_names, 'missing_inputs': missing_inputs,
    'tikz_inclusions': tikz_paths, 'pdf_pages': len(reader.pages),
    'pdf_internal_links': links, 'pdf_missing_link_destinations': dest_errors,
    'missing_question_labels': missing_questions, 'final_log_issues': issues,
    'pdf_title': str(reader.metadata.title),
    'render_directory': str(review),
    'git_initialized': (B / '.git').exists(),
    'product_requirement_records': sum(len(re.findall(r'\\RequirementID\{REQ-', p.read_text(encoding='utf-8'))) for p in B.glob('*.tex')),
    'product_verification_records': sum(len(re.findall(r'\\VerificationID\{VER-', p.read_text(encoding='utf-8'))) for p in B.glob('*.tex')),
}
(B / 'embswInspection.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2), flush=True)

review.mkdir(parents=True, exist_ok=True)
subprocess.run([shutil.which('pdftoppm'), '-r', '60', '-png', str(pdf), str(review / 'embswPage')], check=True)
pages = sorted(review.glob('embswPage-*.png'))
for start in range(0, len(pages), 12):
    tiles = Image.new('RGB', (1200, 1380), '#bcbcbc')
    draw = ImageDraw.Draw(tiles)
    for pos, path in enumerate(pages[start:start + 12]):
        im = Image.open(path).convert('RGB')
        im.thumbnail((290, 420))
        x, y = (pos % 4) * 300, (pos // 4) * 460
        tiles.paste(im, (x + (300 - im.width) // 2, y + 25))
        draw.text((x + 8, y + 5), f'PDF page {start + pos + 1}', fill='black')
    tiles.save(review / f'embswContactSheet{start // 12 + 1:02}.png')
(review / 'embswPageText.json').write_text(json.dumps(texts, indent=2), encoding='utf-8')
figure_pages = []
for i, text in enumerate(texts, 1):
    if re.search(r'Figure\s+(?:\d+|[A-Z])\.\d+:', text):
        figure_pages.append(i)
        subprocess.run([shutil.which('pdftoppm'), '-f', str(i), '-l', str(i),
            '-scale-to', '1500', '-singlefile', '-png', str(pdf),
            str(review / f'embswFigurePage{i:03}')], check=True)
print('Rendered all pages. Figure pages:', figure_pages, flush=True)
