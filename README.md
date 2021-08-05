# Dynamic_Delta_Hedging
Hedging options by using Monte Carlo simulations or real data  

## Table of Contents
- Background
- Install
- Usage
- Example and Results
- Maintainer
- License


## Background
1. xxx
    1. xxxx  
2. xxxx  
3. 

## Install
xxx

## Usage
xxx

## Example and Results
### daily delta hedging when market close  
`<import delta_hedging_mc>`  


Suppose we buy 100 numbers of call option. The parameters are as follows:  
```
strike price = 100; initial stock price = 100; time to maturity = 20/250 = 0.08;
risk-less short rate = 0.03; volatility of stock value = 0.2
the number of path nodes = 20； the number of simulations = 100000
```

Then one price path can be simulated based on Monte Carlo method:
![Image text]

Following this price path, the result about daily delta hedging when market close are as follows:
```
             s    k     value     delta  underlying_position  PoL_in_stock
0   100.000000  100  2.249024  0.528186                -53.0      0.000000
1    99.792657  100  2.088297  0.512475                -51.0     10.989176
2    98.754161  100  1.557154  0.433872                -43.0     52.963311
3    99.594844  100  1.874472  0.494953                -49.0    -36.149385
4    99.574226  100  1.803350  0.491589                -49.0      1.010282
5    98.096180  100  1.127525  0.370275                -37.0     72.424269
6   100.403404  100  2.095604  0.557338                -56.0    -85.367279
7   100.775555  100  2.235728  0.589557                -59.0    -20.840460
8    97.788877  100  0.841258  0.324372                -32.0    176.213957
9    98.144736  100  0.890919  0.346811                -35.0    -11.387459
10   97.011756  100  0.508059  0.239333                -24.0     39.654271
11   95.874580  100  0.249233  0.143943                -14.0     27.292239
12   94.869292  100  0.108490  0.076725                 -8.0     14.074034
13   94.992759  100  0.088016  0.067702                 -7.0     -0.987740
14   95.283589  100  0.077165  0.064186                 -6.0     -2.035809
15   94.524201  100  0.023866  0.025253                 -3.0      4.556329
16   96.263196  100  0.071753  0.070270                 -7.0     -5.216984
17   96.177148  100  0.032285  0.039910                 -4.0      0.602333
18   95.925056  100  0.005943  0.010631                 -1.0      1.008369
19   96.892785  100  0.002529  0.006576                 -1.0     -0.967729
```

Repeating this process 100000 times, we can get returns best fit distribution. It is a normal distribution centered on 0.
![Image text]



### delta hedging based on changes in stock price
`<import hedging_real_data>`  
xxx

## Maintainer
@ITNeri

## License
