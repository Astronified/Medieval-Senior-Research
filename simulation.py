import math
import random
import numpy as np
import matplotlib.pyplot as plt

#

class Settlement:
    def __init__(self):
        self.population = 0
        self.foodstuff = 0
        self.populace = []
        self.childrenBorn = 0
        self.childrenDied = 0
        self.peopleDied = 0
        self.regionMultiplier = 1 #0.5, 0.7, 0.9, 1.1, 1.4, 1.6
        self.season = "spring"
        self.jobs = ["Farmer", "Clergy", "Solider", "Tavern", "Speciality",
                     "Blacksmith", "Mason", "Butcher", "Housekeeper", "Prostitute", "Child", "Merchant", "Lord"]

    def setPeople(self, pops):
        self.populace = pops
        self.population = len(pops)
    def setRegionalMultiplier(self, multi):
        self.regionMultiplier = multi

    def setFood(self, food):
        self.foodstuff = food

    def nextSeason(self):
        seasons = ["spring", "summer", "fall", "winter"]
        idx = seasons.index(self.season)
        self.season = seasons[(idx + 1) % 4]

    def attempt_marriage(self):
        # Filter for eligible singles
        # Must be Farmer (or add other classes if desired), right gender, single, and old enough
        bachelors = [p for p in self.populace if
                     isinstance(p, Farmer) and p.gender == "male" and p.spouse is None and 17 * 12 <= p.age <= 49 * 12]
        bachelorettes = [p for p in self.populace if
                         isinstance(p, Farmer) and p.gender == "female" and p.spouse is None and 17 * 12 <= p.age <= 49 * 12]

        random.shuffle(bachelors)
        random.shuffle(bachelorettes)

        # Pair them up
        while bachelors and bachelorettes:
            groom = bachelors.pop()
            bride = bachelorettes.pop()

            # chance of marry
            if random.random() < 0.35 and abs(groom.age - bride.age) <= 10:
                groom.spouse = bride
                bride.spouse = groom
                print(f"Wedding! A male farmer ({int(groom.age / 12)}) married a female farmer ({int(bride.age / 12)})")

    def passOneSeason(self):
        seasonalMultiplier = np.random.normal(1.4, 0.67, 1) * self.regionMultiplier
        print(f"\n--- {self.season.upper()} (Pop: {len(self.populace)}) ---")

        foodGainedThisSeason = 0
        deadCount = 0
        babiesBorn = 0

        # Consumption
        self.foodstuff -= len(self.populace)

        for person in self.populace[:]:
            birthDeath = False
            # --- 1. WORK PHASE ---
            if isinstance(person, Farmer):
                foodGainedThisSeason += seasonalMultiplier * person.doWork(self.season)
            elif isinstance(person, Clergy):
                # specific clergy logic here
                pass

            # --- 2. AGING & COOLDOWNS ---
            person.aging()

            # --- 3. JOB TRANSITIONS (Child -> Adult) ---
            if isinstance(person, Child):
                if person.age >= 13 * 12:
                    # Child grows up
                    jobSeed = random.random()
                    new_adult = None

                    if jobSeed < 0.96:
                        new_adult = Farmer(gender=person.gender, age=person.age)
                        print(f"A child grew up to be a {new_adult.gender} Farmer.")
                    else:
                        new_adult = Clergy()  # Randomizes gender in its own init
                        new_adult.age = person.age
                        print("A child grew up to be Clergy.")

                    self.populace.remove(person)
                    self.populace.append(new_adult)
                    continue  # Skip to next person

            # 4. MOTHERHOOD & RETURN TO WORK ---
            # Logic: If Housekeeper and youngest child is old enough, go back to farming
            if isinstance(person, Housekeeper):
                # Housekeepers don't produce food, but they manage the home.
                #
                if person.monthsSinceLastBirth > (7*12):
                    print("A mother has returned to the fields.")
                    # Convert Housekeeper back to Farmer
                    back_to_farmer = Farmer(gender="female", age=person.age)
                    back_to_farmer.spouse = person.spouse
                    back_to_farmer.monthsUntilNextBirth = person.monthsUntilNextBirth

                    # Update Husband's reference
                    if person.spouse and person.spouse in self.populace:
                        person.spouse.spouse = back_to_farmer

                    self.populace.remove(person)
                    self.populace.append(back_to_farmer)
                    person = back_to_farmer  # Update local var for the rest of the loop

            # --- 5. BIRTH LOGIC ---
            # Only check for birth if it's a Female, Married, and correct age
            if (isinstance(person, Farmer) or isinstance(person, Housekeeper)) and \
                    person.gender == "female" and \
                    person.spouse is not None and \
                    17 * 12 <= person.age <= 45 * 12:
                birthAgeMultiplier = 1
                #(17 - 30 (should be like 75%)
                #(31-35) 50%
                # 35 - 40 20%
                #40+ 7%
                # Decrement Cooldown
                if person.age <= 30*12:
                    birthAgeMultiplier = 0.75
                if 30*12 < person.age <= 35*12:
                    birthAgeMultiplier = 0.5
                if 35*12 < person.age <= 40*12:
                    birthAgeMultiplier = 0.2
                if 40*12<person.age:
                    birthAgeMultiplier = 0.07
                if person.monthsUntilNextBirth > 0:
                    person.monthsUntilNextBirth -= 3

                # Check eligibilityp
                # 1. Must have no cooldown
                # 2. Must have enough food (simplistic check)
                if person.monthsUntilNextBirth <= 0 and self.foodstuff > 0:
                    birth_chance = 1.0 * birthAgeMultiplier  # Chance per season if eligible
                    if random.random() < birth_chance:
                        # CREATE BABY
                        new_baby = Child()  # Defaults to age 0
                        self.populace.append(new_baby)
                        babiesBorn += 1
                        self.childrenBorn +=1
                        print("A child was born")
                        # Set Cooldown (18 to 24 months)
                        person.monthsUntilNextBirth = random.randint(18, 24)
                        person.monthsSinceLastBirth = 0
                        death_chance2 = 0.015
                        if random.random() < 0.015:
                            print("The mother died in childbirth")
                            birthDeath = True
                        # If she was a Farmer, she becomes a Housekeeper now
                        elif isinstance(person, Farmer):
                            print("A farmer gave birth and became a Housekeeper.")
                            new_mother = Housekeeper(age=person.age)
                            new_mother.spouse = person.spouse
                            new_mother.monthsUntilNextBirth = person.monthsUntilNextBirth
                            new_mother.monthsSinceLastBirth = 0

                            # Fix Husband's reference
                            if person.spouse:
                                person.spouse.spouse = new_mother

                            self.populace.remove(person)
                            self.populace.append(new_mother)


            # --- 6. DEATH ---
            # Random death chance based on age or starvation
            dying = False
            if birthDeath:
                dying = True
            # Starvation Logic (Simplified)
            if self.foodstuff < -10 and random.random() < 0.1 and not dying:
                dying = True
                print(f"A {type(person).__name__} starved.")
                if isinstance(person, Child):
                    self.childrenDied+=1

            # Old Age Logic (Standard Deviation-ish approach)
            if person.age > 50 * 12 and not dying:
                death_chance = (person.age - 50 * 12) / (20 * 12) * 0.1  # Chance increases with age
                if random.random() < death_chance:
                    dying = True
                    print(f"A {type(person).__name__} died of old age at {int(person.age / 12)}.")

            if isinstance(person, Child) and not dying:
                death_chance = 0
                if 0 <= person.age < 12:
                    death_chance = 0.0600
                elif 12 <= person.age < 60:
                    death_chance =  0.0104
                elif 60 <= person.age <= 144:
                    death_chance = 0.0034
                diseases = ["influenza", "spallpox", "tuberculosis", "typhoid fever","dysentery"]
                if random.random() < death_chance:
                    dying = True
                    self.childrenDied+=1

                    print(f"A child died due to {diseases[random.randint(0,4)]} age at {int(person.age / 12)}.")
            if not isinstance(person, Child) and not dying:
                death_chance = 0.0045
                diseases = ["influenza", "spallpox", "tuberculosis", "typhoid fever", "dysentery"]
                if random.random() < death_chance:
                    print((f"A {type(person).__name__} died due to {diseases[random.randint(0,4)]} at {int(person.age / 12)}."))
                    dying=True
            if dying:
                # If married, free the spouse
                if hasattr(person, 'spouse') and person.spouse:
                    person.spouse.spouse = None  # Spouse is single again

                if person in self.populace:
                    self.populace.remove(person)
                    deadCount += 1
                    self.peopleDied +=1

        # --- END OF LOOP CLEANUP ---

        # Add food gained
        self.foodstuff += foodGainedThisSeason

        # Run Marriage Matchmaking
        self.attempt_marriage()

        print(f"Results: {int(foodGainedThisSeason)} food produced. {babiesBorn} babies born. {deadCount} died.")
        print(f"Stockpile: {int(self.foodstuff)}")
        self.nextSeason()


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
        if season != "winter":
            return 2.0 * self.efficiency
        return 0.0


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


class Clergy:
    def __init__(self):
        self.gender = "male" if random.random() < 0.8 else "female"  # Mostly male clergy?
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



def startSim(index):
    # --- SIMULATION SETUP ---
    newSettlement = Settlement()
    peop = []
    farmcount =0
    for i in range(500): #need to pull a random distribution graph
        jobSeed = random.random() #should be adjusting, eric + kent had some good feedback
        if jobSeed < 0.8:           #basically a uniform population is bad because its an aging population
            peop.append(Farmer())   #even with boosted birthrate that is
            farmcount+=1

        elif jobSeed > 0.95:
            peop.append(Clergy())
        else:
            peop.append(Child(age=random.randint(0, 12) * 12))
            newSettlement.childrenBorn +=1


    newSettlement.setRegionalMultiplier(index) #this assumes light green region for 1.1
    newSettlement.setPeople(peop)
    newSettlement.setFood(len(peop) * 1.5)
    print("we have" + str(farmcount) + " farmers")


    population_history = []
    time_steps = []

    total_seasons = 100
    for i in range(total_seasons):
        newSettlement.passOneSeason()
        current_pop = len(newSettlement.populace)
        population_history.append(current_pop)
        time_steps.append(i * 0.25)

# --- STATISTICS & ANALYSIS ---
#
# # 1. Child Mortality
# if newSettlement.childrenBorn > 0:
#     child_mortality_rate = newSettlement.childrenDied / newSettlement.childrenBorn
# else:
#     child_mortality_rate = 0
# print(f"\n--- FINAL STATS ---")
# print(f"Child Mortality Rate: {child_mortality_rate:.2%}")
#
# # 2. Calculate 'r' (Intrinsic Growth Rate) using Log-Linear Regression
# # We fit a line to the Natural Log of the population history
# # Slope of this line = r
# log_pops = np.log(np.array(population_history) + 1e-9)  # +1e-9 avoids log(0) errors
# slope, intercept = np.polyfit(time_steps, log_pops, 1)
# r_value = slope
#
# print(f"Intrinsic Growth Rate (r): {r_value:.5f}")
# if r_value > 0:
#     print(f"Conclusion: Population is GROWING at approx {r_value * 100:.2f}% per year.")
# else:
#     print(f"Conclusion: Population is SHRINKING at approx {r_value * 100:.2f}% per year.")
#
# # --- MATPLOTLIB VISUALIZATION ---
# plt.figure(figsize=(12, 6))
#
# # Plot the population history
# plt.plot(time_steps, population_history, color='blue', linewidth=1, label="Actual Population")
#
# # Optional: Plot the trend line based on r
# # theoretical_pop = initial_pop * e^(rt)
# initial_pop = population_history[0]
# trend_line = [initial_pop * np.exp(r_value * t) for t in time_steps]
# plt.plot(time_steps, trend_line, color='red', linestyle='--', alpha=0.6, label=f"Trend (r={r_value:.3f})")
#
# plt.xlabel("Years")
# plt.ylabel("Population Size")
# plt.title(f"Settlement Population Over {total_seasons / 4} Years")
# plt.legend()
# plt.grid(True, which='both', linestyle='--', linewidth=0.5)
#
# # Show the graph
# plt.tight_layout()
# plt.show()

startSim(1.1)