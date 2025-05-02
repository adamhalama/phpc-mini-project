# 1 Familiarize yourself with the data. Load and visualize the input data for a few floorplans using a seperate Python script, Jupyter notebook or your preferred tool.

[vizualized-input-data](../src/1/figures/floorplan_10000.png)
- here we can see the
- heated walls and the cold walls - cold blue, hot red
- interior mask which denotes the interior in a white color.

# 2. Familiarize yourself with the provided script. Run and time the reference implementation for a small subset of floorplans (e.g., 10 - 20). 

- **How long do you estimate it would take to process all the floorplans? Perform the timing as a batch job so you get relieable results.**

- Elapsed (wall clock) time (h:mm:ss or m:ss): 3:56.88 (for 20 floorplans)
```
Time for 20 floorplans: 237.0 seconds
Estimated total time: 54166.4 seconds
Which is approximately: 15h 2m 46s
```

# 3. Visualize the simulation results for a few floorplans.

[floorplan-visualization](../simulation_plots/10000_plot.png)
- other visualizations are in `../simulation_plots/*`

# 4. Profile the reference jacobi function using kernprof. Explain the different parts of the function and how much time each part takes.

```
gbarlogin1(s243749) $ python -m line_profiler simulate.py.lprof
Timer unit: 1e-06 s
Total time: 199.086 s
File: simulate.py
Function: jacobi at line 13
```

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



- l18 so seems like the computations on line 18 took the majority of the time, which makes sense since thats where the computations happen.
- l19 also like 19 took significant time when copying the computed interior values into a separate array.
- l20 calculating the convergence criteria also takes up a significant amount of time
- l21 Assigning the updated temperature values back to the main array also is significant


# 5. Make a new Python program where you parallelize the computations over the floorplans. 
- Use static scheduling such that each worker is assigned the same amount of floorplans to process.
- You should use no more than 100 floorplans for your timing experiments. Again, use a batch job to ensure consistent results.

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

interestingly when i ran this with 24c this were there the results
```
    ~/Doc/DT/2/P/pyhpc-mini-project  python 5.b\)average_parallel_fraction-XeonGold6342.py 
Core Count | Walltime (plain) | Speedup (plain) | P estimate (plain)
        24 |            151.00 |           10.72 |             0.946

Average parallel fraction (plain): 0.946
    ~/Doc/DT/2/P/pyhpc-mini-project  python 5.c\)max-speedup-amdahls-XeonGold6342.py      
Average parallel fraction (P): 0.946
Theoretical maximum speed-up (1/(1-P)): 18.52
Observed maximum speed-up: 10.72 on 24 cores
Achieved 57.90% of theoretical maximum
```

- this means that with this script maybe we can throw more cores at it and make it a bit more fast, we'll try and see.


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

# 6. The amount of iterations needed to reach convergence will vary from floorplan to floorplan.
*Re-do your parallelization experiment using dynamic scheduling.*


## a) Did it get faster? By how much?
- it did not go noticabely faster with chunk size=1 
- and even with size=4


## b) Did the speed-up improve or worsen?
- it may have actually worsened a tiny bit, if we would to make a series of calculations, or do it on a larger scale, we could see some difference, but not a big reliable change being able to seen on simulation of 100 floorplans.

# 7. Implement another solution where you rewrite the jacobi function using Numba JIT on the CPU.

## a) Run and time the new solution for a small subset of floorplans. How does the performance compare to the reference?
- after running 100 simulations with the `jacobi_numba` solver, the time dropped drastically. with 24 cpu cores it went down to `Total runtime: 32 seconds`
- before the best time for 100 simulations on the same specs was `Total runtime: 151 seconds`. 
- that is a 5 fold speed increase on the same hardware

## b) Explain your function. How did you ensure your access pattern works well with the CPU cache?
writing out the nested loops in the order of `rows outer` and `cols innner` ensures that we got the cache efficiency of bringing one full row with all the columns in at a time.

also copying boundaries in bulk def helps the speed

## c) How long would it now take to process all floorplans?
```
    ~/Doc/DT/2/PythonHPC/pyhpc-mini-project  python 5.d\)est-time-for-all-floorplans.py                     ✔  pyhpc-mini-project   14:29:20  
Estimated total time (parallel): 1462.7 seconds
Which is approximately: 0h 24m 23s
```

# 8. Implement another solution writing a custom CUDA kernel with Numba. 

 - To synchronize threads between each iteration, the kernel should only perform a single iteration of the Jacobi solver. Skip the early stopping criteria and just run for a fixed amount of iterations. Write a helper function which takes the same inputs as the reference implementation (except for the atol input which is not needed) and then calls your kernel repeatedly to perform the implementations.

## a) Briefly describe your new solution. How did you structure your kernel and helper function?
- The kernel is structured structured very simply, the thread computes its coordinates, reads its four neighbours, writes the output, and finishes
- if the points don't match the mask they are just fixed
- the threads with (i,j) outside the grid don't do anything

## b) Run and time the new solution for a small subset of floorplans. How does the performance compare to the reference?
- Sample of 100 floorplans run with this on the a10 took: `Total runtime: 114 seconds` 
- which is good, but not even close to Numba which was 32, but also that was just using one GPU

## c) How long would it now take to process all floorplans?
```
python 5.d\)est-time-for-all-floorplans.py
Estimated total time: 5210.9 seconds
Which is approximately: 1h 26m 51s
```

# 9. Adapt the reference solution to run on the GPU using CuPy.

## a) Run and time the new solution for a small subset of floorplans. How does the performance compare to the reference?
- Takes quite significantly more time than using CUDA as we did before.
- So it is comparatively quicker to the original sequential script
- it took `Total runtime: 242 seconds` for 100simulations which is not terrible

## b) How long would it now take to process all floorplans?
```
Time for 100 floorplans: 242.0 seconds
Estimated total time: 11061.8 seconds
Which is approximately: 3h 4m 22s
```

## c) Was anything surprising about the performance?
- yes definitely, I thought that the GPU would handle it similarly as it did before, but it took something more than 2x the time

# 10. Profile the CuPy solution using the nsys profiler. What is the main issue regarding performance?

*(Hint: see exercises from week 10) Try to fix it.*

There was 14 million kernel launches! thats a crazy amount of overhead

thats 140.005 lanches per one floorplan (100 floorplans)

```
Time (%)  Total Time (ns)  Num Calls     Avg (ns)     Med (ns)    Min (ns)    Max (ns)    StdDev (ns)               Name            
 --------  ---------------  ----------  ------------  -----------  ---------  -----------  ------------  ----------------------------
     99.5   65,113,019,498  14,000,500       4,650.8      4,558.0      3,629    1,398,981       3,284.6  cuLaunchKernel              
```


```
Time (%)  Total Time (ns)  Instances  Avg (ns)  Med (ns)  Min (ns)  Max (ns)  StdDev (ns)     GridXYZ         BlockXYZ                       Name                  
--------  ---------------  ---------  --------  --------  --------  --------  -----------  --------------  --------------  ----------------------------------------
    43.7   42,513,079,928  6,000,000   7,085.5   7,072.0     6,272    15,488        208.3  2048    1    1   128    1    1  cupy_add__float64_float64_float64       
    16.0   15,571,900,265  2,000,000   7,786.0   7,840.0     6,751    15,072        397.3  2048    1    1   128    1    1  cupy_where__bool_float64_float64_float64
    13.6   13,281,836,277  2,000,000   6,640.9   6,656.0     6,048    15,104        175.8  2048    1    1   128    1    1  cupy_copy__bool_bool                    
    13.4   13,053,291,032  2,000,000   6,526.6   6,560.0     5,888    15,040        179.4  2048    1    1   128    1    1  cupy_multiply__float_float64_float64    
    13.3   12,944,583,810  2,000,000   6,472.3   6,400.0     5,983    15,041        165.0  2048    1    1   128    1    1  cupy_copy__float64_float64
```

- the main issue is just no having one kernel that does it all at once.
- the profiler shows that a lot of the GPU time is spent on just launching kernels and device to device copies
- 

- when trying to fix it we got to `Total runtime: 179 seconds` which is not bad, but not as good as the CUDA NUMBA we did.
- this means we cut away a lot of overhead 


# 11. (Optional) Improve the performance of one or more of your solutions further. 
*For example, parallelize your CPU JIT solution. Or use job arrays to parallelize a solution over multiple jobs. How fast can you get?*


- we already have a paralellised Numba kernel, so we can use that, its very fast with just 32 seconds for 100 floorplans.  (25min for all)
- if we parralelize this into few jobs, we can bring it down significantly.

- So after using job arrays (first looking for idle cpus w/ `nodestat -F | grep "Idle"`) and then picking one that has a lot of nodes ready to be used, then checking how many cores does each have, setting the batch script accordingly and then just running it
- we ran array of 10 jobs, the walltimes of them ranged from 2 minutes to `5:36.08`, which was the time for all the to be completed.


# 12. Process all floorplans using one of your implementations (ideally a fast one) and answer the below questions.
*Hint: use Pandas to process the CSV results generated by the script.*

## a) What is the distribution of the mean temperatures? Show your results as histograms.
[Histogram with mean temperature](histogram_mean_temp.png)

## b) What is the average mean temperature of the buildings?
Average mean temperature:      14.62 °C

## c) What is the average temperature standard deviation?
Average temperature std-dev:   6.77 °C

## d) How many buildings had at least 50% of their area above 18ºC?
≥50 % of area above 18 °C:      750 buildings

## e) How many buildings had at least 50% of their area below 15ºC?
≥50 % of area below 15 °C:      2526 buildings