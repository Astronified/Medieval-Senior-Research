import math
import random
from contextlib import nullcontext

import numpy as np
import mapCoordination
import simulationManager as simulation_manager
import matplotlib.pyplot as plt
import advancedSettlementPlacing

class Settlement:
    def __init__(self):
        self.population = 0
        self.foodstuff = 0
        self.populace = []
        self.childrenBorn = 0
        self.childrenDied = 0
        self.peopleDied = 0
        self.regionMultiplier = 1
        self.birthChance = 0
        self.harvest_std = 0
        self.deathChance = 0
        self.season = "spring"
        self.jobs = ["Farmer", "Clergy", "Solider", "Tavern", "Speciality",
                     "Blacksmith", "Mason", "Butcher", "Housekeeper", "Prostitute", "Child", "Merchant", "Lord"]
        self.arable_land = 200
        self.land_expansion_rate = 0.05

    def setPeople(self, pops):
        self.populace = pops
        self.population = len(pops)

    def setRegionalMultiplier(self, multi):
        self.regionMultiplier = multi

    def setFood(self, food):
        self.foodstuff = food

    def setBirth(self, birth):
        self.birthChance = birth

    def setHarvest_std(self, harvstd):
        self.harvest_std = harvstd

    def setDeath(self, death):
        self.deathChance = death

    def setLand(self, landsize):
        self.arable_land = landsize

    def getLand(self):
        return self.arable_land

    def calculateManPower(self):
        current_manPower = 0.0
        for p in self.populace:
            if p.gender == "male" and not isinstance(p, Solider) and not isinstance(p, Child) and p.age < (50 * 12):
                current_manPower += 1.0
            if isinstance(p, Solider) and p.age < (50 * 12):
                current_manPower += 2.5
        return current_manPower

    def nextSeason(self):
        seasons = ["spring", "summer", "fall", "winter"]
        idx = seasons.index(self.season)
        self.season = seasons[(idx + 1) % 4]

    def attempt_marriage(self):
        eligible = [p for p in self.populace if
                    not isinstance(p, Child) and not isinstance(p, Clergy)
                    and p.spouse is None and 17 * 12 <= p.age <= 55 * 12]
        bachelors    = [p for p in eligible if p.gender == "male"]
        bachelorettes = [p for p in eligible if p.gender == "female"]
        random.shuffle(bachelors)
        random.shuffle(bachelorettes)
        while bachelors and bachelorettes:
            groom = bachelors.pop()
            bride = bachelorettes.pop()
            if random.random() < 0.5:
                groom.spouse = bride
                bride.spouse = groom

    def passOneSeason(self):
        raw_multiplier   = np.random.normal(1.8, self.harvest_std)
        seasonalMultiplier = max(0.1, raw_multiplier) * self.regionMultiplier
        foodGainedThisSeason = 0
        deadCount  = 0
        babiesBorn = 0

        random.shuffle(self.populace)
        plots_worked_this_season = 0

        for person in self.populace:
            if isinstance(person, Farmer):
                base_production = person.doWork(self.season)
                if plots_worked_this_season < self.arable_land:
                    foodGainedThisSeason += seasonalMultiplier * base_production
                    plots_worked_this_season += 1
                else:
                    foodGainedThisSeason += seasonalMultiplier * (base_production * 0.05)
            if isinstance(person, Child):
                if plots_worked_this_season < self.arable_land and self.season != "winter":
                    foodGainedThisSeason += seasonalMultiplier * 0.3 * 1.5
            if isinstance(person, Clergy) and self.season != "winter":
                if plots_worked_this_season < self.arable_land:
                    foodGainedThisSeason += seasonalMultiplier * 0.3 * 1.5
            if isinstance(person, Solider) and self.season != "winter":
                if plots_worked_this_season < self.arable_land:
                    foodGainedThisSeason += seasonalMultiplier * 0.3 * 1.5
            if isinstance(person, Housekeeper) and self.season != "winter":
                if plots_worked_this_season < self.arable_land:
                    foodGainedThisSeason += seasonalMultiplier * 0.3 * 1.5

        self.foodstuff += foodGainedThisSeason
        self.foodstuff -= len(self.populace)

        starvation_chance = 0.0
        starvationDeath   = 0
        if self.foodstuff < 0:
            deficit_ratio     = abs(self.foodstuff) / len(self.populace)
            starvation_chance = min(0.15, deficit_ratio * 0.1)

        crowding = len(self.populace) / (self.arable_land * 0.4)

        for person in self.populace[:]:
            birthDeath = False
            dying      = False

            person.aging()

            if isinstance(person, Child) and person.age >= 13 * 12:
                tempr = random.random()
                if 0.96 < tempr < 0.98:
                    new_job = Solider(age=person.age)
                elif tempr > 0.98:
                    new_job = Clergy(age=person.age)
                else:
                    new_job = Farmer(gender=person.gender, age=person.age)
                self.populace.remove(person)
                self.populace.append(new_job)
                continue

            if isinstance(person, Housekeeper) and person.monthsSinceLastBirth > (2.1 * 12):
                back_to_farmer = Farmer(gender="female", age=person.age)
                back_to_farmer.spouse = person.spouse
                back_to_farmer.monthsUntilNextBirth = person.monthsUntilNextBirth
                if person.spouse:
                    person.spouse.spouse = back_to_farmer
                self.populace.remove(person)
                self.populace.append(back_to_farmer)
                person = back_to_farmer

            if (isinstance(person, Farmer) or isinstance(person, Housekeeper)) and \
                    person.gender == "female" and person.spouse is not None and \
                    17 * 12 <= person.age <= 45 * 12:
                if person.monthsUntilNextBirth > 0:
                    person.monthsUntilNextBirth -= 3
                safety_buffer = len(self.populace) * 2
                if person.monthsUntilNextBirth <= 0 and self.foodstuff > safety_buffer:
                    birth_chance = self.birthChance if person.age <= 30 * 12 else (0.05 if person.age <= 35 * 12 else 0.002)
                    if crowding > 0.8:
                        birth_chance *= (0.8 / crowding)
                    if random.random() < birth_chance:
                        new_baby = Child()
                        self.populace.append(new_baby)
                        babiesBorn += 1
                        self.childrenBorn += 1
                        person.monthsUntilNextBirth = random.randint(18, 24)
                        if isinstance(person, Farmer):
                            new_mother = Housekeeper(age=person.age)
                            new_mother.spouse = person.spouse
                            new_mother.monthsUntilNextBirth = person.monthsUntilNextBirth
                            new_mother.monthsSinceLastBirth = 0
                            if person.spouse:
                                person.spouse.spouse = new_mother
                            self.populace.remove(person)
                            self.populace.append(new_mother)
                        elif isinstance(person, Housekeeper):
                            person.monthsSinceLastBirth = 0
                        if random.random() < 0.015:
                            birthDeath = True

            if birthDeath:
                dying = True
            if not dying and self.foodstuff < 0:
                if random.random() < starvation_chance:
                    starvationDeath += 1
                    dying = True
                    if isinstance(person, Child):
                        self.childrenDied += 1
            if not dying:
                if person.age > 50 * 12:
                    if random.random() < (person.age - 50 * 12) / (20 * 12) * 0.1:
                        dying = True
                death_rate = self.deathChance if not isinstance(person, Child) else 0.006
                if random.random() < death_rate:
                    dying = True
            if dying:
                if hasattr(person, 'spouse') and person.spouse:
                    person.spouse.spouse = None
                if person in self.populace:
                    self.populace.remove(person)
                    deadCount += 1
                    self.peopleDied += 1

        if self.foodstuff > 0:
            self.foodstuff -= int(self.foodstuff * 0.009)
        else:
            self.foodstuff = 0

        self.attempt_marriage()
        self.nextSeason()


# ── JOB CLASSES ──────────────────────────────────────────────────────────────

class Farmer:
    def __init__(self, gender=None, age=None):
        self.gender = gender if gender else ("male" if random.random() < 0.5 else "female")
        self.age    = age    if age    else random.randint(13, 50) * 12
        self.spouse = None
        self.monthsUntilNextBirth = 0
        self.efficiency = random.uniform(0.5, 1.5)

    def aging(self):
        self.age += 3

    def doWork(self, season):
        if season == "fall":
            return 2.5 * self.efficiency
        elif season in ["spring", "summer"]:
            return 1.0 * self.efficiency
        else:
            return 0.25


class Housekeeper:
    def __init__(self, age):
        self.gender = "female"
        self.age    = age
        self.spouse = None
        self.monthsUntilNextBirth  = 0
        self.monthsSinceLastBirth  = 0

    def aging(self):
        self.age += 3
        self.monthsSinceLastBirth += 3

    def doWork(self, season):
        return 0.25


class Clergy:
    def __init__(self, age=None):
        self.gender  = "male" if random.random() < 0.8 else "female"
        self.age     = age if age else random.randint(13, 65) * 12
        self.holiness = random.uniform(0.2, 1.5)

    def aging(self):
        self.age += 3

    def doWork(self):
        return 5.0 * self.holiness


class Solider:
    def __init__(self, age=None):
        self.gender  = "male"
        self.spouse  = None
        self.age     = age if age else random.randint(13, 65) * 12
        self.holiness = random.uniform(0.2, 1.5)

    def aging(self):
        self.age += 3

    def doWork(self):
        return 5.0 * self.holiness


class Child:
    def __init__(self, age=0):
        self.age    = age
        self.gender = "male" if random.random() < 0.5 else "female"

    def aging(self):
        self.age += 3


# ── FACTORY ──────────────────────────────────────────────────────────────────

def createSettlement(landSizeJax, populationSize, regionalMulti):
    newSettlement = Settlement()
    peop = []
    for i in range(populationSize):
        jobSeed = random.random()
        age     = np.random.normal(20, 13.75)
        if age < 0:
            age = 0
        if age > 12:
            if jobSeed <= 0.9:
                peop.append(Farmer(age=age * 12))
            elif 0.90 < jobSeed < 0.97:
                peop.append(Solider(age=age * 12))
            else:
                peop.append(Clergy(age=age * 12))
        else:
            peop.append(Child(age=age * 12))
            newSettlement.childrenBorn += 1

    newSettlement.setRegionalMultiplier(regionalMulti)
    newSettlement.setPeople(peop)
    newSettlement.setFood(len(peop) * 8)
    newSettlement.setLand(landSizeJax)
    return newSettlement


def advanceOneSeason(settlement):
    settlement.passOneSeason()
    land = settlement.getLand()
    if land <= 400:
        settlement.setBirth(0.13);  settlement.setDeath(0.006); settlement.setHarvest_std(0.4)
    elif land <= 450:
        settlement.setBirth(0.14);  settlement.setDeath(0.006); settlement.setHarvest_std(0.3)
    elif land <= 600:
        settlement.setBirth(0.13);  settlement.setDeath(0.0055); settlement.setHarvest_std(0.4)
    else:
        settlement.setBirth(0.13);  settlement.setDeath(0.006); settlement.setHarvest_std(0.4)


# ── STANDALONE ENTRY POINT (not run on import) ────────────────────────────────

if __name__ == "__main__":
    map_data  = mapCoordination.load_map_data("riverTest.png", "testFast2.png")
    world_map = mapCoordination.WorldMap(map_data[0], map_data[1])
    sim       = simulation_manager.SimulationManager(world_map)
    monitor   = simulation_manager.SimulationMonitor(sim)
    best_three = advancedSettlementPlacing.mian()
    print(best_three)

    river_id = sim.create_settlement({
        'name': "Jax's settlement",
        'land': 1500, 'population': 200, 'regional_multiplier': 1.3,
        'spawn_x': best_three[0][1], 'spawn_y': best_three[0][2]
    })
    test_id = sim.create_settlement({
        'name': "Eric's settlement",
        'land': 1500, 'population': 200, 'regional_multiplier': 0.9,
        'spawn_x': best_three[1][1], 'spawn_y': best_three[1][2]
    })
    greenfield_id = sim.create_settlement({
        'name': "Kohlen's settlement",
        'land': 1500, 'population': 200, 'regional_multiplier': 1.5,
        'spawn_x': best_three[2][1], 'spawn_y': best_three[2][2]
    })

    for i in range(200):
        sim.advance_all_settlements()
        if sim.total_seasons_passed % 4 == 0:
            monitor.take_snapshot()
        if sim.total_seasons_passed % 40 == 0:
            monitor.print_status()

    monitor.print_status(detailed=True)
    monitor.plot_population_over_time(save_path='population_chart.png')
    monitor.generate_report('simulation_report.txt')