# T0 — Earth4All sanity check with Earth4All.jl, run as published (D-011).
#
# Run from the repository root, in the pinned environment audit/env-earth4all (Project.toml and
# Manifest.toml committed; resolved once for commit 16f37d0 plus DataFrames and CSV), with the
# Earth4All.jl clone outside this repository:
#   julia --project=audit/env-earth4all -e 'using Pkg; Pkg.instantiate()'
#   julia --project=audit/env-earth4all audit/t0/earth4all_t0.jl <clone>
#
# The model code is not modified. The clone is only read (its src/ and, for the package's own
# comparison, its VensimOutput/, D-014); the packages come from the committed Manifest, not from a
# run-time resolve. The clone's own Project.toml is not used and is not modified.

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

# Discovery: repository layout of the clone (top two levels). Needed to find out
# whether reference output for the Vensim comparison ships with the repository.
step("Record the repository layout of the clone") do
    lines = String[]
    for (root, dirs, files) in walkdir(CLONE)
        rel = relpath(root, CLONE)
        (rel == ".git" || startswith(rel, ".git/")) && continue
        depth = rel == "." ? 0 : length(splitpath(rel))
        depth > 2 && continue
        listing = isempty(files) ? "" : " — " * join(first(sort(files), 15), ", ") * (length(files) > 15 ? ", …" : "")
        push!(lines, "$(rel)/  ($(length(files)) files)$(listing)")
    end
    write(joinpath(OUT, "earth4all_repo_tree.txt"), join(lines, "\n") * "\n")
    push!(REPORT, "  - " * join(first(lines, 30), "\n  - "))
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

# Numeric Julia-vs-Vensim check, using the package's OWN function `Earth4All.all_mre`
# (src/functions.jl). It reads the Vensim output shipped inside the clone
# (VensimOutput/<scenario>/<sector>.txt) at run time, from the clone only (D-011, D-014):
# nothing from VensimOutput/ is copied into the F3 repository or into the results.
# Error metric defined by the package: |julia - vensim| / (|vensim| + 1), over 7681 points.
# The function prints one line per variable ("description<TAB>error"); we capture and
# summarise those lines. The package's own run is not a test suite; we only report.
for (scen, fname) in [("TLTL", :run_tltl_solution), ("GL", :run_gl_solution)]
    step("Julia vs Vensim with the package's own `all_mre(\"$scen\", sol)`") do
        mod = getfield(Main, :Earth4All)
        isdefined(mod, :all_mre) || error("`all_mre` is not defined in the Earth4All module")
        sol = Base.invokelatest(getfield(mod, fname))
        logfile = joinpath(OUT, "earth4all_all_mre_$(scen).txt")
        cd(CLONE) do                       # all_mre uses paths relative to the clone root
            open(logfile, "w") do io
                redirect_stdout(io) do
                    Base.invokelatest(getfield(mod, :all_mre), scen, sol)
                end
            end
        end
        errs = Tuple{String,Float64}[]
        for line in eachline(logfile)
            parts = split(line, '\t')
            length(parts) == 2 || continue
            v = tryparse(Float64, strip(parts[2]))
            v === nothing || push!(errs, (String(parts[1]), v))
        end
        isempty(errs) && error("no per-variable errors found in the captured output ($(basename(logfile)))")
        sort!(errs; by = x -> -x[2])
        push!(REPORT, "  - $(length(errs)) variables compared; maximum error **$(round(errs[1][2]; sigdigits = 3))** (`$(errs[1][1])`)")
        push!(REPORT, "  - variables with error above 1e-3: $(count(x -> x[2] > 1e-3, errs)); above 1e-2: $(count(x -> x[2] > 1e-2, errs)); above 1e-1: $(count(x -> x[2] > 1e-1, errs))")
        push!(REPORT, "  - ten largest: " * join(["`$(x[1])` ($(round(x[2]; sigdigits = 3)))" for x in errs[1:min(10, length(errs))]], "; "))
    end
end

# Error statistics beyond the maximum (D-014 approved 2026-10-05). The package's `all_mre`
# reports only the worst of 7,681 time points per variable, which a one-step timing offset
# of a switched input can dominate. Here the same comparison (same data, same metric
# |julia - vensim| / (|vensim| + 1), same variable filter as `mre_sys`) is repeated with
# median, mean and 95th percentile over time and the year of the maximum.
# Only variable descriptions and error figures are stored; no Vensim values (D-014).
for (scen, fname) in [("TLTL", :run_tltl_solution), ("GL", :run_gl_solution)]
    step("Error statistics per variable, $scen (median, 95th percentile, year of maximum)") do
        mod = getfield(Main, :Earth4All)
        sol = Base.invokelatest(getfield(mod, fname))
        sa = Base.invokelatest(getfield(mod, :system_array))
        sn = Base.invokelatest(getfield(mod, :sector_name))
        MTK = parentmodule(typeof(sa[1]))                      # ModelingToolkit
        nt = 7681
        rows = NamedTuple[]
        skipped = 0
        for (s, sector) in enumerate(sn)
            path = joinpath(CLONE, "VensimOutput", lowercase(scen), sector * ".txt")
            vs = Base.invokelatest(getfield(mod, :read_vensim_dataset), path, " : E4A-220501 " * scen)
            for v in Base.invokelatest(MTK.namespace_variables, sa[s])
                d = Base.invokelatest(MTK.getdescription, v)
                (d == "" || d == "Time instants" || startswith(d, "LV functions") || startswith(d, "RT functions")) && continue
                try
                    a = Base.invokelatest(getindex, sol, v)[1:nt]
                    b = vs[lowercase(d)]
                    re = abs.(a .- b) ./ (abs.(b) .+ 1)
                    srt = sort(re)
                    n = length(srt)
                    imax = argmax(re)
                    push!(rows, (sector = sector, variable = d, max_error = re[imax],
                                 year_of_max = sol.t[imax], median_error = srt[(n + 1) ÷ 2],
                                 mean_error = sum(re) / n, p95_error = srt[clamp(ceil(Int, 0.95 * n), 1, n)]))
                catch
                    skipped += 1
                end
            end
        end
        isempty(rows) && error("no variable could be compared")
        df = DataFrame(map(identity, rows))          # concrete element type
        CSV.write(joinpath(OUT, "earth4all_error_stats_$(scen).csv"), df)
        sortedp = sort(df, :p95_error; rev = true)
        push!(REPORT, "  - $(nrow(df)) variables ($(skipped) skipped); median of per-variable medians **$(round(sort(df.median_error)[(nrow(df) + 1) ÷ 2]; sigdigits = 3))**; " *
                      "95th percentile above 1e-2: $(count(>(1e-2), df.p95_error)); above 1e-1: $(count(>(1e-1), df.p95_error)); " *
                      "maximum above 1e-1: $(count(>(1e-1), df.max_error))")
        for sector in sn
            sub = df[df.sector .== sector, :]
            nrow(sub) == 0 && continue
            push!(REPORT, "  - `$sector`: $(nrow(sub)) variables, 95th percentile above 1e-2: $(count(>(1e-2), sub.p95_error)), maximum above 1e-1: $(count(>(1e-1), sub.max_error))")
        end
        push!(REPORT, "  - ten largest by 95th percentile: " * join(["`$(r.variable)` (p95 $(round(r.p95_error; sigdigits = 3)), max $(round(r.max_error; sigdigits = 3)) in $(round(r.year_of_max; digits = 1)))" for r in eachrow(sortedp[1:min(10, nrow(sortedp)), :])], "; "))
        lab = df[occursin.(r"(?i)workforce|employ|labou?r", df.variable), :]
        if nrow(lab) > 0
            push!(REPORT, "  - labour-related variables (D-010 test T2): " * join(["`$(r.variable)` (median $(round(r.median_error; sigdigits = 2)), p95 $(round(r.p95_error; sigdigits = 2)), max $(round(r.max_error; sigdigits = 2)) in $(round(r.year_of_max; digits = 1)))" for r in eachrow(lab[1:min(12, nrow(lab)), :])], "; "))
        end
    end
end

write(joinpath(OUT, "t0_2_earth4all_report.md"), join(REPORT, "\n") * "\n")
println(join(REPORT, "\n"))
