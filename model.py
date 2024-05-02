#### Load necessary packages 



#### Import python scrips
from data_generation import *

# Erzeuge Sets für das Gurobi Modell - eventuall als load function schreiben? 
# Planungshorizont
T = [i for i in range(0,30)]

#Produktfamilien 
F =  [i for i in range(0,4)]

#Scenarios 
S = [i for i in range(0,243)]

# Family types
FT = [0,1]

#Manufacturing Plants
MP = [i for i in range(0,4)]

# Produktion camp. types
CT = [0,1]

# Distribution centers

L = [i for i in range(0,9)]

### Get the needede parameters

data = Parameters(T,F,S,FT,MP,CT,L)