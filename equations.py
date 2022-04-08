import math

density = 995.27 #kg/m^3, average for water at 20-40C
gravity = 9.81 #m/s^2
viscosity = 0.0008272 #N*s/m^2, average for water at 20-40C
PI = math.pi

#Calculate Q:
flow = (15000 * 15 + 12000 * 45 + 5000 * 80) * 4 #In kWh/yr
flow = flow * 3600 #Convert to kJ/yr
flow = flow / (365 * 24 * 3600) #Convert to kJ/s
flow = flow / (4.2 * 20 * density) #Convert to m^3/s

#Intake a minimum pressure in pascals, find the pressure before and after the heat exchanger in m of head
def pressures(diameter, k, min_pressure):
    p0_head = min_pressure / (density * gravity)
    v = velocity(diameter)
    p2_head = p0_head + (k * (v ** 2)) / (2 * gravity)
    return p0_head, p2_head

#Calculate loss of head due to friciton
def hloss(length, diameter, roughness):
    v = velocity(diameter)
    f = friction(length, diameter, roughness)
    hl = (f * length * (v ** 2)) / (2 * diameter * gravity)
    return hl

#Calculate friction factor
def friction(length, diameter, roughness):
    re = reynolds(length, diameter)
    f = (-1.8 * math.log((((roughness / diameter) / 3.7) ** 1.11 + (6.9 / re)), 10)) ** -2
    return f

#calculate reynolds number
def reynolds(length, diameter):
    v = velocity(diameter)
    re = (density * (v ** 2) * length) / viscosity
    return re

#Calculate velocity
def velocity(diameter):
    v = (4 * flow) / ((diameter ** 2) * PI)
    return v


