#### Load necessary packages 



#### Import python scrips
from data_generation import *

# Defining the parameters for the model
# Planungshorizont (days)
T_end = 30

# Produktfamilien 
F_end = 4

# Scenarios 
S_end = 243

# Family types
FT_values = [0, 1]

# Manufacturing Plants
MP_end = 4

# Produktion camp. types
CT_values = [0, 1]

# Distribution centers
L_end = 9

# Erzeuge Sets für das Gurobi Modell - eventuell als load function schreiben?
T = [i for i in range(T_end)]
F = [i for i in range(F_end)]
S = [i for i in range(S_end)]
FT = FT_values
MP = [i for i in range(MP_end)]
CT = CT_values
L = [i for i in range(L_end)]

### Get the needed parameters

data = Parameters(T,F,S,FT,MP,CT,L)

print(data.cmin)