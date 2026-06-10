from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

content = """
TESLA INC - ANNUAL REPORT 2024

EXECUTIVE SUMMARY
Tesla Inc reported record revenues for fiscal year 2024.
Total revenue reached $97.7 billion, up 19% from 2023.
Net income was $15.0 billion, up 19% year over year.

REVENUE BREAKDOWN
- Automotive revenue: $82.4 billion
- Energy generation and storage: $9.4 billion
- Services and other: $5.9 billion

KEY METRICS
- Total vehicles delivered: 1.81 million units
- Gross margin: 17.9%
- Free cash flow: $3.6 billion
- Cash and equivalents: $29.1 billion

MARKET POSITION
Tesla remains the leading EV manufacturer in the US with 55% market share.
Global EV market share stands at 14.6%.
Main competitors: BYD, Volkswagen, GM, Ford.

RISKS
- Increased competition from Chinese EV makers especially BYD
- Raw material costs for lithium and cobalt
- Regulatory changes in key markets
- Elon Musk's involvement in other ventures causing distraction

FUTURE OUTLOOK
Tesla plans to launch the affordable Model 2 at $25,000 price point.
Cybertruck production ramping up to 250,000 units per year.
Full Self Driving (FSD) expected to reach Level 4 autonomy by 2025.
New Gigafactories planned in India and Southeast Asia.
"""

for line in content.split('\n'):
    pdf.cell(0, 8, line, ln=True)

pdf.output("/home/ubuntu/agentops/tesla_report_2024.pdf")
print("PDF created successfully!")
