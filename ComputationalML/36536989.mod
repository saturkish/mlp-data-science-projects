param n := 47;  # Number of hours

set i := {0..n};  # Time index

param a{i};  # Cost coefficient a
param b{i};  # Cost coefficient b

param Tlwb{i};  # Lower bound of temperature
param Tupb{i};  # Upper bound of temperature
param Topt{i};  # Ideal temperature
param Tout{i};  # Outside temperature

param PenaltyCoefficient >= 0;  # Penalty for deviation from Topt

var q{i} >= 0, <= 100;  # Percentage of air replaced (0-100%)
var cost;  # Electricity cost

var Tinside{i};  # Inside temperature
var dev{i} >= 0;  # Deviation from the ideal temperature

# Objective: Minimize electricity cost + penalty for deviation
minimize total_cost: 
    sum {xx in i} (a[xx] * (q[xx]^3) / 1000 + b[xx] * q[xx]) 
    + PenaltyCoefficient * sum {xx in i} dev[xx];

# Constraints for temperature changes
s.t. initialTemp: Tinside[0] = 19;

s.t. tempUpdate{xx in i diff {0}}:  # Updating temperature for t > 0
    Tinside[xx] = (1 - q[xx] / 100) * Tinside[xx-1] + (q[xx] / 100) * Tout[xx];

# Temperature constraints
s.t. lowerBound{xx in i}: Tinside[xx] >= Tlwb[xx];
s.t. upperBound{xx in i}: Tinside[xx] <= Tupb[xx];

# Deviation from the optimal temperature constraints
s.t. deviationDef1{xx in i}: dev[xx] >= Tinside[xx] - Topt[xx];
s.t. deviationDef2{xx in i}: dev[xx] >= Topt[xx] - Tinside[xx];

# Compute electricity cost separately
s.t. costDef: 
    cost = sum {xx in i} (a[xx] * (q[xx]^3) / 1000 + b[xx] * q[xx]);
