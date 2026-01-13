from fast_perlin_noise import PerlinNoise
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from fast_perlin_noise.PerlinNoise import RandomMode


seed = random.randint(-1000000,1000000) #8192 is about 15-20 seconds, 18500 is 90 seconds
def set_seed(val):
    global seed
    seed = val
def makeMap():
    #randx =
    randx=seed
    randomjax = RandomMode.defined
    # noise_generator: PerlinNoise = PerlinNoise(width=8192, height=8192, persistence=0.65,num_layers=30,
    #                                            roughness=2.85,base_roughness=0.5,strength=5.0, random_mode=RandomMode.defined)
    # noise_image: np.ndarray = noise_generator.generate_noise_matrix(random_seed=rand)
    noise_image = PerlinNoise(
        width=8192, height=8192,
        persistence=0.7,
        num_layers=20,
        roughness=3.0,
        strength=3.5,
        base_roughness=0.6,
        random_mode=RandomMode.defined
    ).generate_noise_matrix(random_seed=randx)

    # noise_image = PerlinNoise(
    #     width=8192, height=8192,
    #     persistence=0.9999999, #1.0 appears to be a strange limit
    #     num_layers=20,
    #     roughness=1.3, #1.3
    #     strength=3.5,
    #     base_roughness=0.6,
    #     random_mode=RandomMode.defined
    # ).generate_noise_matrix(random_seed=randx)

    plt.imshow(noise_image)

    colors1 = [
    "#d62c20",
        "#db7900",
    "#d6c720",
        "#bed60b",
    "#5bbf39",
        "#138713",

    ]

    terrain_cmap = mcolors.ListedColormap(colors1)

    plt.imsave("testFast2.png", noise_image, cmap=terrain_cmap)
    print("the seed is " + str(randx))
    return randx
def get_seed():
    return seed
