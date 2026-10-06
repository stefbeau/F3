# T0 — World3 sanity check with WorldDynamics.jl v1.0.0 (MIT, D-012).
#
# Run from the repository root:
#   julia --project=audit/env audit/t0/world3_t0.jl
#
# RUN #8 (pinned-dependency search, see .github/workflows/audit-world3-pins.yml): default-option
# variants added, so the same script can show whether a given dependency set solves World3
# WITHOUT any workaround. (Notes from run #5 below.)
# RUN #5. Findings so far (see audit/T0-FINDINGS.md):
#   * Run #4 confirmed that with default options the solver returns
#     `InitialFailure` and a single time point, while `initializealg = NoInit()`
#     returns `Success` over 1900–2100. Only a solver option differs from the
#     defaults; no equation, parameter or package file is modified.
#   * With NoInit the solution had only 50 saved points and a ~0.9% maximum
#     population gap to PyWorld3. PyWorld3 itself carries a time-step error of
#     about the same size (dt=0.5 vs dt=0.05: max 0.9%). This run therefore
#     (a) saves the solution every 0.5 years and (b) adds a tight-tolerance
#     variant, to see how much of the gap is numerical.
# Every usable variant is exported to its own CSV for the cross-check.

using WorldDynamics, DataFrames, CSV, Pkg

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const REPORT = ["## T0 — World3 reference (WorldDynamics.jl)", ""]
const W3 = WorldDynamics.World3
const SYS = Ref{Any}(nothing)
const FIRST = Ref{Any}(nothing)               # any solution at all (to locate SciMLBase)
const SOLS = Pair{String,Any}[]               # tag => usable solution

function step(f, name)
    try
        f()
        push!(REPORT, "- ✅ $name")
    catch e
        msg = first(sprint(showerror, e, catch_backtrace()), 1800)
        push!(REPORT, "- ❌ $name")
        push!(REPORT, "  ```")
        push!(REPORT, "  " * replace(msg, "\n" => "\n  "))
        push!(REPORT, "  ```")
    end
end

step("Versions of key packages in this environment") do
    keep = ["WorldDynamics", "ModelingToolkit", "DifferentialEquations", "OrdinaryDiffEq",
            "OrdinaryDiffEqCore", "SciMLBase", "DiffEqBase"]
    for (_, info) in Pkg.dependencies()
        info.name in keep && push!(REPORT, "  - $(info.name) $(info.version)")
    end
end

step("Build the system with `World3.historicalrun()`") do
    SYS[] = Base.invokelatest(W3.historicalrun)
    push!(REPORT, "  - returned type: `$(typeof(SYS[]))`")
end

# One solve attempt. The return code and number of time points are always reported.
function attempt(tag, label, kw)
    step("Solve (1900–2100), $label") do
        sol = Base.invokelatest(WorldDynamics.solve, SYS[], (1900, 2100); kw...)
        FIRST[] === nothing && (FIRST[] = sol)
        n = length(sol.t)
        push!(REPORT, "  - return code: `$(sol.retcode)`; $n time point(s); last time $(last(sol.t))")
        if n >= 50
            push!(SOLS, tag => sol)
        else
            push!(REPORT, "  - ⚠️ not usable: too few time points")
        end
    end
end

attempt("default", "default options", NamedTuple())
attempt("default_saveat", "default options, saveat = 0.5", (saveat = 0.5,))
attempt("default_tight", "default options, saveat = 0.5, reltol = abstol = 1e-8",
        (saveat = 0.5, reltol = 1e-8, abstol = 1e-8))

step("Try solver variants with `initializealg = NoInit()`") do
    FIRST[] === nothing && error("no solution object available to locate SciMLBase")
    SB = parentmodule(typeof(FIRST[]))
    if !isdefined(SB, :NoInit)
        push!(REPORT, "  - `NoInit` is not defined in `$SB`: variants skipped")
        return
    end
    ni = getfield(SB, :NoInit)()
    attempt("noinit", "NoInit()", (initializealg = ni,))
    attempt("noinit_saveat", "NoInit(), saveat = 0.5", (initializealg = ni, saveat = 0.5))
    attempt("noinit_tight", "NoInit(), saveat = 0.5, reltol = abstol = 1e-8",
            (initializealg = ni, saveat = 0.5, reltol = 1e-8, abstol = 1e-8))
end

step("Export every usable solution to `world3_worlddynamics_states_<variant>.csv`") do
    isempty(SOLS) && error("no solver variant produced a usable solution")
    MTK = parentmodule(typeof(SYS[]))                 # ModelingToolkit
    wrote_columns = false
    for (tag, sol) in SOLS
        ts = collect(sol.t)
        syms = string.(Base.invokelatest(MTK.unknowns, sol.prob.f.sys))
        M = permutedims(reduce(hcat, sol.u))          # time x states
        size(M, 2) == length(syms) || error("$tag: $(size(M, 2)) state columns but $(length(syms)) names")
        df = DataFrame(M, syms; makeunique = true)
        insertcols!(df, 1, :time => ts)
        CSV.write(joinpath(OUT, "world3_worlddynamics_states_$(tag).csv"), df)
        if !wrote_columns
            open(joinpath(OUT, "world3_worlddynamics_columns.txt"), "w") do io
                foreach(c -> println(io, c), names(df))
            end
            pop_cols = [c for c in names(df) if occursin(r"(^|[₊.])p[1-4](\(t\))?$", c)]
            push!(REPORT, "  - $(ncol(df)) columns; candidate population-cohort columns: `$(pop_cols)`")
            wrote_columns = true
        end
        push!(REPORT, "  - `$tag`: $(nrow(df)) time points, $(first(ts))–$(last(ts))")
    end
end

# The package's own figure functions call `solve` with default options, so they
# cannot work while the default solve fails. Figures are drawn from the exported
# CSV files by compare_world3.py instead.

write(joinpath(OUT, "t0_1_world3_report.md"), join(REPORT, "\n") * "\n")
println(join(REPORT, "\n"))
