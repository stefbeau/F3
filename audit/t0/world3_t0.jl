# T0 — World3 sanity check with WorldDynamics.jl v1.0.0 (MIT, D-012).
#
# Run from the repository root:
#   julia --project=audit/env audit/t0/world3_t0.jl
#
# RUN #4 — diagnosis revised after reading the package's own test log (run #3):
#   * Its tests fail with `BoundsError: attempt to access 1-element Vector{Float64}`,
#     i.e. the solver returns a ONE-point solution. That also explains the empty
#     Figure 7.7 and the 1-row export seen in run #3 (not an export problem).
#   * The log shows a warning "Initialization system is overdetermined. 16 equations
#     for 7 unknowns" and dependencies far newer than the package (ModelingToolkit
#     v9.84.0, OrdinaryDiffEq v6.105.0; the package dates from April 2024).
#   * Working hypothesis (NOT yet confirmed): the solver's initialization step fails
#     and returns early. This script records the return code and tries the solver's
#     documented initialization options. No equation, parameter or package file is
#     modified; only solver options are changed, and the cross-check against PyWorld3
#     then decides whether the result is right.

using WorldDynamics, DataFrames, CSV, Pkg

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const REPORT = ["## T0 — World3 reference (WorldDynamics.jl)", ""]
const W3 = WorldDynamics.World3
const SYS = Ref{Any}(nothing)
const SOL = Ref{Any}(nothing)     # first solution with enough time points
const FIRST = Ref{Any}(nothing)   # any solution at all (used to locate SciMLBase)

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

# One solve attempt. Never throws away information: the return code and the
# number of time points are always reported.
function attempt(label, kw)
    step("Solve (1900–2100), $label") do
        sol = Base.invokelatest(WorldDynamics.solve, SYS[], (1900, 2100); kw...)
        FIRST[] === nothing && (FIRST[] = sol)
        n = length(sol.t)
        push!(REPORT, "  - return code: `$(sol.retcode)`; $n time point(s); last time $(last(sol.t))")
        if n >= 50
            if SOL[] === nothing
                SOL[] = sol
                push!(REPORT, "  - **usable: this solution is used for the export and the cross-check**")
            end
        else
            push!(REPORT, "  - ⚠️ not usable: too few time points")
        end
    end
end

attempt("default options", NamedTuple())

step("Try solver initialization options") do
    FIRST[] === nothing && error("no solution object available to locate SciMLBase")
    SB = parentmodule(typeof(FIRST[]))
    push!(REPORT, "  - solution type lives in module `$SB`")
    for name in (:NoInit, :BrownFullBasicInit, :ShampineCollocationInit)
        if isdefined(SB, name)
            attempt("initializealg = $name()", (initializealg = getfield(SB, name)(),))
        else
            push!(REPORT, "  - ⚠️ `$name` not defined in `$SB`")
        end
    end
end

step("Export states to `world3_worlddynamics_states.csv`") do
    sol = SOL[]
    sol === nothing && error("no solver variant produced a usable solution")
    ts = collect(sol.t)
    MTK = parentmodule(typeof(SYS[]))                 # ModelingToolkit
    syms = string.(Base.invokelatest(MTK.unknowns, sol.prob.f.sys))
    M = permutedims(reduce(hcat, sol.u))              # time x states
    size(M, 2) == length(syms) || error("$(size(M, 2)) state columns but $(length(syms)) names")
    df = DataFrame(M, syms; makeunique = true)
    insertcols!(df, 1, :time => ts)
    CSV.write(joinpath(OUT, "world3_worlddynamics_states.csv"), df)
    open(joinpath(OUT, "world3_worlddynamics_columns.txt"), "w") do io
        foreach(c -> println(io, c), names(df))
    end
    push!(REPORT, "  - $(nrow(df)) time points from $(first(ts)) to $(last(ts)), $(ncol(df)) columns")
    pop_cols = [c for c in names(df) if occursin(r"(^|[₊.])p[1-4](\(t\))?$", c)]
    push!(REPORT, "  - candidate population-cohort columns: `$(pop_cols)`")
end

# The package's own figure functions call `solve` with default options, so they
# cannot work while the default solve returns a single point. Our own figure is
# drawn from the exported CSV by compare_world3.py instead.

write(joinpath(OUT, "t0_1_world3_report.md"), join(REPORT, "\n") * "\n")
println(join(REPORT, "\n"))
