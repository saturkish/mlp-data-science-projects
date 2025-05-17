# Set of machines, components, and heads
set MACHINES := {1, 2, 3};  # Three machines
set HEADS := {1..9};
set COMPONENTS := {1..102};
set FEEDERS := {1..10};



set COMPATIBLE_HEADS{COMPONENTS};

# Coordinates of components and feeders
param X{COMPONENTS};
param Y{COMPONENTS};

param XF{FEEDERS};  # X-coordinates of feeders
param YF{FEEDERS};  # Y-coordinates of feeders

param component_coords{c in COMPONENTS, d in 1..2} :=
  if d = 1 then X[c]
  else Y[c];

param component_feeders{f in FEEDERS, d in 1..2} :=
  if d = 1 then X[f]
  else Y[f];

#param machine_of_head{h in HEADS};



#param upper_limit{COMPONENTS};
param upper_limit default 1;

# Binary variable to represent whether head i is assigned to component j
var x{h in HEADS, c in COMPONENTS} binary;

# Variable to keep track of the number of components assigned to each machine
var machine_workload{MACHINES} >= 0;

# Distance calculation between two points

# Objective: Minimize the total distance moved by all heads
minimize total_distance:
    sum {m in MACHINES, h in HEADS, c in COMPONENTS} x[m, h, c];

# Constraint to ensure each component is placed exactly once
subject to single_assignment{c in COMPONENTS}:
    sum {h in COMPATIBLE_HEADS[c]} x[h, c] = 1;

#each head can only place one component per cycle
subject to head_capacity{h in HEADS}:
    sum {c in COMPONENTS: h in COMPATIBLE_HEADS[c]} x[h, c] <= 1;
    
# Constraint for head compatibility
subject to head_compatibility{h in HEADS, c in COMPONENTS}:
    x[h, c] = 0  if h not in COMPATIBLE_HEADS[c];

# Constraint to respect upper limits on component quantities
subject to upper_limit_constraint{c in COMPONENTS}:
    sum {m in MACHINES, h in HEADS} x[m, h, c] <= upper_limit;
    
# Constraint to balance the workload between machines
subject to balance_workload{m in MACHINES}:
    machine_workload[m] = sum {h in HEADS, c in COMPONENTS} x[m, h, c];

# Ensure that each head can only carry one component at a time
subject to head_capacity{m in MACHINES, h in HEADS}:
    sum {c in COMPONENTS} x[m, h, c] <= 1;

