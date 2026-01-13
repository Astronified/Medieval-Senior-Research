from fast_perlin_noise import PerlinNoise
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from fast_perlin_noise.PerlinNoise import RandomMode

def overall():

    randx = random.randint(-1000000,1000000) #8192 is about 15-20 seconds, 18500 is 90 seconds

    randomjax = RandomMode.defined
    noise_image = PerlinNoise(
        width=8192, height=8192,
        persistence=0.7,
        num_layers=20,
        roughness=3.0,
        strength=3.5,
        base_roughness=0.6,
        random_mode=RandomMode.defined
    ).generate_noise_matrix(random_seed=randx)
    colors1 = [
        "#18400b",
        "#2a8a0c",
        "#4fde23",
        "#baf252"
    ]

    terrain_cmap = mcolors.ListedColormap(colors1)
    #now to start the river flowing

    bounds = np.linspace(noise_image.min(), noise_image.max(), len(colors1)+1)
    norm = mcolors.BoundaryNorm(bounds, terrain_cmap.N)
    terrain_rgb = terrain_cmap(norm(noise_image))[:, :, :3]

    #99.55% of NO turn for average river straight length to be about 1500 feet which is all approximations
    #to start I will be making single line rivers. then I will thicken them, add things like splits, etc
    def place_random_Xriver(image, x, y, river_length):
        blue = np.array([0, 0, 1.0])
        cx = 1
        cy = 0
        for i in range(river_length-1):
            x = x+cx
            y=y+cy
            if 0 <= y  < image.shape[0] and 0 <= x < image.shape[1]:
                image[y, x] = blue #95% for testing
            chance = random.randint(1,100)
            if chance>65:
                ls = getRandomY()
                cy = ls
            random_thickness = random.randint(1,3) #consistent 18 seconds with random 1-3
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
                image[y + random_thickness, x] = blue
            if 0 <= y - random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
                image[y - random_thickness, x] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
                image[y + random_thickness, x + random_thickness] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
                image[y + random_thickness, x - random_thickness] = blue
            if 0 <= y < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
                image[y, x + random_thickness] = blue
            if 0 <= y < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
                image[y, x - random_thickness] = blue

    def place_random_Yriver(image, x, y, river_length):
        blue = np.array([0, 0, 1.0])
        cx = 1
        cy = 0
        # direction = random.randint(1,4)
        # if direction == 1:
        #     image[y-1, x] = blue
        # if direction == 2:
        #     image[y+1, x] = blue
        # if direction == 3:
        #     image[y, x-1] = blue
        # if direction == 4:
        #     image[y, x+1] = blue
        for i in range(river_length-1):
            x = x+cy
            y=y+cx
            if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
                image[y, x] = blue #95% for testing
            chance = random.randint(1,100)
            if chance>65:
                ls = getRandomY()
                cy = ls
            random_thickness = random.randint(1, 3)
            # for random_thickness in range(1,random_thickness_val):
            #     if 0 <= y + random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
            #         image[y + random_thickness, x] = blue
            #     if 0 <= y - random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
            #         image[y - random_thickness, x] = blue
            #     if 0 <= y + random_thickness < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
            #         image[y + random_thickness, x + random_thickness] = blue
            #     if 0 <= y + random_thickness < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
            #         image[y + random_thickness, x - random_thickness] = blue
            #     if 0 <= y < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
            #         image[y, x + random_thickness] = blue
            #     if 0 <= y < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
            #         image[y, x - random_thickness] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
                image[y + random_thickness, x] = blue
            if 0 <= y - random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
                image[y - random_thickness, x] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
                image[y + random_thickness, x + random_thickness] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
                image[y + random_thickness, x - random_thickness] = blue
            if 0 <= y < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
                image[y, x + random_thickness] = blue
            if 0 <= y < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
                image[y, x - random_thickness] = blue
        if random.randint(1,5) == 4:
            place_rightDiagonalRiver(image,x,y,int(river_length/2))

    def place_rightDiagonalRiver(image, x, y, river_length):
        blue = np.array([0, 0, 1.0])
        cx = 1
        cy = 1
        for i in range(river_length-1):
            x = x+cx
            y=y+cy
            if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
                image[y, x] = blue  # 95% for testing
            chance = random.randint(1,100)
            if chance>65:
                ls = getRandomY()
                lx = getRandomY()
                cy = ls
                cx = lx
            else:
                cy =1
                cx=1
            random_thickness = random.randint(1,3) #consistent 18 seconds with random 1-3
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
                image[y + random_thickness, x] = blue
            if 0 <= y - random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
                image[y - random_thickness, x] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
                image[y + random_thickness, x + random_thickness] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
                image[y + random_thickness, x - random_thickness] = blue
            if 0 <= y < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
                image[y, x + random_thickness] = blue
            if 0 <= y < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
                image[y, x - random_thickness] = blue
        print("placed a diagonal")

    def getRandomY():
        randomy = random.randint(-1,1)

        return randomy


        # if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
        #     image[y, x] = blue
    def testRiver(image, x, y, river_length):
        blue = np.array([0, 0, 1.0])
        cx = 1
        cy = 1
        for i in range(river_length-1):
            x = x+cx
            y=y+cy
            if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
                image[y, x] = blue  # 95% for testing
            chance = random.randint(1,100)
            if chance>95:
                ls = getRandomY()
                lx = getRandomY()
                cy = ls
                cx = lx
                while cx == -1 and cy == -1 or cy == -1 and cx==0:
                    cx = getRandomY()
                    cy = getRandomY()
            random_thickness = random.randint(1,3) #consistent 18 seconds with random 1-3
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
                image[y + random_thickness, x] = blue
            if 0 <= y - random_thickness < image.shape[0] and 0 <= x < image.shape[1]:
                image[y - random_thickness, x] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
                image[y + random_thickness, x + random_thickness] = blue
            if 0 <= y + random_thickness < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
                image[y + random_thickness, x - random_thickness] = blue
            if 0 <= y < image.shape[0] and 0 <= x + random_thickness < image.shape[1]:
                image[y, x + random_thickness] = blue
            if 0 <= y < image.shape[0] and 0 <= x - random_thickness < image.shape[1]:
                image[y, x - random_thickness] = blue
        print("placed a diagonal")


    # drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(100,1000))
    # drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(100,1000))
    # drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(100,1000))
    # drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(100,1000))
    # drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(100,1000))
    # drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(100,1000))
    # drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(100,1000))
    # drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(100,1000))

    print("started swamping")
    #[0.09411765 0.25098039 0.04313725]= swamp

    def printvals(image):
        for i in range(len(image)):
            for y in range(len(image[i])):
                print(image[i][y])

    def placeRiversFromSwamps(image, interations):
        for i in range(interations):
            randomx = random.randint(100,8000)
            randomy = random.randint(100,8000)

          #  print(str(image[randomx][randomy]))

           # if image[randomx][randomy] ==  [0.09411765, 0.25098039, 0.04313725]:
            #if np.array_equal(image[randomx][randomy],[0.09411765, 0.25098039, 0.04313725]):
            if str(image[randomx][randomy])=="[0.09411765 0.25098039 0.04313725]":
                if random.randint(1,2) == 1:
                    testRiver(image, randomx,randomy,1000)
                else:
                    testRiver(image, randomx, randomy, 1000)
                print("X: " + str(randomx) + " Y: " + str(randomy) )




    #placeRiversFromSwamps(terrain_rgb,1500)
    #printvals(terrain_rgb)
    #testRiver(terrain_rgb, 500,500, 1000)





    def drawBlueRiver(image, x, y, river_length, drift_chance=0.1, drift_angle_max=20):
        blue = np.array([0.0, 0.0, 1.0])
        direction_angle = math.radians(random.randint(0,180))
        step_size = 0.5
        for _ in range(river_length):
            xi = int(round(x))
            yi = int(round(y))
            if 0 <= yi < image.shape[0] and 0 <= xi < image.shape[1]:
                image[yi, xi] = blue
            if random.random() < drift_chance:
                drift = random.uniform(-drift_angle_max, drift_angle_max)
                direction_angle += math.radians(drift)
            x += step_size * math.cos(direction_angle)
            y += step_size * math.sin(direction_angle)

        print("Placed a blue river.")



    #Rivers will NEVER work
    #im going to go for the best approach i can but this is really holding me back
    #im gonna take probably the boring implementation thats like mid in order to get ahead on the sim

    drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(1000,10000))
    drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(1000,10000))
    drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(1000,10000))
    drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(1000,10000))
    drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(1000,10000))
    drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(1000,10000))
    drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(1000,10000))
    drawBlueRiver(terrain_rgb, random.randint(0,8000), random.randint(0,8000), random.randint(1000,10000))


    #drawBlueRiver(terrain_rgb,500,500,1000)

    plt.imsave("riverTest.png", terrain_rgb)
    print(randx)
