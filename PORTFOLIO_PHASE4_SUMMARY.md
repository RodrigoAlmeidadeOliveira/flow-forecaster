# Phase 4: Portfolio Risk Management - Implementation Summary

**Date:** 2025-11-07
**Status:** ✅ Complete
**Implementation Time:** ~3 hours
**Commits:** 85c63c8, e8b8d9c, 3c742d7, 2f5f87a

---

## 📋 Overview

Phase 4 implements comprehensive portfolio-level risk management capabilities, including:
- Risk identification and tracking
- Probability × Impact assessment (5x5 matrix)
- Risk heatmap visualization
- Automated risk suggestions based on portfolio health
- Risk rollup from projects
- Expected Monetary Value (EMV) calculations
- Intelligent risk alerts

---

## 🗄️ Database Schema

### New Model: `PortfolioRisk`

**File:** `models.py` (lines 470-563)

```python
class PortfolioRisk(Base):
    """Portfolio-level risk tracking and management"""
    __tablename__ = 'portfolio_risks'

    # Identification
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)

    # Risk details
    risk_title = Column(String(200), nullable=False)
    risk_description = Column(Text, nullable=True)
    risk_category = Column(String(50), default='general')

    # Assessment (1-5 scale)
    probability = Column(Integer, nullable=False, default=3)
    impact = Column(Integer, nullable=False, default=3)
    risk_score = Column(Integer, nullable=True)  # prob × impact (1-25)

    # Management
    status = Column(String(50), default='identified')
    owner = Column(String(200), nullable=True)
    mitigation_plan = Column(Text, nullable=True)
    contingency_plan = Column(Text, nullable=True)

    # Costs
    estimated_cost_if_occurs = Column(Float, nullable=True)
    mitigation_cost = Column(Float, nullable=True)

    # Dates
    identified_date = Column(DateTime, default=datetime.utcnow)
    target_resolution_date = Column(DateTime, nullable=True)
    last_reviewed_date = Column(DateTime, nullable=True)
    occurred_date = Column(DateTime, nullable=True)
    closed_date = Column(DateTime, nullable=True)
```

**Risk Categories:**
- `technical` - Technical debt, architecture, implementation risks
- `resource` - Team capacity, skills, availability
- `schedule` - Timeline, dependencies, delays
- `budget` - Cost overruns, funding risks
- `compliance` - Regulatory, legal, policy risks
- `external` - Market, vendor, stakeholder risks
- `strategic` - Business alignment, portfolio direction

**Risk Status Workflow:**
```
identified → assessed → mitigated/accepted → occurred/closed
```

**Risk Levels (based on score):**
- **Critical:** 20-25 (Probability 4-5 × Impact 4-5)
- **High:** 15-19
- **Medium:** 10-14
- **Low:** 5-9
- **Very Low:** 1-4

**Key Methods:**
- `calculate_risk_score()` - Auto-calculate probability × impact
- `get_risk_level()` - Get risk level classification
- `to_dict()` - JSON serialization

---

## 📦 Backend Components

### 1. Portfolio Risk Manager Module

**File:** `portfolio_risk_manager.py` (550 lines)

**Core Classes:**

#### RiskMetrics (Dataclass)
Aggregated risk metrics for a portfolio:
```python
@dataclass
class RiskMetrics:
    total_risks: int
    critical_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int
    very_low_risks: int

    active_risks: int
    mitigated_risks: int
    accepted_risks: int
    occurred_risks: int
    closed_risks: int

    total_risk_score: float
    average_risk_score: float
    weighted_risk_score: float

    total_potential_cost: float
    total_mitigation_cost: float
    expected_monetary_value: float  # EMV

    risks_by_category: Dict[str, int]
    high_risk_categories: List[str]
    high_risk_projects: List[Dict[str, Any]]
```

#### RiskHeatmapData (Dataclass)
5×5 matrix for visualization:
```python
@dataclass
class RiskHeatmapData:
    matrix: List[List[int]]  # 5x5 grid with counts
    risks_by_cell: Dict[Tuple[int, int], List[Dict]]
    total_in_red_zone: int     # Critical (score >= 15)
    total_in_yellow_zone: int  # Medium (score 10-14)
    total_in_green_zone: int   # Low (score <= 9)
```

#### PortfolioRiskManager
Main analysis engine:

**Methods:**
- `calculate_risk_metrics(risks)` - Comprehensive risk aggregation
- `generate_heatmap_data(risks)` - Create 5×5 probability×impact matrix
- `rollup_project_risks(projects)` - Suggest portfolio risks from project patterns
- `generate_risk_alerts(metrics)` - Intelligent alerts based on metrics

**Risk Rollup Logic:**
Analyzes portfolio patterns and suggests risks:
- **Excessive High-Risk Projects** - >30% of projects marked high/critical
- **Resource Capacity Risk** - Total FTE allocation tracking
- **Lack of Project Deadlines** - >40% projects without target dates
- **Portfolio Value Dilution** - >25% projects with low business value

---

## 🔌 API Endpoints

**File:** `app.py` (lines 2964-3196)

### 1. List/Create Portfolio Risks
```
GET/POST /api/portfolios/<portfolio_id>/risks
```

**GET Response:**
```json
[
  {
    "id": 1,
    "portfolio_id": 5,
    "project_id": 12,
    "project_name": "Project Alpha",
    "risk_title": "Resource Shortage",
    "risk_description": "May lose 2 team members next month",
    "risk_category": "resource",
    "probability": 4,
    "impact": 5,
    "risk_score": 20,
    "risk_level": "critical",
    "status": "identified",
    "owner": "Jane Doe",
    "mitigation_plan": "Hire 2 contractors as backup",
    "contingency_plan": "Reduce scope by 20%",
    "estimated_cost_if_occurs": 100000,
    "mitigation_cost": 30000,
    "identified_date": "2025-11-07T10:00:00",
    "target_resolution_date": "2025-11-15T00:00:00",
    "last_reviewed_date": "2025-11-07T10:00:00",
    "occurred_date": null,
    "closed_date": null,
    "created_at": "2025-11-07T10:00:00",
    "updated_at": "2025-11-07T10:00:00",
    "created_by": "John Smith"
  }
]
```

**POST Request:**
```json
{
  "risk_title": "Resource Shortage",
  "risk_description": "May lose 2 team members next month",
  "risk_category": "resource",
  "probability": 4,
  "impact": 5,
  "status": "identified",
  "owner": "Jane Doe",
  "project_id": 12,
  "estimated_cost_if_occurs": 100000,
  "mitigation_cost": 30000,
  "mitigation_plan": "Hire 2 contractors as backup",
  "contingency_plan": "Reduce scope by 20%"
}
```

### 2. Get/Update/Delete Specific Risk
```
GET/PUT/DELETE /api/portfolios/<portfolio_id>/risks/<risk_id>
```

**PUT Request:** Same fields as POST

**Features:**
- Auto-updates `occurred_date` when status = 'occurred'
- Auto-updates `closed_date` when status = 'closed'
- Auto-recalculates risk score
- Updates `last_reviewed_date` on edit

### 3. Risk Analysis
```
GET /api/portfolios/<portfolio_id>/risks/analysis
```

**Response:**
```json
{
  "metrics": {
    "total_risks": 15,
    "by_level": {
      "critical": 2,
      "high": 4,
      "medium": 6,
      "low": 2,
      "very_low": 1
    },
    "by_status": {
      "active": 10,
      "mitigated": 3,
      "accepted": 1,
      "occurred": 0,
      "closed": 1
    },
    "scores": {
      "total": 185,
      "average": 12.3,
      "weighted": 48.5
    },
    "costs": {
      "total_potential": 500000,
      "total_mitigation": 120000,
      "expected_monetary_value": 250000
    },
    "by_category": {
      "resource": 5,
      "technical": 4,
      "schedule": 3,
      "budget": 2,
      "external": 1
    },
    "high_risk_categories": ["resource", "technical"],
    "high_risk_projects": [
      {
        "name": "Project Alpha",
        "project_id": 12,
        "total_risks": 5,
        "critical_risks": 2,
        "high_risks": 2
      }
    ]
  },
  "heatmap": {
    "matrix": [
      [0, 0, 1, 2, 1],
      [0, 1, 2, 3, 2],
      [1, 2, 3, 1, 0],
      [1, 1, 0, 0, 0],
      [0, 0, 0, 0, 0]
    ],
    "risks_by_cell": {
      "5,5": [/* risk objects */],
      "4,5": [/* risk objects */]
    },
    "zones": {
      "red": 6,
      "yellow": 5,
      "green": 4
    }
  },
  "alerts": [
    {
      "type": "critical",
      "severity": "critical",
      "title": "2 Critical Risk(s) Identified",
      "message": "Immediate attention required for 2 critical risk(s) with score >= 20",
      "action": "Review critical risks and implement mitigation plans immediately",
      "icon": "exclamation-triangle"
    }
  ],
  "suggested_risks": [
    {
      "risk_title": "Excessive High-Risk Projects",
      "risk_description": "5 out of 12 projects are marked as high/critical risk",
      "risk_category": "strategic",
      "probability": 4,
      "impact": 5,
      "suggested": true,
      "affected_projects": ["Project A", "Project B", "Project C"]
    }
  ]
}
```

### 4. Suggest Risks (AI)
```
POST /api/portfolios/<portfolio_id>/risks/suggest
```

Analyzes portfolio health and suggests risks to track.

**Response:**
```json
{
  "suggested_risks": [
    {
      "risk_title": "Excessive High-Risk Projects",
      "risk_description": "5 out of 12 projects are marked as high/critical risk",
      "risk_category": "strategic",
      "probability": 4,
      "impact": 5,
      "suggested": true,
      "affected_projects": ["Project A", "Project B"]
    }
  ],
  "count": 1
}
```

---

## 🎨 Frontend Components

### 1. Risk Management Page

**File:** `templates/portfolio_risks.html` (650 lines)

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Navbar: Flow Forecaster | Back | Logout                │
├──────────────┬──────────────────────────────────────────┤
│   Sidebar    │          Main Content                    │
│              │                                          │
│ Portfolio    │  Risk Matrix (5×5 Heatmap)              │
│ Selector     │  ┌────────────────────────────┐         │
│              │  │  P5 │ □  □  □  □  □         │         │
│ Risk Summary │  │  P4 │ □  □  □  □  □         │         │
│ - Total      │  │  P3 │ □  □  □  □  □         │         │
│ - By Level   │  │  P2 │ □  □  □  □  □         │         │
│ - By Status  │  │  P1 │ □  □  □  □  □         │         │
│ - EMV        │  │     │ I1 I2 I3 I4 I5        │         │
│              │  └────────────────────────────┘         │
│ Alerts       │                                          │
│ - Critical   │  Risk List Table                        │
│ - Warnings   │  ┌────────────────────────────┐         │
│              │  │ Title │ Cat │ P │ I │ Score│         │
│              │  │ Risk1 │ ... │...│...│ 20   │         │
│              │  │ Risk2 │ ... │...│...│ 15   │         │
│              │  └────────────────────────────┘         │
└──────────────┴──────────────────────────────────────────┘
```

**Key Features:**
- Color-coded risk matrix cells (critical=dark red, high=red, medium=orange, low=yellow, very-low=green)
- Click heatmap cells to see risks in that cell
- Comprehensive risk table with sorting
- Add/Edit risk modal with full form
- Bootstrap 5 dark theme
- Responsive design

### 2. Risk Management JavaScript

**File:** `static/js/portfolio_risks.js` (700 lines)

**Key Functions:**

#### Data Loading
```javascript
loadPortfolios()              // Load portfolio list
selectPortfolio(portfolioId)  // Load portfolio risks
loadRisks()                   // Fetch all risks
loadRiskAnalysis()           // Fetch analysis data
loadPortfolioProjects()      // Load projects for dropdown
```

#### Visualization
```javascript
renderRiskSummary(metrics)   // Render metrics panel
renderRiskHeatmap(heatmap)   // Render 5×5 matrix
renderRisksList(risks)       // Render risk table
renderAlerts(alerts)         // Render alert boxes
showCellRisks(prob, impact)  // Show risks in matrix cell
```

#### CRUD Operations
```javascript
showAddRiskModal()           // Open blank modal
editRisk(riskId)             // Load and edit risk
saveRisk()                   // Create or update
deleteRisk(riskId)           // Delete with confirmation
```

#### AI Features
```javascript
suggestRisks()               // Get AI-suggested risks
setupRiskCalculator()        // Auto-calculate risk score
```

**Auto Risk Score Calculation:**
Updates score in real-time as user changes probability/impact:
```javascript
score = probability × impact
```

Updates cell color based on score:
- 20-25: Critical (dark red)
- 15-19: High (red)
- 10-14: Medium (orange)
- 5-9: Low (yellow)
- 1-4: Very Low (green)

### 3. Navigation Integration

**File:** `templates/index.html` (lines 184-188)

Added "Risks" menu item between "Dashboard" and "Documentação":
```html
<li class="nav-item">
  <a class="nav-link" href="/portfolio/risks">
    <i class="fas fa-shield-alt"></i> Risks
  </a>
</li>
```

### 4. Route Handler

**File:** `app.py` (lines 3471-3486)

```python
@app.route('/portfolio/risks')
@login_required
def portfolio_risks_page():
    """Render the Portfolio Risk Management page"""
    return render_template('portfolio_risks.html')
```

---

## 🎯 Use Cases

### Use Case 1: Identify and Track Risks

**Scenario:** Portfolio manager wants to track a resource shortage risk

**Steps:**
1. Navigate to Portfolio → Risks
2. Select portfolio from dropdown
3. Click "Add Risk"
4. Fill in form:
   - Title: "Senior Developer Leaving"
   - Category: Resource
   - Probability: 4 (High)
   - Impact: 5 (Very High)
   - Score: 20 (Auto-calculated)
   - Project: "Project Alpha"
   - Owner: "Jane Doe"
   - Mitigation: "Hire replacement ASAP, knowledge transfer"
   - Contingency: "Extend timeline by 4 weeks"
   - Cost if occurs: R$ 150,000
   - Mitigation cost: R$ 40,000
5. Click "Save Risk"

**Result:**
- Risk appears in table with Critical badge
- Risk appears in heatmap at P=4, I=5 (dark red cell)
- Alert shown: "1 Critical Risk Identified"
- EMV increases by R$ 120,000 (4/5 × 150k)

### Use Case 2: Analyze Portfolio Risk Profile

**Scenario:** Executive wants to see overall portfolio risk exposure

**Steps:**
1. Navigate to Portfolio → Risks
2. Select portfolio
3. View automatically:
   - Risk Summary: 15 total, 2 critical, 4 high
   - Risk Matrix: Visual heatmap showing concentration
   - EMV: R$ 250,000
   - High-risk projects: Project Alpha (2 critical, 2 high)
   - Alerts: "2 Critical Risks Require Attention"

**Result:**
Executive sees:
- Most risks are in resource and technical categories
- 2 critical risks need immediate action
- Expected loss from risks: R$ 250k
- Project Alpha is highest risk project

### Use Case 3: Get AI-Suggested Risks

**Scenario:** Portfolio manager wants proactive risk identification

**Steps:**
1. Navigate to Portfolio → Risks
2. Select portfolio with 12 projects (5 marked high-risk)
3. Click "Suggest Risks"
4. System analyzes and suggests:
   - "Excessive High-Risk Projects" (P=4, I=5)
   - "Resource Capacity Risk" (P=3, I=4)
5. Manager clicks "Yes" to add suggested risks

**Result:**
- 2 new risks auto-added with "identified" status
- Manager can now assign owners and create mitigation plans

### Use Case 4: Track Risk Over Time

**Scenario:** Risk owner implements mitigation and closes risk

**Steps:**
1. Edit risk: "Senior Developer Leaving"
2. Update status: "Identified" → "Mitigated"
3. Add note: "Hired replacement, 2-week overlap completed"
4. Later: Risk didn't occur
5. Update status: "Mitigated" → "Closed"

**Result:**
- `last_reviewed_date` updated automatically
- `closed_date` set to current time
- Risk moves from "Active" to "Closed" in summary
- EMV decreases (risk no longer counted)

---

## 📊 Analytics & Insights

### Expected Monetary Value (EMV)

**Formula:**
```
EMV = Σ (Probability/5 × Estimated Cost if Occurs)
```

**Example:**
```
Risk A: P=4, Cost=R$ 100k → EMV = 0.8 × 100k = R$ 80k
Risk B: P=2, Cost=R$ 50k  → EMV = 0.4 × 50k  = R$ 20k
Total EMV = R$ 100k
```

**Interpretation:**
- Portfolio expected to lose R$ 100k due to risks
- Used for:
  - Budget planning (add contingency = EMV)
  - Prioritization (focus on high EMV risks)
  - Mitigation ROI (mitigation cost vs EMV reduction)

### Risk Concentration Analysis

**By Level:**
- Critical: Immediate executive escalation
- High: Weekly review in portfolio meetings
- Medium: Bi-weekly monitoring
- Low: Monthly check-in
- Very Low: Quarterly review

**By Category:**
- Identifies systemic issues (e.g., all risks are "resource")
- Enables specialized interventions (hire contractors, training, etc.)

**By Project:**
- Identifies troubled projects
- Triggers deep-dive analysis
- May trigger project pause/cancellation

### Intelligent Alerts

**Alert Types:**
1. **Critical Risk Alert** - Any risk with score >= 20
2. **High-Risk Projects** - Projects with multiple high/critical risks
3. **High EMV** - Total EMV > R$ 100k
4. **Many Active Risks** - >10 unresolved risks
5. **Category Concentration** - High risks clustered in one category

---

## 🧪 Testing

**Manual Test Scenarios:**

### Test 1: Create Risk
1. Navigate to /portfolio/risks
2. Select a portfolio
3. Click "Add Risk"
4. Fill form and save
5. ✅ Risk appears in table and heatmap

### Test 2: Risk Score Calculation
1. Create risk with P=5, I=4
2. ✅ Score auto-calculates to 20
3. ✅ Cell shows "Critical" badge
4. Change P to 3
5. ✅ Score updates to 12
6. ✅ Cell shows "Medium" badge

### Test 3: Risk Analysis
1. Create 5 risks with varying levels
2. View summary panel
3. ✅ Counts match by level
4. ✅ EMV calculated correctly
5. ✅ Heatmap shows correct distribution

### Test 4: Suggest Risks
1. Create portfolio with 10 projects
2. Mark 4 as high-risk
3. Click "Suggest Risks"
4. ✅ Suggestion: "Excessive High-Risk Projects"
5. Accept suggestion
6. ✅ Risk created automatically

### Test 5: Edit Risk
1. Edit existing risk
2. Change probability from 3 to 5
3. Update status to "mitigated"
4. Save
5. ✅ Risk score updated
6. ✅ last_reviewed_date updated
7. ✅ Status changed in summary

### Test 6: Delete Risk
1. Delete a critical risk
2. Confirm deletion
3. ✅ Risk removed from table
4. ✅ Risk removed from heatmap
5. ✅ Summary counts updated
6. ✅ EMV recalculated

---

## 🚀 Benefits

### For Portfolio Managers
- **Visibility** - See all risks in one place
- **Prioritization** - Focus on critical/high risks first
- **Proactive** - AI suggests risks you might miss
- **Data-Driven** - EMV helps justify mitigation budget

### For Executives
- **Dashboard** - Quick portfolio risk snapshot
- **Metrics** - Understand risk exposure (EMV)
- **Alerts** - Notified of critical situations
- **Trends** - Track risk reduction over time

### For Risk Owners
- **Accountability** - Clear ownership assigned
- **Guidance** - Mitigation/contingency templates
- **Progress** - Status tracking (identified → closed)

### For Stakeholders
- **Transparency** - Risks documented and visible
- **Confidence** - Proactive risk management
- **Context** - Understand why projects delayed/over-budget

---

## 🔮 Future Enhancements

### Short Term (Next Sprint)
- [ ] Risk history/audit log
- [ ] Email notifications for critical risks
- [ ] Risk templates by category
- [ ] Export to PDF/Excel

### Medium Term (Next Month)
- [ ] Risk dependencies (Risk A triggers Risk B)
- [ ] Monte Carlo simulation with risks
- [ ] Risk burn-down chart
- [ ] Risk velocity tracking

### Long Term (Next Quarter)
- [ ] Machine learning risk prediction
- [ ] Natural language risk extraction from docs
- [ ] Automatic risk status updates from project data
- [ ] Risk correlation analysis

---

## 📚 References

### Risk Management Standards
- **PMI PMBOK** - Project Risk Management chapter
- **ISO 31000** - Risk Management standard
- **PRINCE2** - Risk theme

### Risk Assessment Methods
- **Probability × Impact Matrix** - Used in this implementation
- **Monte Carlo Analysis** - Future enhancement
- **Risk Burndown** - Future enhancement

### Cost of Risk
- **Expected Monetary Value (EMV)** - Decision tree analysis
- **Risk-Adjusted NPV** - Project valuation
- **Contingency Reserve** - Budget planning

---

## 📝 Changelog

### 2025-11-07 - Phase 4 Complete

**Added:**
- PortfolioRisk database model
- Portfolio Risk Manager module
- 4 API endpoints for risk CRUD and analysis
- Full-featured risk management UI
- 5×5 risk matrix heatmap
- AI-powered risk suggestions
- Expected Monetary Value calculations
- Intelligent alerts system
- Navigation integration

**Fixed:**
- models.py indentation errors
- Corrected to_dict() methods in PortfolioProject and CoDTrainingDataset

**Commits:**
- `85c63c8` - PortfolioRisk model
- `e8b8d9c` - API endpoints and risk manager
- `3c742d7` - UI and navigation
- `2f5f87a` - Fix models.py errors

---

## ✅ Phase 4 Completion Checklist

- [x] Database schema designed and tested
- [x] PortfolioRisk model with methods
- [x] Portfolio Risk Manager module
- [x] Risk metrics calculation
- [x] Risk heatmap generation
- [x] Risk rollup logic
- [x] Intelligent alerts
- [x] 4 API endpoints (CRUD + analysis)
- [x] Full-featured UI with heatmap
- [x] AI-suggested risks
- [x] Navigation integration
- [x] Code compiles without errors
- [x] Manual testing passed
- [x] Documentation complete
- [x] All changes committed and pushed

**Phase 4 Status: ✅ COMPLETE and PRODUCTION-READY**

---

**Next Phase:** Phase 5 - Portfolio Optimization (Linear Programming, What-If Scenarios)
