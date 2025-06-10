# from: https://stackoverflow.com/questions/23451388/z3-sudoku-solver

# pip install z3-solver if necessary
from z3 import *

# overview: represent each number in the 9x9 grid as an integer variable x_ij
# for row i \in {1,...9} and column j \in {1,...,9}

# set up 9x9 matrix of integer variables
X = [ [ Int("x_%s_%s" % (i+1, j+1)) for j in range(9) ] 
      for i in range(9) ]
print(X)

# each cell contains a value in {1, ..., 9}
cells_c  = [ And(1 <= X[i][j], X[i][j] <= 9) 
             for i in range(9) for j in range(9) ]

# each row contains a digit at most once
rows_c   = [ Distinct(X[i]) for i in range(9) ]
# this distinct basically encodes: X[0][0] != X[1][0] != X[2][0] ...

# each column contains a digit at most once
cols_c   = [ Distinct([ X[i][j] for i in range(9) ]) 
             for j in range(9) ]
# this distinct basically encodes: X[0][0] != X[0][1] != X[0][2] ...


# each 3x3 square contains a digit at most once
# this part a little tricky with the indexing, but basically setting up
# the constraints on all 9 of the the 3x3 grids for the overall 9x9 grid
sq_c     = [ Distinct([ X[3*i0 + i][3*j0 + j] 
                        for i in range(3) for j in range(3) ]) 
             for i0 in range(3) for j0 in range(3) ]

# set up all the constraints as the conjunction of the constraints over the cells, 
# all the rows, all the columns and all of the 9 smaller grids
sudoku_c = cells_c + rows_c + cols_c + sq_c

# next part is for setting up individual boards with a few example boards

# sudoku instance, we use '0' for empty cells
instance = ((5,3,0,0,7,0,0,0,0),
            (6,0,0,1,9,5,0,0,0),
            (0,9,8,0,0,0,0,6,0),
            (8,0,0,0,6,0,0,0,3),
            (4,0,0,8,0,3,0,0,1),
            (7,0,0,0,2,0,0,0,6),
            (0,6,0,0,0,0,2,8,0),
            (0,0,0,4,1,9,0,0,5),
            (0,0,0,0,8,0,0,7,9))
            
"""
# unconstrained: any sudoku solution
instance = ((0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0))
"""

"""
# unsatisfiable: 2 ones in 1st column
instance = ((1,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (0,0,0,0,0,0,0,0,0),
            (1,0,0,0,0,0,0,0,0))
"""

# add constraint to specify the initial board values as specified
# in the initial boards above, or any value possible if specified as a 0
instance_c = [ If(instance[i][j] == 0, 
                  True, 
                  X[i][j] == instance[i][j]) 
               for i in range(9) for j in range(9) ]

# set up z3 solver
s = Solver()

# add the problem constraints and the individual instance/initial board constraints
overall_c = sudoku_c + instance_c
s.add(overall_c)
print(overall_c)

# if satisfiable, that means there exists a solution meeting all the constraints
if s.check() == sat:
    m = s.model()
    
    # save the "model", ie, the satisfying assignment to the constraints, 
    # that is, all the variable values that are the solution to the puzzle
    r = [ [ m.evaluate(X[i][j]) for j in range(9) ] 
          for i in range(9) ]
    print_matrix(r)
    
    quit()

    # optional, asking for another solution if not quitting early
    # could put this next bit into a loop: keep preventing previous solutions
    # from being used, by constraining variables to not equal previous 
    # solutions (models) found
    # prevent next model from being equal to previous: generate other
    # solutions
    c_different = [ And([ X[i][j] != m.evaluate(X[i][j]) for j in range(9) ]) 
          for i in range(9) ]
    
    print(c_different)
    s.add(c_different)
    
    if s.check() == sat:
	    m = s.model()
	    r = [ [ m.evaluate(X[i][j]) for j in range(9) ] 
	          for i in range(9) ]
    else:
    	print("no other solution")

          
    print_matrix(r)
else:
    print("failed to solve: constraints unsatisfiable")
