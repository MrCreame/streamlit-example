import re
import pandas as pd
import decimal
import math

# Import Main EA Excel
df_main = pd.read_excel(EA_Data.xlsx)

# Import Input File
df_input = pd.read_csv(Test_ini_v0.csv)

# Extract Values from Input File
fit = int(df_input.iloc[0][0].split(":")[1])
boundary_in =str((df_input.iloc[1][0].split(":")[1]))
boundary = boundary_in.replace(" ", "")
current_value = float(df_input.iloc[2][0].split(":")[1])
dimension_in = str((df_input.iloc[3][0].split(":")[1]))
dimension = dimension_in.replace(" ", "")

# Get row of chosen fit location
rows = df_main.loc[df_main['Fit'] == fit]
if rows.empty == True:
    print("Fit has never been requested before. Please send ENC Information to J.Kremer after submitting.")
else:
    # Choose comparable dimensions - Leerzeichen müssen so bleiebn
    # todo: extraction change for strings due to string function
    if boundary == "Min" or "min":
        vals_compare_mm = rows.loc[:,"Min_EA[mm]"]
        val_basis_mm = rows.loc[:,"Min_manual[mm]"]
        vals_compare_in = rows.loc[:, "Min_EA[in]"]
        val_basis_in = rows.loc[:, "Min_manual[in]"]
    elif boundary == "Max" or "max":
        vals_compare_mm = rows.loc[:, "Max_manual[mm]"]
        val_basis_mm = rows.loc[:, "Max_manual[mm]"]
        vals_compare_in = rows.loc[:, "Max_EA[in]"]
        val_basis_in = rows.loc[:, "Max_manual[in]"]

    # Vorzeichenvariable - wenn Max (+) wenn Min (-)
    min_max_switch = 0
    if current_value < 0:
        min_max_switch = -1
    else:
        min_max_switch = 1

    # Check round-off rules if applicable - round rule = 1 = yes & 0 = no
    d = decimal.Decimal(str(val_basis_mm.iloc[0]))
    dec_check = abs(d.as_tuple().exponent)
    if dec_check == 3:
        round_rule = 1
    else:
        round_rule = 0

    # if round-off = True -> Check for other dimension
    if dimension == "mm" and round_rule == 1:
        current_value_ro_in = current_value/25.4
        current_value_ro = round(current_value_ro_in,3)*min_max_switch
    elif dimension == "in" and round_rule == 1:
        current_value_ro_in = current_value * 25.4
        current_value_ro = round(current_value_ro_in, 3)*min_max_switch
    elif round_rule == 0:
        current_value_ro = current_value*min_max_switch

    def ea_compare(dim, cw):
        # compare current value with EA boundary and manual boundary
        # 0 = larger than EA / 1 = Equal to EA / 1.5 = Zwischen EA und Manual / 2 = Kleiner oder gleich als Manual  / 3 = Nan Wert (existiert dann wenn die EA die Dimension nicht freigibt)
        i = 0
        j = 0
        hit = []
        if dim == "mm":
            j = int(vals_compare_mm.size)
            compare = vals_compare_mm*min_max_switch
        elif dim == "in":
            j = int(vals_compare_in.size)
            compare = vals_compare_in*min_max_switch

        while i < j:
            if cw > compare.iloc[i]:
                hit.append(0)
                i += 1
            elif cw == compare.iloc[i]:
                hit.append(1)
                i += 1
            elif cw < compare.iloc[i] and cw > float(d*min_max_switch):
                hit.append(1.5)
                i += 1
            elif cw <= float(d*min_max_switch):
                hit.append(2)
                i += 1
            elif math.isnan(compare.iloc[i]) == True:
                hit.append(3)
                i += 1
        return hit

    check_vals = ea_compare(dim=dimension, cw= current_value*min_max_switch)
    # Gedanke: Es soll immer nur eine EA mit den maximalsten Limits existieren in der Datenbank
    if 1 in check_vals:
        print("EA was found")
        index = check_vals.index(1)
        x = 0
        print(rows["EA"].iloc[index])
        print(rows["ENC"].iloc[index])
    elif 1.5 in check_vals:
        print("Fit lies between max. EA and Manual")
        index = check_vals.index(1.5)
        x = 0
        print(rows["EA"].iloc[index])
        print(rows["ENC"].iloc[index])
    elif 2 in check_vals:
        print("Dimension seems to be in Manual Limits, please re-check before raising ENC.")
    elif 0 in check_vals:
        if dimension == " mm":
            check_vals = ea_compare(dim=" in", cw= current_value_ro)
        else:
            check_vals = ea_compare(dim=" mm", cw= current_value_ro)

        if 1 in check_vals:
            print("EA was found")
            index = check_vals.index(1)
            x = 0
            print(rows["EA"].iloc[index])
            print(rows["ENC"].iloc[index])
        elif 1.5 in check_vals:
            print("Fit lies between max. EA and Manual")
            index = check_vals.index(1.5)
            x = 0
            print(rows["EA"].iloc[index])
            print(rows["ENC"].iloc[index])
        elif 2 in check_vals:
            print("Dimension seems to be in Manual Limits, please re-check before raising ENC.")
        elif 0 in check_vals:
            print("Limit excceds known EAs, consider a new ENC and report result to J.Kremer for database extension.")
    y = 0
