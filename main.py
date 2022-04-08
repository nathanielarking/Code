import equations
import solvers
import pumps
import heat_exchangers
import pandas as pd

min_pressure = 101.3 * 1000 #Minimum pressure of system in Pa
lifetime = 50 #Lifetime of project in years

#Optimize pumps for cost or power
target = "power" 
#target = "cost"

if __name__ == '__main__':

    #Get heat exchangers in df
    heat_exchangers_dataframe = pd.DataFrame.from_dict(heat_exchangers.heat_exchangers_dict)

    #Scope lists of optimal designs
    minimum_capital_cost_design = None
    minimum_operating_cost_design = None
    minimum_lifetime_cost_design = None
    minimum_power_design = None

    #Open output file
    with open("results.txt", "w") as file:
        #For every possible combination of pipe and heat exchanger
        for OD in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]:
            for schedule in [40, 80]:
                for material in ["Steel", "PVC"]:
                    for hx in heat_exchangers_dataframe.iterrows():

                        file.write("----------------------------------------------------------------------------------------------\n")

                        #Turn false only if there are errors with the optimization
                        successful = True

                        #Based on pipe properties, find the max pressure, wall thickness, cost/m, and roughness
                        diameter, roughness, pipe_cost, max_pressure = solvers.pipe_properties(OD, schedule, material)
                        #print(diameter, roughness, pipe_cost, maximum_pressure)

                        #Get k of hx
                        k = hx[1][2]

                        #Calculating pressures (in head) before and after heat exchanger
                        p0, p2 = equations.pressures(diameter, k, min_pressure)
                        #Check if p2 is over max pressure
                        if p2 > max_pressure:
                            #Write to file that design is not feasible
                            file.write(f"Using OD of {OD} inch schedule {schedule} {material} pipe with {hx[1][0]} heat exchanger\n")
                            file.write(f"Design unsuccessful. Maximum pressure of system exceeds maximum pressure of pipe by {p2 - max_pressure}m of head")
                            file.write("\n\n\n")
                            successful = False

                        #Solve each section, returning an error if the design is not feasible
                        if successful:
                            try: 
                                length0, pump_capital_cost0, pump_operating_cost0, pump_total_cost0, pump_power0, selected_pump0 = solvers.solve_section(diameter, roughness, k, p0, p2, 72, 63, 800, target, lifetime, False)
                                length1, pump_capital_cost1, pump_operating_cost1, pump_total_cost1, pump_power1, selected_pump1 = solvers.solve_section(diameter, roughness, k, p0, p2, 63, 93, 400, target, lifetime, False)
                                length2, pump_capital_cost2, pump_operating_cost2, pump_total_cost2, pump_power2, selected_pump2 = solvers.solve_section(diameter, roughness, k, p0, p2, 93, 75, 800, target, lifetime, False)
                                length3, pump_capital_cost3, pump_operating_cost3, pump_total_cost3, pump_power3, selected_pump3 = solvers.solve_section(diameter, roughness, k, p0, p2, 75, 72, 500, target, lifetime, False)
                            except OverflowError:
                                #Write to file that the head loss cannot be compensated for by slant
                                file.write(f"Using OD of {OD} inch schedule {schedule} {material} pipe with {hx[1][0]} heat exchanger\n")
                                file.write(f"Design unsuccessful. Numerical analysis of slant required to overcome head loss due to friction diverges")
                                file.write("\n\n\n")
                                successful = False
                                break

                        if successful:
                            try:
                                #Find total capital cost, operating cost, and power
                                total_length = length0 + length1 + length2 + length3
                                total_pipe_cost = pipe_cost * total_length
                                total_pump_capital_cost = pump_capital_cost0 + pump_capital_cost1 + pump_capital_cost2 + pump_capital_cost3
                                total_capital_cost = total_pipe_cost + total_pump_capital_cost + hx[1][1]

                                total_operating_cost = pump_operating_cost0 + pump_operating_cost1 + pump_operating_cost2 + pump_operating_cost3

                                total_pump_lifetime_cost = pump_total_cost0 + pump_total_cost1 + pump_total_cost2 + pump_total_cost3
                                total_lifetime_cost = total_pump_lifetime_cost + total_pipe_cost + hx[1][1]

                                total_power = pump_power0 + pump_power1 + pump_power2 + pump_power3

                            except TypeError:
                                #Write to file that design is not feasible
                                file.write(f"Using OD of {OD} inch schedule {schedule} {material} pipe with {hx[1][0]} heat exchanger\n")
                                file.write(f"Design unsuccessful. Head required by pump exceeds that of pumps available at the given flow rate")
                                file.write("\n\n\n")
                                successful = False

                        if successful:

                            #Output to file
                            file.write(f"Using OD of {OD} inch schedule {schedule} {material} pipe with {hx[1][0]} heat exchanger\n")
                            file.write(f"Total length of pipe: {total_length}m\n")
                            file.write(f"Total capital cost: ${total_capital_cost}\n")
                            file.write(f"Total operating cost: ${total_operating_cost}/hr\n")
                            file.write(f"Total lifetime cost over {lifetime} years: ${total_lifetime_cost}\n")
                            file.write(f"Total power consumption: {total_power}kW\n")
                            file.write(f"Section 1 uses {length0}m of pipe with the {selected_pump0[0]} {selected_pump0[1]}RPM pump\n")
                            file.write(f"Section 2 uses {length1}m of pipe with the {selected_pump1[0]} {selected_pump1[1]}RPM pump\n")
                            file.write(f"Section 3 uses {length2}m of pipe with the {selected_pump2[0]} {selected_pump2[1]}RPM pump\n")
                            file.write(f"Section 4 uses {length3}m of pipe with the {selected_pump3[0]} {selected_pump3[1]}RPM pump\n")

                            file.write("\n\n\n")

                            #Check if this design is optimal and if so, save it
                            if minimum_capital_cost_design is None or total_capital_cost < minimum_capital_cost_design[5]:
                                minimum_capital_cost_design = [OD, schedule, material, hx[1][0], total_length, total_capital_cost, total_operating_cost, lifetime, total_lifetime_cost, total_power, 
                                                            length0, selected_pump0[0], selected_pump0[1],
                                                            length1, selected_pump1[0], selected_pump1[1],
                                                            length2, selected_pump2[0], selected_pump2[1],
                                                            length3, selected_pump3[0], selected_pump3[1]]

                            if minimum_operating_cost_design is None or total_operating_cost < minimum_operating_cost_design[6]:
                                minimum_operating_cost_design = [OD, schedule, material, hx[1][0], total_length, total_capital_cost, total_operating_cost, lifetime, total_lifetime_cost, total_power, 
                                                            length0, selected_pump0[0], selected_pump0[1],
                                                            length1, selected_pump1[0], selected_pump1[1],
                                                            length2, selected_pump2[0], selected_pump2[1],
                                                            length3, selected_pump3[0], selected_pump3[1]]

                            if minimum_lifetime_cost_design is None or total_lifetime_cost < minimum_lifetime_cost_design[8]:
                                minimum_lifetime_cost_design = [OD, schedule, material, hx[1][0], total_length, total_capital_cost, total_operating_cost, lifetime, total_lifetime_cost, total_power, 
                                                            length0, selected_pump0[0], selected_pump0[1],
                                                            length1, selected_pump1[0], selected_pump1[1],
                                                            length2, selected_pump2[0], selected_pump2[1],
                                                            length3, selected_pump3[0], selected_pump3[1]]

                            if minimum_power_design is None or total_power < minimum_power_design[9]:
                                minimum_power_design = [OD, schedule, material, hx[1][0], total_length, total_capital_cost, total_operating_cost, lifetime, total_lifetime_cost, total_power, 
                                                            length0, selected_pump0[0], selected_pump0[1],
                                                            length1, selected_pump1[0], selected_pump1[1],
                                                            length2, selected_pump2[0], selected_pump2[1],
                                                            length3, selected_pump3[0], selected_pump3[1]]

    #Output optimal designs to file
    with open(f"optimal_{target}_results.txt", "w") as file:
        file.write("----------------------------------------------------------------------------------------------\n")
        file.write("Design that is optimized for capital cost:\n")
        file.write(f"OD of {minimum_capital_cost_design[0]} inch schedule {minimum_capital_cost_design[1]} {minimum_capital_cost_design[2]} pipe with {minimum_capital_cost_design[3]} heat exchanger\n")
        file.write(f"Total length of pipe: {minimum_capital_cost_design[4]}m\n")
        file.write(f"Total capital cost: ${minimum_capital_cost_design[5]}\n")
        file.write(f"Total operating cost: ${minimum_capital_cost_design[6]}/hr\n")
        file.write(f"Total lifetime cost over {minimum_capital_cost_design[7]} years: ${minimum_capital_cost_design[8]}\n")
        file.write(f"Total power consumption: {minimum_capital_cost_design[9]}kW\n")
        file.write(f"Section 1 uses {minimum_capital_cost_design[10]}m of pipe with the {minimum_capital_cost_design[11]} {minimum_capital_cost_design[12]}RPM pump\n")
        file.write(f"Section 2 uses {minimum_capital_cost_design[13]}m of pipe with the {minimum_capital_cost_design[14]} {minimum_capital_cost_design[15]}RPM pump\n")
        file.write(f"Section 3 uses {minimum_capital_cost_design[16]}m of pipe with the {minimum_capital_cost_design[17]} {minimum_capital_cost_design[18]}RPM pump\n")
        file.write(f"Section 4 uses {minimum_capital_cost_design[19]}m of pipe with the {minimum_capital_cost_design[20]} {minimum_capital_cost_design[21]}RPM pump\n")
        file.write("\n\n\n")

        file.write("----------------------------------------------------------------------------------------------\n")
        file.write("Design that is optimized for operating cost:\n")
        file.write(f"OD of {minimum_operating_cost_design[0]} inch schedule {minimum_operating_cost_design[1]} {minimum_operating_cost_design[2]} pipe with {minimum_operating_cost_design[3]} heat exchanger\n")
        file.write(f"Total length of pipe: {minimum_operating_cost_design[4]}m\n")
        file.write(f"Total capital cost: ${minimum_operating_cost_design[5]}\n")
        file.write(f"Total operating cost: ${minimum_operating_cost_design[6]}/hr\n")
        file.write(f"Total lifetime cost over {minimum_operating_cost_design[7]} years: ${minimum_operating_cost_design[8]}\n")
        file.write(f"Total power consumption: {minimum_operating_cost_design[9]}kW\n")
        file.write(f"Section 1 uses {minimum_operating_cost_design[10]}m of pipe with the {minimum_operating_cost_design[11]} {minimum_operating_cost_design[12]}RPM pump\n")
        file.write(f"Section 2 uses {minimum_operating_cost_design[13]}m of pipe with the {minimum_operating_cost_design[14]} {minimum_operating_cost_design[15]}RPM pump\n")
        file.write(f"Section 3 uses {minimum_operating_cost_design[16]}m of pipe with the {minimum_operating_cost_design[17]} {minimum_operating_cost_design[18]}RPM pump\n")
        file.write(f"Section 4 uses {minimum_operating_cost_design[19]}m of pipe with the {minimum_operating_cost_design[20]} {minimum_operating_cost_design[21]}RPM pump\n")
        file.write("\n\n\n")

        file.write("----------------------------------------------------------------------------------------------\n")
        file.write(f"Design that is optimized for lifetime cost over {lifetime} years:\n")
        file.write(f"OD of {minimum_lifetime_cost_design[0]} inch schedule {minimum_lifetime_cost_design[1]} {minimum_lifetime_cost_design[2]} pipe with {minimum_lifetime_cost_design[3]} heat exchanger\n")
        file.write(f"Total length of pipe: {minimum_lifetime_cost_design[4]}m\n")
        file.write(f"Total capital cost: ${minimum_lifetime_cost_design[5]}\n")
        file.write(f"Total operating cost: ${minimum_lifetime_cost_design[6]}/hr\n")
        file.write(f"Total lifetime cost over {minimum_lifetime_cost_design[7]} years: ${minimum_lifetime_cost_design[8]}\n")
        file.write(f"Total power consumption: {minimum_lifetime_cost_design[9]}kW\n")
        file.write(f"Section 1 uses {minimum_lifetime_cost_design[10]}m of pipe with the {minimum_lifetime_cost_design[11]} {minimum_lifetime_cost_design[12]}RPM pump\n")
        file.write(f"Section 2 uses {minimum_lifetime_cost_design[13]}m of pipe with the {minimum_lifetime_cost_design[14]} {minimum_lifetime_cost_design[15]}RPM pump\n")
        file.write(f"Section 3 uses {minimum_lifetime_cost_design[16]}m of pipe with the {minimum_lifetime_cost_design[17]} {minimum_lifetime_cost_design[18]}RPM pump\n")
        file.write(f"Section 4 uses {minimum_lifetime_cost_design[19]}m of pipe with the {minimum_lifetime_cost_design[20]} {minimum_lifetime_cost_design[21]}RPM pump\n")
        file.write("\n\n\n")

        file.write("----------------------------------------------------------------------------------------------\n")
        file.write("Design that is optimized for power consumption:\n")
        file.write(f"OD of {minimum_power_design[0]} inch schedule {minimum_power_design[1]} {minimum_power_design[2]} pipe with {minimum_power_design[3]} heat exchanger\n")
        file.write(f"Total length of pipe: {minimum_power_design[4]}m\n")
        file.write(f"Total capital cost: ${minimum_power_design[5]}\n")
        file.write(f"Total operating cost: ${minimum_power_design[6]}/hr\n")
        file.write(f"Total lifetime cost over {minimum_power_design[7]} years: ${minimum_power_design[8]}\n")
        file.write(f"Total power consumption: {minimum_power_design[9]}kW\n")
        file.write(f"Section 1 uses {minimum_power_design[10]}m of pipe with the {minimum_power_design[11]} {minimum_power_design[12]}RPM pump\n")
        file.write(f"Section 2 uses {minimum_power_design[13]}m of pipe with the {minimum_power_design[14]} {minimum_power_design[15]}RPM pump\n")
        file.write(f"Section 3 uses {minimum_power_design[16]}m of pipe with the {minimum_power_design[17]} {minimum_power_design[18]}RPM pump\n")
        file.write(f"Section 4 uses {minimum_power_design[19]}m of pipe with the {minimum_power_design[20]} {minimum_power_design[21]}RPM pump\n")