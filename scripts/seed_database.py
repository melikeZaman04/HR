"""
Database Seeder - Populates database with diverse test scenarios.

Usage:
    python scripts/seed_database.py --count 100
    python scripts/seed_database.py --count 200 --simulate
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.seed_data_generator import generate_dataset, generate_edge_cases


def seed_via_api(count: int, run_simulations: bool = False, base_url: str = "http://localhost:8000"):
    """Seed database using the API endpoints."""
    import requests
    
    print(f"\n🌱 Seeding database with {count} scenarios...")
    print(f"   API: {base_url}")
    print(f"   Simulations: {'Yes' if run_simulations else 'No'}\n")
    
    # Check API health
    try:
        health = requests.get(f"{base_url}/health", timeout=5)
        if health.status_code != 200:
            print("❌ API not healthy!")
            return
    except requests.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print("✅ API is healthy\n")
    
    # Track statistics
    stats = {
        "created": 0,
        "simulated": 0,
        "errors": 0,
        "by_type": {},
    }
    
    scenarios = list(generate_dataset(count))
    scenarios.extend(generate_edge_cases())
    
    total = len(scenarios)
    
    for i, scenario in enumerate(scenarios, 1):
        # Create scenario
        payload = {
            "name": scenario.name,
            "description": scenario.description,
            "budget_million_usd": scenario.budget_million_usd,
            "expected_roi_percent": scenario.expected_roi_percent,
            "risk_level": scenario.risk_level,
            "team_readiness": scenario.team_readiness,
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/scenarios",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                scenario_id = data["scenario_id"]
                stats["created"] += 1
                stats["by_type"][scenario.expected_type] = stats["by_type"].get(scenario.expected_type, 0) + 1
                
                # Run simulation if requested
                if run_simulations:
                    sim_response = requests.post(
                        f"{base_url}/api/v1/scenarios/{scenario_id}/simulate",
                        timeout=30
                    )
                    if sim_response.status_code == 200:
                        stats["simulated"] += 1
                        sim_data = sim_response.json()
                        decision = sim_data["final_decision"]
                        print(f"  [{i:3}/{total}] ✅ #{scenario_id} {scenario.name[:30]:30} → {decision}")
                    else:
                        print(f"  [{i:3}/{total}] ⚠️  #{scenario_id} Created but simulation failed")
                else:
                    print(f"  [{i:3}/{total}] ✅ #{scenario_id} {scenario.name[:40]}")
            else:
                stats["errors"] += 1
                print(f"  [{i:3}/{total}] ❌ Failed: {response.text[:50]}")
                
        except requests.RequestException as e:
            stats["errors"] += 1
            print(f"  [{i:3}/{total}] ❌ Error: {e}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 SEEDING COMPLETE")
    print(f"{'='*60}")
    print(f"   Created:   {stats['created']}")
    print(f"   Simulated: {stats['simulated']}")
    print(f"   Errors:    {stats['errors']}")
    print(f"\n   By Type:")
    for type_name, count in sorted(stats["by_type"].items()):
        print(f"      {type_name:20}: {count}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Seed database with test scenarios")
    parser.add_argument("--count", type=int, default=100, help="Number of scenarios to generate")
    parser.add_argument("--simulate", action="store_true", help="Also run simulations for each scenario")
    parser.add_argument("--url", type=str, default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    seed_via_api(
        count=args.count,
        run_simulations=args.simulate,
        base_url=args.url
    )


if __name__ == "__main__":
    main()
