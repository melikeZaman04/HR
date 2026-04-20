"""
Seed Data Generator for AI Decision Ecosystem Engine

Generates diverse, realistic scenarios across all 5 classification types
to provide a robust training/testing dataset.
"""
import random
from dataclasses import dataclass
from typing import Generator


@dataclass
class ScenarioSeed:
    """A seed scenario for data generation."""
    name: str
    description: str
    budget_million_usd: float
    expected_roi_percent: float
    risk_level: int
    team_readiness: int
    expected_type: str  # For validation


# Scenario templates by category
SCENARIO_TEMPLATES = {
    "high_growth": [
        {
            "names": [
                "AI Platform Expansion",
                "Cloud Infrastructure Investment",
                "Global Market Entry",
                "Digital Transformation Initiative",
                "E-commerce Platform Launch",
                "Mobile App Ecosystem",
                "Data Analytics Platform",
                "IoT Product Line",
            ],
            "descriptions": [
                "Major investment to capture emerging market opportunity",
                "Strategic expansion into high-growth sector",
                "Platform development for rapid scaling",
                "Technology investment for market leadership",
            ],
            "budget_range": (15, 50),
            "roi_range": (35, 80),
            "risk_range": (4, 7),
            "readiness_range": (6, 9),
        }
    ],
    "cost_optimization": [
        {
            "names": [
                "Process Automation",
                "Legacy System Migration",
                "Operational Efficiency Program",
                "Supply Chain Optimization",
                "Energy Cost Reduction",
                "Workforce Efficiency Initiative",
                "Vendor Consolidation",
                "Infrastructure Rightsizing",
            ],
            "descriptions": [
                "Reduce operational costs through automation",
                "Streamline processes for efficiency gains",
                "Optimize resource utilization and spending",
                "Cost reduction through technology modernization",
            ],
            "budget_range": (1, 8),
            "roi_range": (5, 20),
            "risk_range": (1, 4),
            "readiness_range": (7, 10),
        }
    ],
    "team_expansion": [
        {
            "names": [
                "Engineering Team Scale-up",
                "New Department Creation",
                "Talent Acquisition Program",
                "Regional Office Expansion",
                "R&D Team Building",
                "Customer Success Team",
                "DevOps Capability Building",
                "AI/ML Team Formation",
            ],
            "descriptions": [
                "Build team capabilities for future growth",
                "Critical hiring to address skill gaps",
                "Team expansion to meet demand",
                "Invest in human capital for strategic goals",
            ],
            "budget_range": (5, 20),
            "roi_range": (15, 35),
            "risk_range": (3, 6),
            "readiness_range": (1, 4),  # Low readiness = team expansion needed
        }
    ],
    "strategic_pivot": [
        {
            "names": [
                "Business Model Transformation",
                "Technology Stack Overhaul",
                "Market Repositioning",
                "Platform Re-architecture",
                "Product Portfolio Restructure",
                "Channel Strategy Shift",
                "Geographic Refocus",
                "Core Technology Migration",
            ],
            "descriptions": [
                "Major strategic direction change",
                "Fundamental business transformation",
                "High-risk, high-reward pivot",
                "Complete transformation of operations",
            ],
            "budget_range": (10, 40),
            "roi_range": (25, 60),
            "risk_range": (7, 10),  # High risk = strategic pivot
            "readiness_range": (3, 7),
        }
    ],
    "maintenance": [
        {
            "names": [
                "Annual System Updates",
                "Security Patch Deployment",
                "Infrastructure Maintenance",
                "Compliance Updates",
                "Performance Optimization",
                "Bug Fix Release",
                "Documentation Refresh",
                "Monitoring Enhancement",
            ],
            "descriptions": [
                "Routine maintenance and updates",
                "Incremental improvements to existing systems",
                "Steady-state operational enhancement",
                "Low-risk maintenance activities",
            ],
            "budget_range": (0.5, 5),
            "roi_range": (5, 15),
            "risk_range": (1, 3),
            "readiness_range": (7, 10),
        }
    ],
}

# Industry/domain prefixes for variety
INDUSTRY_PREFIXES = [
    "Healthcare", "FinTech", "E-commerce", "Manufacturing", "Logistics",
    "Education", "Media", "Energy", "Retail", "Telecom", "Insurance",
    "Real Estate", "Automotive", "Pharma", "Gaming"
]


def generate_scenario(category: str, include_industry: bool = True) -> ScenarioSeed:
    """Generate a random scenario for a given category."""
    templates = SCENARIO_TEMPLATES[category]
    template = random.choice(templates)
    
    name = random.choice(template["names"])
    if include_industry and random.random() > 0.5:
        name = f"{random.choice(INDUSTRY_PREFIXES)} {name}"
    
    return ScenarioSeed(
        name=name,
        description=random.choice(template["descriptions"]),
        budget_million_usd=round(random.uniform(*template["budget_range"]), 1),
        expected_roi_percent=round(random.uniform(*template["roi_range"]), 1),
        risk_level=random.randint(*template["risk_range"]),
        team_readiness=random.randint(*template["readiness_range"]),
        expected_type=category,
    )


def generate_dataset(
    total_scenarios: int = 100,
    distribution: dict[str, float] | None = None,
) -> Generator[ScenarioSeed, None, None]:
    """
    Generate a balanced dataset of scenarios.
    
    Args:
        total_scenarios: Total number of scenarios to generate
        distribution: Optional dict of category -> proportion (must sum to 1.0)
                     Defaults to equal distribution.
    
    Yields:
        ScenarioSeed objects
    """
    if distribution is None:
        distribution = {
            "high_growth": 0.25,
            "cost_optimization": 0.20,
            "team_expansion": 0.20,
            "strategic_pivot": 0.15,
            "maintenance": 0.20,
        }
    
    for category, proportion in distribution.items():
        count = int(total_scenarios * proportion)
        for _ in range(count):
            yield generate_scenario(category)


def generate_edge_cases() -> Generator[ScenarioSeed, None, None]:
    """Generate edge case scenarios for testing."""
    edge_cases = [
        # Minimum values
        ScenarioSeed(
            name="Minimal Investment Test",
            description="Testing minimum budget scenario",
            budget_million_usd=0.1,
            expected_roi_percent=1.0,
            risk_level=1,
            team_readiness=1,
            expected_type="maintenance",
        ),
        # Maximum values
        ScenarioSeed(
            name="Maximum Scale Project",
            description="Testing maximum values scenario",
            budget_million_usd=100.0,
            expected_roi_percent=200.0,
            risk_level=10,
            team_readiness=10,
            expected_type="strategic_pivot",
        ),
        # High ROI with low budget
        ScenarioSeed(
            name="High Efficiency Initiative",
            description="Low investment, high return opportunity",
            budget_million_usd=2.0,
            expected_roi_percent=80.0,
            risk_level=3,
            team_readiness=8,
            expected_type="cost_optimization",
        ),
        # Low team readiness with high budget
        ScenarioSeed(
            name="Talent Gap Challenge",
            description="Major investment hampered by team readiness",
            budget_million_usd=30.0,
            expected_roi_percent=40.0,
            risk_level=5,
            team_readiness=2,
            expected_type="team_expansion",
        ),
        # Mixed signals - let classifier decide
        ScenarioSeed(
            name="Ambiguous Strategy Decision",
            description="Scenario with conflicting indicators",
            budget_million_usd=15.0,
            expected_roi_percent=25.0,
            risk_level=5,
            team_readiness=5,
            expected_type="maintenance",  # Balanced = likely maintenance
        ),
    ]
    yield from edge_cases


def print_sample_dataset(count: int = 20):
    """Print a sample dataset for review."""
    print(f"\n{'='*80}")
    print(f"SAMPLE DATASET ({count} scenarios)")
    print(f"{'='*80}\n")
    
    for i, scenario in enumerate(generate_dataset(count), 1):
        print(f"{i:3}. [{scenario.expected_type:18}] {scenario.name}")
        print(f"     Budget: ${scenario.budget_million_usd}M | ROI: {scenario.expected_roi_percent}% | "
              f"Risk: {scenario.risk_level}/10 | Team: {scenario.team_readiness}/10")
        print()


if __name__ == "__main__":
    print_sample_dataset(20)
    print("\nEdge Cases:")
    print("-" * 40)
    for scenario in generate_edge_cases():
        print(f"- {scenario.name}: {scenario.expected_type}")
