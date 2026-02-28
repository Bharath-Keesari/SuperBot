"""Static knowledge base for SuperBot RAG."""
KNOWLEDGE_DOCS = [
    {"text": """HR Policy: Annual Leave
Employees are entitled to 24 days of Annual Leave per year. Leave accrues at 2 days per month.
Carry forward: Maximum 10 days can be carried forward to next year. Remaining balance lapses.
Application: Apply at least 3 working days in advance via the HR portal.
Approval: Requires manager approval within 2 working days.
Encashment: Up to 5 days can be encashed per year at basic salary rate.
New joiners: Employees joining mid-year get prorated leave based on months remaining.""",
     "metadata": {"type": "hr_policy", "source": "HR Policy Manual", "label": "Leave Policy"}},

    {"text": """HR Policy: Sick Leave
All employees get 10 days of Sick Leave per year. Sick leave does not carry forward.
For absences > 2 consecutive days: A medical certificate from a registered doctor is mandatory.
Half-day sick leave: Allowed. Must be applied by 10 AM for morning half, 2 PM for afternoon half.
Chronic illness: Employees with serious conditions may apply for extended medical leave under the Medical Leave policy (separate document).
Sick leave cannot be combined with Annual Leave on the same day.""",
     "metadata": {"type": "hr_policy", "source": "HR Policy Manual", "label": "Leave Policy"}},

    {"text": """HR Policy: Work From Home (WFH)
Standard WFH allowance: 2 days per week for all employees in eligible roles.
Engineering, BI, and Finance roles: Fully eligible for WFH.
Sales and Client-facing roles: Maximum 1 day WFH per week.
WFH days: Tuesday and Thursday are designated WFH days by default. Changes require manager approval.
Monday and Friday WFH: Requires VP-level approval.
Home setup: Company provides ₹15,000 one-time WFH allowance for eligible equipment.
Connectivity: Employees must maintain stable internet. VPN required for all internal systems.""",
     "metadata": {"type": "hr_policy", "source": "HR Policy Manual", "label": "WFH Policy"}},

    {"text": """HR Policy: Performance Review
Review cycle: Bi-annual — June and December.
Process: Self-assessment → Manager assessment → Calibration → Final rating → Salary revision.
Ratings: Exceptional (5), Exceeds Expectations (4), Meets Expectations (3), Below Expectations (2), Unsatisfactory (1).
Salary revision: Based on rating — Exceptional: 20-30%, Exceeds: 12-20%, Meets: 6-12%, Below: 0-5%, Unsatisfactory: 0%.
PIP: Employees rated Below for 2 consecutive cycles are placed on Performance Improvement Plan (90 days).
Promotion eligibility: Rating of 4+ for 2 consecutive cycles + manager nomination required.""",
     "metadata": {"type": "hr_policy", "source": "HR Policy Manual", "label": "Performance"}},

    {"text": """HR Policy: Reimbursements and Expenses
Travel: Air travel requires approval 7 days in advance. Economy class for domestic, Business for international >6hrs.
Accommodation: ₹5000/night for metro cities, ₹3500/night for tier-2 cities.
Meals: ₹800/day per diem for official travel. No receipts needed below ₹500.
Client Entertainment: Up to ₹5000 per event. Director approval required above ₹5000.
Submission deadline: All expense claims within 30 days of incurring the expense.
Rejected claims: Non-compliant expenses are rejected without exception.""",
     "metadata": {"type": "hr_policy", "source": "HR Policy Manual", "label": "Expenses"}},

    {"text": """HR Policy: Code of Conduct and Ethics
Confidentiality: All company data, client information, and trade secrets are strictly confidential.
Conflict of Interest: Employees must disclose any personal interest in company decisions.
Anti-harassment: Zero tolerance for workplace harassment. Report to HR or Ethics hotline anonymously.
Social Media: Do not post confidential company information. Use personal accounts for personal opinions.
Gifts: Employees may not accept gifts > ₹2000 in value from vendors or clients.
Violation consequences: Warning → Final warning → Termination depending on severity.""",
     "metadata": {"type": "hr_policy", "source": "HR Policy Manual", "label": "Code of Conduct"}},

    {"text": """HR Policy: Maternity and Paternity Leave
Maternity Leave: 26 weeks fully paid. Eligible after 80 days of work in preceding 12 months.
Paternity Leave: 15 days paid leave within 6 months of child's birth or adoption.
Adoption Leave: Primary caregiver gets 12 weeks. Secondary caregiver gets 5 days.
Extension: Unpaid leave up to 6 months available post maternity leave.
Creche: Company provides creche facility or ₹3000/month creche allowance for children under 6.
Return to work: Phased return program available — 50% capacity for first month.""",
     "metadata": {"type": "hr_policy", "source": "HR Policy Manual", "label": "Parental Leave"}},

    {"text": """IT Policy: Acceptable Use of Company Assets
Devices: Company laptops are for professional use. Personal use is permitted within limits.
Prohibited: Torrenting, mining cryptocurrency, running personal servers, installing unlicensed software.
Data storage: Store company data on OneDrive/SharePoint. Personal cloud storage (Google Drive personal) is prohibited for company data.
Password policy: Minimum 12 characters, complexity required. Must change every 90 days. No reuse of last 10 passwords.
Screen lock: Auto-lock after 5 minutes of inactivity is mandatory.
Reporting: Report lost/stolen devices to IT within 1 hour. Device will be remotely wiped.""",
     "metadata": {"type": "it_policy", "source": "IT Policy Manual", "label": "IT Acceptable Use"}},

    {"text": """Onboarding Checklist for New Employees
Day 1: Collect ID/address proof, sign employment contract, collect laptop, set up email and Slack.
Week 1: Complete security awareness training, HR portal onboarding, meet your buddy.
Month 1: Complete department orientation, shadow a sprint cycle, set up 1:1 with manager.
Tools access: Jira, Confluence, GitHub, Azure Portal — raise IT ticket for access.
Buddy program: Each new joiner is assigned a buddy from their team for first 90 days.
Probation: 3 months probation. Performance review at end of probation. Confirmation by HR.""",
     "metadata": {"type": "hr_policy", "source": "Onboarding Guide", "label": "Onboarding"}},

    {"text": """Compensation and Benefits Summary
CTC structure: Basic (40%), HRA (20%), Special Allowance (25%), PF (12% of basic), Gratuity, LTA, Medical.
Provident Fund: 12% of basic salary contributed by employee, matched by employer.
Gratuity: Payable after 5 years of service. Formula: 15 days salary per year of service.
LTA: Leave Travel Allowance — 1 month basic salary per year. Reimbursed on actual travel bills.
Health Insurance: ₹10 Lakhs family floater (self + spouse + 2 children). Includes dental and vision.
Life Insurance: 3x annual CTC. Accidental disability cover included.
ESOP: Senior employees (L5+) eligible for ESOP grants. 4-year vesting with 1-year cliff.""",
     "metadata": {"type": "hr_policy", "source": "Compensation Guide", "label": "Compensation"}},
]
