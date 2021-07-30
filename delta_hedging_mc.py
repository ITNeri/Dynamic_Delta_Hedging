from math import log, sqrt, exp
import matplotlib.pyplot as plt
from scipy.stats import norm
import random
import pandas as pd

'''
k = strike price
s0 = initial stock price
dt = t/T = time to maturity
rf = remaining time
r = risk-less short rate
sig = volatility of stock value
m = the number of path nodes
n = the number of simulations
'''


class EuropeanCallOption:
    def __init__(self, s0, k, r, sig, dt):
        self.s0 = s0
        self.k = k
        self.r = r
        d1_1 = self.d1(s0, k, r, sig, dt)
        d2_1 = self.d2(d1_1, sig, dt)
        self.dt = dt
        self.value_1 = self.value(s0, k, r, dt, d1_1, d2_1)
        self.delta_1 = self.delta(d1_1)

    def d1(self, s0, k, r, sig, dt):
        return (log(s0 / k) + (r + 0.5 * sig ** 2) * dt) / (sig * sqrt(dt))

    def d2(self, d1, sig, dt):
        return d1 - sig * sqrt(dt)

    def value(self, s0, k, r, dt, d1, d2):
        return s0 * exp(-r * dt) * norm.cdf(d1) - k * exp(-r * dt) * norm.cdf(d2)

    def delta(self, d1):
        return norm.cdf(d1)


class EuropeanPutOption:
    def __init__(self, s0, k, r, sig, dt):
        self.s0 = s0
        self.k = k
        self.r = r
        d1_1 = self.d1(s0, k, r, sig, dt)
        d2_1 = self.d2(d1_1, sig, dt)
        self.dt = dt
        self.value_1 = self.value(s0, k, r, dt, d1_1, d2_1)
        self.delta_1 = self.delta(d1_1)

    def d1(self, s0, k, r, sig, dt):
        return (log(s0 / k) + (r + 0.5 * sig ** 2) * dt) / (sig * sqrt(dt))

    def d2(self, d1, sig, dt):
        return d1 - sig * sqrt(dt)

    def value(self, s0, k, r, dt, d1, d2):
        return k * exp(-r * dt) * norm.cdf(-d2) - s0 * exp(-r * dt) * norm.cdf(-d1)

    def delta(self, d1):
        return norm.cdf(d1) - 1


class EuropeanOption:
    def __init__(self, s0, k, dt, r, sig, m):
        self.stock_1 = self.stock_list(s0, dt, r, sig, m)
        self.strike_1 = self.strike_list(k, m)

    def stock_list(self, s0, dt, r, sig, m):
        delta_t = dt / m  # length of time interval

        path = [s0]
        for j in range(1, m):
            path.append(path[-1] * exp((r - 0.5 * sig ** 2) * delta_t + (sig * sqrt(delta_t) * random.gauss(0, 1))))

        stock = path
        return stock

    def strike_list(self, k, m):
        strike = [k]
        for i in range(1, m):
            strike.append(k)
        return strike


class Hedging:
    def __init__(self, name, s0, k, dt, r, sig, m, towards, number, start_date, end_date):
        sth = EuropeanOption(s0, k, dt, r, sig, m)
        s_l = sth.stock_1
        self.fixed_stock_path_1 = self.fixed_stock_path(s_l)
        self.total_delta_1 = self.total_delta(name, s_l, k, r, sig, m, start_date, end_date)
        total_delta_2 = self.total_delta(name, s_l, k, r, sig, m, start_date, end_date)
        self.underlying_position_1 = self.underlying_position(total_delta_2, m, towards, number)
        underlying_position_2 = self.underlying_position(total_delta_2, m, towards, number)
        self.pol_1 = self.pol(s_l, underlying_position_2, m)
        self.totaling_value_1 = self.totaling_value(name, s_l, k, r, sig, m, start_date, end_date)

    def fixed_stock_path(self, s_l):
        return s_l

    def total_delta(self, name, s_l, k, r, sig, m, start_date, end_date):
        # s_l = stock list
        # name: "c"=call, "p"=put
        delta_number = []
        for i in range(0, m):
            current_s = s_l[i]
            s0 = current_s
            t = pd.bdate_range(start_date, end_date)
            dt = (len(t) / 250) * (1 - i / m)

            if name == "c":
                total = EuropeanCallOption(s0, k, r, sig, dt)
                delta_number.append(total.delta_1)
            else:
                total = EuropeanPutOption(s0, k, r, sig, dt)
                delta_number.append(total.delta_1)

        return delta_number

    def underlying_position(self, total_delta, m, towards, number):
        # towards: buy=1, sell=-1
        total_position = []

        for i in range(0, m):
            b = total_delta[i]
            position = -round(b * number, 0) * towards
            total_position.append(position)

        return total_position

    def pol(self, s_l, underlying_position, m):
        pol_in_stock = [0]
        for i in range(1, m):
            pol_in_stock.append(
                (s_l[i] - s_l[i - 1]) * underlying_position[i - 1])

        return pol_in_stock

    def totaling_value(self, name, s_l, k, r, sig, m, start_date, end_date):
        # name: "c"=call, "p"=put
        total_value = []
        for i in range(0, m):
            s0 = s_l[i]  # s0 = current s
            t = pd.bdate_range(start_date, end_date)
            dt = (len(t) / 250) * (1 - i / m)

            if name == "c":
                total = EuropeanCallOption(s0, k, r, sig, dt)
            else:
                total = EuropeanPutOption(s0, k, r, sig, dt)

            total_value.append(total.value_1)

        return total_value


def graph_show(name, s0, k, dt, r, sig, m, towards, number, start_date, end_date):
    # graph simulation (underlying price monte carlo simulation)
    one_path = Hedging(name, s0, k, dt, r, sig, m, towards, number, start_date, end_date)
    list_stock = one_path.fixed_stock_path_1
    fixed_strike = EuropeanOption(s0, k, dt, r, sig, m)
    list_strike = fixed_strike.strike_1

    plt.figure(figsize=(12, 6))
    plt.grid(True)  # 显示网格线
    plt.xlabel('Time step')
    plt.ylabel('price')
    plt.legend()
    plt.plot(list_stock)
    plt.show()

    # list show
    list_value = one_path.totaling_value_1
    list_delta = one_path.total_delta_1
    list_position = one_path.underlying_position_1
    list_pol = one_path.pol_1

    my_dict = {'s': list_stock, 'k': list_strike, 'value': list_value, 'delta': list_delta,
               'underlying_position': list_position,
               'PoL_in_stock': list_pol}
    total_list = pd.DataFrame(my_dict)
    print(total_list)


def distribution(name, s0, k, dt, r, sig, m, n, towards, number, start_date, end_date):
    # name: "c"=call, "p"=put
    acc_value = []
    acc_pol = []

    for i in range(0, n):
        # the final value - the initial value
        one_list = Hedging(name, s0, k, dt, r, sig, m, towards, number, start_date, end_date)
        list_stock = one_list.fixed_stock_path_1

        s0 = list_stock[0]
        t = pd.bdate_range(start_date, end_date)
        dt = (len(t) / 250)
        if name == "c":
            total_0 = EuropeanCallOption(s0, k, r, sig, dt)
            value_0 = total_0.value_1
        else:
            total_0 = EuropeanPutOption(s0, k, r, sig, dt)
            value_0 = total_0.value_1

        s0 = list_stock[-1]
        t = pd.bdate_range(start_date, end_date)
        dt = (len(t) / 250) * (1 / m)
        if name == "c":
            total_1 = EuropeanCallOption(s0, k, r, sig, dt)
            value_1 = total_1.value_1
        else:
            total_1 = EuropeanPutOption(s0, k, r, sig, dt)
            value_1 = total_1.value_1

        acc_s = (value_1 - value_0) * number

        acc_value.append(acc_s)

        # accelerate PoL in stock
        v = 0
        for z in range(1, m):
            a = one_list.underlying_position_1
            b = (list_stock[z] - list_stock[z - 1]) * a[z - 1]
            v = v + b

        acc_pol.append(v)

    # revenue = value - pol in stock
    if len(acc_pol) == len(acc_value):
        revenue = []

        for x in range(0, n):
            revenue_1 = acc_value[x] - acc_pol[x]
            revenue.append(revenue_1)

        my_dict_1 = {'revenue': revenue}
        revenue_data = pd.DataFrame(my_dict_1)

        plt.hist(revenue_data.revenue, bins=50, density=False)
        plt.xlabel('Returns')
        plt.ylabel('Frequency')
        plt.title('Returns Best fit Distribution')
        plt.show()

    else:
        print('please check acc_value and acc_pol')


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# strike price = 100; initial stock price = 100; time to maturity = 20/250 = 0.08;
# risk-less short rate = 0.03; volatility of stock value = 0.2
# the number of path nodes = 20； the number of simulations = 100000
# type = call option; towards = buy; number of stock = 100
graph_show('c', 100, 100, 0.08, 0.03, 0.2, 20, 1, 100, "2021-7-05", "2021-7-31")
distribution('c', 100, 100, 0.08, 0.03, 0.2, 20, 100000, 1, 100, "2021-7-05", "2021-7-31")

