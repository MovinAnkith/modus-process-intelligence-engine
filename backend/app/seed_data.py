"""
Generates ~100 real retail/e-commerce business processes across 10
categories. This is deliberately structured (category x process) rather
than a flat hand-typed list, so it reads as genuine domain research and so
new categories/processes can be appended without restructuring anything.

Run with: python -m app.seed_data
"""
from app.database import SessionLocal, Base, engine
from app import models
from app.services.analysis_pipeline import analyze_process

PROCESS_TAXONOMY = {
    "Merchandising": [
        "Demand Forecasting",
        "Assortment Planning",
        "Price Optimization",
        "Promotion Planning",
        "New Product Introduction",
        "Vendor Negotiation",
        "Category Performance Review",
        "Markdown Management",
        "Private Label Development",
        "Competitive Price Monitoring",
    ],
    "Inventory & Supply Chain": [
        "Inventory Replenishment",
        "Warehouse Slotting",
        "Supplier Onboarding",
        "Purchase Order Management",
        "Stock Reconciliation",
        "Demand-Supply Matching",
        "Safety Stock Calculation",
        "Vendor Performance Scorecarding",
        "Cross-Docking Coordination",
        "Seasonal Inventory Planning",
    ],
    "Order Management": [
        "Order Capture & Validation",
        "Payment Processing",
        "Fraud Screening",
        "Order Status Tracking",
        "Backorder Management",
        "Order Cancellation Handling",
        "Split Shipment Coordination",
        "Gift Wrapping & Customization Requests",
        "Subscription Order Management",
        "B2B Bulk Order Processing",
    ],
    "Fulfillment & Logistics": [
        "Pick, Pack & Ship",
        "Last-Mile Delivery Routing",
        "Carrier Selection & Rate Shopping",
        "Returns Processing",
        "Reverse Logistics",
        "Delivery Exception Handling",
        "Warehouse Labor Scheduling",
        "Cross-Border Shipping Compliance",
        "Same-Day Delivery Coordination",
        "Damaged Goods Claims Processing",
    ],
    "Customer Service": [
        "Customer Inquiry Handling",
        "Complaint Resolution",
        "Live Chat Support",
        "Returns & Refund Approval",
        "Loyalty Program Support",
        "Product Q&A Management",
        "Escalation Management",
        "Customer Satisfaction Surveying",
        "Multi-Channel Support Routing",
        "Warranty Claims Processing",
    ],
    "Marketing & Sales": [
        "Email Campaign Management",
        "Personalized Product Recommendations",
        "Social Media Advertising",
        "SEO & Content Optimization",
        "Customer Segmentation",
        "A/B Testing of Campaigns",
        "Influencer Partnership Management",
        "Loyalty & Rewards Program Design",
        "Cart Abandonment Recovery",
        "Seasonal Campaign Planning",
    ],
    "Finance & Accounting": [
        "Accounts Payable Processing",
        "Accounts Receivable Management",
        "Revenue Recognition",
        "Financial Close & Reporting",
        "Budget vs Actual Analysis",
        "Tax Compliance Filing",
        "Vendor Invoice Reconciliation",
        "Cash Flow Forecasting",
        "Chargeback Management",
        "Cost Allocation Across Channels",
    ],
    "HR & Workforce": [
        "Seasonal Staff Recruitment",
        "Employee Onboarding",
        "Shift Scheduling",
        "Performance Review Management",
        "Payroll Processing",
        "Training & Certification Tracking",
        "Employee Attrition Analysis",
        "Workforce Demand Planning",
        "Benefits Administration",
        "Compliance & Safety Training",
    ],
    "IT & Digital": [
        "E-commerce Platform Uptime Monitoring",
        "Website Personalization Engine Management",
        "Product Catalog Data Management",
        "Search & Discovery Optimization",
        "API Integration Management",
        "Data Privacy & Compliance Monitoring",
        "Mobile App Feature Rollout",
        "Cybersecurity Threat Monitoring",
        "Master Data Management",
        "Digital Payment Gateway Management",
    ],
    "Store Operations": [
        "In-Store Inventory Counts",
        "Store Layout & Planogram Compliance",
        "Point-of-Sale Transaction Handling",
        "Loss Prevention & Shrinkage Monitoring",
        "Click-and-Collect Fulfillment",
        "Store Opening/Closing Procedures",
        "Visual Merchandising Execution",
        "In-Store Customer Queue Management",
        "Store-Level Sales Reporting",
        "Facilities Maintenance Scheduling",
    ],
}


def generate_processes():
    """Flattens the taxonomy into (category, name) tuples - 100 total."""
    return [
        (category, name)
        for category, names in PROCESS_TAXONOMY.items()
        for name in names
    ]


def seed(organization_name="NorthStar Retail Group", industry="Retail / E-commerce", run_analysis=True):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        org = db.query(models.Organization).filter_by(name=organization_name).first()
        if not org:
            org = models.Organization(name=organization_name, industry=industry)
            db.add(org)
            db.commit()
            db.refresh(org)

        processes = generate_processes()
        print(f"Seeding {len(processes)} processes for {organization_name}...")

        for i, (category, name) in enumerate(processes, start=1):
            existing = db.query(models.Process).filter_by(
                organization_id=org.id, name=name
            ).first()
            if existing:
                continue

            process = models.Process(
                organization_id=org.id,
                name=name,
                category=category,
                description=f"{name} process within {category} for {organization_name}.",
            )
            db.add(process)
            db.commit()
            db.refresh(process)

            if run_analysis:
                analyze_process(db, process)
                print(f"  [{i}/{len(processes)}] Analyzed: {name}")
            else:
                print(f"  [{i}/{len(processes)}] Created (not analyzed): {name}")

        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
