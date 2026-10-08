# Earth4All.jl audit, D-010 tests T1b, T2, T3 (counterfactual), T4. Facts only.
#
# Run from the repository root, in the pinned environment audit/env-earth4all (see earth4all_t0.jl),
# with the Earth4All.jl clone outside this repository:
#   julia --project=audit/env-earth4all audit/t0/earth4all_audit.jl <clone>
# The model code is not modified. Only the package's own parameters (SSP2 switches) are changed in T3.
# Vensim files are not used (D-014). Outputs: $F3_OUT (default audit/results).

using DataFrames, CSV, ModelingToolkit, DifferentialEquations
const CLONE = ARGS[1]
const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
include(joinpath(CLONE, "src", "Earth4All.jl"))
const E = Earth4All
const WD = E.WorldDynamics
const REPORT = ["## Earth4All.jl audit: T1b, T2, T3 counterfactual, T4", ""]
note(s) = (push!(REPORT, s); println(s))

function step(f, name)
    try
        f()
        note("- ok: $name")
    catch e
        note("- FAILED: $name: `$(replace(first(sprint(showerror, e), 500), '\n' => ' '))`")
    end
end

const SA = Base.invokelatest(getfield(E, :system_array))
const SN = Base.invokelatest(getfield(E, :sector_name))

# (sector, description) => variable, main systems only (support systems are not in the composed model)
const VARS = Dict{Tuple{String,String},Any}()
for (s, sector) in enumerate(SN)
    for v in Base.invokelatest(ModelingToolkit.namespace_variables, SA[s])
        d = Base.invokelatest(ModelingToolkit.getdescription, v)
        (d == "" || d == "Time instants" || startswith(d, "LV functions") || startswith(d, "RT functions")) && continue
        haskey(VARS, (sector, d)) || (VARS[(sector, d)] = v)
    end
end
getv(sector, d) = VARS[(sector, d)]
series(sol, sector, d) = Base.invokelatest(getindex, sol, getv(sector, d))

solve_to(sys, t1) = Base.invokelatest(WD.solve, sys, (1980, t1); solver = Euler(), dt = 0.015625,
                                      dtmax = 0.015625, initializealg = CheckInit())
const SOLS = Dict{String,Any}()
step("Solve TLTL and GL, 1980-2100, as the package does") do
    SOLS["TLTL"] = Base.invokelatest(E.run_tltl_solution)
    SOLS["GL"] = Base.invokelatest(E.run_gl_solution)
    for (k, s) in SOLS
        note("  - $k: $(length(s.t)) time points, last t = $(s.t[end]), retcode $(s.retcode)")
    end
end

# ---------------- T1b: minimum of each cohort stock ----------------
step("T1b: minimum of the four cohort stocks, 1980-2100") do
    rows = NamedTuple[]
    for (scen, sol) in SOLS, d in ["Aged 0-20 years Mp", "Aged 20-40 years Mp", "Aged 40-60 Mp", "Aged 60 + Mp"]
        x = series(sol, "population", d)
        i = argmin(x)
        push!(rows, (scenario = scen, stock = d, minimum = x[i], year_of_minimum = sol.t[i], value_1980 = x[1], value_2100 = x[end]))
    end
    df = DataFrame(map(identity, rows))
    CSV.write(joinpath(OUT, "earth4all_t1b_cohort_minima.csv"), df)
    for r in eachrow(df)
        note("  - $(r.scenario) `$(r.stock)`: min $(round(r.minimum; sigdigits = 5)) Mp in $(round(r.year_of_minimum; digits = 1)); 1980 $(round(r.value_1980; sigdigits = 5)), 2100 $(round(r.value_2100; sigdigits = 5))")
    end
end

# ---------------- T2: employed vs working-age population ----------------
# Definitions (code, labourmarket/subsystems.jl): AVWO = WAP * LPR (available workforce);
# UNEM = max(0, AVWO - WF), so WF ("WorkForce") is the employed stock; WAP = A20PA = A2040 + A4060 + A60PL - OP.
step("T2: workforce (employed) vs working-age population, every year") do
    summ = NamedTuple[]
    for (scen, sol) in SOLS
        years = collect(1980:2100)
        idx = [findmin(abs.(sol.t .- y))[2] for y in years]
        wf = series(sol, "labourmarket", "WorkForce Mp")[idx]
        wap = series(sol, "labourmarket", "Working Age Population Mp")[idx]
        avwo = series(sol, "labourmarket", "AVailable WOrkforce Mp")[idx]
        lpr = series(sol, "labourmarket", "Labour Participation Rate (1)")[idx]
        CSV.write(joinpath(OUT, "earth4all_t2_yearly_$(scen).csv"),
                  DataFrame(year = years, workforce = wf, working_age = wap, available_workforce = avwo,
                            lpr = lpr, wf_over_wap = wf ./ wap, wf_over_avwo = wf ./ avwo))
        r1 = wf ./ wap; r2 = wf ./ avwo
        push!(summ, (scenario = scen, years_wf_above_wap = count(>(1), r1), max_wf_over_wap = maximum(r1),
                     year_of_max = years[argmax(r1)], min_wf_over_wap = minimum(r1),
                     years_wf_above_avwo = count(>(1 + 1e-9), r2), max_wf_over_avwo = maximum(r2),
                     max_lpr = maximum(lpr), min_lpr = minimum(lpr)))
    end
    df = DataFrame(map(identity, summ))
    CSV.write(joinpath(OUT, "earth4all_t2_summary.csv"), df)
    for r in eachrow(df)
        note("  - $(r.scenario): workforce above working-age population in $(r.years_wf_above_wap) of 121 years; max WF/WAP $(round(r.max_wf_over_wap; digits = 4)) (year $(r.year_of_max)), min $(round(r.min_wf_over_wap; digits = 4)); WF above available workforce in $(r.years_wf_above_avwo) years (max ratio $(round(r.max_wf_over_avwo; digits = 4))); participation rate range $(round(r.min_lpr; digits = 3))-$(round(r.max_lpr; digits = 3))")
    end
end

# ---------------- T3 counterfactual: switch off the SSP2 assumptions (package parameters only) ----------------
const HEAD = [("population", "Population Mp"), ("population", "GDP per Person kDollar/p/y"),
              ("wellbeing", "Average WellBeing Index (1)"), ("wellbeing", "Social TEnsion (1)"),
              ("demand", "INEQuality Index (1980=1)"), ("climate", "OBserved WArming deg C"),
              ("population", "Life Expectancy y")]
step("T3 counterfactual: TLTL with SSP2FA2022F = 0 (fertility and life-expectancy ramps off) and SSP2LMA = 0 (land-management ramps off)") do
    base = solve_to(Base.invokelatest(E.run_e4a), 2100)
    popp = Base.invokelatest(E.Population.getparameters); popp[:SSP2FA2022F] = 0
    foop = Base.invokelatest(E.FoodLand.getparameters); foop[:SSP2LMA] = 0
    cases = ["SSP2FA2022F=0" => (pop_pars = popp,), "SSP2LMA=0" => (foo_pars = foop,)]
    rows = NamedTuple[]
    for (label, kw) in cases
        alt = solve_to(Base.invokelatest(E.run_e4a; kw...), 2100)
        for (sector, d) in HEAD
            a = series(base, sector, d); b = series(alt, sector, d)
            rel = abs.(b .- a) ./ (abs.(a) .+ 1e-12)
            i = argmax(rel)
            push!(rows, (case = label, variable = d, base_2100 = a[end], switched_2100 = b[end],
                         rel_diff_2100 = rel[end], max_rel_diff = rel[i], year_of_max = base.t[i]))
        end
    end
    df = DataFrame(map(identity, rows))
    CSV.write(joinpath(OUT, "earth4all_t3_counterfactual.csv"), df)
    for r in eachrow(df)
        note("  - $(r.case), `$(r.variable)`: 2100 $(round(r.base_2100; sigdigits = 4)) -> $(round(r.switched_2100; sigdigits = 4)) ($(round(100 * r.rel_diff_2100; digits = 2))%); max difference $(round(100 * r.max_rel_diff; digits = 2))% in $(round(r.year_of_max; digits = 1))")
    end
end

# ---------------- T4: run to 2200 ----------------
# "Plausible range" is not defined in D-010; defined here (three criteria, reported separately):
#  (a) a value is NaN or Inf; (b) a variable that is >= 0 at every point of 1980-2100 becomes negative
#  (below -1e-9 * its 1980-2100 maximum); (c) |value| exceeds 10 x the maximum |value| over 1980-2100
#  (variables whose 1980-2100 maximum |value| is 0 are skipped for (c)).
step("T4: run to 2200 and find the first variable to leave a plausible range") do
    for (scen, fn) in ["TLTL" => E.run_tltl, "GL" => E.run_gl]
        sol = solve_to(Base.invokelatest(fn), 2200)
        note("  - $scen to 2200: retcode $(sol.retcode), last t = $(sol.t[end]), $(length(sol.t)) points")
        i2100 = findlast(<=(2100.0), sol.t)
        first = Dict("nonfinite" => (Inf, "", ""), "turns_negative" => (Inf, "", ""), "exceeds_10x" => (Inf, "", ""))
        counts = Dict("nonfinite" => 0, "turns_negative" => 0, "exceeds_10x" => 0)
        offenders = NamedTuple[]
        for ((sector, d), v) in VARS
            x = try Base.invokelatest(getindex, sol, v) catch; continue end
            ref = view(x, 1:i2100); late = view(x, (i2100 + 1):length(x))
            tl = view(sol.t, (i2100 + 1):length(x))
            mx = maximum(abs, filter(isfinite, ref); init = 0.0)
            function hit(kind, k)
                counts[kind] += 1
                tt = tl[k]
                push!(offenders, (scenario = scen, kind = kind, sector = sector, variable = d, first_time = tt,
                                  max_abs_1980_2100 = mx, value_at_first = late[k], value_at_end = late[end]))
                tt < first[kind][1] && (first[kind] = (tt, sector, d))
            end
            k = findfirst(z -> !isfinite(z), late); k === nothing || hit("nonfinite", k)
            if all(>=(0), ref) && mx > 0
                k = findfirst(<(-1e-9 * mx), late); k === nothing || hit("turns_negative", k)
            end
            if mx > 0
                k = findfirst(z -> isfinite(z) && abs(z) > 10 * mx, late); k === nothing || hit("exceeds_10x", k)
            end
        end
        isempty(offenders) || CSV.write(joinpath(OUT, "earth4all_t4_offenders_$(scen).csv"),
                                        sort(DataFrame(map(identity, offenders)), :first_time))
        for kind in ["nonfinite", "turns_negative", "exceeds_10x"]
            t, sector, d = first[kind]
            note(isfinite(t) ? "    - $scen, $kind: $(counts[kind]) variables; first: `$d` ($sector) at $(round(t; digits = 2))" :
                               "    - $scen, $kind: no variable up to 2200")
        end
        # headline values at 2100, 2150, 2200
        for (sector, d) in HEAD
            x = series(sol, sector, d)
            vals = [x[findmin(abs.(sol.t .- y))[2]] for y in (2100, 2150, 2200)]
            note("    - $scen `$d`: 2100 $(round(vals[1]; sigdigits = 4)), 2150 $(round(vals[2]; sigdigits = 4)), 2200 $(round(vals[3]; sigdigits = 4))")
        end
    end
end

write(joinpath(OUT, "earth4all_audit_report.md"), join(REPORT, "\n") * "\n")
