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
         #       print(f"Wedding! A male farmer ({int(groom.age / 12)}) married a female farmer ({int(bride.age / 12)})")

    def passOneSeason(self):
        seasonalMultiplier = np.random.normal(1.4, 0.67) * self.regionMultiplier
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
         #               print(f"A child grew up to be a {new_adult.gender} Farmer.")
                    else:
                        new_adult = Clergy()  # Randomizes gender in its own init
                        new_adult.age = person.age
          #              print("A child grew up to be Clergy.")

                    self.populace.remove(person)
                    self.populace.append(new_adult)
                    continue  # Skip to next person

            # 4. MOTHERHOOD & RETURN TO WORK ---
            # Logic: If Housekeeper and youngest child is old enough, go back to farming
            if isinstance(person, Housekeeper):
                # Housekeepers don't produce food, but they manage the home.
                #
                if person.monthsSinceLastBirth > (7*12):
       #             print("A mother has returned to the fields.")
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

                # Check eligibility
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
                    #    print("A child was born")
                        # Set Cooldown (18 to 24 months)
                        person.monthsUntilNextBirth = random.randint(18, 24)
                        person.monthsSinceLastBirth = 0
                        death_chance2 = 0.015
                        if random.random() < 0.015:
                     #       print("The mother died in childbirth")
                            birthDeath = True
                        # If she was a Farmer, she becomes a Housekeeper now
                        elif isinstance(person, Farmer):
                      #      print("A farmer gave birth and became a Housekeeper.")
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
        #        print(f"A {type(person).__name__} starved.")
                if isinstance(person, Child):
                    self.childrenDied+=1

            # Old Age Logic (Standard Deviation-ish approach)
            if person.age > 50 * 12 and not dying:
                death_chance = (person.age - 50 * 12) / (20 * 12) * 0.1  # Chance increases with age
                if random.random() < death_chance:
                    dying = True
         #           print(f"A {type(person).__name__} died of old age at {int(person.age / 12)}.")

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

           #         print(f"A child died due to {diseases[random.randint(0,4)]} age at {int(person.age / 12)}.")
            if not isinstance(person, Child) and not dying:
                death_chance = 0.0045
                diseases = ["influenza", "spallpox", "tuberculosis", "typhoid fever", "dysentery"]
                if random.random() < death_chance:
         #           print((f"A {type(person).__name__} died due to {diseases[random.randint(0,4)]} at {int(person.age / 12)}."))
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
        decay = int(self.foodstuff*0.1)
        print("food decayed from stockpile: " + str(decay))
        self.foodstuff -= decay

        self.foodstuff += foodGainedThisSeason

        print("food gained: " + str(foodGainedThisSeason))
        # Run Marriage Matchmaking
        self.attempt_marriage()

   #     print(f"Results: {int(foodGainedThisSeason)} food produced. {babiesBorn} babies born. {deadCount} died.")
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
            return 2.5 * self.efficiency
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



newSettlement = Settlement()
peop = []
farmcount =0
for i in range(500):
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
newSettlement.setFood(len(peop) * 1.5)
print("we have" + str(farmcount) + " farmers")

# ... (Previous simulation setup code) ...

population_history = []
food_history = []
avg_age_history = []
time_steps = []

total_seasons = 5000
for i in range(total_seasons):
    print("season: " + str(i))
    newSettlement.passOneSeason()

    # Record Data
    current_pop = len(newSettlement.populace)
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

# --- MATPLOTLIB VISUALIZATION ---
# <--- 3. CHANGE TO 3 SUBPLOTS
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

# Plot 1: Population
ax1.plot(time_steps, population_history, color='blue', linewidth=1)
ax1.set_ylabel("Population Size")
ax1.set_title(f"Settlement Population Over {total_seasons / 4} Years")
ax1.grid(True, linestyle='--', linewidth=0.5)

# Plot 2: Food
ax2.plot(time_steps, food_history, color='green', linewidth=1)
ax2.set_ylabel("Food Units")
ax2.set_title("Food Stockpile History")
ax2.grid(True, linestyle='--', linewidth=0.5)


# Plot 3: Average Age (NEW)
ax3.plot(time_steps, avg_age_history, color='purple', linewidth=1)
ax3.set_ylabel("Avg Age (Years)")
ax3.set_xlabel("Years")
ax3.set_title("Average Age of Populace")
ax3.grid(True, linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.show()