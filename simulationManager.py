"""
Sprint 1 Implementation: Multi-Simulation Foundation
This file contains the core infrastructure to run multiple settlements simultaneously.
"""

import random
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt


class SimulationManager:
    """
    Orchestrates multiple settlements advancing in lockstep.
    This is the central coordinator for the entire simulation.
    """

    def __init__(self, world_map):
        self.world_map = world_map
        self.current_year = 1000  # Starting year (medieval baseline)
        self.current_season = "spring"
        self.total_seasons_passed = 0

        # Settlement registry
        self.settlement_registry = {}  # settlement_id -> metadata dict
        self.next_settlement_id = 1000

        # Future expansion hooks
        self.trade_manager = None  # Will be added in Sprint 4
        self.war_manager = None  # Will be added in Sprint 5

    def create_settlement(self, config: dict) -> int:
        """
        Factory method for creating and registering settlements.

        Args:
            config: Dictionary with keys:
                - 'land': initial arable land size
                - 'population': starting population
                - 'regional_multiplier': fertility multiplier for region
                - 'spawn_x', 'spawn_y': optional starting coordinates
                - 'name': optional settlement name
                - 'culture': optional culture identifier

        Returns:
            settlement_id: Unique identifier for the settlement
        """
        from firstPythonMapTest import createSettlement  # Import your settlement creation function

        settlement_id = self.next_settlement_id
        self.next_settlement_id += 1

        # Create the settlement
        settlement = createSettlement(
            landSizeJax=config['land'],
            populationSize=config['population'],
            regionalMulti=config['regional_multiplier']
        )

        # Find spawn location
        if 'spawn_x' in config and 'spawn_y' in config:
            spawn_x, spawn_y = config['spawn_x'], config['spawn_y']
        else:
            spawn_x, spawn_y = self._find_spawn_location(config.get('preferred_region'))

        # Register in world map
        self.world_map.add_settlement(settlement, spawn_x, spawn_y, settlement_id)

        # Register metadata
        self.settlement_registry[settlement_id] = {
            'name': config.get('name', f'Settlement_{settlement_id}'),
            'founded_year': self.current_year,
            'founded_season': self.current_season,
            'culture': config.get('culture', 'default'),
            'settlement_ref': settlement,
            'spawn_location': (spawn_x, spawn_y),
            'is_active': True,  # False if settlement dies out
        }

        return settlement_id

    def advance_all_settlements(self):
        """
        Advance all settlements by one season simultaneously.
        This is the main game loop - call this repeatedly to run the simulation.
        """
        # 1. Process lord decisions (Sprint 2)
        # for settlement_id in self.settlement_registry.keys():
        #     self._process_lord_decisions(settlement_id)

        # 2. Execute trades (Sprint 4)
        # if self.trade_manager:
        #     self.trade_manager.execute_all_trades()

        # 3. Process wars (Sprint 5)
        # if self.war_manager:
        #     self.war_manager.process_wars(self)

        # 4. Advance each settlement's internal simulation
        for settlement_id, metadata in self.settlement_registry.items():
            if not metadata['is_active']:
                continue

            settlement = metadata['settlement_ref']
            settlement.passOneSeason()
            settlement.population = len(settlement.populace)

            # Check if settlement needs land expansion
            if self._should_expand(settlement):
                current_land = settlement.arable_land
                target_land = self._calculate_target_land(settlement.population)
                expansion_needed = target_land - current_land

                settlement.setLand(target_land)
                self.world_map.expand_territory(settlement_id)

            # Check if settlement has died out
            if settlement.population == 0:
                metadata['is_active'] = False
                print(f"💀 {metadata['name']} has been abandoned (population reached zero)")

        # 5. Advance calendar
        self._advance_calendar()

    def _should_expand(self, settlement) -> bool:
        """Determine if settlement needs more land based on population"""
        current_land = settlement.arable_land
        target_land = self._calculate_target_land(settlement.population)
        return current_land < target_land

    def _calculate_target_land(self, population: int) -> int:
        """
        Calculate how much land a settlement needs for its population.

        Rule of thumb: ~1 arable land per 2 people, with 20% buffer for growth.
        Adjust this based on your food production rates.
        """
        if population == 0:
            return 50  # Minimum land for abandoned settlements

        base_land = int(population * 0.5)
        buffer = int(base_land * 0.2)
        return max(50, base_land + buffer)

    def _find_spawn_location(self, preferred_region: Optional[str] = None) -> Tuple[int, int]:
        """
        Find a suitable spawn location for a new settlement.

        For now, returns random location. Later, could be smarter:
        - Check habitability score
        - Avoid spawning too close to existing settlements
        - Prefer certain biomes
        """
        # Simple random for now
        x = random.randint(100, self.world_map.width - 100)
        y = random.randint(100, self.world_map.height - 100)

        # TODO: Add smarter logic
        # - Check self.world_map.get_pixel_value(x, y) for quality
        # - Check distance to nearest settlement
        # - Check if already owned

        return x, y

    def _advance_calendar(self):
        """Move time forward by one season"""
        seasons = ["spring", "summer", "fall", "winter"]
        idx = seasons.index(self.current_season)
        self.current_season = seasons[(idx + 1) % 4]
        self.total_seasons_passed += 1

        if self.current_season == "spring":
            self.current_year += 1

    def get_settlement_by_id(self, settlement_id: int):
        """Get settlement object by ID"""
        if settlement_id in self.settlement_registry:
            return self.settlement_registry[settlement_id]['settlement_ref']
        return None

    def get_active_settlements(self) -> List[int]:
        """Get list of settlement IDs that are still active"""
        return [sid for sid, meta in self.settlement_registry.items() if meta['is_active']]


class SimulationMonitor:
    """
    Monitors and visualizes the state of the simulation.
    Tracks history and provides reporting capabilities.
    """

    def __init__(self, sim_manager: SimulationManager):
        self.sim = sim_manager
        self.history = []  # List of snapshot dictionaries
        self.snapshot_interval = 4  # Take snapshot every N seasons (default: every year)

    def take_snapshot(self) -> dict:
        """
        Capture current state of all settlements.

        Returns:
            snapshot: Dictionary containing current state
        """
        snapshot = {
            'year': self.sim.current_year,
            'season': self.sim.current_season,
            'total_seasons': self.sim.total_seasons_passed,
            'settlements': {}
        }

        for sid, metadata in self.sim.settlement_registry.items():
            settlement = metadata['settlement_ref']

            # Calculate job distribution
            job_counts = self._count_jobs(settlement)

            snapshot['settlements'][sid] = {
                'name': metadata['name'],
                'is_active': metadata['is_active'],
                'population': settlement.population,
                'food': settlement.foodstuff,
                'land': settlement.arable_land,
                'territory_pixels': len(settlement.owned_pixels),
                'total_births': settlement.childrenBorn,
                'total_deaths': settlement.peopleDied,
                'child_deaths': settlement.childrenDied,
                'manpower': settlement.calculateManPower(),
                'job_distribution': job_counts,
            }

        self.history.append(snapshot)
        return snapshot

    def _count_jobs(self, settlement) -> dict:
        """Count how many people have each job"""
        from firstPythonMapTest import Farmer, Child, Clergy, Solider, Housekeeper

        counts = {
            'Farmer': 0,
            'Child': 0,
            'Clergy': 0,
            'Soldier': 0,
            'Housekeeper': 0,
        }

        for person in settlement.populace:
            if isinstance(person, Farmer):
                counts['Farmer'] += 1
            elif isinstance(person, Child):
                counts['Child'] += 1
            elif isinstance(person, Clergy):
                counts['Clergy'] += 1
            elif isinstance(person, Solider):
                counts['Soldier'] += 1
            elif isinstance(person, Housekeeper):
                counts['Housekeeper'] += 1

        return counts

    def print_status(self, detailed: bool = False):
        """
        Print current status of all settlements to console.

        Args:
            detailed: If True, shows job distribution and other details
        """
        print(f"\n{'=' * 70}")
        print(f"  Year {self.sim.current_year} - {self.sim.current_season.capitalize()}")
        print(f"  Total Seasons Elapsed: {self.sim.total_seasons_passed}")
        print(f"{'=' * 70}")

        active_count = sum(1 for m in self.sim.settlement_registry.values() if m['is_active'])
        total_population = sum(
            m['settlement_ref'].population
            for m in self.sim.settlement_registry.values()
            if m['is_active']
        )

        print(f"\n World Summary:")
        print(f"   Active Settlements: {active_count}/{len(self.sim.settlement_registry)}")
        print(f"   Total Population: {total_population:,}")

        print(f"\n Settlement Details:")
        for sid, meta in self.sim.settlement_registry.items():
            settlement = meta['settlement_ref']

            status_icon = "good" if meta['is_active'] else "dead"
            print(f"\n   {status_icon} {meta['name']} (ID: {sid})")

            if not meta['is_active']:
                print(f"      ABANDONED in {meta.get('death_year', 'unknown')}")
                continue

            print(f"      Population: {settlement.population:,}")
            print(f"      Food Stores: {settlement.foodstuff:.0f}")
            print(f"      Land: {settlement.arable_land} plots ({len(settlement.owned_pixels):,} pixels)")
            print(f"      Manpower: {settlement.calculateManPower():.0f}")
            print(f"      Total Births: {settlement.childrenBorn:,} | Deaths: {settlement.peopleDied:,}")

            if detailed:
                job_counts = self._count_jobs(settlement)
                print(f"      Jobs: {', '.join(f'{job}: {count}' for job, count in job_counts.items() if count > 0)}")

    def plot_population_over_time(self, save_path: Optional[str] = None):
        """
        Create a line plot showing population over time for all settlements.

        Args:
            save_path: If provided, saves plot to this path instead of showing
        """
        if not self.history:
            print("No history data to plot. Run simulation first.")
            return

        plt.figure(figsize=(12, 6))

        # Get all settlement IDs
        settlement_ids = set()
        for snapshot in self.history:
            settlement_ids.update(snapshot['settlements'].keys())

        # Plot each settlement
        for sid in settlement_ids:
            years = []
            populations = []

            for snapshot in self.history:
                if sid in snapshot['settlements']:
                    years.append(
                        snapshot['year'] + ['spring', 'summer', 'fall', 'winter'].index(snapshot['season']) * 0.25)
                    populations.append(snapshot['settlements'][sid]['population'])

            if populations:
                settlement_name = self.sim.settlement_registry[sid]['name']
                plt.plot(years, populations, label=settlement_name, linewidth=2)

        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Population', fontsize=12)
        plt.title('Settlement Populations Over Time', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()

    def generate_report(self, filepath: str):
        """
        Generate a text report summarizing the simulation.

        Args:
            filepath: Path to save the report
        """
        with open(filepath, 'w') as f:
            f.write(f"SIMULATION REPORT\n")
            f.write(f"{'=' * 60}\n\n")

            f.write(f"Simulation Duration: {self.sim.current_year - 1000} years\n")
            f.write(f"Total Seasons: {self.sim.total_seasons_passed}\n")
            f.write(f"Final Year: {self.sim.current_year}\n\n")

            f.write(f"SETTLEMENTS:\n")
            f.write(f"{'-' * 60}\n\n")

            for sid, meta in self.sim.settlement_registry.items():
                settlement = meta['settlement_ref']

                f.write(f"{meta['name']} (ID: {sid})\n")
                f.write(f"  Founded: {meta['founded_year']} ({meta['founded_season']})\n")

                if meta['is_active']:
                    f.write(f"  Status: ACTIVE\n")
                    f.write(f"  Final Population: {settlement.population:,}\n")
                else:
                    f.write(f"  Status: ABANDONED\n")

                f.write(f"  Total Births: {settlement.childrenBorn:,}\n")
                f.write(f"  Total Deaths: {settlement.peopleDied:,}\n")
                f.write(f"  Territory: {len(settlement.owned_pixels):,} pixels\n")
                f.write(f"\n")

        print(f"Report generated: {filepath}")


# Example usage function
def run_example_simulation():
    """
    Example of how to set up and run a multi-settlement simulation.
    """
    import mapCoordination_improved as mapCoordination

    # Load map data
    print("Loading map data...")
    map_data = mapCoordination.load_map_data("riverTest.png", "testFast2.png")
    world_map = mapCoordination.WorldMap(map_data[0], map_data[1])

    # Create simulation manager
    sim = SimulationManager(world_map)
    monitor = SimulationMonitor(sim)

    # Create settlements
    print("Creating settlements...")

    settlement_configs = [
        {
            'name': 'Riverside',
            'land': 200,
            'population': 150,
            'regional_multiplier': 1.3,
            'spawn_x': 1500,
            'spawn_y': 2000,
            'culture': 'riverfolk'
        },
        {
            'name': 'Highpeak',
            'land': 150,
            'population': 100,
            'regional_multiplier': 0.9,
            'spawn_x': 2500,
            'spawn_y': 1500,
            'culture': 'mountain'
        },
        {
            'name': 'Greenfield',
            'land': 250,
            'population': 200,
            'regional_multiplier': 1.5,
            'spawn_x': 1000,
            'spawn_y': 3000,
            'culture': 'plains'
        }
    ]

    for config in settlement_configs:
        settlement_id = sim.create_settlement(config)
        print(f"  Created {config['name']} (ID: {settlement_id})")

    # Run simulation
    print("\nRunning simulation...")
    years_to_simulate = 50
    seasons_to_simulate = years_to_simulate * 4

    for i in range(seasons_to_simulate):
        sim.advance_all_settlements()

        # Take snapshot every year
        if sim.total_seasons_passed % 4 == 0:
            monitor.take_snapshot()

        # Print status every 5 years
        if sim.total_seasons_passed % 20 == 0:
            monitor.print_status()

    # Final report
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    monitor.print_status(detailed=True)

    # Generate outputs
    monitor.plot_population_over_time(save_path='population_over_time.png')
    monitor.generate_report('simulation_report.txt')

    return sim, monitor


if __name__ == "__main__":
    # Uncomment to run example
    # sim, monitor = run_example_simulation()
    pass