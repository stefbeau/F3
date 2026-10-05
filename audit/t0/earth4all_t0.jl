# T0 — Earth4All sanity check with Earth4All.jl, run as published (D-011).
#
# Run from the repository root, inside the Earth4All.jl clone's own environment:
#   julia --project=<clone> audit/t0/earth4all_t0.jl <clone>
#
# The model code is not modified. The only change to the clone's environment
# is adding DataFrames and CSV so results can be exported.

using DataFrames, CSV

const CLONE = ARGS[1]
const OUT = get(ENV, "F3_OUT", joinpath(@__DIR__, "..", "results"))
mkpath(OUT)
const REPORT = ["## T0 — Earth4All reference (Earth4All.jl)", ""]
push!(REPORT, "- Commit audited: `$(get(ENV, "EARTH4ALL_COMMIT", "unknown"))`")

function step(f, name)
    try
        f()
        push!(REPORT, "- ✅ $name")
    catch e
        msg = first(sprint(showerror, e), 600)
        push!(REPORT, "- ❌ $name: `$(replace(msg, '\n' => ' '))`")
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

step("Load Earth4All module from the clone") do
    include(joinpath(CLONE, "src", "Earth4All.jl"))
end

# Discovery: record what the module offers, so T1–T4 can target real names.
step("List module functions in `earth4all_module_names.txt`") do
    mod = getfield(Main, :Earth4All)
    open(joinpath(OUT, "earth4all_module_names.txt"), "w") do io
        foreach(n -> println(io, n), names(mod; all = true))
    end
end

for (label, fname) in [("Too Little Too Late", :run_tltl_solution),
                       ("Giant Leap", :run_gl_solution)]
    step("Solve $label with `$fname()` and export states") do
        mod = getfield(Main, :Earth4All)
        isdefined(mod, fname) || error("function $fname not found (see module names list)")
        sol = Base.invokelatest(getfield(mod, fname))
        df = DataFrame(sol)
        CSV.write(joinpath(OUT, "earth4all_$(fname)_states.csv"), df)
        push!(REPORT, "  - $(nrow(df)) time points, $(ncol(df)) columns")
    end
end

for (label, fname) in [("TLTL figure vs Vensim", :fig_baserun_tltl),
                       ("Giant Leap figure vs Vensim", :fig_baserun_gl)]
    step("Regenerate $label with `$fname()`") do
        mod = getfield(Main, :Earth4All)
        isdefined(mod, fname) || error("function $fname not found")
        save_figure(Base.invokelatest(getfield(mod, fname)), "earth4all_$(fname)")
    end
end

write(joinpath(OUT, "t0_2_earth4all_report.md"), join(REPORT, "\n") * "\n")
println(join(REPORT, "\n"))
