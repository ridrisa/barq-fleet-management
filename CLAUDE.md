PROMPT FOR APP ENHANCEMENTS

Phase 1 – Discovery & Technical Audit
1.1 Inputs
APP_DETAILS: current features, tech stack, known issues
BUSINESS_GOALS (optional): if note provided, AI will infer objectives (e.g., user growth, engagement, retention) based on APP_DETAILS
1.2 Activities
Code & Architecture Inventory: catalog frontend modules, backend services, shared libraries
Build & CI/CD Review: assess pipelines, scripts, environment setups
Performance Baseline: measure load times, bundle sizes, API latencies
Security Audit: check dependencies, auth flows, headers, input validation
Analytics Gap Analysis: compare existing event tracking against inferred or provided business objectives
1.3 Opportunities & Changes
Upgrade core dependencies & frameworks
Modularize into micro‑frontends/services or a mono‑repo
Implement code‑splitting and lazy loading
Harden security with modern headers, tokens, sanitization
Enhance monitoring and error reporting
1.4 Deliverables
technical_audit_report.md
performance_baseline.json
security_checklist.md
analytics_gap_analysis.xlsx

Phase 2 – User Research & Benchmarking
2.1 Inputs
APP_DETAILS, inferred BUSINESS_GOALS
2.2 Activities
Define key user personas based on feature set and target use cases
Map end‑to‑end journeys for each persona (onboarding, primary flows, support)
Benchmark core features and UX patterns of top competitors in the same domain
2.3 Opportunities & Changes
Simplify primary flows for target personas
Identify and prioritize features to meet inferred goals (e.g., reduce drop‑off, boost engagement)
2.4 Deliverables
personas.pdf
journey_maps.svg
benchmark_report.md

Phase 3 – Heuristic & Accessibility Audit
3.1 Activities
Evaluate screens against usability heuristics
Run automated a11y scans and manual checks (ARIA, keyboard, contrast)
Test responsive behavior at breakpoints
3.2 Opportunities & Changes
Fix accessibility violations (labels, roles, focus management)
Improve usability (clear feedback, error recovery, affordances)
3.3 Deliverables
heuristic_matrix.csv
accessibility_report.html
responsive_checklist.md

Phase 4 – Information Architecture & Wireframing
4.1 Activities
Propose updated navigation hierarchy or site map
Identify and wireframe key screens/flows based on audit findings and goals
Annotate interactions, content hierarchy, and decision points
4.2 Opportunities & Changes
Consolidate or re-order menu items for clarity
Streamline multi‑step processes (e.g., merge related steps)
4.3 Deliverables
site_map.drawio
wireframes.pdf
interaction_flows.svg

Phase 5 – Visual Design & Prototyping
5.1 Activities
Define or update design tokens: colors, typography, spacing, elevation
Build a reusable component library (e.g., Storybook) with core UI elements
Create high‑fidelity mockups and an interactive prototype for validation
5.2 Opportunities & Changes
Establish consistent branding and UI patterns
Add micro‑interactions and motion for key user actions
5.3 Deliverables
DesignSystem.md
storybook/ components
mockups.fig (or Sketch/Figma)
prototype.html

Phase 6 – Validation & Testing Plan
6.1 Activities
Develop a usability test plan (scenarios, metrics such as SUS, task time)
Write automated unit and end‑to‑end tests covering critical paths
Re‑audit performance (Lighthouse) and accessibility (axe‑core) post‑changes
Outline A/B experiments for major UX changes
6.2 Deliverables
usability_test_plan.docx
test_suite/ (unit & E2E)
performance_comparison.xlsx
ab_test_roadmap.md

Phase 7 – Handoff & Implementation Roadmap
7.1 Activities
Generate developer docs: API spec (OpenAPI), component docs (Storybook)
Break down work into Epics, Features, Stories, and Tasks for sprint planning
Define release strategy: feature flags, phased rollout, rollback plan
7.2 Deliverables
handoff_package.zip (code snippets, tokens, specs)
sprint_backlog.jira export
release_plan.md
<mind_map>
Generic App Redesign
├─ Discovery & Audit
│  ├─ Code & Architecture
│  ├─ Performance Metrics
│  ├─ Security & Compliance
│  └─ Analytics & Goals
├─ Research & Benchmarking
│  ├─ Personas
│  ├─ Journeys
│  └─ Competitive Analysis
├─ Heuristic & Accessibility
│  ├─ Usability Heuristics
│  ├─ A11y Compliance
│  └─ Responsive Checks
├─ Information Architecture
│  ├─ Site Map
│  ├─ Navigation
│  └─ Wireframes
├─ Visual Design & Prototyping
│  ├─ Design Tokens
│  ├─ Component Library
│  └─ Interactive Prototypes
├─ Validation & Testing
│  ├─ Usability Tests
│  ├─ Automated Tests
│  └─ A/B Experiments
└─ Handoff & Implementation
   ├─ Documentation (API, Components)
   ├─ Sprint Backlog
   └─ Release Strategy
</mind_map>
