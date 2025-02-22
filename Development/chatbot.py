import pandas as pd
import numpy as np
def main():
    data = pd.read_csv("nutrients.csv")
    print(data.head())
    print(data.info())
    print(data.describe())
    print(data.shape())