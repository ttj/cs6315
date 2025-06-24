# install z3 python setup
# package name: z3-solver
# 
# manual install: https://github.com/Z3Prover/z3
#
# PS C:\Users\taylo\Dropbox\Class\eecs6315> pip install z3-solver
# Collecting z3-solver
#  Downloading z3_solver-4.8.10.0-py2.py3-none-win_amd64.whl (35.5 MB)
# Installing collected packages: z3-solver
# Successfully installed z3-solver-4.8.10.0
#
# run:
# python .\eecs6315-lecture16-2021-03-23-bmc_fsm_counter.py

from z3 import *

# bounded model checking applied to counter example
# other examples can be checked by redefining the bad states, initial states, and step and time transition relations appropriately, etc.

# control locations defined as an enumeration datatype
ControlLocation = Datatype('Location')

ControlLocation.declare('off')
ControlLocation.declare('on')
ControlLocation = ControlLocation.create()

length = 15 # k: number of transition relation steps to unroll

s = Solver() # instantiate a solver

opt_debug = True

# alternative encoding of transition relation: 
# checks if each transition is enabled, then 
# essentially constructs a tree of each 
# execution path
opt_trans_enabled = False

# number of bits to use in encoding counter x
bits = 64

x=[] # list of steps for counter variable x
q=[] # list of steps for control location
press=[] # list of steps for press variable press

reachedList = []
reachedAllList = []

# allocate 1st vars
x.append( BitVec('x0', bits ) ) # counter variable
# x[0] : equals x0: value of x at step 0 (initial value)
# x[1] : equals x1: value of x at step 1
q.append( Const('q0',  ControlLocation) ) # control location
press.append( Const('press0', BoolSort() )) # press variable

reachedList.append( [] ) # append empty list (stores reach sets this direction)

# bounded model checking for bound iterations
def bmc(bound):
    initList = []
    # note: leave input press unconstrained (so it can always be either true or false)
    initList.append( And( q[0] == ControlLocation.off, x[0] == 0 ) ) # q0 = off /\ x0 = 0
    if len(initList) > 1:
        init = And( initList )
    else:
        init = initList[0]
    
    reachedOld = False # no states reached in iteration 0-1
    reachedOldAll = init
    reachedAll = init
    #reachedAllList.append( reachedAll )
    reached = init
    reachedList[0].append(init)
    
    terminate = 0
    fp = False
    
    # k is the iteration
    for k in range(bound):
    
        # allocate new variables lazily / on-the-fly
        x.append( BitVec('x' + str(k+1), bits ) ) # continuous variable
        q.append( Const('q'+ str(k+1),  ControlLocation) ) # control location
        press.append( Const('press'+ str(k+1), BoolSort() )) # press variable

        reachedList.append( [] ) # append empty list (stores reach sets this iteration)

        if terminate >= 1 or len(reachedList[k]) == 0:
            print("Termination condition reached")
            break
        
        # write bad states in terms of the k^th iteration variables
        # this is the negation of the property
        badList = []
        #badList.append( q[k] == ControlLocation.on );
        #badList.append( x[k] >= 5 );
        badList.append( x[k] >= 10 );
        
        if len(badList) > 1:
            bad = Or( badList )
        else:
            bad = badList[0]
        
        nt = len(reachedList[k])
        rt = 1
        
        reachedOldAll = reachedAll
        if len(reachedList[k]) > 1:
            print('trans')
            reachedAll = Or(reachedList[k])
        else:
            print('reachedList')
            print(reachedList)
            reachedAll = reachedList[k][0]
        reachedAllList.append( reachedAll )
        
        if k >= bound - 1:
            print("Terminated without finding a path to bad states after " + str( k ) + " iterations.")
            break
        
        if fp:
            print("Terminating by finding fixpoint, unsafe states not found, safe (for any k)")
            break

        reachedBad = And(reachedAll, bad)
        if opt_debug:
            print("\n\nBMC check: ")
            print(reachedBad)
            print("\n\n")
        s.push() # save context
        s.add(reachedBad) # assert in smtlib
        result = s.check() # check in smtlib

        #print result
        if result == sat:
            print("UNSAFE")
            print("Old:\n")
            print(reachedOldAll)
            print("\nNew:\n")
            print(reachedAll)
            print("\nBad check:\n")
            print(reachedBad)
            print(s.model())
            print("Bad states reached after " + str( k ) + " iterations.")
            print(bad)
            
            model = s.model()
            print(os.linesep)
            print("Counterexample trace:")
            print(model)
            for i in range(0, k+1):    
                print("step " + str(i) + "/" + str(k) + " state:")
                print("mode: " + str(model[q[i]]))
                print("x: " + str(model[x[i]]))
                print("press: " + str(model[press[i]]))
            break

        # must be done after getting model, etc
        s.pop() # restore context
        
        if k >= 1:
            s.push() # save context for fixpoint check
            if opt_debug:
                print("old:\n\n")
                print(reachedOldAll)
                print("new:\n\n")
                print(reachedAll)
                print("\n\n\n")

            # this fixedpoint check is over all reachable states
            # for efficiency, probably want to consider frontier only; otherwise, probably want to project away all step indices (e.g., just variable name, not keeping track of step)
            fixedPoint = Implies( reachedAllList[k], substitute(reachedAllList[k-1], (q[k-1],q[k]), (x[k-1],x[k]), (press[k-1],press[k]) ) )
#            reachProjectedLast = []
#            reachProjectedCurrent = []
#            for j in range(1,k+1):
#                print(j)
#                reachProjectedLast.append( substitute(reachedAllList[j-1], (q[j-1],q[0]), (x[j-1],x[0]), (press[j-1],press[0]) ))
#                reachProjectedCurrent.append( substitute(reachedAllList[j], (q[j],q[0]), (x[j],x[0]), (press[j],press[0])))
#            print(reachProjectedLast)
#            print(reachProjectedCurrent)
#            fixedPoint = Implies( Or(reachProjectedLast), Or(reachProjectedCurrent) )

            # TODO: probably need to substitute all indices away instead of only k-1, would want to have cached this from prior iterations
            
            print(fixedPoint)
            
            s.add( Not(fixedPoint) ) # validity check
            result = s.check()
            
            if result == unsat: # valid if negation unsat
                print("TERMINATING: FIXED POINT")
                fp = True
                terminate = 1
#            if k >= 5:
#                break
            s.pop() # restore context from fixpoint check
        
        for reached in reachedList[k]:
            print("k=" + str(k) + " nt=" + str(nt) + " rt=" + str(rt))
            if opt_debug:
                print(reached)
            
            if k >= 1 and result == unsat:# and rt >= nt:
                print("Old:\n")
                print(reachedOldAll)
                print("\nNew:\n")
                print(reachedAll)
                print("Fixedpoint:\n")
                print(fixedPoint)
                terminate = 1
                print("SAFE after " + str(k) + " iterations")
                break
            else:
                reachedOld = reached
                ts = []
                if k < bound - 1: # termination
                    ts.extend( stepTransition(k) )
                    
                # check if each transition enabled, 
                # then only consider each of these transitions
                if opt_trans_enabled:
                    #tnum = 0
                    for t in ts:
                        treached = simplify(And(reached, t))
                        s.push()
                        s.add(treached)
                        res = s.check()
                        if True:#opt_debug:
                            print("transition can be taken? " + str(res))
                            print(treached)
                            if res == sat:
                                print(s.model())
                        s.pop()
                    
                        # only explore enabled transitions, no reason to continue down a branch if transitions cannot be taken
                        if res == sat:
                            reachedList[k+1].append( treached )
                        #tnum = tnum + 1
                # just use disjunct of all transitions 
                # instead of tracking which are enabled
                else:
                    reachedList[k+1].append( simplify(And(reached, Or(ts))))
            rt = rt + 1

    return 0

# create transition relation for step k
# directly encodes symbolic transition relation
# at step k for this specific example
#
# other examples could be handled by defining this 
# transition relation differently (replace elements of ts)
def stepTransition(k):
    ts = [] # list of transitions
    count_max = 10 # counter maximum value

    # off -> off
    ts.append(  And(q[k] == ControlLocation.off, Not(press[k]), q[k+1] == ControlLocation.off, x[k+1] == x[k]) )

    # off -> on
    ts.append(  And(q[k] == ControlLocation.off, press[k], q[k+1] == ControlLocation.on, x[k+1] == x[k]) )

    # on -> on
    #ts.append(  And(q[k] == ControlLocation.on, Not(press[k]), q[k+1] == ControlLocation.on, x[k+1] == x[k] + 1) )
    ts.append(  And(q[k] == ControlLocation.on, Not(press[k]), x[k] < count_max, q[k+1] == ControlLocation.on, x[k+1] == x[k] + 1) )

    # on -> off
    ts.append(  And(q[k] == ControlLocation.on, Or(press[k], x[k] >= count_max), q[k+1] == ControlLocation.off, x[k+1] == 0) )
    
    if opt_debug:
        print(ts)

# from nuxmv representation   
#    ((mode = off & !press) -> (next(mode) = off & next(x) = x)) &
#    ((mode = off & press) -> (next(mode) = on & next(x) = x)) &
#    ((mode = on & !press) & x < count_max -> (next(mode) = on & next(x) = x + 1)) &
#    ((mode = on & (press | x >= count_max)) -> (next(mode) = off & next(x) = 0));
    return ts


# call BMC for length iterations
bmc(length)


