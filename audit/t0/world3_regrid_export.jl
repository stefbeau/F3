# Fixture correction (docs/m3-fixture-regrid-reading.md, 2026-10-21): re-export the recorded inputs of S1 (s1_inputs_*) and of the four
# M3 sectors (w3_signals_*) on a 1/64-year grid, 12 significant digits, from the same pinned environment and default-option solve as the
# originals. The REFERENCE files (0.5-year grid, default and tight) are NOT touched. Values at 1/64-year points are the adaptive
# solver's dense output (no new solver steps).
#
#   julia +1.10 --project=audit/env audit/t0/world3_regrid_export.jl      (F3_OUT: output folder, default audit/results)
using WorldDynamics, DataFrames, CSV

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const W3 = WorldDynamics.World3
const W303 = WorldDynamics.World3_03
const S1_INPUTS = ["dr₊fpc(t)", "br₊sopc(t)", "dr₊iopc(t)", "dr₊ppolx(t)"]
const SIGNALS = [
    "ld₊pop", "ld₊io", "ld₊iopc", "lfd₊ppolx",
    "is₊pop", "is₊fcaor", "is₊fioaa", "js₊aiph", "js₊al", "js₊p2", "js₊p3",
    "nr₊pop", "nr₊iopc",
    "pp₊pcrum", "pp₊pop", "pp₊aiph", "pp₊al",
]
r12(x) = round(x; sigdigits = 12)

function solve_variant(f, label)
    sys = Base.invokelatest(f)
    MTK = parentmodule(typeof(sys))
    sol = Base.invokelatest(WorldDynamics.solve, sys, (1900, 2100); saveat = 1 / 64)
    println("$label: retcode $(sol.retcode), $(length(sol.t)) points, last $(last(sol.t))")
    sol.retcode == :Success || sol.retcode == WorldDynamics.ModelingToolkit.SciMLBase.ReturnCode.Success || error("$label did not return Success")
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
    for n in S1_INPUTS
        inp[!, replace(n, "(t)" => "")] = r12.(series(n))
    end
    CSV.write(joinpath(OUT, "s1_inputs_$(tag).csv"), inp)
    df = DataFrame(time = t)
    for n in SIGNALS
        df[!, n] = r12.(series(n * "(t)"))
    end
    CSV.write(joinpath(OUT, "w3_signals_$(tag).csv"), df)
    println("  wrote s1_inputs and w3_signals: $(nrow(df)) rows")
end

export_variant("world3_1974", W3.historicalrun)
export_variant("world3_2004", W303.scenario1)
