
# from array1 import Array2D


# class Array2D:
#     def __init__(self, numRows, numCols):
#         self._rows = [ [0] * numCols for _ in range(numRows) ]

#     def numRows(self):
#         return len(self._rows)

#     def numCols(self):
#         return len(self._rows[0])

#     def clear(self, value):
#         for r in range(self.numRows()):
#             for c in range(self.numCols()):
#                 self._rows[r][c] = value

#     def __getitem__(self, indexTuple):
#         row, col = indexTuple
#         return self._rows[row][col]

#     def __setitem__(self, indexTuple, value):
#         row, col = indexTuple
#         self._rows[row][col] = value


# class LifeGrid:
#     DEAD_CELL = 0
#     LIVE_CELL = 1

#     def __init__(self, numRows, numCols):
#         self._grid = Array2D(numRows, numCols)
#         self.configure(list())

#     def numRows(self):
#         return self._grid.numRows()
    
#     def numCols(self):
#         return self._grid.numCols()
    
#     def configure(self, coordList):
        
#         for i in range(self.numRows()):
#             for j in range(self.numCols()):
#                 self.clearCell(i, j)

#         for coord in coordList:
#             self.setCell(coord[0], coord[1])

    
#     def isLiveCell(self, row, col):
#         return self._grid[row, col] == LifeGrid.LIVE_CELL

#     def clearCell(self, row, col):
#         self._grid[row, col] = LifeGrid.DEAD_CELL

#     def setCell(self, row, col):
#         self._grid[row, col] = LifeGrid.LIVE_CELL
    
#     def numLiveNeighbours(self, row, col):
#         count = 0

#         for i in range(row - 1, row + 2):
#             for j in range(col - 1, col + 2):
#                 if i == row and j == col:
#                     continue

#                 if (0 <= i < self.numRows()) and (0 <= j < self.numCols()):
#                     if self.isLiveCell(i, j):
#                         count += 1

#         return count    



    
# #from life import LifeGrid

# init_config = [ (1, 1), (2, 2), (3, 2) ]

# grid_width = 5
# grid_height = 5

# num_gens = 8

# def main():
#     grid = LifeGrid(grid_width, grid_height)
#     grid.configure(init_config)

#     draw(grid)

#     for i in range(num_gens):
#         evolve(grid)
#         draw(grid)

    
# def evolve(grid):
#     liveCells = list()

#     for i in range(grid.numRows()):
#         for j in range(grid.numCols()):

#             neighbours = grid.numLiveNeighbours(i, j)

#             if (neighbours == 2 and grid.isLiveCell(i, j)) or (neighbours == 3):
#                 liveCells.append((i, j))
    
#     grid.configure(liveCells)

# def draw(grid):
#     for i in range(grid.numRows()):
#         for j in range(grid.numCols()):
#             if grid.isLiveCell(i, j):
#                 print("O", end = " ")
#             else:
#                 print(".", end = " ")

#         print()
    
#     print("-" * (2*grid.numCols()))


# if __name__ == "__main__":
#     main()