"""
TruPulse AI - Expanded Data Generator
Generates 55 employees with diverse profit/loss/break-even scenarios.
Run: python generate_data.py
"""

import csv, os, random
from pathlib import Path

random.seed(42)
DATA_DIR = Path(__file__).parent / "data"

TEAMS = [
    "Sales", "Product", "Engineering", "Security", "Support",
    "Infrastructure", "Finance", "HR", "Marketing", "Legal", "Operations",
    "Data", "Design", "Strategy"
]

ROLES_BY_TEAM = {
    "Sales": ["Sales Manager", "Account Executive", "Sales Development Rep", "Enterprise Sales", "Sales Analyst"],
    "Product": ["Product Manager", "Business Analyst", "Product Owner", "UX Researcher", "Product Analyst"],
    "Engineering": ["Lead Backend Engineer", "Senior Frontend Engineer", "Backend Engineer", "DevOps Engineer", "QA Lead", "QA Engineer", "Junior Backend Engineer", "Full Stack Engineer", "Data Engineer", "Mobile Engineer"],
    "Security": ["Security Architect", "Security Analyst", "Security Engineer", "SOC Analyst", "Compliance Officer"],
    "Support": ["Support Lead", "Senior Support Engineer", "Support Engineer", "Customer Success Manager", "Technical Writer"],
    "Infrastructure": ["Cloud Architect", "System Administrator", "Network Engineer", "Junior Sysadmin", "SRE Engineer"],
    "Finance": ["Finance Manager", "Senior Accountant", "Accountant", "Financial Analyst", "Auditor"],
    "HR": ["HR Manager", "HR Business Partner", "Recruiter", "Learning & Development", "Payroll Specialist"],
    "Marketing": ["Marketing Lead", "Content Strategist", "Marketing Designer", "SEO Specialist", "Growth Marketer"],
    "Legal": ["Legal Counsel", "Legal Analyst", "Contracts Manager", "Paralegal", "IP Specialist"],
    "Operations": ["Operations Manager", "Operations Analyst", "Supply Chain Coordinator", "Procurement Specialist", "Facilities Manager"],
    "Data": ["Data Scientist", "Data Analyst", "Analytics Engineer", "ML Engineer", "BI Developer"],
    "Design": ["Design Lead", "UI Designer", "Brand Designer", "Motion Designer", "DesignOps"],
    "Strategy": ["Strategy Lead", "Business Strategist", "Corporate Development", "Innovation Lead", "Research Associate"],
}

def employee_gen():
    used_names = set()
    first_names = [
        "Vikram","Anjali","Rohit","Priya","Aditya","Neha","Arjun","Pooja","Meera","Kavya",
        "Rahul","Amit","Sneha","Karan","Ravi","Isha","Sanjay","Tanvi","Deepak","Rishi",
        "Nikhil","Harsh","Manoj","Rajesh","Sunita","Kavita","Aarti","Vivek","Aakash",
        "Suresh","Lakshmi","Ganesh","Divya","Mohan","Rekha","Vijay","Sita","Arun","Nalini",
        "Kishore","Padma","Rajan","Geeta","Mahesh","Usha","Prakash","Lalita","Venkat",
        "Sarita","Dinesh","Anita","Gopal","Radha","Shyam","Bhavna","Hari","Indira","Jatin",
        "Kirti","Lalit","Mukesh","Neelam","Omkar","Pallavi","Quasim","Rashmi","Shivani",
        "Tara","Uday","Vani","Ajay","Bela","Chandan","Deepali","Esha","Farhan","Gauri",
        "Hemant","Ishita","Jagdish","Kamla","Lalit","Manisha","Naresh","Ojas","Poonam",
    ]
    random.shuffle(first_names)
    teams_by_name = {}
    for i, name in enumerate(first_names):
        team = random.choice(TEAMS)
        teams_by_name[name] = team
    names = list(teams_by_name.keys())
    random.shuffle(names)
    return names, teams_by_name

def profile_type(name):
    """Classify as profit/loss/break-even based on name hash."""
    h = sum(ord(c) for c in name)
    if h % 3 == 0: return "profit"
    if h % 3 == 1: return "loss"
    return "break_even"

def gen_salary(profile, role, experience):
    base = {"profit": 1.2, "loss": 0.7, "break_even": 1.0}[profile]
    role_base = max(40000, 120000 - len(role) * 2000 + random.randint(-20000, 20000))
    return int(base * role_base * (0.8 + experience * 0.04))

def gen_contract_value(profile, base):
    multipliers = {"profit": (1.5, 3.0), "loss": (0.2, 0.7), "break_even": (0.8, 1.2)}
    low, high = multipliers[profile]
    return int(base * random.uniform(low, high))

print("Generating expanded data files...")

names, teams_by_name = employee_gen()
team_members = {t: [] for t in TEAMS}
for n in names:
    team_members[teams_by_name[n]].append(n)

# ---- EMPLOYEES ----
employees = []
for idx, name in enumerate(names):
    eid = f"EMP{idx+1:03d}"
    team = teams_by_name[name]
    role = random.choice(ROLES_BY_TEAM[team])
    exp = random.randint(1, 15)
    prof = profile_type(name)
    salary = gen_salary(prof, role, exp)
    tenure = min(exp, random.randint(1, 12))
    is_spof = prof == "loss" and exp > 5
    backup = "No" if is_spof else "Yes" if random.random() < 0.6 else "No"
    crit = "High" if is_spof else "Medium" if exp > 4 else "Low"
    employees.append({
        "EmployeeID": eid, "Employee": name, "Team": team, "Role": role,
        "Criticality": crit, "BackupAvailable": backup,
        "ExperienceYears": exp, "AnnualSalaryUSD": salary, "TenureYears": tenure
    })

# ---- KNOWLEDGE AREAS ----
KNOWLEDGE_AREAS = [
    "Strategic Account Management","Sales Pipeline Management","Client Relationship Management",
    "Product Roadmap Planning","User Research","UX Design","API Design","System Architecture",
    "Cloud Infrastructure (AWS/Azure)","Database Administration","DevOps & CI/CD","Security Compliance",
    "Network Security","Penetration Testing","Customer Success","Technical Support","Incident Management",
    "Financial Planning & Analysis","Budgeting & Forecasting","Accounts Payable/Receivable",
    "Talent Acquisition","Employee Relations","Compensation Planning","Organizational Development",
    "Brand Strategy","Campaign Management","Content Writing","SEO & SEM","Contract Negotiation",
    "Legal Compliance (SOC2/ISO27001)","Intellectual Property","Risk Management","Supply Chain Management",
    "Vendor Management","Process Optimization","Data Analytics","Machine Learning","Business Intelligence",
    "A/B Testing","Marketing Automation","CRM Tools (Salesforce)","ERP Systems","Project Management (Agile)",
    "Change Management","Stakeholder Communication","Negotiation","Presentation Skills",
    "Mentoring & Coaching","Technical Writing","Quality Assurance","Test Automation",
    "Mobile Development","Frontend Frameworks","Backend Systems","Microservices Architecture",
    "Containerization (Docker/K8s)","Monitoring & Observability","Disaster Recovery",
    "Identity & Access Management","Threat Modeling","Vulnerability Management",
]

knowledge_records = []
for emp in employees:
    count = random.randint(2, 6)
    areas = random.sample(KNOWLEDGE_AREAS, count)
    for area in areas:
        prof_val = profile_type(emp["Employee"])
        doc_level = "High" if prof_val == "profit" else "Low" if prof_val == "loss" else random.choice(["Low","Medium","High"])
        knowledge_records.append({
            "EmployeeID": emp["EmployeeID"], "Employee": emp["Employee"],
            "KnowledgeArea": area, "DocumentationLevel": doc_level,
            "Proficiency": random.choice(["Beginner","Intermediate","Advanced","Expert"]),
            "LastUpdated": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        })

# ---- PROJECTS ----
PROJECT_TEMPLATES = [
    ("Project Phoenix", "Engineering", "Global Bank", 850000),
    ("Salesforce Migration", "Sales", "TechCorp", 1200000),
    ("Cloud Security Audit", "Security", "FinSecure", 600000),
    ("Product Redesign", "Design", "ConsumerApp", 450000),
    ("Data Lake Platform", "Data", "RetailMax", 950000),
    ("Employee Portal", "Engineering", "Internal", 350000),
    ("Compliance Dashboard", "Legal", "Regulatory", 280000),
    ("AI Chatbot", "Data", "ServicePro", 520000),
    ("Mobile App v3", "Mobile", "SocialNet", 780000),
    ("Infra Migration", "Infrastructure", "CloudCo", 1100000),
    ("Analytics Suite", "Data", "AdPlatform", 670000),
    ("Brand Refresh", "Marketing", "Internal", 180000),
    ("Training Platform", "HR", "EduCorp", 420000),
    ("Lead Scoring Engine", "Sales", "SaaSPro", 560000),
    ("Security Operations Center", "Security", "GovtAgency", 2100000),
    ("API Gateway", "Engineering", "FinTech", 740000),
    ("Customer Portal", "Support", "Telco", 490000),
    ("BI Migration", "Data", "HealthCare", 830000),
    ("CRM Integration", "Sales", "RetailChain", 380000),
    ("Zero Trust Architecture", "Security", "BankCorp", 1650000),
    ("Payment Gateway", "Engineering", "EComPlus", 920000),
    ("Design System", "Design", "Internal", 220000),
    ("Expense Tool", "Finance", "Internal", 150000),
    ("SRE Playbook", "Infrastructure", "Internal", 310000),
    ("Partnership Portal", "Operations", "PartnerCo", 410000),
    ("Research Lab", "Data", "University", 290000),
    ("Brand Guidelines", "Design", "Internal", 95000),
    ("OKR Platform", "Strategy", "Internal", 260000),
]
projects = []
for i, (name, team, client, value) in enumerate(PROJECT_TEMPLATES):
    prof = profile_type(name)
    multiplier = {"profit": random.uniform(1.2, 2.5), "loss": random.uniform(0.1, 0.6), "break_even": random.uniform(0.8, 1.2)}[prof]
    final_value = int(value * multiplier)
    status = random.choice(["Active","Active","Active","At Risk","Completed"])
    projects.append({
        "ProjectID": f"PRJ{i+1:04d}", "Project": name, "Team": team,
        "Criticality": "High" if final_value > 800000 else "Medium",
        "DeadlineDays": random.randint(7, 90),
        "Client": client, "AnnualContractValueUSD": final_value, "Status": status,
    })

# ---- DEPENDENCIES ----
dependencies = []
for emp in employees:
    if random.random() < 0.4:
        continue
    num_deps = random.randint(1, 4) if profile_type(emp["Employee"]) == "loss" else random.randint(0, 2)
    possible_deps = [e for e in employees if e["Employee"] != emp["Employee"] and e["Team"] == emp["Team"]]
    if not possible_deps:
        possible_deps = [e for e in employees if e["Employee"] != emp["Employee"]]
    deps = random.sample(possible_deps, min(num_deps, len(possible_deps)))
    for dep in deps:
        dependencies.append({
            "OwnerID": emp["EmployeeID"], "Owner": emp["Employee"],
            "DependentID": dep["EmployeeID"], "Dependent": dep["Employee"],
            "DependencyType": random.choice(["Knowledge Transfer","Project Handoff","Approval Chain","Technical Consultation","Client Relationship"]),
            "Criticality": random.choice(["High","Medium","Low"]),
        })

# ---- PERFORMANCE ----
performance = []
for emp in employees:
    prof = profile_type(emp["Employee"])
    if prof == "profit":
        eng = random.randint(8, 10)
        rating = random.choice(["Exceeds Expectations","Outstanding"])
    elif prof == "loss":
        eng = random.randint(2, 5)
        rating = random.choice(["Needs Improvement","Below Expectations"])
    else:
        eng = random.randint(5, 8)
        rating = random.choice(["Meets Expectations","Exceeds Expectations"])
    goals_total = random.randint(6, 12)
    goals_done = int(goals_total * (random.uniform(0.5, 1.0) if prof != "loss" else random.uniform(0.2, 0.7)))
    performance.append({
        "EmployeeID": emp["EmployeeID"], "Employee": emp["Employee"],
        "Team": emp["Team"], "PerformanceRating": rating,
        "GoalsCompleted": goals_done, "GoalsTotal": goals_total,
        "LastReviewDate": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "EngagementScore": eng, "TenureAtCompany": emp["TenureYears"],
    })

# ---- WORKLOAD ----
workload = []
for emp in employees:
    prof = profile_type(emp["Employee"])
    hours = random.randint(35, 45) if prof == "profit" else random.randint(45, 70) if prof == "loss" else random.randint(38, 50)
    difficulty = "Low" if prof == "profit" else "High" if prof == "loss" else random.choice(["Medium","High"])
    overdue = 0 if prof == "profit" else random.randint(1, 5) if prof == "loss" else random.randint(0, 2)
    workload.append({
        "EmployeeID": emp["EmployeeID"], "Employee": emp["Employee"],
        "Team": emp["Team"], "WeeklyHours": hours,
        "TaskDifficulty": difficulty, "ActiveProjects": random.randint(1, 5),
        "OverdueTasks": overdue, "PTOPlannedDays": random.randint(0, 10),
        "LastPTODays": random.randint(1, 60) if prof == "profit" else random.randint(60, 180) if prof == "loss" else random.randint(10, 90),
    })

# ---- REVIEW NOTES ----
review_notes = []
for emp in employees:
    prof = profile_type(emp["Employee"])
    if prof == "profit":
        notes = [
            f"[EMP{employees.index(emp)+1:03d} - {emp['Employee']}, {emp['Role']}] Exceptional performer. {emp['Employee']} consistently exceeds targets and mentors junior team members. Knowledge is well-documented with zero SPOF risk. Engagement score at {performance[employees.index(emp)]['EngagementScore']}/10. Revenue contribution estimated at ${projects[employees.index(emp) // 3]['AnnualContractValueUSD'] if employees.index(emp) // 3 < len(projects) else 500000:,}. Low attrition risk — strong retention candidate. Recommend accelerated promotion track.\nAction: Fast-track to senior role. Assign as mentor to 2 junior employees.",
            f"[EMP{employees.index(emp)+1:03d} - {emp['Employee']}] Profit center. High output-to-cost ratio. Salary ${emp['AnnualSalaryUSD']:,} justified by {projects[employees.index(emp) // 3]['AnnualContractValueUSD'] if employees.index(emp) // 3 < len(projects) else 500000:,} in managed portfolio. Zero overdue tasks. Full documentation compliance.",
        ][random.randint(0,1)]
    elif prof == "loss":
        notes = [
            f"[EMP{employees.index(emp)+1:03d} - {emp['Employee']}, {emp['Role']}] Critical concern. {emp['Employee']} is a single point of failure with no backup and undocumented processes. Engagement at {performance[employees.index(emp)]['EngagementScore']}/10 — lowest in team. Weekly hours at {workload[employees.index(emp)]['WeeklyHours']} with {workload[employees.index(emp)]['OverdueTasks']} overdue tasks. Revenue at risk estimated at ${projects[employees.index(emp) // 3]['AnnualContractValueUSD'] * 2 if employees.index(emp) // 3 < len(projects) else 750000:,}. Flight risk is HIGH. Manager reports disengagement in last 3 1-on-1s.\nAction: Immediate cross-training required. Consider performance improvement plan. Schedule skip-level meeting.",
            f"[EMP{employees.index(emp)+1:03d} - {emp['Employee']}] Loss-making scenario. Salary ${emp['AnnualSalaryUSD']:,} exceeds productivity contribution. Goals completion at {performance[employees.index(emp)]['GoalsCompleted']}/{performance[employees.index(emp)]['GoalsTotal']}. High burnout indicators. Knowledge areas undocumented. If {emp['Employee']} leaves, recovery cost estimated at 2.5x salary.",
        ][random.randint(0,1)]
    else:
        notes = [
            f"[EMP{employees.index(emp)+1:03d} - {emp['Employee']}, {emp['Role']}] Stable performer. {emp['Employee']} meets expectations consistently but shows no exceptional initiative. Engagement at {performance[employees.index(emp)]['EngagementScore']}/10 — adequate. Documentation is partial. Not a SPOF but cross-training recommended. Revenue contribution is break-even against cost.\nAction: Encourage upskilling in {random.choice(KNOWLEDGE_AREAS)}. Set stretch goals for next quarter.",
            f"[EMP{employees.index(emp)+1:03d} - {emp['Employee']}] Break-even contributor. Salary ${emp['AnnualSalaryUSD']:,} aligned with output. Performance at expected levels. No critical risks identified. Knowledge partially documented. Moderate retention risk — could improve with development opportunities.",
        ][random.randint(0,1)]
    review_notes.append(notes)

# ---- WRITE CSVs ----
os.makedirs(DATA_DIR, exist_ok=True)

with open(DATA_DIR / "employees.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=employees[0].keys())
    w.writeheader(); w.writerows(employees)
print(f"  employees.csv: {len(employees)} employees")

with open(DATA_DIR / "knowledge.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=knowledge_records[0].keys())
    w.writeheader(); w.writerows(knowledge_records)
print(f"  knowledge.csv: {len(knowledge_records)} records")

with open(DATA_DIR / "projects.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=projects[0].keys())
    w.writeheader(); w.writerows(projects)
print(f"  projects.csv: {len(projects)} projects")

with open(DATA_DIR / "dependencies.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["OwnerID","Owner","DependentID","Dependent","DependencyType","Criticality"])
    w.writeheader(); w.writerows(dependencies)
print(f"  dependencies.csv: {len(dependencies)} links")

with open(DATA_DIR / "performance.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=performance[0].keys())
    w.writeheader(); w.writerows(performance)
print(f"  performance.csv: {len(performance)} records")

with open(DATA_DIR / "workload.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=workload[0].keys())
    w.writeheader(); w.writerows(workload)
print(f"  workload.csv: {len(workload)} records")

with open(DATA_DIR / "review_notes.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(review_notes))
    f.write("\n")
print(f"  review_notes.txt: {len(review_notes)} notes")

print(f"\nDone! Generated {len(employees)} employees with diverse profit/loss/break-even profiles.")
print(f"Profit: {sum(1 for e in employees if profile_type(e['Employee'])=='profit')}")
print(f"Loss: {sum(1 for e in employees if profile_type(e['Employee'])=='loss')}")
print(f"Break-even: {sum(1 for e in employees if profile_type(e['Employee'])=='break_even')}")
