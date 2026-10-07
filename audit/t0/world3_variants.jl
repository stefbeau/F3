# D-015 evidence: World3 (1974) versus World3_03 (2004 variant) in WorldDynamics.jl v1.0.0 (MIT, D-012).
#
# Run from the repository root, in the pinned environment (D-017), default solver options:
#   julia +1.10 --project=audit/env audit/t0/world3_variants.jl
# Outputs go to $F3_OUT (default audit/results). Nothing in the package is modified, and no package is
# added to audit/env: ModelingToolkit is reached through the type of the system (as world3_t0.jl does). States are
# compared BY NAME, never by position (the two systems list states in different orders).

using WorldDynamics, DataFrames, CSV

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const W3 = WorldDynamics.World3
const W303 = WorldDynamics.World3_03
const REPORT = ["## World3 (1974) versus World3_03 (2004 variant), pinned environment", ""]
note(s) = (push!(REPORT, s); println(s))

# ---- 1. which parameters and tables does the 2004 variant change? -------------------------------
# World3_03.scenario1 = World3_91.scenario1 (parameter/table overrides on World3.historicalrun) + a
# `sfsn` override + two extra subsystems (human welfare index, human ecological footprint).
mods = ["pop", "capital", "agriculture", "nonrenewable", "pollution"]
getp = Dict("pop" => W3.Pop4.getparameters, "capital" => W3.Capital.getparameters,
            "agriculture" => W3.Agriculture.getparameters, "nonrenewable" => W3.NonRenewable.getparameters,
            "pollution" => W3.Pollution.getparameters)
gett = Dict("pop" => W3.Pop4.gettables, "capital" => W3.Capital.gettables,
            "agriculture" => W3.Agriculture.gettables, "nonrenewable" => W3.NonRenewable.gettables,
            "pollution" => W3.Pollution.gettables)

# Reproduce what World3_91.scenario1 / World3_03.scenario1 overwrite, by reading the package's own
# default dictionaries and applying the same overrides, then diffing.
base_p = Dict(m => Base.invokelatest(getp[m]) for m in mods)
base_t = Dict(m => Base.invokelatest(gett[m]) for m in mods)

new_p = Dict(m => Base.invokelatest(getp[m]) for m in mods)
new_t = Dict(m => Base.invokelatest(gett[m]) for m in mods)
# overrides copied from World3_91/world3_91/scenarios.jl and World3_03/world3_03/scenarios.jl (read, not run)
new_p["agriculture"][:alln] = 1000
new_p["pop"][:dcfsn] = 3.8
new_t["pop"][:lmf] = (0.0, 1.0, 1.43, 1.5, 1.5, 1.5)
new_t["pop"][:lmhs2] = (1.0, 1.5, 1.9, 2.0, 2.0, 2.0)
new_t["pop"][:fm] = (0.0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.79, 0.84, 0.87)
new_t["agriculture"][:lymc] = (1.0, 3.0, 4.5, 5.0, 5.3, 5.6, 5.9, 6.1, 6.35, 6.6, 6.9, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0)
new_t["nonrenewable"][:pcrum] = (0.0, 0.85, 2.6, 3.4, 3.8, 4.1, 4.4, 4.7, 5.0)
new_t["pop"][:sfsn] = (1.25, 0.94, 0.715, 0.59, 0.5)

note("### Parameters and tables that differ (World3 1974 value -> World3_03 value)")
for m in mods
    for k in sort(collect(keys(base_p[m])); by = string)
        base_p[m][k] == new_p[m][k] || note("- parameter `$m.$k`: $(base_p[m][k]) -> $(new_p[m][k])")
    end
    for k in sort(collect(keys(base_t[m])); by = string)
        base_t[m][k] == new_t[m][k] || note("- table `$m.$k`: $(base_t[m][k]) -> $(new_t[m][k])")
    end
end

# ---- 2. run both, default options, saveat 0.5 ------------------------------------------------
function run_sys(f, label)
    sys = Base.invokelatest(f)
    MTK = parentmodule(typeof(sys))
    sol = Base.invokelatest(WorldDynamics.solve, sys, (1900, 2100); saveat = 0.5)
    note("- $label: return code `$(sol.retcode)`; $(length(sol.t)) points; last time $(last(sol.t))")
    syms = string.(Base.invokelatest(MTK.unknowns, sol.prob.f.sys))
    M = permutedims(reduce(hcat, sol.u))
    df = DataFrame(M, syms; makeunique = true)
    insertcols!(df, 1, :time => collect(sol.t))
    return df, sys
end
note("")
note("### Runs")
d74, _ = run_sys(W3.historicalrun, "World3 (1974) `historicalrun()`")
d03, sys03 = run_sys(W303.scenario1, "World3_03 `scenario1()`")
CSV.write(joinpath(OUT, "world3_1974_states.csv"), d74)
CSV.write(joinpath(OUT, "world3_03_states.csv"), d03)

note("- states in World3: $(ncol(d74) - 1); in World3_03: $(ncol(d03) - 1); in both (by name): $(length(intersect(names(d74), names(d03))) - 1)")
note("- only in World3_03: " * join(setdiff(names(d03), names(d74)), ", "))
note("- only in World3: " * join(setdiff(names(d74), names(d03)), ", "))

# ---- 3. compare common states by name ----------------------------------------------------------
note("")
note("### Differences in the common states, World3_03 against World3 (1974), by name")
common = [c for c in names(d74) if c != "time" && c in names(d03)]
@assert d74.time == d03.time
years = (1900.0, 1950.0, 1970.0, 2000.0, 2025.0, 2050.0, 2100.0)
rows = NamedTuple[]
for c in common
    a = d74[!, c]; b = d03[!, c]
    rel = abs.(b .- a) ./ max.(abs.(a), 1e-30)
    i = argmax(rel)
    push!(rows, (state = c, max_rel_diff = rel[i], year_of_max = d74.time[i],
                 rel_1970 = rel[findfirst(==(1970.0), d74.time)], rel_2000 = rel[findfirst(==(2000.0), d74.time)],
                 rel_2025 = rel[findfirst(==(2025.0), d74.time)], rel_2100 = rel[end]))
end
cmp = DataFrame(map(identity, rows))
CSV.write(joinpath(OUT, "world3_variants_state_differences.csv"), cmp)
for r in eachrow(sort(cmp, :max_rel_diff; rev = true))
    note("- `$(r.state)`: max $(round(100 * r.max_rel_diff; digits = 2))% ($(r.year_of_max)); 1970 $(round(100 * r.rel_1970; digits = 2))%, 2000 $(round(100 * r.rel_2000; digits = 2))%, 2025 $(round(100 * r.rel_2025; digits = 2))%, 2100 $(round(100 * r.rel_2100; digits = 2))%")
end

# ---- 4. population and key values at selected years ------------------------------------------
note("")
note("### Population (sum of the four cohorts, millions) and key stocks at selected years")
popcols = ["pop₊p1(t)", "pop₊p2(t)", "pop₊p3(t)", "pop₊p4(t)"]
function at(df, y, c) df[findfirst(==(y), df.time), c] end
function tot(df, y) sum(at(df, y, c) for c in popcols) / 1e6 end
for y in years
    note("- $(Int(y)): population World3 $(round(tot(d74, y); digits = 1)), World3_03 $(round(tot(d03, y); digits = 1)); " *
         "industrial capital $(round(at(d74, y, "is₊ic(t)") / 1e9; digits = 1)) vs $(round(at(d03, y, "is₊ic(t)") / 1e9; digits = 1)) G; " *
         "non-renewable resources $(round(at(d74, y, "nr₊nr(t)") / 1e9; digits = 1)) vs $(round(at(d03, y, "nr₊nr(t)") / 1e9; digits = 1)) G; " *
         "persistent pollution $(round(at(d74, y, "pp₊ppol(t)") / 1e9; digits = 2)) vs $(round(at(d03, y, "pp₊ppol(t)") / 1e9; digits = 2)) G")
end
pk74 = argmax([tot(d74, y) for y in d74.time]); pk03 = argmax([tot(d03, y) for y in d03.time])
note("- peak population: World3 $(round(tot(d74, d74.time[pk74]); digits = 0)) M in $(d74.time[pk74]); World3_03 $(round(tot(d03, d03.time[pk03]); digits = 0)) M in $(d03.time[pk03])")

write(joinpath(OUT, "world3_variants_report.md"), join(REPORT, "\n") * "\n")
