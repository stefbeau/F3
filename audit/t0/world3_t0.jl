# T0 — World3 sanity check with WorldDynamics.jl v1.0.0 (MIT, D-012).
#
# Run from the repository root:
#   julia --project=audit/env audit/t0/world3_t0.jl
#
# DISCOVERY VERSION (run #2). Run #1 showed that the names guessed for the
# solver entry points were wrong. This version records what WorldDynamics.jl
# really exposes, and calls the one entry point its documentation confirms:
# `WorldDynamics.World3.fig_7()`. Every step is isolated; failures are
# reported with a short stack trace so the next fix is based on facts.

using WorldDynamics, DataFrames, CSV

const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const REPORT = ["## T0 — World3 reference (WorldDynamics.jl)", ""]
const W3 = WorldDynamics.World3

function step(f, name)
    try
        f()
        push!(REPORT, "- ✅ $name")
    catch e
        msg = first(sprint(showerror, e, catch_backtrace()), 2500)
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

# Names defined by a module, without compiler-generated ones.
public_names(mod) = sort([n for n in names(mod; all = true) if !startswith(string(n), "#")]; by = string)

step("List names defined by WorldDynamics and World3") do
    for (label, mod) in [("worlddynamics", WorldDynamics), ("world3_module", W3)]
        ns = public_names(mod)
        open(joinpath(OUT, "$(label)_names.txt"), "w") do io
            for n in ns
                kind = isdefined(mod, n) ? string(typeof(getfield(mod, n))) : "undefined"
                println(io, n, "\t", kind)
            end
        end
        fns = [string(n) for n in ns if isdefined(mod, n) && getfield(mod, n) isa Function]
        push!(REPORT, "  - `$label`: $(length(ns)) names, $(length(fns)) functions")
        push!(REPORT, "  - functions: " * join(first(fns, 120), ", "))
    end
end

step("Regenerate book Figure 7.7 with `World3.fig_7()`") do
    fig = Base.invokelatest(W3.fig_7)
    save_figure(fig, "world3_fig_7_7")
end

write(joinpath(OUT, "t0_1_world3_report.md"), join(REPORT, "\n") * "\n")
println(join(REPORT, "\n"))
