import math
import random
import numpy as np
import matplotlib.pyplot as plt


class Settlement:
    def __init__(self):
        self.population = 0
        self.foodstuff = 0
        self.populace = []
        self.childrenBorn = 0
        self.childrenDied = 0
        self.peopleDied = 0
        self.regionMultiplier = 1
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
    def setLand(self,landsize):
        self.arable_land=landsize

    def nextSeason(self):
        seasons = ["spring", "summer", "fall", "winter"]
        idx = seasons.index(self.season)
        self.season = seasons[(idx + 1) % 4]

    def attempt_marriage(self):
        eligible = [p for p in self.populace if
                    not isinstance(p, Child) and not isinstance(p,Clergy) and p.spouse is None and 17 * 12 <= p.age <= 55 * 12]

        bachelors = [p for p in eligible if p.gender == "male"]
        bachelorettes = [p for p in eligible if p.gender == "female"]

        random.shuffle(bachelors)
        random.shuffle(bachelorettes)

        while bachelors and bachelorettes:
            groom = bachelors.pop()
            bride = bachelorettes.pop()
            if random.random() < 0.5:  # Increased chance to marry if eligible
                groom.spouse = bride
                bride.spouse = groom

    def passOneSeason(self):
        # 1. SETUP AND SEASONAL VARIANCE
        # FIX: Clamp the multiplier so it never goes below 0.1 (prevent negative food)
        raw_multiplier = np.random.normal(1.8, 0.67)
        seasonalMultiplier = max(0.1, raw_multiplier) * self.regionMultiplier

        foodGainedThisSeason = 0
        deadCount = 0
        babiesBorn = 0

        # 2. HARVEST PHASE
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
                if plots_worked_this_season < self.arable_land:
                    foodGainedThisSeason += seasonalMultiplier * 0.3 * 1.5 #estimated base production
            if isinstance(person, Clergy):
                if plots_worked_this_season < self.arable_land:
                    foodGainedThisSeason += seasonalMultiplier * 0.3 * 1.5 #estimated base production
            if isinstance(person, Housekeeper):
                if plots_worked_this_season < self.arable_land:
                    foodGainedThisSeason += seasonalMultiplier * 0.3 * 1.5 #estimated base production

        self.foodstuff += foodGainedThisSeason
      #  print("foodstuff:" + str(self.foodstuff))
        # 3. CONSUMPTION
        self.foodstuff -= len(self.populace)
       # if self.foodstuff <0:
       #     print("starvation: " + str(self.foodstuff))
        # Starvation Logic
        starvation_chance = 0.0
        starvation = False
        starvationDeath = 0
        if self.foodstuff < 0:
            starvation = True
            # Cap chance to ensure one bad harvest doesn't wipe everyone instantly
            starvation_chance = min(0.4, abs(self.foodstuff) / len(self.populace))

        # 4. INDIVIDUAL LIFE LOOP
        crowding = len(self.populace) / (self.arable_land * 1.5)
        for person in self.populace[:]:
            birthDeath = False
            dying = False

            # --- A. AGING ---
            person.aging()

            # --- B. JOB TRANSITIONS (Child -> Adult) ---
            if isinstance(person, Child) and person.age >= 13 * 12:
                # 4% chance to be Clergy, otherwise Farmer
                new_job = Clergy(age=person.age) if random.random() > 0.96 else Farmer(gender=person.gender,
                                                                                       age=person.age)
                self.populace.remove(person)
                self.populace.append(new_job)
                continue

            # --- C. MOTHERHOOD LOGIC (Return to Work) ---
            # Only return to work if NOT pregnant/nursing a new baby
            if isinstance(person, Housekeeper) and person.monthsSinceLastBirth > (2.1 * 12):
                back_to_farmer = Farmer(gender="female", age=person.age)
                # Restore pointers
                back_to_farmer.spouse = person.spouse
                back_to_farmer.monthsUntilNextBirth = person.monthsUntilNextBirth

                # Update husband's pointer to the new Farmer object
                if person.spouse:
                    person.spouse.spouse = back_to_farmer

                self.populace.remove(person)
                self.populace.append(back_to_farmer)
                # Update local reference so birth logic below uses the Farmer object
                person = back_to_farmer

            # --- D. BIRTH LOGIC ---
            if (isinstance(person, Farmer) or isinstance(person, Housekeeper)) and \
                    person.gender == "female" and person.spouse is not None and \
                    17 * 12 <= person.age <= 45 * 12:

                if person.monthsUntilNextBirth > 0:
                    person.monthsUntilNextBirth -= 3

                # Only give birth if fed and cooldown is ready
                if person.monthsUntilNextBirth <= 0 < self.foodstuff:
                    birth_chance = 0.09 if person.age <= 30 * 12 else (0.05 if person.age <= 35 * 12 else 0.002)

                    if crowding > 0.8:
                        birth_chance *= (0.8 / crowding)

                    if random.random() < birth_chance:
                        new_baby = Child()
                        self.populace.append(new_baby)
                        babiesBorn += 1
                        self.childrenBorn += 1

                        # Reset cooldown for next child
                        person.monthsUntilNextBirth = random.randint(18, 24)

                        # Logic Split:
                        # 1. If Farmer, become Housekeeper.
                        # 2. If already Housekeeper, RESET timer (fix for the bug).
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

                        # Maternal Mortality
                        if random.random() < 0.015:
                            birthDeath = True

            # --- E. DEATH LOGIC ---
            if birthDeath:
                dying = True

            if not dying and self.foodstuff < 0:
                if random.random() < starvation_chance:
                    starvationDeath += 1
                    dying = True
                    if isinstance(person, Child): self.childrenDied += 1

            if not dying:
                if person.age > 50 * 12:
                    if random.random() < (person.age - 50 * 12) / (20 * 12) * 0.1:
                        dying = True
                death_rate = 0.0045 if not isinstance(person, Child) else 0.006
                if random.random() < death_rate:
                    dying = True

            if dying:
                if hasattr(person, 'spouse') and person.spouse:
                    person.spouse.spouse = None
                if person in self.populace:
                    self.populace.remove(person)
                    deadCount += 1
                    self.peopleDied += 1

        # 5. END OF SEASON CLEANUP
        if self.foodstuff > 0:
            #decay
           self.foodstuff -= int(self.foodstuff * 0.009)
        else:
            self.foodstuff = 0

        self.attempt_marriage()
        self.nextSeason()
   #     print("STARVATION DEATHS" + str(starvationDeath))

# --- JOBS CLASSES ---

class Farmer:
    def __init__(self, gender=None, age=None):
        # Allow passing gender/age for when children grow up or jobs change
        if gender:
            self.gender = gender
        else:
            self.gender = "male" if random.random() < 0.5 else "female"

        if age:
            self.age = age
        else:
            self.age = random.randint(13, 50) * 12

        self.spouse = None
        self.monthsUntilNextBirth = 0  # Cooldown
        self.efficiency = random.uniform(0.5, 1.5)

    def aging(self):
        self.age += 3

    def doWork(self, season):
        # Only work if not winter
        if season == "fall":
            return 2.5 * self.efficiency

        elif season in ["spring", "summer"]:
            return 1*self.efficiency
        else:
            return 0.25


class Housekeeper:
    def __init__(self, age):
        self.gender = "female"
        self.age = age
        self.spouse = None
        self.monthsUntilNextBirth = 0  # Cooldown
        self.monthsSinceLastBirth = 0  # Tracker to return to work

    def aging(self):
        self.age += 3
        self.monthsSinceLastBirth += 3

    def doWork(self, season):
        return 0.25

class Clergy:
    def __init__(self, age=None):
        self.gender = "male" if random.random() < 0.8 else "female"  # Mostly male clergy?
        if age:
            self.age = age
        else:
            self.age = random.randint(13, 65) * 12

        self.holiness = random.uniform(0.2, 1.5)

    def aging(self):
        self.age += 3

    def doWork(self):
        return 5.0 * self.holiness


class Child:
    def __init__(self, age=0):
        self.age = age  # Default 0 for newborns
        self.gender = "male" if random.random() < 0.5 else "female"

    def aging(self):
        self.age += 3

averageEndStart = 0.0
for zzz in range(100):
    newSettlement = Settlement()
    newSettlement.setLand(200)
    peop = []
    farmcount =0
    for i in range(100):
        jobSeed = random.random()
        age = np.random.normal(20,13.75)
        if age < 0:
            age = 0
        if age > 12:
            if jobSeed <= 0.9:
                peop.append(Farmer(age= age*12))
                farmcount+=1

            elif jobSeed > 0.90:
                peop.append(Clergy(age = age*12))
        else:
            peop.append(Child(age=age * 12))
            newSettlement.childrenBorn +=1


    newSettlement.setRegionalMultiplier(1.1) #this assumes light green region for now
    newSettlement.setPeople(peop)
    newSettlement.setFood(len(peop) * 8)
    newSettlement.setLand(210)
    #print("we have" + str(farmcount) + " farmers")


    population_history = []
    food_history = []
    avg_age_history = []
    time_steps = []
    firstPop = 0
    highestPop = 0
    lastPop = 0
    total_seasons = 3500
    for i in range(total_seasons):
       # print("season: " + str(i))
        newSettlement.passOneSeason()

        # Record Data
        current_pop = len(newSettlement.populace)
        if current_pop>highestPop:
            highestPop = current_pop
        if i == 0:
            firstPop =current_pop
        if i == 3499:
            lastPop = current_pop
        population_history.append(current_pop)
        food_history.append(newSettlement.foodstuff)

        # <--- 2. CALCULATE AVERAGE AGE
        if len(newSettlement.populace) > 0:
            # Sum all ages in months, divide by count, then divide by 12 for years
            total_months = sum(p.age for p in newSettlement.populace)
            avg_age_years = (total_months / len(newSettlement.populace)) / 12
            avg_age_history.append(avg_age_years)
        else:
            avg_age_history.append(0)

        # Convert step 'i' to Years (each step is 0.25 years)
        time_steps.append(i * 0.25)

    # # --- MATPLOTLIB VISUALIZATION ---
    # # <--- 3. CHANGE TO 3 SUBPLOTS
    # fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    #
    # # Plot 1: Population
    # ax1.plot(time_steps, population_history, color='blue', linewidth=1)
    # ax1.set_ylabel("Population Size")
    # ax1.set_title(f"Settlement Population Over {total_seasons / 4} Years")
    # ax1.grid(True, linestyle='--', linewidth=0.5)
    #
    # # Plot 2: Food
    # ax2.plot(time_steps, food_history, color='green', linewidth=1)
    # ax2.set_ylabel("Food Units")
    # ax2.set_title("Food Stockpile History")
    # ax2.grid(True, linestyle='--', linewidth=0.5)
    #
    #
    # # Plot 3: Average Age (NEW)
    # ax3.plot(time_steps, avg_age_history, color='purple', linewidth=1)
    # ax3.set_ylabel("Avg Age (Years)")
    # ax3.set_xlabel("Years")
    # ax3.set_title("Average Age of Populace")
    # ax3.grid(True, linestyle='--', linewidth=0.5)
    #
    # plt.tight_layout()
    # #plt.show()
    if lastPop-firstPop>0:
        print("end-start: " + str(lastPop-firstPop))
        averageEndStart += (lastPop-firstPop)
    else:
        print("failed ")
        print("highestPop: " + str(highestPop))
    print("----------------------")

print("avg end-start: " + str(averageEndStart/100))

    #One arable land = ~430 pixels (should be mapped in furrows)
    #300x300 area is approximately 210 arable land units
    # A 300x300 area's carry capacity is about XYZ
    #occasionally settlements fail
    # 2x:
    # A (300x300 * 2) area's carry capacity is about XYZ
    #4x:
    # A 600x600 area's carry capacity is about XYZ


