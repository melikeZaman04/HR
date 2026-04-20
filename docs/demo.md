# 3-Minute Demo Script

This script demonstrates the complete workflow of the AI Decision Ecosystem Engine.

**Prerequisites:**
- Docker and Docker Compose installed
- Terminal/PowerShell open in project directory

## Step 1: Start the Application (1 min)

### Linux/macOS:
```bash
make start
```

### Windows (PowerShell):
```powershell
.\start.ps1
```

**Expected output:**
```
Starting containers...
Waiting for db to be healthy...
Running migrations...
API docs: http://localhost:8000/docs
```

The application is now running at `http://localhost:8000`.

---

## Step 2: Open Swagger UI (30 sec)

Open browser to: **http://localhost:8000/docs**

You'll see the interactive API documentation with all endpoints listed.

---

## Step 3: Create a Scenario (1 min)

In Swagger UI, click on `POST /api/v1/scenarios` and expand it.

Click "Try it out" and enter this JSON in the request body:

```json
{
  "name": "Southeast Asia Expansion",
  "description": "Enter Southeast Asian market with new product line",
  "budget_million_usd": 8.5,
  "expected_roi_percent": 35.0,
  "risk_level": 6,
  "team_readiness": 8
}
```

Click "Execute".

**Expected response:**
```json
{
  "scenario_id": 1
}
```

**Note the scenario_id (should be 1 for first scenario).**

---

## Step 4: Run Simulation (1 min)

Click on `POST /api/v1/scenarios/{id}/simulate`.

Click "Try it out" and enter: `1` for the scenario_id.

Click "Execute".

**Expected response:**
```json
{
  "scenario_id": 1,
  "agent_outputs": [
    {
      "agent_name": "CEO",
      "score": 70,
      "rationale": "Strategic fit 35% with market risk 0.6 yields strategic score 70."
    },
    {
      "agent_name": "CFO",
      "score": 61,
      "rationale": "ROI 41.2% with risk factor 0.6 yields financial score 61."
    },
    {
      "agent_name": "HR",
      "score": 72,
      "rationale": "Team readiness 8/10 with 8 hires needed and 3 months to readiness yields HR score 72."
    }
  ],
  "final_score": 67.67,
  "final_decision": "REVISE"
}
```

**Decision interpretation:**
- Average score: 67.67
- Since 50 ≤ 67.67 < 75: Decision = **REVISE**
- Recommendation: Study feedback and resubmit with improvements

---

## Step 5: Retrieve Simulation Results (1 min)

### Option A: Get Scenario Details
Click on `GET /api/v1/scenarios/{id}`.

Enter scenario_id: `1`

You'll see the scenario metadata and creation timestamp.

### Option B: Get Simulation with All Outputs
Click on `GET /api/v1/scenarios/{id}/simulation`.

Enter scenario_id: `1`

You'll see:
- Full scenario record
- All agent outputs with scores and rationale
- Final aggregated score and decision

### Option C: List All Scenarios
Click on `GET /api/v1/scenarios`.

You can paginate with `limit` and `offset` parameters (default: limit=20, offset=0).

---

## Alternative: Using curl

Instead of Swagger, you can use curl from terminal:

```bash
# 1. Create scenario
SCENARIO=$(curl -s -X POST http://localhost:8000/api/v1/scenarios \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Launch",
    "description": "Q2 product release",
    "budget_million_usd": 3.0,
    "expected_roi_percent": 25.0,
    "risk_level": 4,
    "team_readiness": 9
  }')

echo "Created: $SCENARIO"
SCENARIO_ID=$(echo $SCENARIO | grep -o '"scenario_id":[0-9]*' | grep -o '[0-9]*')

# 2. Run simulation
curl -s -X POST http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/simulate | jq .

# 3. Get simulation results
curl -s http://localhost:8000/api/v1/scenarios/$SCENARIO_ID/simulation | jq .
```

---

## Alternative: Using Python

```python
import requests
import json

base_url = "http://localhost:8000/api/v1"

# 1. Create scenario
scenario_data = {
    "name": "Digital Transformation",
    "description": "Cloud infrastructure modernization",
    "budget_million_usd": 12.0,
    "expected_roi_percent": 50.0,
    "risk_level": 5,
    "team_readiness": 7,
}

scenario = requests.post(f"{base_url}/scenarios", json=scenario_data).json()
scenario_id = scenario["scenario_id"]
print(f"✓ Created scenario {scenario_id}\n")

# 2. Run simulation
simulation = requests.post(f"{base_url}/scenarios/{scenario_id}/simulate").json()
print(f"Final Decision: {simulation['final_decision']} (score: {simulation['final_score']})\n")

# 3. Display agent opinions
for agent in simulation["agent_outputs"]:
    print(f"{agent['agent_name']}: {agent['score']}")
    print(f"  → {agent['rationale']}\n")

# 4. Get full results
full_results = requests.get(f"{base_url}/scenarios/{scenario_id}/simulation").json()
print(f"Final result stored with timestamp: {full_results['scenario']['created_at']}")
```

---

## Testing Edge Cases

### Low Score Scenario (Should result in REJECT)

```json
{
  "name": "Risky Venture",
  "description": "Uncertain market with low ROI",
  "budget_million_usd": 15.0,
  "expected_roi_percent": 5.0,
  "risk_level": 9,
  "team_readiness": 2
}
```

Expected: Low scores from all agents → REJECT decision

### High Score Scenario (Should result in APPROVE)

```json
{
  "name": "Safe Bet",
  "description": "Clear market opportunity, expert team",
  "budget_million_usd": 2.0,
  "expected_roi_percent": 80.0,
  "risk_level": 2,
  "team_readiness": 10
}
```

Expected: High scores from all agents → APPROVE decision

---

## Stopping the Application

### Linux/macOS:
```bash
make stop
```

### Windows (PowerShell):
```powershell
.\stop.ps1
```

This runs `docker compose down` and stops all containers.

---

## Summary

You've now:
1. ✓ Started the application with Docker Compose
2. ✓ Created a scenario with normalized inputs
3. ✓ Ran multi-agent simulation
4. ✓ Retrieved results with agent reasoning
5. ✓ Verified decision logic (CEO/CFO/HR scoring → aggregation)

The system demonstrates clean architecture, deterministic agent logic, and complete API coverage.
