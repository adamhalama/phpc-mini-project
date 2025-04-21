# 2. task

**Familiarize yourself with the provided script. Run and time the reference implementation for a
small subset of floorplans (e.g., 10 - 20). How long do you estimate it would take to process all
the floorplans? Perform the timing as a batch job so you get relieable results.**

*How long do you estimate it would take to process all
the floorplans? Perform the timing as a batch job so you get relieable results.*

- Elapsed (wall clock) time (h:mm:ss or m:ss): 3:56.88 (for 20 floorplans)
- 

# 4. Profile the reference jacobi function using kernprof. Explain the different parts of the function and how much time each part takes.

gbarlogin1(s243749) $ python -m line_profiler simulate.py.lprof
Timer unit: 1e-06 s

Total time: 199.086 s
File: simulate.py
Function: jacobi at line 13

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    13                                           @profile
    14                                           def jacobi(u, interior_mask, max_iter, atol=1e-6):
    15        20      10135.7    506.8      0.0      u = np.copy(u)
    16    118118      59762.0      0.5      0.0      for i in range(max_iter):
    17                                                   # Compute average of left, right, up and down neighbors
    18    354354  110015275.5    310.5     55.3          u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] +
    19    236236     286186.9      1.2      0.1                          u[:-2, 1:-1] + u[2:, 1:-1])
    20    118118   21517584.2    182.2     10.8          u_new_interior = u_new[interior_mask]
    21    118118   41506892.9    351.4     20.8          delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
    22    118118   25550451.5    216.3     12.8          u[1:-1, 1:-1][interior_mask] = u_new_interior
    23                                           
    24    118118     139668.3      1.2      0.1          if delta < atol:
    25        20         14.9      0.7      0.0              break
    26        20          5.4      0.3      0.0      return u



gbarlogin1(s243749) $ python -m line_profiler simulate.py.lprof
Timer unit: 1e-06 s

Total time: 198.576 s
File: simulate.py
Function: jacobi at line 13

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    13                                           @profile
    14                                           def jacobi(u, interior_mask, max_iter, atol=1e-6):
    15        20      10345.4    517.3      0.0      u = np.copy(u)
    16    118118      61231.4      0.5      0.0      for i in range(max_iter):
    17                                                   # Compute average of left, right, up and down neighbors
    18    118118  108371200.5    917.5     54.6          u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
    19    118118   21630652.5    183.1     10.9          u_new_interior = u_new[interior_mask]
    20    118118   41861889.0    354.4     21.1          delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
    21    118118   26506040.3    224.4     13.3          u[1:-1, 1:-1][interior_mask] = u_new_interior
    22                                           
    23    118118     134451.5      1.1      0.1          if delta < atol:
    24        20         12.8      0.6      0.0              break
    25        20          5.4      0.3      0.0      return u



l18 so seems like the computations on line 18 took the majority of the time, which makes sense since thats where the computations happen.
l19 also like 19 took significant time when copying the computed interior values into a separate array.
l20 calculating the convergence criteria also takes up a significant amount of time
l21 Assigning the updated temperature values back to the main array also is significant


# 5. 

## a) Measure the speed-up as more workers are added. Plot your speed-ups.
[plot](plot-speedups-with-ht.png)


## b) Estimate your parallel fraction according to Amdahl's law. How much (roughly) is parallelized?

```
    ~/Doc/DT/2/P/pyhpc-mini-project  python 5.b\)average_parallel_fraction.py 
Core Count | Walltime (plain) | Speedup (plain) | P estimate (plain)
         2 |            837.96 |            1.86 |             0.926
         4 |            583.71 |            2.67 |             0.835
         8 |            390.60 |            4.00 |             0.857
        12 |            205.06 |            7.61 |             0.948

Core Count | Walltime (HT)    | Speedup (HT)    | P estimate (HT)
         2 |            729.38 |            2.24 |             1.107
         4 |            471.99 |            3.46 |             0.948
         8 |            246.84 |            6.62 |             0.970
        12 |            223.43 |            7.31 |             0.942
```

## c) What is your theoretical maximum speed-up according to Amdahl's law? How much of that did you achieve? How many cores did that take?

 *TODO: come back to this with 24c CPU results*
```
    ~/Doc/DT/2/P/pyhpc-mini-project  python 5.c\)max-speedup-amdahls.py    ✔  pyhpc-mini-project   13:35:50  
Average parallel fraction (P): 0.892
Theoretical maximum speed-up (1/(1-P)): 9.22
Observed maximum speed-up: 7.61 on 12 cores
Achieved 82.60% of theoretical maximum
```

this means maybe we can throw more cores at it and make it a bit more fast, we'll try and see.



## d) How long would you estimate it would take to process all floorplans using your fastest parallel solution?



we take our best run for 100 floorplans, and then we extrapolate the time it would take, assuming the parralelization ratios don't change

12c CPU XeonGold6126
```
python 5.d\)est-time-for-all-floorplans.py 
Estimated total time (parallel): 9373.3 seconds
Which is approximately: 2h 36m 13s
```

24c CPU XeonGold6342
```
python 5.d\)est-time-for-all-floorplans.py
Estimated total time (parallel): 6899.9 seconds
Which is approximately: 1h 54m 60s
```

