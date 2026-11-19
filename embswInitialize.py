"""One-time AIS-02 initialization. Refuses to overwrite an initialized manual."""
from pathlib import Path
import hashlib
import json
import re

B = Path(__file__).resolve().parent
A = B.parent / 'ArchitectureDesignTemplate-2.33'
if (B / 'embswManual.tex').exists():
    raise SystemExit('Already initialized; subsequent edits require a branch and pull request.')

manifest = {str(p.relative_to(A)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(A.rglob('*')) if p.is_file()}
(B / 'embswTemplateManifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

def transform(s):
    return (s.replace('dsn', 'embsw').replace('prologue.tex', 'embswPrologue.tex')
            .replace('{prologue}', '{embswPrologue}').replace('abstract.tex', 'embswAbstract.tex')
            .replace('makefilePowerShell.ps1', 'embswBuild.ps1').replace('makefileMacLinux', 'embswMakefile'))

for src in list(A.glob('*.tex')) + [A / 'dsnReferences.bib'] + list((A / 'TikZ').rglob('*.tex')):
    rel = str(src.relative_to(A)).replace('dsn', 'embsw')
    if rel == 'prologue.tex': rel = 'embswPrologue.tex'
    if rel == 'abstract.tex': rel = 'embswAbstract.tex'
    dst = B / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(transform(src.read_text(encoding='utf-8-sig')), encoding='utf-8')
for name in ['cornell.cls', 'IEEEtran.bst']:
    (B / name).write_bytes((A / name).read_bytes())
for src, dst in [('makefilePowerShell.ps1', 'embswBuild.ps1'), ('makefileMacLinux', 'embswMakefile'),
                 ('AGENTS.md', 'AGENTS.md'), ('SKILL.md', 'SKILL.md')]:
    (B / dst).write_text(transform((A / src).read_text(encoding='utf-8-sig')), encoding='utf-8')

def read(name): return (B / ('embsw' + name + '.tex')).read_text(encoding='utf-8')
def write(name, text): (B / ('embsw' + name + '.tex')).write_text(text.rstrip() + '\n', encoding='utf-8')
def question(qid, text):
    return '\\par\\noindent\\textbf{Open question ' + qid + '.} ' + text + ' Owner: project requester, pending delegation. Status: Open.\n'
def qref(qid): return '\\hyperref[Question:' + qid + ']{' + qid + '}'
def section_question(qid, title, text):
    return '\\section{' + title + '}\n\\label{Question:' + qid + '}\n' + question(qid, text)

manual = read('Manual')
for old, new in [('{[Project Name]}', '{Embedded\\_Software}'), ('{[Owner or Team]}', '{Project requester}'),
                 ('{[Organization]}', '{Organization unresolved}'), ('{[Month Day, Year]}', '{November 11, 2026}'),
                 ('{2.33}', '{0.1}'), ('{Draft Template}', '{Initialization Draft - Human Review Pending}'),
                 ('[Project Name] - System', 'Embedded\\_Software - System'),
                 ('pdfauthor={[Owner or Team]}', 'pdfauthor={Project requester}'),
                 ('pdfsubject={Reusable software architecture design template}',
                  'pdfsubject={Embedded software architecture initialization draft}')]:
    manual = manual.replace(old, new)
write('Manual', manual)
write('Prologue', read('Prologue').replace('Software Architecture Design Template', 'System and Software Architecture Design'))
write('Abstract', r'''This initialization draft establishes the architecture record for
\ProjectName, derived from ArchitectureDesignTemplate version 2.33 using
\hyperref[Skill:AIS-02]{AIS-02}. The project namespace is \texttt{embsw}; the
Embedded Systems profile is Applicable by the requester's direction on
November 11, 2026. Product purpose, capabilities, platform, and quantitative
constraints remain open questions. This draft contains no approved product
requirements, selected product architecture, implemented product version,
executed product tests, or product verification or validation conclusions.
The complete book is a reviewable starting point, not a completed product
specification. See \hyperref[Section:InitializationGaps]{the initialization gap
register} for owners and decision gates.''')

intro = read('Introduction')
start, end = intro.index('Define the system boundary'), intro.index('\\section{Normative Language')
intro = intro[:start] + r'''The document-initialization scope covers a separate architecture book under
\path|ArchitectureDesign/| while preserving the reusable template. The system's
product scope, capabilities, exclusions, operating environment, and release
boundary remain unresolved in \hyperref[Question:Q-01]{Q-01}. No product scope
is inferred from the project name or the selected domain profile.

\section{Audience}
The project requester is the initial document owner and decision contact under
the requested defaults, pending delegation. Other stakeholders and reviewers
remain unresolved in \hyperref[Question:Q-02]{Q-02}. The template's general
engineering audience is retained as authoring guidance, not an assigned team.

''' + intro[end:]
# One authoritative profile decision; Introduction navigates to it.
start, end = intro.index('\\small\n\\begin{tabularx}', intro.index('\\section{Template Tailoring')), intro.index('When the Embedded Systems profile')
intro = intro[:start] + r'''\phantomsection\label{Table:DomainProfileApplicability}
See \hyperref[Table:ProjectDomainProfiles]{the authoritative project profile
decision register}. The supplied Embedded Systems profile is retained.
No additional domain profile was supplied; additional assurance needs are
tracked in \hyperref[Question:Q-09]{Q-09}.

''' + intro[end:]
write('Introduction', intro)

plan = read('DevelopmentPlan')
plan = plan[:plan.index('\\section{Domain Profile Selection}')]
plan += r'''\section{Initialization Decisions}
\label{Section:InitializationDecisions}
The requester confirmed \ProjectName\ and the \texttt{embsw} file namespace,
requested defaults for other initialization choices, and directed inclusion of
the Embedded Systems profile on November 11, 2026. The initial document version
is 0.1; version 2.33 identifies the source template, not a product release.
The requester is the initial document owner and decision contact pending
delegation. Organization and named role assignments remain unresolved.
These confirmations authorize draft initialization; acceptance of this book,
product baselines, and publication remain pending.

\section{Domain Profile Selection}
\label{Section:DevelopmentPlanProfiles}
\begin{tabularx}{\linewidth}{L{3.1cm}L{2.3cm}Y}
\caption{Project Domain Profile Decisions\label{Table:ProjectDomainProfiles}}\\
\toprule Profile & Status & Rationale, owner, and date\\\midrule
\endfirsthead
\toprule Profile & Status & Rationale, owner, and date\\\midrule
\endhead
\hyperref[Chapter:EmbeddedSystemsProfile]{Embedded Systems} & Applicable &
Included by explicit requester direction on November 11, 2026. Decision owner:
project requester. Platform class and hardware revisions remain open in
\hyperref[Question:Q-05]{Q-05}; inclusion does not establish hardware facts.\\
\bottomrule\end{tabularx}
No other domain profile is provided in the supplied template. Additional
domain or assurance tailoring remains subject to \hyperref[Question:Q-09]{Q-09}.

\section{Governance and Change Control}
\label{Section:ProjectChangeControl}
Codex is the AI tool used for this initialization. One agent performs
\texttt{aiaCoordinator} and \texttt{aiaDeveloper} responsibilities sequentially,
then performs self-review. No independent agent review is claimed.
The requester retains acceptance, scope, architecture, safety, security,
evidence, validation, and release decisions until named authorities are assigned.
Resolve each material question before dependent product design or implementation.

After the requester accepts the initialized book and explicitly authorizes
publication, initialize Git in this project directory, commit the sources on
\texttt{main}, and push to the repository the requester specifies.
Every later change uses a branch and pull request. Repository URL, visibility,
reviewers, and branch-protection settings remain undecided; see
\hyperref[Question:Q-12]{Q-12}. No Git repository or remote is created during
this draft initialization.

\section{Initialization Gap Register}
\label{Section:InitializationGaps}
All questions below have status Open and are owned by the project requester
pending delegation. A question is resolved only by supported evidence and an
authorized disposition. Location links identify the authoritative question;
the register does not duplicate its definition.
\begin{tabularx}{\linewidth}{L{1.5cm}YL{4.3cm}}
\caption{Owned Initialization Questions\label{Table:InitializationQuestions}}\\
\toprule Question & Subject & Resolution gate\\\midrule
\endfirsthead
\toprule Question & Subject & Resolution gate\\\midrule
\endhead
'''
gaps = [
('Q-01','Purpose and product scope','Before stories and requirements'),
('Q-02','Stakeholders and approval roles','Before stakeholder approval'),
('Q-03','Boundary and interfaces','Before allocations and contracts'),
('Q-04','Quality targets and constraints','Before measurable obligations'),
('Q-05','Platform and hardware revisions','Before hardware-dependent design'),
('Q-06','Firmware and toolchain','Before implementation baseline'),
('Q-07','Timing, resource, and power budgets','Before feasibility claims'),
('Q-08','Boot, update, recovery, and service','Before lifecycle design'),
('Q-09','Safety, security, and standards','Before assurance decisions'),
('Q-10','Controlled source evidence','Before derived product facts'),
('Q-11','Verification and validation plan','Before evidence sufficiency'),
('Q-12','Publication and repository','Before Git initialization and push')]
for qid, subject, gate in gaps:
    plan += qref(qid) + ' & ' + subject + ' & ' + gate + '\\\\\n'
plan += r'''\bottomrule\end{tabularx}

\section{Initial Ownership and Risks}
'''
plan += section_question('Q-02', 'Stakeholders and Approval Roles',
    'Who are the users, document owner, organization, architect, hardware and firmware owners, '
    'verification and validation owners, reviewers, and approval authorities? The requester is the initial contact under the requested defaults.')
plan += section_question('Q-12', 'Publication Decision',
    'Will the requester accept this initialized project and authorize publication? Supply the repository URL, '
    'visibility, and review policy before publication. The initial source commit uses main; every later change uses a branch and pull request.')
plan += r'''\section{Planning Estimate and Review Gates}
AIS-01 planning estimate: source initialization 8--16k tokens, supported drafting
and trace review 5--12k, and build and visual review 4--10k. These are uncertain
planning ranges, excluding new product design and tool installation, not measured
usage or guaranteed costs. Work is sequential because metadata, naming,
registers, and build paths depend on shared inputs. No delegation was used.
The draft review gate checks source naming, evidence boundaries, links, complete
compilation, and PDF layout. Product requirements, architecture, verification,
validation, release, and publication have separate human decision gates.
'''
write('DevelopmentPlan', plan)

context = read('SystemContext').split('\\section{Example}')[0]
context += section_question('Q-01','Purpose and Product Scope',
    'What problem does Embedded\\_Software solve, for whom, and with what included capabilities, exclusions, operating environment, and intended release?')
context += section_question('Q-03','System Boundary and Interfaces',
    'Which functions belong to hardware, firmware, software, operators, and external systems? Identify sensors, actuators, buses, power sources, tools, interface owners, contracts, and failure assumptions.')
context += section_question('Q-10','Controlled Project Evidence',
    'Which controlled project brief, schematics, datasheets, interface-control documents, existing code, hazard and threat analyses, approvals, and test records may be used? None has been supplied as product evidence.')
write('SystemContext', context)

# Remove inherited service-request records; reserve IDs instead of reusing them.
for name, marker, qid, msg in [
('UserStories','\\section{User Story Register}','Q-01','No project user stories are defined. Obtain stakeholder goals and acceptance criteria before drafting linked stories.'),
('UseCases','\\section[High-Level','Q-03','No project actors or use cases are defined. Obtain system boundaries and actor goals before detailed scenarios.'),
('ArchitectureOverview','\\section{Decision Template','Q-04','No product architecture decision is selected. Confirm driving requirements and constraints before comparing alternatives.'),
('UserInterfaceDesign','\\section{Example}','Q-01','User interfaces and personas remain unresolved. A graphical interface is not assumed.'),
('LogicalView','\\section{Example}','Q-03','No project classes or interfaces are defined; no product responsibility register is populated.'),
('ProcessView','\\section{Example State Model}','Q-07','Execution contexts, state transitions, scheduling, synchronization, and fault behavior remain unresolved.'),
('DevelopmentView','\\section{Example}','Q-06','Product module boundaries, dependency rules, source layout, and build artifacts remain unresolved.'),
('PhysicalView','\\section{Example}','Q-05','Processor, board, network, deployment, and hardware revision allocations remain unresolved.'),
('Implementation','\\section{Example}','Q-06','No product language, RTOS, BSP, HAL, SDK, compiler, linker, build variant, or image format is selected.'),
('Tests','\\section{Example Test Cases}','Q-11','No product test procedures or execution records are defined; document-build checks are not product tests.'),
('Verification','\\section{Verification Register}','Q-11','No product compliance conclusions are recorded. There are no supplied execution results or waivers.'),
('Validation','\\section{Validation Register}','Q-11','No stakeholder validation has occurred or been claimed.'),
('TestEvidence','\\section{Example Evidence Record}','Q-11','No product execution evidence has been supplied or generated.')]:
    body = read(name).split(marker)[0]
    body += '\\section{Project Draft Status}\n' + msg + ' See ' + qref(qid) + '.\n'
    write(name, body)

requirements = read('Requirements')
cut = requirements.find('\\begin{landscape}')
assert cut > 0
requirements = requirements[:cut] + r'''\section{Project Requirements Register}
No product requirements are defined in this initialization. The service-request
examples from the reusable template are excluded from this project baseline.
Their identifiers remain reserved under \ChapterRef{Traceability}.
Complete \hyperref[Question:Q-01]{Q-01} and \hyperref[Question:Q-04]{Q-04}
before drafting project obligations. Each applicable embedded concern still
requires a requirement mapping or an authorized Not Applicable disposition;
this initialization does not claim that translation is complete.
'''
requirements += section_question('Q-04','Quality Targets and Constraints',
    'What measurable performance, reliability, availability, usability, data, environmental, cost, schedule, and other binding limits apply, under what operating conditions and verification methods?')
requirements += section_question('Q-07','Timing, Resource, and Power Budgets',
    'What periods, deadlines, latency, jitter, CPU, flash, RAM, stack, bus bandwidth, power, energy, and thermal allocations apply? Supply units, conditions, margins, owners, and evidence.')
requirements += section_question('Q-08','Boot, Update, Recovery, and Lifecycle',
    'What boot chain, self-test, reset, recovery, safe or degraded behavior, diagnostics, calibration, configuration, authenticated update, rollback, manufacturing, provisioning, field service, and component-lifecycle obligations apply?')
requirements += section_question('Q-09','Safety, Security, and Applicable Standards',
    'What hazards, threats, safe states, trust boundaries, privacy needs, physical and environmental conditions, regulatory standards, assurance profiles, and approval authorities apply? No safety classification, certification, or security posture is asserted.')
write('Requirements', requirements)

write('PhysicalView', read('PhysicalView') + section_question('Q-05','Platform and Hardware Revisions',
    'Is the platform bare metal, RTOS, embedded Linux, programmable logic, or mixed? Identify processors, boards, programmable devices, hardware revisions, memory and peripherals, and authoritative hardware evidence.'))
write('Implementation', read('Implementation') + section_question('Q-06','Product Toolchain and Implementation Baseline',
    'Identify firmware layers, language, RTOS or operating system, bootloader, BSP, HAL, SDK, compiler, linker, libraries, generators, programming tools, configurations, image formats, and exact product build/test commands.') + r'''
\section{Architecture Document Build}
\label{Section:ProjectDocumentBuild}
From the project directory, with the installed MiKTeX binaries on the process
PATH, run \texttt{.\textbackslash embswBuild.ps1 -Action pdf}.
The script compiles \texttt{embswManual.tex}, runs BibTeX, makeglossaries and
makeindex, then runs two additional LaTeX passes. The final review uses a full
build with no active include-only selection. The output is
\texttt{embswManual.pdf}. Source and build checks are retained in
\texttt{embswReviewReport.txt}; they establish document quality, not product
verification. Product build and test commands remain in
\hyperref[Question:Q-06]{Q-06}.
''')
write('Tests', read('Tests') + section_question('Q-11','Verification and Validation Planning',
    'Who will define and review unit, integration, system, target, SIL/PIL/HIL, timing, power, environmental, fault-injection, compatibility, update, and recovery checks? Specify fixtures, controlled revisions, objective criteria, evidence locations, validation participants, and human disposition authority.'))

trace = read('Traceability').split('\\section{Traceability Register}')[0]
trace += r'''\section{Project Traceability Status}
\label{Table:TraceabilityMatrix}
There are no project stories, requirements, use cases, tests, or verification
and validation records yet. Consequently there is no populated product mapping
to assess. Traceability is structurally prepared, not demonstrated as product
coverage. The owned question register in
\hyperref[Table:InitializationQuestions]{the Development Plan} links each gap
to its authoritative question. Future artifacts require reciprocal links.

\section{Reserved Template Identifiers}
Template example IDs US-001--US-003; REQ-B-001; REQ-F-001--REQ-F-003;
REQ-Q-001; REQ-I-001; REQ-S-001; REQ-D-001; REQ-C-001; UC-001--UC-003;
TC-001--TC-009; VER-001--VER-009; VAL-001--VAL-003; and ARC-001 are reserved
and will not be reused for new project artifacts. They describe removed
instructional examples, not retired product requirements or implementation
evidence. Existing guide and diagram labels are preserved when their targets
remain in the derived book.
'''
write('Traceability', trace)

# Preserve the independent use-case TikZ source without asserting actor facts.
write('UseCases', read('UseCases') + r'''
\section{Unresolved Use-Case Inputs}
Figure~\ref{Figure:UseCaseDiagram} links the unresolved inputs to their owners'
questions; it is a gap-navigation diagram, not a selected system architecture.
\begin{figure}[htbp]\centering
\input{TikZ/embswUseCases/embswUseCaseDiagram.tex}
\caption{Unresolved inputs for project use cases.}\label{Figure:UseCaseDiagram}
\end{figure}
''')
(B / 'TikZ/embswUseCases/embswUseCaseDiagram.tex').write_text(r'''\begin{tikzpicture}[
box/.style={draw=embswBlue,fill=embswLightBlue,align=center,text width=3.0cm,minimum height=1.3cm,font=\small},
flow/.style={->,>=Stealth,draw=embswGray}]
\node[box] (scope) {\hyperref[Question:Q-01]{Q-01: Purpose and scope}\\Open; requester owns};
\node[box,right=1cm of scope] (boundary) {\hyperref[Question:Q-03]{Q-03: Boundary and actors}\\Open; requester owns};
\node[box,below=1cm of boundary] (tests) {\hyperref[Question:Q-11]{Q-11: Acceptance and evidence}\\Open; requester owns};
\draw[flow] (scope.east) -- (boundary.west);
\draw[flow] (boundary.south) -- (tests.north);
\end{tikzpicture}
''', encoding='utf-8')

write('Release', read('Release').replace('\\section{Example Checklist}', '\\section{Release Review Guidance}') + r'''
\section{Current Disposition}
This is an initialization draft for human review. No product release,
requirements baseline, architecture approval, or evidence-sufficiency decision
is recorded. Publication is separately gated by
\hyperref[Question:Q-12]{Q-12} and \hyperref[Section:ProjectChangeControl]{change control}.
''')

write('AIPromptLog', read('AIPromptLog').split('\\section{Example Record}')[0] + r'''
\section{Initialization Interaction - November 11, 2026}
\label{Section:InitializationPrompt}
Tool: Codex desktop; agent: OpenAI Codex. Exact runtime model identifier was
not independently observed. The requester instructed AIS-02 initialization
from template 2.33 into a separate ArchitectureDesign directory, preservation
of the template, a facts/gaps/files/checks proposal before dependent edits,
owned unresolved questions, separate TikZ sources and trace links, and a full
build with PDF inspection. Git initialization and publication require later
acceptance and authorization; later changes require branches and pull requests.

After the proposal, the requester stated: ``Project name will be
Embedded\_Software and the namespace will be embsw. Use the default for the rest
and include the Embedded Systems profile.'' This confirms the name, namespace,
profile inclusion, and default document workflow. It does not supply product
scope, hardware facts, test evidence, or release approval. The requester is
the initial owner of unresolved questions pending delegation. A complete draft
is prepared with core chapters and profile guidance; unsupported service-request
examples and PASS/Done records are removed. Human review of the result is pending.
See \hyperref[Section:InitializationDecisions]{the decision record},
\hyperref[Section:InitializationGaps]{the gap register}, and
\hyperref[Section:ProjectDocumentBuild]{document build instructions}.
''')
write('DocumentHistory', r'''\chapter{Document History}
\ChapterLabel{DocumentHistory}
\index{document history}
\section{Chapter Responsibility}
\label{Section:DocumentHistoryResponsibility}
Preserve the evolution of the project document and distinguish approval states.
\noindent\textbf{Expected result:} Traceable changes with explicit human disposition.

\section{Project Draft History}
\begin{tabularx}{\linewidth}{L{2.6cm}L{2.0cm}Y}
\caption{Document Update History\label{Table:DocumentHistory}}\\
\toprule Date / version & State & Change and location\\\midrule
\endfirsthead
\toprule Date / version & State & Change and location\\\midrule
\endhead
November 11, 2026 / 0.1 & Draft; acceptance pending & OpenAI Codex initialized
the separate project with the requester-confirmed name, namespace, default
workflow, and Embedded Systems profile. See
\hyperref[Section:InitializationDecisions]{decisions},
\hyperref[Section:InitializationGaps]{gaps}, and
\hyperref[Section:InitializationPrompt]{AI interaction}.\\
\bottomrule\end{tabularx}
\section{Template Provenance}
This book derives from ArchitectureDesignTemplate version 2.33, supplied in
\path|ArchitectureDesignTemplate-2.33/|. Its history is retained in the unchanged
template and is not presented as project approval history. Template attribution
remains in \hyperref[Chapter:TemplateAttribution]{the front matter} and
\ChapterRef{DocumentGuide}. The source-file hash inventory is
\texttt{embswTemplateManifest.json}. No project baseline has yet been accepted.
''')

guide = read('DocumentGuide')
guide += r'''
\section{Project Initialization File Inventory}
\label{Section:ProjectFileInventory}
The confirmed namespace is \texttt{embsw}. Project chapters, front matter,
build scripts, diagram sources, initialization helper, source manifest, and
review evidence use it. The exact discovery names \texttt{AGENTS.md} and
\texttt{SKILL.md} are documented exceptions. The externally maintained
\texttt{cornell.cls} and \texttt{IEEEtran.bst} are copied without modification
and retain their upstream names. Standard compiler-produced auxiliary extensions
use the namespaced input stem. Diagram directory names match their including
chapter stems. Legacy Graphviz, raster, Visio and EPS samples, slide decks,
unused bibliography and support files, and the prebuilt template PDF are not
part of this project book's source/build closure and are not copied.
The template's provenance and authoring guidance remain distinct from project
ownership; organizational identity is unresolved in \hyperref[Question:Q-02]{Q-02}.
'''
write('DocumentGuide', guide)

# Describe this derivative rather than the template's tool inventory.
guide = read('AIAgentGuide').replace("The template stores \\texttt{SKILL.md} beside \\texttt{AGENTS.md} and\n\\texttt{CLAUDE.md}. Both bootstrap files explicitly direct the agent to read",
    "This project stores \\texttt{SKILL.md} beside \\texttt{AGENTS.md}. The bootstrap directs the agent to read")
write('AIAgentGuide', guide)
agents = (B / 'AGENTS.md').read_text(encoding='utf-8')
agents += '\nThe human-confirmed project namespace is `embsw`.\n'
(B / 'AGENTS.md').write_text(agents, encoding='utf-8')
print(f'Initialized {len(list(B.rglob("*")))} entries in {B}; source template untouched.')
