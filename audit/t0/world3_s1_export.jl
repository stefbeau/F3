# Step 1.4: export the test fixtures for the Python port of the World3 population sector (S1).
#
# Run from the repository root, in the pinned environment (D-017), default solver options:
#   julia +1.10 --project=audit/env audit/t0/world3_s1_export.jl
# Output goes to $F3_OUT (default audit/results); the small files the tests need are copied to tests/fixtures/.
#
# For each variant (World3 = 1974 set, World3_03.scenario1 = 2004 set) two things are written:
#   * inputs: the four time series the population sector reads from the rest of World3, on a 1/16-year grid:
#       food per capita `dr₊fpc`, service output per capita `br₊sopc`, industrial output per capita `dr₊iopc`,
#       persistent pollution index `dr₊ppolx`. They are matched BY NAME (CLAUDE.md: the two Julia environments
#       list states in different orders) and are the values the full model had at each time.
#   * reference: the 15 states of the population sector and four derived rates (life expectancy, births, deaths,
#       total fertility) on a 0.5-year grid, from the default-option solve (D-017) and, as a diagnostic of the
#       reference's own solver error, from a solve with reltol = abstol = 1e-8.
# Nothing in the package is modified; ModelingToolkit is reached through the type of the system, as in world3_t0.jl.

using WorldDynamics, DataFrames, CSV

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const W3 = WorldDynamics.World3
const W303 = WorldDynamics.World3_03

const INPUTS = ["dr₊fpc(t)", "br₊sopc(t)", "dr₊iopc(t)", "dr₊ppolx(t)"]
const STATES = ["pop₊p1(t)", "pop₊p2(t)", "pop₊p3(t)", "pop₊p4(t)", "dr₊ehspc(t)",
                "br₊ple(t)", "br₊ple2(t)", "br₊ple1(t)",
                "br₊diopc(t)", "br₊diopc2(t)", "br₊diopc1(t)", "br₊aiopc(t)",
                "br₊fcfpc(t)", "br₊fcfpc2(t)", "br₊fcfpc1(t)"]
const DERIVED = ["dr₊le(t)", "pop₊br(t)", "pop₊dr(t)", "br₊tf(t)"]

r10(x) = round(x; sigdigits = 10)

function solve_variant(f, label; kw...)
    sys = Base.invokelatest(f)
    MTK = parentmodule(typeof(sys))
    sol = Base.invokelatest(WorldDynamics.solve, sys, (1900, 2100); saveat = 0.0625, kw...)
    println("$label: retcode $(sol.retcode), $(length(sol.t)) points, last $(last(sol.t))")
    sol.retcode == :Success || sol.retcode == WorldDynamics.ModelingToolkit.SciMLBase.ReturnCode.Success ||
        error("$label did not return Success")
    simp = sol.prob.f.sys
    names = Dict{String,Any}()
    for u in Base.invokelatest(MTK.unknowns, simp)
        names[string(u)] = u
    end
    for e in Base.invokelatest(MTK.observed, simp)
        names[string(e.lhs)] = e.lhs
    end
    series(n) = (haskey(names, n) || error("$label: variable $n not found"); Base.invokelatest(getindex, sol, names[n]))
    return collect(sol.t), series
end

function export_variant(tag, f)
    t, series = solve_variant(f, tag)
    inp = DataFrame(time = t)
    for n in INPUTS
        inp[!, replace(n, "(t)" => "")] = r10.(series(n))
    end
    CSV.write(joinpath(OUT, "s1_inputs_$(tag).csv"), inp)

    for (suffix, kw) in (("default", NamedTuple()), ("tight", (reltol = 1e-8, abstol = 1e-8)))
        tt, ser = suffix == "default" ? (t, series) : solve_variant(f, "$tag $suffix"; kw...)
        keep = [i for i in eachindex(tt) if abs(tt[i] * 2 - round(tt[i] * 2)) < 1e-9]    # 0.5-year grid
        ref = DataFrame(time = tt[keep])
        for n in vcat(STATES, DERIVED)
            ref[!, replace(n, "(t)" => "")] = r10.(ser(n)[keep])
        end
        CSV.write(joinpath(OUT, "s1_reference_$(tag)_$(suffix).csv"), ref)
        println("  wrote reference $suffix: $(nrow(ref)) rows")
    end
end

export_variant("world3_1974", W3.historicalrun)
export_variant("world3_2004", W303.scenario1)
