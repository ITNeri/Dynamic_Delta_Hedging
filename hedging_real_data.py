import xlrd
from delta_hedging_mc import EuropeanCallOption, EuropeanPutOption
import pandas as pd

'''
HC2110 2021-7-26到2021-7-29日每30分钟的实际数据
到期时间 7-31 0点
'''

# import the real data (this part may be varied in the different cases)
workbook = xlrd.open_workbook('HC2110.xls')
table = workbook.sheets()[0]

col_stock = table.col_values(3)
col_time = table.col_values(5)
rows_number = table.nrows

l_strike = []
for z in range(0, rows_number):
    l_strike.append(6011)

# delta s = (s(a) - s(a-1)) / s(a-1)
l_0 = []  # list of s(a-1)
l_1 = []  # list of s(a)
l_ds = [0]  # list of delta s

for x in range(0, rows_number - 1):
    s_0_value = col_stock[x]
    l_0.append(s_0_value)

for j in range(1, rows_number):
    s_1_value = col_stock[j]
    l_1.append(s_1_value)

if len(l_0) == len(l_1):
    for z in range(0, rows_number - 1):
        d_s = (l_1[z] - l_0[z]) / l_0[z]
        l_ds.append(d_s)


class Hedging1:
    def __init__(self, name, r, sig, towards, number):
        self.total_delta_1 = self.total_delta(name, r, sig)
        total_delta_2 = self.total_delta(name, r, sig)
        self.underlying_position_1 = self.underlying_position(total_delta_2, towards, number)
        underlying_position_2 = self.underlying_position(total_delta_2, towards, number)
        self.pol_1 = self.pol(underlying_position_2)
        self.totaling_value_1 = self.totaling_value(name, r, sig)

    def total_delta(self, name, r, sig):
        # s_l = stock list
        # name: "c"=call, "p"=put
        delta_number = []
        for i in range(0, rows_number):
            current_s = col_stock[i]
            s0 = current_s
            dt = col_time[i] / (360 * 24)  # time unit = hour
            k = l_strike[i]

            if name == "c":
                total = EuropeanCallOption(s0, k, r, sig, dt)
                delta_number.append(total.delta_1)
            else:
                total = EuropeanPutOption(s0, k, r, sig, dt)
                delta_number.append(total.delta_1)

        return delta_number

    def underlying_position(self, total_delta, towards, number):
        # towards: buy=1, sell=-1
        total_position = []

        for i in range(0, rows_number):
            b = total_delta[i]
            position = -round(b * number, 0) * towards
            total_position.append(position)

        return total_position

    def pol(self, underlying_position):
        pol_in_stock = [0]
        for i in range(1, rows_number):
            pol_in_stock.append(
                (col_stock[i] - col_stock[i - 1]) * underlying_position[i - 1])

        return pol_in_stock

    def totaling_value(self, name, r, sig):
        # name: "c"=call, "p"=put
        total_value = []
        for i in range(0, rows_number):
            s0 = col_stock[i]  # s0 = current s
            dt = col_time[i] / (360 * 24)
            k = l_strike[i]

            if name == "c":
                total = EuropeanCallOption(s0, k, r, sig, dt)
            else:
                total = EuropeanPutOption(s0, k, r, sig, dt)

            total_value.append(total.value_1)

        return total_value


def hedging_in_fixed_gap(name, r, sig, towards, number):
    # step 1: making a DataFrame
    one_path = Hedging1(name, r, sig, towards, number)
    list_stock = col_stock
    list_strike = l_strike
    list_ds = l_ds
    list_value = one_path.totaling_value_1
    list_delta = one_path.total_delta_1
    list_position = one_path.underlying_position_1
    list_time = col_time

    my_dict = {'s': list_stock, 'k': list_strike, 'ds': list_ds, 'value': list_value,
               'delta': list_delta,
               'underlying_position': list_position, 'time': list_time}
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
    g = list_time[0]
    top_row = pd.DataFrame({'s': [a], 'k': [b], 'ds': [c], 'value': [d],
                            'delta': [e],
                            'underlying_position': [f], 'time': [g]})
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


hedging_in_fixed_gap('c', 0.03, 0.21, 1, 100)
