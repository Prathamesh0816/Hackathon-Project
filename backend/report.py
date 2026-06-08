"""
TruPulse AI - Report rendering (HTML & Text)
Extracted from main.py for maintainability.
"""
from __future__ import annotations
import time
from typing import Any, Optional


def _bar(val: float, high: float = 100, color: Optional[str] = None) -> str:
    pct = min(val / high * 100, 100)
    if not color:
        color = "#dc2626" if val < 40 else "#d97706" if val < 70 else "#16a34a"
    return (
        f'<div style="background:#e5e7eb;border-radius:999px;height:20px;'
        f'overflow:hidden;position:relative">'
        f'<div style="width:{pct:.0f}%;height:100%;background:{color};'
        f'border-radius:999px;transition:width .3s"></div>'
        f'<span style="position:absolute;inset:0;display:flex;align-items:center;'
        f'justify-content:center;font-size:11px;font-weight:700;color:#1f2937">'
        f'{val}/{high}</span></div>'
    )


def _vbar(val: float, high: float = 100, color: Optional[str] = None, label: str = "") -> str:
    pct = min(val / high * 100, 100)
    if not color:
        color = "#dc2626" if val < 40 else "#d97706" if val < 70 else "#16a34a"
    return (
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px">'
        f'<div style="width:40px;height:120px;background:#e5e7eb;border-radius:4px;'
        f'overflow:hidden;position:relative;display:flex;align-items:flex-end">'
        f'<div style="width:100%;height:{pct:.0f}%;background:{color};border-radius:4px;'
        f'transition:height .3s"></div></div>'
        f'<span style="font-size:11px;font-weight:700;color:#1f2937">{label}</span>'
        f'<span style="font-size:14px;font-weight:800">{val}</span></div>'
    )


def render_html_report(
    *,
    title: str,
    health: dict,
    spof_data: dict,
    gaps: dict,
    succession: dict,
    readiness: dict,
    knowledge: dict,
    feedback: list,
    pipeline_out: dict,
    scenario_type: str,
    removed_list: list,
    scenario: Any,
) -> str:
    comp = health["composite_score"]
    ind = health["indicators"]
    revenue_total = spof_data.get("total_annual_revenue_at_risk_usd", 0)
    insight = pipeline_out["summary"]["insight"]
    coaching = pipeline_out["summary"]["coaching"]
    governance = pipeline_out["summary"]["governance"]

    spofs_full = spof_data.get("spofs", [])
    spof_rows = "".join(
        f'<tr><td>{s["employee"]}</td><td>{s["team"]}</td><td>{s["role"]}</td>'
        f'<td><span class="risk-{s.get("severity_level","Medium").lower()}">{s.get("severity_level","")}</span></td>'
        f'<td align=center>{s.get("dependents_count",0)}</td>'
        f'<td align=center>{s.get("low_doc_areas",0)}</td>'
        f'<td align=right>${s.get("revenue_at_risk_usd",0):,}</td></tr>'
        for s in spofs_full[:15]
    )

    gaps_rows = "".join(
        f'<tr><td>{t["team"]}</td><td align=center>{t["employee_count"]}</td>'
        f'<td>{_bar(t["coverage_pct"],100)}</td>'
        f'<td>{", ".join(t.get("missing_areas",[])[:4]) or "None"}</td>'
        f'<td>{", ".join(t.get("critical_missing",[])) or "None"}</td></tr>'
        for t in gaps.get("teams", [])
    )

    succession_rows = "".join(
        f'<tr><td>{r["role"]}</td><td>{r["employee"]}</td><td>{r["team"]}</td>'
        f'<td align=center>{"✓" if r.get("backup_available") else "✗"}</td>'
        f'<td align=center>{"✓" if r.get("has_ready_successor") else "✗"}</td>'
        f'<td align=right>{len(r.get("potential_successors",[]))}</td></tr>'
        for r in succession.get("roles", [])
    )

    knowledge_rows = "".join(
        f'<tr><td>{a["knowledge_area"]}</td><td align=center>{a["holder_count"]}</td>'
        f'<td>{_bar(a["risk_score"],100)}</td>'
        f'<td><span class="risk-{a["risk_level"].lower()}">{a["risk_level"]}</span></td>'
        f'<td>{", ".join(a["holders"][:4])}{" +" + str(len(a["holders"])-4) + " more" if len(a["holders"])>4 else ""}</td></tr>'
        for a in knowledge.get("concentrated_areas", [])
    )

    readiness_rows = "".join(
        f'<tr><td>{t["team"]}</td><td align=center>{t["member_count"]}</td>'
        f'<td align=center>{t["active_projects"]}</td>'
        f'<td>{_bar(t["readiness_score"],100)}</td>'
        f'<td align=center>{t.get("advanced_experts",0)}</td></tr>'
        for t in readiness.get("team_readiness", [])
    )

    actions = coaching.get("actions", [])
    actions_html = "".join(
        f'<div style="border:1px solid #d1d5db;border-radius:8px;padding:12px;margin-bottom:8px">'
        f'<div style="font-weight:600;font-size:14px">{a["title"]}</div>'
        f'<div style="font-size:12px;color:#6b7280;margin-top:4px">'
        f'Owner: {a.get("owner_role","-")} &middot; Deadline: {a.get("deadline_days","-")}d &middot; '
        f'Est. Cost: ${a.get("estimated_cost_usd",0):,} &middot; Impact: {a.get("estimated_impact","-")}'
        f'</div><div style="font-size:12px;color:#4b5563;margin-top:2px">{a.get("rationale","")}</div></div>'
        for a in actions
    )

    upskill_items = coaching.get("upskilling_plan", [])
    upskill_html = "".join(
        f'<tr><td>{u.get("employee","")}</td><td>{u.get("skill_to_develop","")}</td>'
        f'<td>{u.get("method","")}</td><td align=center>{u.get("duration_weeks","")}w</td></tr>'
        for u in upskill_items
    ) or "<tr><td colspan=4 style='text-align:center;color:#9ca3af'>No upskilling recommendations</td></tr>"

    feedback_rows = "".join(
        f'<tr><td>{f.get("employee","")}</td><td>{f.get("action_title","")}</td>'
        f'<td><span class="risk-{f.get("decision","").lower()}">{f.get("decision","")}</span></td>'
        f'<td style="font-size:11px;color:#6b7280">{f.get("reason","")}</td></tr>'
        for f in feedback[-10:]
    ) or "<tr><td colspan=4 style='text-align:center;color:#9ca3af'>No human feedback recorded</td></tr>"

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', -apple-system, sans-serif; max-width: 1100px; margin: 0 auto; padding: 40px 30px; color: #111827; font-size: 13px; line-height: 1.5; }}
  h1 {{ font-size: 26px; border-bottom: 4px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px; color: #111827; }}
  h2 {{ font-size: 18px; color: #2563eb; margin-top: 30px; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #e5e7eb; }}
  h3 {{ font-size: 15px; color: #374151; margin-top: 20px; margin-bottom: 8px; }}
  .meta {{ color: #6b7280; font-size: 12px; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 12px; }}
  th {{ background: #f3f4f6; text-align: left; padding: 8px 10px; font-weight: 600; color: #374151; border: 1px solid #d1d5db; }}
  td {{ padding: 7px 10px; border: 1px solid #d1d5db; color: #374151; }}
  tr:nth-child(even) {{ background: #f9fafb; }}
  .risk-high {{ color: #dc2626; font-weight: 700; }}
  .risk-medium {{ color: #d97706; font-weight: 700; }}
  .risk-low {{ color: #16a34a; font-weight: 700; }}
  .risk-accept {{ color: #16a34a; font-weight: 700; }}
  .risk-veto {{ color: #dc2626; font-weight: 700; }}
  .risk-modify {{ color: #d97706; font-weight: 700; }}
  .kpi-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }}
  .kpi {{ flex: 1; min-width: 140px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; text-align: center; }}
  .kpi .val {{ font-size: 32px; font-weight: 800; line-height: 1.2; }}
  .kpi .lbl {{ font-size: 11px; color: #64748b; margin-top: 4px; }}
  .kpi .sub {{ font-size: 10px; color: #94a3b8; margin-top: 2px; }}
  .section {{ page-break-inside: avoid; }}
  .footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #d1d5db; font-size: 11px; color: #9ca3af; text-align: center; }}
  .badge {{ display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }}
  .badge-high {{ background: #fef2f2; color: #dc2626; }}
  .badge-medium {{ background: #fffbeb; color: #d97706; }}
  .badge-low {{ background: #f0fdf4; color: #16a34a; }}
  .col-charts {{ display: flex; gap: 12px; justify-content: center; padding: 16px 0; }}
  .summary-box {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 16px 20px; margin: 16px 0; }}
  .summary-box p {{ font-size: 14px; color: #1e40af; }}
  .no-print {{ display: block; }}
  @media print {{ body {{ padding: 20px; }} .no-print {{ display: none; }} }}
  .print-btn {{ display: inline-block; background: #2563eb; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }}
  .print-btn:hover {{ background: #1d4ed8; }}
</style>
<script>
  function printReport() {{ window.print(); }}
  window.addEventListener('DOMContentLoaded', function() {{
    var p = new URLSearchParams(window.location.search);
    if (p.get('print') === '1') setTimeout(function() {{ window.print(); }}, 500);
  }});
</script>
</head><body>

<div class="no-print" style="text-align:right;margin-bottom:12px">
  <button class="print-btn" onclick="printReport()">Print Report</button>
  &nbsp;
  <a href="?format=text" style="color:#2563eb;font-size:13px;text-decoration:underline">Download as Text</a>
</div>
<h1>{title}</h1>
<p class="meta">Generated {time.strftime('%Y-%m-%d %H:%M:%S')} by <b>TruPulse AI</b> &middot; Organizational Resilience Analytics &middot; Predict. Simulate. Strengthen.</p>

<!-- EXECUTIVE SUMMARY -->
<div class="summary-box section">
  <h2 style="border:none;margin:0 0 8px 0;color:#1e40af">Executive Summary</h2>
  <p><b>Composite Health Score: {comp}/100</b> &mdash; <span class="badge badge-{"high" if comp<40 else "medium" if comp<70 else "low"}">{health["overall_risk"]} RISK</span></p>
  <p style="margin-top:6px">{health["employee_count"]} employees across {health["team_count"]} teams &middot; {health["project_count"]} active projects &middot; <b>${revenue_total:,} annual revenue at risk</b></p>
  <p style="margin-top:6px">{insight.get("headline","")}</p>
</div>

<!-- INDICATOR SCORES -->
<div class="section">
  <h2>1. Organizational Health Indicators</h2>
  <div class="kpi-row">
    <div class="kpi"><div class="val" style="color:{'#dc2626' if comp<40 else '#d97706' if comp<70 else '#16a34a'}">{comp}</div><div class="lbl">Composite Score</div><div class="sub">{health["overall_risk"]} Risk</div></div>
    <div class="kpi"><div class="val" style="color:#dc2626">{ind["resilience"]["score"]}</div><div class="lbl">Resilience</div><div class="sub">{ind["resilience"]["risk_level"]} Risk &middot; {ind["resilience"]["details"]["spof_count"]} SPOFs</div></div>
    <div class="kpi"><div class="val" style="color:{'#dc2626' if ind['trust']['score']<40 else '#d97706'}">{ind["trust"]["score"]}</div><div class="lbl">Trust</div><div class="sub">{ind["trust"]["risk_level"]} Risk</div></div>
    <div class="kpi"><div class="val" style="color:{'#dc2626' if ind['burnout']['score']<40 else '#d97706'}">{ind["burnout"]["score"]}</div><div class="lbl">Burnout</div><div class="sub">{ind["burnout"]["risk_level"]} Risk</div></div>
    <div class="kpi"><div class="val" style="color:#16a34a">{ind["retention"]["score"]}</div><div class="lbl">Retention</div><div class="sub">{ind["retention"]["risk_level"]} Risk</div></div>
  </div>
  <div class="col-charts">
    {_vbar(ind["resilience"]["score"], 100, "#dc2626", "Resilience")}
    {_vbar(ind["trust"]["score"], 100, "#d97706", "Trust")}
    {_vbar(ind["burnout"]["score"], 100, "#d97706", "Burnout")}
    {_vbar(ind["retention"]["score"], 100, "#16a34a", "Retention")}
  </div>
</div>

{ f"""
<div class="section">
  <h2>2. What-If Scenario Impact</h2>
  <p>Scenario: <b>{', '.join(removed_list)}</b> leaving the organization</p>
  <div class="kpi-row">
    <div class="kpi"><div class="val">{health['composite_score']}</div><div class="lbl">Before</div></div>
    <div class="kpi"><div class="val" style="color:{'#dc2626' if scenario and scenario['composite_score']<health['composite_score'] else '#16a34a'}">{scenario['composite_score'] if scenario else health['composite_score']}</div><div class="lbl">After</div></div>
    <div class="kpi"><div class="val" style="color:{'#dc2626' if scenario and scenario['composite_score']<health['composite_score'] else '#16a34a'}">{scenario['composite_score']-health['composite_score'] if scenario else 0}</div><div class="lbl">Delta</div></div>
    <div class="kpi"><div class="val">${scenario.get('revenue_at_risk_usd',0):,}</div><div class="lbl">Revenue at Risk</div></div>
  </div>
</div>
""" if scenario_type != "baseline" and scenario else "" }

<!-- SPOF RANKING -->
<div class="section">
  <h2>{"3. " if scenario_type != "baseline" and scenario else "2."} Single Points of Failure ({spof_data['total_spofs']} total)</h2>
  <p><b>{spof_data['critical_spofs']} critical</b> &middot; Total annual revenue at risk: <b>${revenue_total:,}</b></p>
  <table><thead><tr><th>Employee</th><th>Team</th><th>Role</th><th>Severity</th><th>Dep.</th><th>Low Doc</th><th>Rev. at Risk</th></tr></thead>
  <tbody>{spof_rows}</tbody></table>
</div>

<!-- SKILL GAPS -->
<div class="section">
  <h2>{"4. " if scenario_type != "baseline" and scenario else "3."} Skill Gap Analysis</h2>
  <p>Org-wide gaps: <b>{gaps.get('total_gap_count',0)}</b> knowledge areas with insufficient coverage</p>
  <table><thead><tr><th>Team</th><th>Employees</th><th>Coverage</th><th>Missing Areas</th><th>Critical Gaps</th></tr></thead>
  <tbody>{gaps_rows}</tbody></table>
</div>

<!-- SUCCESSION PLANNING -->
<div class="section">
  <h2>{"5. " if scenario_type != "baseline" and scenario else "4."} Succession Planning</h2>
  <p>Org readiness: <b>{succession.get('org_readiness','N/A')}%</b> &middot; {succession.get('total_high_roles',0)} critical roles &middot; {succession.get('roles_covered',0)} ready-now successors</p>
  <table><thead><tr><th>Role</th><th>Current Holder</th><th>Team</th><th>Backup?</th><th>Successor?</th><th>Potential</th></tr></thead>
  <tbody>{succession_rows}</tbody></table>
</div>

<!-- KNOWLEDGE CONCENTRATION -->
<div class="section">
  <h2>{"6. " if scenario_type != "baseline" and scenario else "5."} Knowledge Concentration Risk</h2>
  <p>{knowledge.get('critical_areas',0)} critical areas &middot; {knowledge.get('org_exposure_pct',0)}% org exposure &middot; {knowledge.get('total_areas',0)} total knowledge areas</p>
  <table><thead><tr><th>Knowledge Area</th><th>Holders</th><th>Risk Score</th><th>Level</th><th>Holders</th></tr></thead>
  <tbody>{knowledge_rows}</tbody></table>
</div>

<!-- WORKFORCE READINESS -->
<div class="section">
  <h2>{"7. " if scenario_type != "baseline" and scenario else "6."} Workforce Readiness</h2>
  <p>Overall readiness: <b>{readiness.get('readiness_score','N/A')}</b> &middot; <span class="badge badge-{readiness.get('readiness_level','Medium').lower()}">{readiness.get('readiness_level','')}</span></p>
  <table><thead><tr><th>Team</th><th>Members</th><th>Projects</th><th>Readiness</th><th>Experts</th></tr></thead>
  <tbody>{readiness_rows}</tbody></table>
</div>

<!-- AI PIPELINE RECOMMENDATIONS -->
<div class="section">
  <h2>{"8. " if scenario_type != "baseline" and scenario else "7."} AI Pipeline Recommendations</h2>
  <h3>Insight</h3>
  <p>{insight.get("headline","")}</p>
  <ul style="margin:8px 0 16px 20px">{"".join(f'<li style="margin:4px 0;font-size:13px"><b>{p.get("title","")}:</b> {p.get("evidence","")} <span class="badge badge-{p.get("severity","low").lower()}">{p.get("severity","")}</span></li>' for p in insight.get("patterns",[]))}</ul>

  <h3>Recommended Actions</h3>
  {actions_html or "<p style='color:#9ca3af'>No specific actions generated</p>"}

  { f'''
  <h3>Upskilling Plan</h3>
  <table><thead><tr><th>Employee</th><th>Skill</th><th>Method</th><th>Duration</th></tr></thead>
  <tbody>{upskill_html}</tbody></table>
  ''' if upskill_items else "" }
</div>

<!-- HUMAN FEEDBACK -->
<div class="section">
  <h2>{"9. " if scenario_type != "baseline" and scenario else "8."} Human-in-the-Loop Feedback</h2>
  <p>Past {len(feedback)} decision(s) recorded by human reviewers</p>
  <table><thead><tr><th>Employee</th><th>Action</th><th>Decision</th><th>Reason</th></tr></thead>
  <tbody>{feedback_rows}</tbody></table>
</div>

<!-- GOVERNANCE -->
<div class="section">
  <h2>{"10. " if scenario_type != "baseline" and scenario else "9."} Governance & Validation</h2>
  <p><b>Confidence Score:</b> {governance.get('confidence_score','N/A')}/100</p>
  <p><b>Rationale:</b> {governance.get('confidence_rationale','N/A')}</p>
  <p><b>Counter-Argument:</b> {governance.get('counter_argument','N/A')}</p>
  <p><b>Human Review Required:</b> {governance.get('human_review_required','N/A')} &mdash; {governance.get('human_review_reason','')}</p>
</div>

<!-- SUMMARY TABLE -->
<div class="section">
  <h2>{"11. " if scenario_type != "baseline" and scenario else "10."} At a Glance</h2>
  <table>
    <tr><td><b>Composite Score</b></td><td>{comp}/100</td><td><b>Overall Risk</b></td><td><span class="badge badge-{"high" if comp<40 else "medium" if comp<70 else "low"}">{health["overall_risk"]}</span></td></tr>
    <tr><td><b>Total Employees</b></td><td>{health["employee_count"]}</td><td><b>Total Teams</b></td><td>{health["team_count"]}</td></tr>
    <tr><td><b>SPOFs</b></td><td>{spof_data["total_spofs"]} (critical: {spof_data["critical_spofs"]})</td><td><b>Revenue at Risk</b></td><td>${revenue_total:,}</td></tr>
    <tr><td><b>Skill Gaps</b></td><td>{gaps.get('total_gap_count',0)}</td><td><b>Knowledge Exposure</b></td><td>{knowledge.get('org_exposure_pct',0)}%</td></tr>
    <tr><td><b>Succession Readiness</b></td><td>{succession.get('org_readiness','N/A')}%</td><td><b>Workforce Readiness</b></td><td>{readiness.get('readiness_score','N/A')}</td></tr>
    <tr><td><b>Human Decisions</b></td><td>{len(feedback)}</td><td><b>Report Type</b></td><td>{'Current State' if scenario_type=='baseline' else 'What-If'}</td></tr>
  </table>
</div>

<div class="footer">
  <p>TruPulse AI &middot; Generated {time.strftime('%Y-%m-%d at %H:%M:%S')} &middot; Local LLM via Ollama &middot; 5-Agent Collective Intelligence &middot; ChromaDB Vector Knowledge &middot; Human-in-the-Loop Governance</p>
  <p style="margin-top:4px"><b>Predict. Simulate. Strengthen.</b> &mdash; This report is confidential and intended for management use.</p>
</div>

</body></html>"""


def render_text_report(
    *,
    title: str,
    health: dict,
    spof_data: dict,
    gaps: dict,
    succession: dict,
    readiness: dict,
    knowledge: dict,
    feedback: list,
    pipeline_out: dict,
    scenario_type: str,
    removed_list: list,
    scenario: Any,
) -> str:
    comp = health["composite_score"]
    revenue_total = spof_data.get("total_annual_revenue_at_risk_usd", 0)
    insight = pipeline_out["summary"]["insight"]
    upskill_items = pipeline_out["summary"]["coaching"].get("upskilling_plan", [])

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    lines = []
    def a(l): lines.append(l)
    a("=" * 72)
    a(f"  {title}")
    a("=" * 72)
    a(f"  Generated {now} by TruPulse AI")
    a(f"  Organizational Resilience Analytics")
    a("-" * 72)
    a("")
    a(f"EXECUTIVE SUMMARY")
    a(f"  Composite Health Score: {comp}/100 — {health['overall_risk']} RISK")
    a(f"  {health['employee_count']} employees across {health['team_count']} teams | {health['project_count']} active projects")
    a(f"  Annual Revenue at Risk: ${revenue_total:,}")
    a(f"  {insight.get('headline','')}")
    a("")
    a(f"HEALTH INDICATORS")
    for key, label in [("resilience","Resilience"),("trust","Trust"),("burnout","Burnout"),("retention","Retention")]:
        s = health["indicators"][key]["score"]
        a(f"  {label}: {s}/100 — {health['indicators'][key]['risk_level']} Risk")
    a("")
    if scenario_type != "baseline" and scenario:
        a(f"WHAT-IF SCENARIO: {', '.join(removed_list)} leaving")
        a(f"  Before: {health['composite_score']}")
        a(f"  After:  {scenario['composite_score']}")
        a(f"  Delta:  {scenario['composite_score'] - health['composite_score']}")
        a(f"  Revenue at Risk: ${scenario.get('revenue_at_risk_usd',0):,}")
        a("")
    a(f"SINGLE POINTS OF FAILURE ({spof_data['total_spofs']} total)")
    a(f"  Critical: {spof_data['critical_spofs']} | Revenue at Risk: ${revenue_total:,}")
    for r in spof_data.get("rankings",[]):
        a(f"  - {r['employee_name']} ({r['team_name']}, {r['role']}) — {r['severity']} — {r['dependents']} dependents — rev risk ${r['annual_revenue_at_risk_usd']:,}")
    a("")
    a(f"SKILL GAP ANALYSIS")
    a(f"  Gaps: {gaps.get('total_gap_count',0)} areas with insufficient coverage")
    for t in gaps.get("teams",[]):
        tn = t.get("team_name") or t.get("team","?")
        a(f"  Team {tn}: {t['coverage_pct']}% coverage — {len(t.get('missing_areas',[]))} missing — {len(t.get('critical_gaps',[]))} critical")
    a("")
    a(f"SUCCESSION PLANNING")
    a(f"  Org Readiness: {succession.get('org_readiness','N/A')}% | Roles: {succession.get('total_high_roles',0)} | Covered: {succession.get('roles_covered',0)}")
    for s in succession.get("succession_data",[]):
        a(f"  {s['role']}: {s['current_holder']} — backup={'YES' if s.get('has_backup') else 'NO'} | successor={'YES' if s.get('has_successor') else 'NO'} (potential: {s.get('successor_potential','N/A')})")
    a("")
    a(f"KNOWLEDGE CONCENTRATION")
    a(f"  Critical: {knowledge.get('critical_areas',0)} | Exposure: {knowledge.get('org_exposure_pct',0)}% | Areas: {knowledge.get('total_areas',0)}")
    for k in (knowledge.get("concentrated_areas",[]) or knowledge.get("knowledge_data",[])):
        a(f"  {k.get('knowledge_area','?')}: holders={len(k.get('holders',[]))} | risk={k.get('risk_score',0)} | level={k.get('risk_level','')}")
    a("")
    a(f"WORKFORCE READINESS")
    a(f"  Score: {readiness.get('readiness_score','N/A')} | Level: {readiness.get('readiness_level','')}")
    for t in readiness.get("teams",[]):
        a(f"  {t.get('team_name','?')}: {t.get('employee_count',0)} members | {t.get('project_count',0)} projects | readiness={t.get('readiness_pct',0)}%")
    a("")
    a(f"AI RECOMMENDATIONS")
    a(f"  {insight.get('headline','')}")
    for p in insight.get("patterns",[]):
        a(f"  [{p.get('severity','?')}] {p.get('title','')}: {p.get('evidence','')}")
    for a_ in insight.get("actions",[]):
        a(f"  Action: {a_.get('action','')} — {a_.get('impact','')} (${a_.get('cost_estimate_usd',0):,}, {a_.get('duration_months',0)}mo)")
    if upskill_items:
        a(f"  UPSKILLING PLAN:")
        for u in upskill_items:
            a(f"    {u.get('employee','?')} → {u.get('skill_to_develop','?')} via {u.get('method','?')} ({u.get('duration_weeks','?')}w)")
    a("")
    a(f"HUMAN FEEDBACK ({len(feedback)} decisions)")
    for f in feedback:
        a(f"  {f.get('employee_name','?')}: {f.get('action','?')} — {f.get('decision','?')} ({f.get('reason','')})")
    a("")
    a(f"GOVERNANCE & VALIDATION")
    g = pipeline_out.get("governance",{})
    a(f"  Confidence: {g.get('confidence_score','N/A')}/100")
    a(f"  Rationale: {g.get('confidence_rationale','N/A')}")
    a(f"  Counter-Argument: {g.get('counter_argument','N/A')}")
    a(f"  Review: {g.get('human_review_required','N/A')} — {g.get('human_review_reason','')}")
    a("")
    a("=" * 72)
    a("  AT A GLANCE")
    a(f"  Composite: {comp}/100 | Risk: {health['overall_risk']}")
    a(f"  Employees: {health['employee_count']} | Teams: {health['team_count']}")
    a(f"  SPOFs: {spof_data['total_spofs']} | Revenue at Risk: ${revenue_total:,}")
    a(f"  Skill Gaps: {gaps.get('total_gap_count',0)} | Knowledge Exposure: {knowledge.get('org_exposure_pct',0)}%")
    a(f"  Succession: {succession.get('org_readiness','N/A')}% | Readiness: {readiness.get('readiness_score','N/A')}")
    a(f"  Human Decisions: {len(feedback)} | Type: {'Current State' if scenario_type=='baseline' else 'What-If'}")
    a("-" * 72)
    a(f"  TruPulse AI | Generated {now}")
    a(f"  Predict. Simulate. Strengthen.")
    a("=" * 72)
    return "\n".join(lines)
