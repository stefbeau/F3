# T0 — World3 sanity check with WorldDynamics.jl v1.0.0 (MIT, D-012).
#
# Run from the repository root:
#   julia --project=audit/env audit/t0/world3_t0.jl
#
# RUN #3. Run #2 showed that `World3.fig_7()` fails inside the package:
# `historicalrunsolution()` (plots.jl:6) calls `solve`, which is not visible in
# the World3 module. `WorldDynamics.solve` itself exists. This version
#   1. repeats the plain call (to keep the failure documented),
#   2. solves the historical run directly: World3.historicalrun() + WorldDynamics.solve,
#   3. retries Figure 7.7 after making `solve` visible inside the World3 module.
# Step 3 only changes name visibility at run time. No equation, parameter or
# package file is modified. Every step is isolated and reported.

using WorldDynamics, DataFrames, CSV

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const REPORT = ["## T0 — World3 reference (WorldDynamics.jl)", ""]
const W3 = WorldDynamics.World3
const SYS = Ref{Any}(nothing)
const SOL = Ref{Any}(nothing)

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

function save_figure(fig, base)
    saved = String[]
    if showable(MIME"text/html"(), fig)
        open(joinpath(OUT, base * ".html"), "w") do io
            show(io, MIME"text/html"(), fig)
        end
        push!(saved, base * ".html")
    end
    if showable(MIME"image/png"(), fig)
        try
            open(joinpath(OUT, base * ".png"), "w") do io
                show(io, MIME"image/png"(), fig)
            end
            push!(saved, base * ".png")
        catch
        end
    end
    isempty(saved) && error("figure of type $(typeof(fig)) could not be saved as HTML or PNG")
    push!(REPORT, "  - saved: " * join(saved, ", ") * " (type `$(typeof(fig))`)")
end

step("Plain `World3.fig_7()` (known to fail in v1.0.0 — see run #2)") do
    save_figure(Base.invokelatest(W3.fig_7), "world3_fig_7_7_plain")
end

step("Build the system with `World3.historicalrun()`") do
    SYS[] = Base.invokelatest(W3.historicalrun)
    push!(REPORT, "  - returned type: `$(typeof(SYS[]))`")
end

step("Solve it with `WorldDynamics.solve(system, (1900, 2100))`") do
    SOL[] = Base.invokelatest(WorldDynamics.solve, SYS[], (1900, 2100))
    push!(REPORT, "  - solution type: `$(typeof(SOL[]))`")
end

step("Export states to `world3_worlddynamics_states.csv`") do
    df = DataFrame(SOL[])
    CSV.write(joinpath(OUT, "world3_worlddynamics_states.csv"), df)
    open(joinpath(OUT, "world3_worlddynamics_columns.txt"), "w") do io
        foreach(c -> println(io, c), names(df))
    end
    push!(REPORT, "  - $(nrow(df)) time points, $(ncol(df)) columns")
    pop_cols = [c for c in names(df) if occursin(r"(^|[₊.])p[1-4](\(t\))?$", c)]
    push!(REPORT, "  - candidate population-cohort columns: `$(pop_cols)`")
end

step("Figure 7.7 after making `solve` visible inside World3 (run-time workaround)") do
    isdefined(W3, :solve) || Core.eval(W3, :(solve = $(WorldDynamics.solve)))
    save_figure(Base.invokelatest(W3.fig_7), "world3_fig_7_7")
end

write(joinpath(OUT, "t0_1_world3_report.md"), join(REPORT, "\n") * "\n")
println(join(REPORT, "\n"))
