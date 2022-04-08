import equations
import pandas
import pumps
import pandas as pd

#Error threshold for numerical analysis
error_threshold = 0.001

#Minimum distance of pipe underground
x = 5

def solve_section(diameter, roughness, k, p0, p2, z0, z2, adjacent, target, lifetime, debug):

    #Calculate length of the first section with numerical methods (diameter, roughness, k, z0, adj, debug)
    length0, y = solve_section0(diameter, roughness, p0, z0, adjacent, debug)

    #Calculate length of the second section and the minimum required pump head (diameter, roughness, p2, y, z2, debug)
    length1, pump_head = solve_section1(diameter, roughness, p2, y, z2, debug)

    #Find total length
    total_length = length0 + length1

    #Grab pumps dict into a pandas dataframe
    pumps_dataframe = pd.DataFrame.from_dict(pumps.pumps_dict)
    #Limit the dataframe to pumps which have head above the minimum required head
    pumps_dataframe = pumps_dataframe.loc[pumps_dataframe["head"] >= pump_head]

    #Loop across each viable pump, find minimum cost and power
    pump_capital_cost = None
    pump_operating_cost = None
    pump_total_cost = None
    pump_power = None
    selected_pump = 0
    for pump in pumps_dataframe.iterrows():

        capital_cost = pump[1][2] #Capital cost of purchasing pump in $
        power = pump_head * equations.density * equations.gravity * equations.flow #Hydraulic power required of pump in watts
        power = (power / pump[1][3]) / 1000 #Electrical power required of pump, in kilowatts (taking into account the efficiency)
        operating_cost = power * 3600 * 0.16 #Operating cost in $/hr
        total_operating_cost = operating_cost * 24 * 365 * lifetime #Operating cost over lifetime
        total_cost = capital_cost + total_operating_cost

        if target == "cost":
            if pump_total_cost is None or total_cost < pump_total_cost:
                pump_total_cost = total_cost
                pump_capital_cost = capital_cost
                pump_operating_cost = operating_cost
                pump_power = power
                selected_pump = pump[1]

        elif target == "power":
            if pump_power is None or power < pump_power:
                pump_total_cost = total_cost
                pump_capital_cost = capital_cost
                pump_operating_cost = operating_cost
                pump_power = power
                selected_pump = pump[1]
    
    if(debug): print("Selected pump: ", selected_pump)
    if(debug): print("Capital cost: ", pump_capital_cost, "$")
    if(debug): print("Operating cost: ", pump_operating_cost, "$/hr")
    if(debug): print("Lifetime cost: ", pump_total_cost, "$")
    if(debug): print("Power: ", pump_power, "kW")

    return total_length, pump_capital_cost, pump_operating_cost, pump_total_cost, pump_power, selected_pump

#Use equation 0 to solve for the length of section 0
def solve_section0(diameter, roughness, p0, z0, adj, debug):

    #Initial guess for y0 and initial error
    y = 0
    length = 0
    last_guess = 0
    error = 100
    iter = 0

    while abs(error) > error_threshold:
        #Calcluation of length
        length = (z0 - (60 - x)) + (adj ** 2 + y ** 2) ** 0.5

        #Realculation of y (with equation 1)
        hloss = equations.hloss(length, diameter, roughness)
        y = 62 - z0 - x - p0 + hloss

        #Error calculation:
        error = y - last_guess
        last_guess = y
        iter = iter + 1

    #Restrict y to > 0
    if(y < 0): y = 0

    #Final calcluation of length
    length = (z0 - (60 - x)) + (adj ** 2 + y ** 2) ** 0.5
    if(debug): print("Length of Section 0: ", length)
    if(debug): print("y: ", y)
    if(debug): print("Error: ", error)
    if(debug): print("Iterations: ", iter)

    return length, y

#Use equation 1 to solve section 2
def solve_section1(diameter, roughness, p2, y, z2, debug):

    #Calcluate the length, head loss, and minimum required pump head of the section
    length = z2 - (60 - x - y)
    hloss = equations.hloss(length, diameter, roughness)
    pump_head = z2 - 62 + p2 + hloss + x + y

    if(debug): print("Length of Section 1: ", length)
    if(debug): print("Head loss: ", hloss)
    if(debug): print("Pump head: ", pump_head)

    return length, pump_head

#Find properties of a given combination of pump
def pipe_properties(OD, schedule, material):

    #Declare properly scoped variables
    pipe_cost = None
    wall_thickness = None
    max_pressure = None
    roughness = None

    if schedule == 40:
        wall_thickness = 0.021 * OD + 0.112
        max_pressure = 154.71 #Maximum pressure in m of head, obtained from online calculator https://www.convertunits.com/from/PSI/to/meter+of+head

        if material == "Steel":
            pipe_cost = 10 * OD + 30
            roughness = 0.1 / 1000

        elif material == "PVC":
            pipe_cost = 5 * OD + 40
            roughness = 0.001 / 1000

    elif schedule == 80:
        wall_thickness = 0.039 * OD + 0.14
        max_pressure = 225.04 #Maximum pressure in m of head, obtained from online calculator https://www.convertunits.com/from/PSI/to/meter+of+head

        if material == "Steel":
            pipe_cost = 15 * OD + 60
            roughness = 0.1 / 1000

        elif material == "PVC":
            pipe_cost = 10 * OD + 80
            roughness = 0.001 / 1000

    #Trenching and remediation
    if OD <= 2:
        pipe_cost += 35

    elif OD > 2:
        pipe_cost += 50

    diameter = (OD - (2 * wall_thickness)) * 0.0254 #Inner diameter in metres

    return diameter, roughness, pipe_cost, max_pressure