# T0 — World3 sanity check with WorldDynamics.jl v1.0.0 (MIT, D-012).
#
# Run from the repository root:
#   julia --project=audit/env audit/t0/world3_t0.jl
#
# Each step is isolated: a failure is recorded in the report and the next
# step still runs. This first run is also a discovery run: it records the
# variable names WorldDynamics.jl exposes, which later tests depend on.

using WorldDynamics, DataFrames, CSV

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const REPORT = ["## T0 — World3 reference (WorldDynamics.jl)", ""]

function step(f, name)
    try
        f()
        push!(REPORT, "- ✅ $name")
    catch e
        msg = first(sprint(showerror, e), 600)
        push!(REPORT, "- ❌ $name: `$(replace(msg, '\n' => ' '))`")
    end
end

# Save any figure object as HTML (and PNG if the type supports it).
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

const SOL = Ref{Any}(nothing)

step("Solve World3 standard run, 1900–2100") do
    system = WorldDynamics.World3.world3()
    SOL[] = WorldDynamics.solve(system, (1900, 2100))
end

step("Export solver states to `world3_worlddynamics_states.csv`") do
    df = DataFrame(SOL[])
    CSV.write(joinpath(OUT, "world3_worlddynamics_states.csv"), df)
    open(joinpath(OUT, "world3_worlddynamics_columns.txt"), "w") do io
        foreach(c -> println(io, c), names(df))
    end
    push!(REPORT, "  - $(nrow(df)) time points, $(ncol(df)) columns (list in `world3_worlddynamics_columns.txt`)")
end

step("Regenerate book Figure 7.7 with `World3.fig_7()`") do
    save_figure(WorldDynamics.World3.fig_7(), "world3_fig_7_7")
end

write(joinpath(OUT, "t0_1_world3_report.md"), join(REPORT, "\n") * "\n")
println(join(REPORT, "\n"))
