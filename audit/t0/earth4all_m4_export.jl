# M4 export: pinned runs of Earth4All.jl (MIT, commit 16f37d0) in both scenarios, exported BY NAME for the F3 port tests.
#
# Run from the repository root in the pinned environment, with the Earth4All.jl clone outside the repository:
#   julia +1.10 --project=audit/env-earth4all audit/t0/earth4all_m4_export.jl <clone> <fixtures dir> <audit data dir>
#
# Writes, per scenario (tltl, gl):
#   <fixtures>/e4a_reference_<scen>.csv   every variable of the eight reused sectors (output, inventory, finance, labourmarket,
#                                          public, demand, energy, other) at the 0.5-year points 1980.0 ... 2100.0; columns "sector.VAR"
#   <fixtures>/e4a_signals_<scen>.csv     every variable that crosses a sector boundary in the composed model (source sector variables
#                                          listed in audit/data/earth4all_cross_sector_links.csv, including the replaced sectors'
#                                          POP, GDPP, EGDPP, A20PA, OW, CAC, COFO, IPP) on the 1/16-year grid
#   <audit>/e4a_vs_vensim_<scen>.csv      Earth4All.jl's OWN error against Vensim, per variable of the eight sectors: TRUE relative error
#                                          |julia - vensim| / |vensim| (median, 95th percentile, maximum, year of maximum, points
#                                          excluded). Names and error figures only; no Vensim value is stored (D-014). The Vensim files are
#                                          read from the clone at run time through the package's own `read_vensim_dataset`.
#   <fixtures>/e4a_names.csv              column -> package description (names only)
#
# Points where |vensim| <= 1e-6 x max |vensim| of the series are excluded from the relative error and counted (plan, track-c-plan.md).
# The model code is not modified. The clone is only read. `vensim_source/` is not used.

using ModelingToolkit, DifferentialEquations, DataFrames, CSV, Printf
include(joinpath(ARGS[1], "src", "Earth4All.jl"))
const E = Earth4All
const CLONE = ARGS[1]
const FIX = ARGS[2]
const AUD = ARGS[3]
mkpath(FIX); mkpath(AUD)

const SECT = Dict("pop" => "population", "cli" => "climate", "foo" => "foodland", "wel" => "wellbeing", "out" => "output",
                  "dem" => "demand", "inv" => "inventory", "fin" => "finance", "pub" => "public", "ene" => "energy",
                  "lab" => "labourmarket", "oth" => "other")
const REUSED = ["output", "inventory", "finance", "labourmarket", "public", "demand", "energy", "other"]

function split_name(v)
    s = string(v)
    m = match(r"^([a-z]{3})₊([^(]+)\(t\)$", s)
    m === nothing ? nothing : (SECT[m.captures[1]], String(m.captures[2]))
end

links = CSV.read(joinpath(@__DIR__, "..", "data", "earth4all_cross_sector_links.csv"), DataFrame)
signal_pairs = sort(unique([(r.source_sector, r.source_variable) for r in eachrow(links)]))

sa = Base.invokelatest(E.system_array)
sn = Base.invokelatest(E.sector_name)
MTK = ModelingToolkit

names_rows = NamedTuple[]
for (scen, fname) in [("tltl", :run_tltl_solution), ("gl", :run_gl_solution)]
    println("solving ", scen); flush(stdout)
    sol = Base.invokelatest(getfield(E, fname))
    nt = length(sol.t)
    @assert nt == 7681 && sol.t[1] == 1980.0 && abs(sol.t[end] - 2100.0) < 1e-9
    @assert maximum(abs.(diff(sol.t) .- 0.015625)) < 1e-12
    # column index: sector => variable symbol => unknown
    idx = Dict{Tuple{String,String},Any}()
    desc = Dict{Tuple{String,String},String}()
    for s in 1:length(sn)
        for v in Base.invokelatest(MTK.namespace_variables, sa[s])
            p = split_name(v)
            p === nothing && continue
            idx[p] = v
            desc[p] = Base.invokelatest(MTK.getdescription, v)
        end
    end
    # the signals come from every system: add the other four sectors' variables not in system_array's reused list (all are, system_array covers 12)
    refcols = Pair{String,Vector{Float64}}[]
    half = 1:32:nt            # 0.5 year
    for sector in REUSED
        keys_s = sort([k for k in keys(idx) if k[1] == sector]; by = k -> k[2])
        for k in keys_s
            vals = Base.invokelatest(getindex, sol, idx[k])
            push!(refcols, "$(k[1]).$(k[2])" => Float64.(vals[half]))
            scen == "tltl" && push!(names_rows, (column = "$(k[1]).$(k[2])", description = desc[k]))
        end
    end
    df = DataFrame(:time => sol.t[half])
    for (c, v) in refcols
        df[!, c] = v
    end
    CSV.write(joinpath(FIX, "e4a_reference_$(scen).csv"), df)
    sixteenth = 1:4:nt
    sigdf = DataFrame(:time => sol.t[sixteenth])
    for p in signal_pairs
        haskey(idx, p) || (println("missing signal ", p); continue)
        sigdf[!, "$(p[1]).$(p[2])"] = Float64.(Base.invokelatest(getindex, sol, idx[p])[sixteenth])
    end
    CSV.write(joinpath(FIX, "e4a_signals_$(scen).csv"), sigdf)
    println("reference columns ", ncol(df) - 1, ", signals ", ncol(sigdf) - 1); flush(stdout)

    # Earth4All.jl's own error against Vensim (true relative error), through the package's own reader, at run time, from the clone
    rows = NamedTuple[]
    skipped = String[]
    for (s, sector) in enumerate(sn)
        sector in REUSED || continue
        path = joinpath(CLONE, "VensimOutput", scen, sector * ".txt")
        vs = Base.invokelatest(E.read_vensim_dataset, path, " : E4A-220501 " * uppercase(scen))
        for v in Base.invokelatest(MTK.namespace_variables, sa[s])
            p = split_name(v)
            p === nothing && continue
            d = Base.invokelatest(MTK.getdescription, v)
            (d == "" || d == "Time instants" || startswith(d, "LV functions") || startswith(d, "RT functions")) && continue
            if !haskey(vs, lowercase(d))
                push!(skipped, "$(p[1]).$(p[2])")
                continue
            end
            a = Float64.(Base.invokelatest(getindex, sol, v)[1:nt])
            b = vs[lowercase(d)]
            length(b) == nt || (push!(skipped, "$(p[1]).$(p[2])"); continue)
            scale = maximum(abs.(b))
            ok = abs.(b) .> 1e-6 * scale
            n_ex = count(!, ok)
            if scale == 0 || count(ok) == 0
                push!(rows, (sector = sector, variable = p[2], median = NaN, p95 = NaN, maximum = NaN, year_of_max = NaN, excluded = n_ex, all_zero = true))
                continue
            end
            re = abs.(a[ok] .- b[ok]) ./ abs.(b[ok])
            tt = sol.t[ok]
            srt = sort(re); n = length(srt)
            im = argmax(re)
            push!(rows, (sector = sector, variable = p[2], median = srt[(n + 1) ÷ 2], p95 = srt[clamp(ceil(Int, 0.95 * n), 1, n)],
                         maximum = re[im], year_of_max = tt[im], excluded = n_ex, all_zero = false))
        end
    end
    CSV.write(joinpath(AUD, "e4a_vs_vensim_$(scen).csv"), DataFrame(rows))
    write(joinpath(AUD, "e4a_vs_vensim_$(scen)_not_compared.txt"), join(sort(skipped), "\n") * "\n")
    println(scen, ": ", length(rows), " variables compared with Vensim, ", length(skipped), " not found in the Vensim file"); flush(stdout)
end
CSV.write(joinpath(FIX, "e4a_names.csv"), DataFrame(names_rows))
println("done")
