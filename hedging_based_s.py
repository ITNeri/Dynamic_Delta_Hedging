from delta_hedging_mc import Hedging, EuropeanOption
import pandas as pd


def ds(name, s0, k, dt, r, sig, m, towards, number, start_date, end_date):  # delta s = (s(a) - s(a-1)) / s(a-1)
    one_path = Hedging(name, s0, k, dt, r, sig, m, towards, number, start_date, end_date)
    list_stock = one_path.fixed_stock_path_1
    l_0 = []  # list of s(a-1)
    l_1 = []  # list of s(a)
    l_ds = [0]  # list of delta s

    for i in range(0, m - 1):
        s_0_value = list_stock[i]
        l_0.append(s_0_value)

    for j in range(1, m):
        s_1_value = list_stock[j]
        l_1.append(s_1_value)

    if len(l_0) == len(l_1):
        for z in range(0, m - 1):
            d_s = (l_1[z] - l_0[z]) / l_0[z]
            l_ds.append(d_s)

    return l_ds


def hedging_in_fixed_gap(name, s0, k, dt, r, sig, m, towards, number, start_date, end_date):
    # step 1: making a DataFrame
    one_path = Hedging(name, s0, k, dt, r, sig, m, towards, number, start_date, end_date)
    list_stock = one_path.fixed_stock_path_1

    fixed_strike = EuropeanOption(s0, k, dt, r, sig, m)
    list_strike = fixed_strike.strike_1

    list_ds = ds(name, s0, k, dt, r, sig, m, towards, number, start_date, end_date)

    list_value = one_path.totaling_value_1

    list_delta = one_path.total_delta_1

    list_position = one_path.underlying_position_1

    my_dict = {'s': list_stock, 'k': list_strike, 'ds': list_ds, 'value': list_value,
               'delta': list_delta,
               'underlying_position': list_position}
    total_list = pd.DataFrame(my_dict)

    # step 2: choosing rows which satisfy the gap requirements (gap = sig / 16)

    choose_dict = total_list[(total_list["ds"] > (sig / 16)) | (total_list["ds"] < -(sig / 16))]

    # step 3: adding the initial row (when s = k)
    a = list_stock[0]
    b = list_strike[0]
    c = list_ds[0]
    d = list_value[0]
    e = list_delta[0]
    f = list_position[0]
    top_row = pd.DataFrame({'s': [a], 'k': [b], 'ds': [c], 'value': [d],
                            'delta': [e],
                            'underlying_position': [f]})
    choose_dict = pd.concat([top_row, choose_dict]).reset_index(drop=True)

    # step 4: adding prior value of stock and underlying position for calculating PoL in stock
    s_to_list = choose_dict["s"].tolist()
    u_p_to_list = choose_dict["underlying_position"].tolist()
    long = len(choose_dict)
    s_for_cal = [0]
    position_for_cal = [0]

    for i in range(1, long):
        s_cal = s_to_list[i - 1]
        s_for_cal.append(s_cal)

        position_cal = u_p_to_list[i - 1]
        position_for_cal.append(position_cal)

    choose_dict.insert(1, 's (prior)', s_for_cal, allow_duplicates=False)
    choose_dict.insert(7, 'position (prior)', position_for_cal, allow_duplicates=False)

    # step 5: calculating PoL in stock
    choose_dict["PoL"] = (choose_dict["s"] - choose_dict["s (prior)"]) * choose_dict["position (prior)"]

    # step 6: printing the DataFrame
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    print(choose_dict)

    # step 7: showing the result and profit
    profit_in_options = (choose_dict.iloc[-1].iat[4] - choose_dict.iloc[0].iat[4]) * number
    profit_in_stock = choose_dict["PoL"].sum()
    benefit = profit_in_options + profit_in_stock

    print("profit in options market is %d \n profit in stock market is %d \n the final profit is %d " % (
        profit_in_options, profit_in_stock, benefit))


hedging_in_fixed_gap('c', 100, 100, 0.08, 0.03, 0.2, 100, 1, 1000, "2021-7-05", "2021-7-31")
