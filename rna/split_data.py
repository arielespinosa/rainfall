import numpy as np

# Split SisPI grid in 6 parts for train each one in diferents RNA models
def split_sispi_grid(grid):

    _lat, _long = grid.shape
    _lat  = int(_lat  / 2)
    _long = int(_long / 3)

    g1 = grid[:_lat , :_long]
    g2 = grid[_lat: , :_long]
    g3 = grid[:_lat , _long:_long*2]
    g4 = grid[_lat: , _long:_long*2]
    g5 = grid[:_lat , _long*2:]
    g6 = grid[_lat: , _long*2:]

    return (g1, g2, g3, g4, g5, g6)


