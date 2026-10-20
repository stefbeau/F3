# M3: export the test fixtures for the Python port of the four remaining World3 sectors (agriculture, capital,
# non-renewable resources, persistent pollution) and for the full coupled run (A3.1 and A3.2 of docs/phase-2-plan.md).
#
# Run from the repository root, in the pinned environment (D-017), default solver options:
#   julia +1.10 --project=audit/env audit/t0/world3_m3_export.jl
# Output goes to $F3_OUT (default audit/results); the files the tests need are copied to tests/fixtures/.
#
# For each variant (World3 = 1974 set, World3_03.scenario1 = 2004 set), matched BY NAME (CLAUDE.md):
#   * w3_signals_<tag>.csv: the recorded inputs of the four sectors (SIGNALS), on a 1/16-year grid, default solve.
#   * w3_reference_<tag>_default.csv / _tight.csv: all 29 states plus the algebraic variables DERIVED on a 0.5-year grid,
#     from the default-option solve (D-017) and from a solve with reltol = abstol = 1e-8 (the reference's own solver error).
# Nothing in the package is modified; ModelingToolkit is reached through the type of the system, as in world3_s1_export.jl.

using WorldDynamics, DataFrames, CSV

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const W3 = WorldDynamics.World3
const W303 = WorldDynamics.World3_03

const STATES = ["pop₊p1", "pop₊p2", "pop₊p3", "pop₊p4", "dr₊ehspc", "br₊ple", "br₊ple2", "br₊ple1",
                "br₊diopc", "br₊diopc2", "br₊diopc1", "br₊aiopc", "br₊fcfpc", "br₊fcfpc2", "br₊fcfpc1",
                "ld₊al", "ld₊pal", "ai₊ai", "leuiu₊uil", "lfd₊lfert", "dlm₊pfr",
                "is₊ic", "ss₊sc", "js₊lufd", "nr₊nr", "pp₊ppapr1", "pp₊ppapr2", "pp₊ppapr3", "pp₊ppol"]
# recorded inputs ("signals") of each sector, by the WorldDynamics.jl name the sector has for them, on a 1/16-year grid
const SIGNALS = [
    "ld₊pop", "ld₊io", "ld₊iopc", "lfd₊ppolx",                                 # agriculture
    "is₊pop", "is₊fcaor", "is₊fioaa", "js₊aiph", "js₊al", "js₊p2", "js₊p3",    # capital (industry, services, jobs)
    "nr₊pop", "nr₊iopc",                                                       # non-renewable resources
    "pp₊pcrum", "pp₊pop", "pp₊aiph", "pp₊al",                                  # persistent pollution
]
# algebraic variables compared on the 0.5-year grid (reference side of A3.1 and A3.2)
const DERIVED = [
    "ld₊fpc", "ld₊f", "ld₊fioaa", "ai₊aiph", "ai₊ly", "ld₊tai", "iad₊fiald",
    "is₊io", "is₊iopc", "ss₊sopc", "ss₊so", "js₊cuf", "js₊j", "js₊lf",
    "nr₊fcaor", "nr₊pcrum", "nr₊nrfr", "nr₊nrur",
    "pp₊ppolx", "pp₊ppgr", "pp₊ppapr", "pp₊ppasr", "pp₊ahl",
    "se₊foa", "se₊foi", "se₊fos",
]

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
    series(n) = (k = n * "(t)"; haskey(names, k) || error("$label: variable $n not found"); Base.invokelatest(getindex, sol, names[k]))
    return collect(sol.t), series
end

function export_variant(tag, f)
    t, series = solve_variant(f, tag)
    df = DataFrame(time = t)
    for n in SIGNALS
        df[!, n] = r10.(series(n))
    end
    CSV.write(joinpath(OUT, "w3_signals_$(tag).csv"), df)
    println("  wrote signals: $(nrow(df)) rows, $(ncol(df) - 1) columns")
    for (suffix, kw) in (("default", NamedTuple()), ("tight", (reltol = 1e-8, abstol = 1e-8)))
        tt, ser = suffix == "default" ? (t, series) : solve_variant(f, "$tag $suffix"; kw...)
        keep = [i for i in eachindex(tt) if abs(tt[i] * 2 - round(tt[i] * 2)) < 1e-9]    # 0.5-year grid
        ref = DataFrame(time = tt[keep])
        for n in vcat(STATES, DERIVED)
            ref[!, n] = r10.(ser(n)[keep])
        end
        CSV.write(joinpath(OUT, "w3_reference_$(tag)_$(suffix).csv"), ref)
        println("  wrote reference $suffix: $(nrow(ref)) rows")
    end
end

export_variant("world3_1974", W3.historicalrun)
export_variant("world3_2004", W303.scenario1)
