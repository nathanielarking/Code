import equations
import solvers
import pumps
import heat_exchangers
import pandas as pd

min_pressure = 100 * 1000
lifetime = 50 #lifetime of project in years

#Optimize pumps for cost or power
#target = "power" 
target = "cost"

if __name__ == '__main__':

    #Get heat exchangers in df
    heat_exchangers_dataframe = pd.DataFrame.from_dict(heat_exchangers.heat_exchangers_dict)

    #For every possible combination of pipe and heat exchanger
    for OD in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]:
        for schedule in [40, 80]:
            for material in ["Steel", "PVC"]:
                for hx in heat_exchangers_dataframe.iterrows():

                    #Based on pipe properties, find the max pressure, wall thickness, cost/m, and roughness
                    diameter, roughness, pipe_cost, maximum_pressure = solvers.pipe_properties(OD, schedule, material)

                    #Get k of hx
                    k = hx[1][2]
                    print(k)

                    #Calculating pressures (in head) before and after heat exchanger
                    p0, p2 = equations.pressures(diameter, k, min_pressure)
                    #Check if p2 is over max pressure

                    #Solve each section
                    length0, pump_capital_cost0, pump_operating_cost0, pump_total_cost0, selected_pump0 = solvers.solve_section(diameter, roughness, k, p0, p2, 72, 63, 800, target, lifetime, False)
                    length1, pump_capital_cost1, pump_operating_cost1, pump_total_cost1, selected_pump1 = solvers.solve_section(diameter, roughness, k, p0, p2, 63, 93, 400, target, lifetime, False)
                    length2, pump_capital_cost2, pump_operating_cost2, pump_total_cost2, selected_pump2 = solvers.solve_section(diameter, roughness, k, p0, p2, 93, 75, 800, target, lifetime, False)
                    length3, pump_capital_cost3, pump_operating_cost3, pump_total_cost3, selected_pump3 = solvers.solve_section(diameter, roughness, k, p0, p2, 75, 72, 500, target, lifetime, False)

                    #Find total capital cost, operating cost, and power

                    #Output to file


    


