## World3 (1974) versus World3_03 (2004 variant), pinned environment

### Parameters and tables that differ (World3 1974 value -> World3_03 value)
- parameter `pop.dcfsn`: 4.0 -> 3.8
- table `pop.fm`: (0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0, 1.05, 1.1) -> (0.0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.79, 0.84, 0.87)
- table `pop.lmf`: (0.0, 1.0, 1.2, 1.3, 1.35, 1.4) -> (0.0, 1.0, 1.43, 1.5, 1.5, 1.5)
- table `pop.lmhs2`: (1.0, 1.4, 1.6, 1.8, 1.95, 2.0) -> (1.0, 1.5, 1.9, 2.0, 2.0, 2.0)
- table `pop.sfsn`: (1.25, 1.0, 0.9, 0.8, 0.75) -> (1.25, 0.94, 0.715, 0.59, 0.5)
- parameter `agriculture.alln`: 6000.0 -> 1000.0
- table `agriculture.lymc`: (1.0, 3.0, 3.8, 4.4, 4.9, 5.4, 5.7, 6.0, 6.3, 6.6, 6.9, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0) -> (1.0, 3.0, 4.5, 5.0, 5.3, 5.6, 5.9, 6.1, 6.35, 6.6, 6.9, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0)
- table `nonrenewable.pcrum`: (0.0, 0.85, 2.6, 4.4, 5.4, 6.2, 6.8, 7.0, 7.0) -> (0.0, 0.85, 2.6, 3.4, 3.8, 4.1, 4.4, 4.7, 5.0)

### Runs
- World3 (1974) `historicalrun()`: return code `Success`; 401 points; last time 2100.0
- World3_03 `scenario1()`: return code `Success`; 401 points; last time 2100.0
- states in World3: 29; in World3_03: 29; in both (by name): 29
- only in World3_03: 
- only in World3: 

### Differences in the common states, World3_03 against World3 (1974), by name
- `br₊fcfpc1(t)`: max 66.26% (1920.0); 1970 4.18%, 2000 11.36%, 2025 5.85%, 2100 34.93%
- `br₊fcfpc2(t)`: max 62.68% (1927.5); 1970 1.76%, 2000 4.54%, 2025 6.91%, 2100 35.39%
- `js₊lufd(t)`: max 61.44% (2097.0); 1970 4.78%, 2000 1.34%, 2025 11.43%, 2100 57.13%
- `br₊fcfpc(t)`: max 59.76% (1934.0); 1970 1.83%, 2000 0.53%, 2025 9.22%, 2100 37.01%
- `ai₊ai(t)`: max 59.06% (2100.0); 1970 4.0%, 2000 12.54%, 2025 14.43%, 2100 59.06%
- `br₊aiopc(t)`: max 43.76% (2100.0); 1970 9.26%, 2000 10.02%, 2025 4.92%, 2100 43.76%
- `pop₊p4(t)`: max 39.98% (2018.0); 1970 23.51%, 2000 32.11%, 2025 39.32%, 2100 4.25%
- `br₊diopc1(t)`: max 37.07% (2100.0); 1970 8.82%, 2000 9.97%, 2025 0.14%, 2100 37.07%
- `pp₊ppapr1(t)`: max 36.79% (2100.0); 1970 6.38%, 2000 10.72%, 2025 5.74%, 2100 36.79%
- `ld₊pal(t)`: max 34.82% (2100.0); 1970 0.7%, 2000 3.66%, 2025 25.39%, 2100 34.82%
- `pp₊ppapr2(t)`: max 30.46% (2100.0); 1970 4.28%, 2000 10.87%, 2025 1.71%, 2100 30.46%
- `br₊ple1(t)`: max 30.07% (2011.0); 1970 16.77%, 2000 27.79%, 2025 25.2%, 2100 0.75%
- `br₊ple2(t)`: max 29.2% (2015.5); 1970 15.71%, 2000 25.74%, 2025 27.15%, 2100 0.08%
- `ld₊al(t)`: max 28.77% (2100.0); 1970 6.47%, 2000 14.21%, 2025 21.58%, 2100 28.77%
- `br₊ple(t)`: max 28.48% (2020.5); 1970 14.58%, 2000 23.44%, 2025 28.1%, 2100 1.58%
- `br₊diopc2(t)`: max 28.38% (2100.0); 1970 7.93%, 2000 9.88%, 2025 5.37%, 2100 28.38%
- `pp₊ppapr3(t)`: max 26.51% (2100.0); 1970 3.11%, 2000 10.59%, 2025 5.73%, 2100 26.51%
- `pp₊ppol(t)`: max 25.76% (2100.0); 1970 2.79%, 2000 11.53%, 2025 9.36%, 2100 25.76%
- `br₊diopc(t)`: max 22.03% (2100.0); 1970 6.99%, 2000 9.72%, 2025 8.03%, 2100 22.03%
- `pop₊p1(t)`: max 16.18% (2088.0); 1970 2.43%, 2000 1.59%, 2025 7.28%, 2100 15.79%
- `dr₊ehspc(t)`: max 15.05% (2012.5); 1970 8.09%, 2000 12.92%, 2025 11.88%, 2100 13.05%
- `is₊ic(t)`: max 13.68% (2100.0); 1970 6.17%, 2000 3.83%, 2025 1.75%, 2100 13.68%
- `pop₊p3(t)`: max 13.5% (2009.5); 1970 9.72%, 2000 12.87%, 2025 11.73%, 2100 8.99%
- `pop₊p2(t)`: max 12.59% (2100.0); 1970 3.53%, 2000 5.47%, 2025 2.68%, 2100 12.59%
- `ss₊sc(t)`: max 12.44% (2060.0); 1970 5.8%, 2000 4.69%, 2025 5.54%, 2100 7.66%
- `dlm₊pfr(t)`: max 11.61% (2019.5); 1970 6.78%, 2000 4.61%, 2025 8.73%, 2100 11.51%
- `nr₊nr(t)`: max 11.57% (2020.0); 1970 0.51%, 2000 4.26%, 2025 10.33%, 2100 3.62%
- `lfd₊lfert(t)`: max 6.16% (2067.0); 1970 0.26%, 2000 0.54%, 2025 0.94%, 2100 3.13%
- `leuiu₊uil(t)`: max 4.33% (1986.0); 1970 1.54%, 2000 3.52%, 2025 1.35%, 2100 1.35%

### Population (sum of the four cohorts, millions) and key stocks at selected years
- 1900: population World3 1600.0, World3_03 1600.0; industrial capital 210.0 vs 210.0 G; non-renewable resources 1000.0 vs 1000.0 G; persistent pollution 0.02 vs 0.02 G
- 1950: population World3 2626.1, World3_03 2705.1; industrial capital 1262.0 vs 1212.9 G; non-renewable resources 960.8 vs 961.6 G; persistent pollution 0.07 vs 0.07 G
- 1970: population World3 3656.8, World3_03 3792.5; industrial capital 2585.2 vs 2425.6 G; non-renewable resources 909.8 vs 914.4 G; persistent pollution 0.14 vs 0.13 G
- 2000: population World3 5692.8, World3_03 6091.9; industrial capital 6353.7 vs 6110.4 G; non-renewable resources 680.7 vs 709.7 G; persistent pollution 0.49 vs 0.44 G
- 2025: population World3 7057.0, World3_03 7523.0; industrial capital 9901.7 vs 9728.4 G; non-renewable resources 314.3 vs 346.7 G; persistent pollution 1.3 vs 1.18 G
- 2050: population World3 6216.7, World3_03 6507.3; industrial capital 5663.1 vs 6016.8 G; non-renewable resources 197.2 vs 210.2 G; persistent pollution 1.0 vs 1.11 G
- 2100: population World3 3996.2, World3_03 3508.5; industrial capital 703.3 vs 799.6 G; non-renewable resources 153.4 vs 158.9 G; persistent pollution 0.08 vs 0.11 G
- peak population: World3 7060.0 M in 2026.0; World3_03 7528.0 M in 2026.0
