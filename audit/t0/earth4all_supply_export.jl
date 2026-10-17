# Track A: export Earth4All.jl electricity production (variable ene.EP, TWh/y) from the two published scenarios (TLTL, GL), by name.
#   julia +1.10 --project=audit/env-earth4all audit/t0/earth4all_supply_export.jl <clone> <output csv>
# Pinned commit 16f37d0, package run as published (Euler, dt = 1/64, 1980-2100). Only numbers are written (MIT-licensed code output).
using ModelingToolkit, DifferentialEquations, DataFrames, CSV
include(joinpath(ARGS[1], "src", "Earth4All.jl"))
const E = Earth4All
out = DataFrame(year = Float64[], scenario = String[], EP_TWh = Float64[], DE_TWh = Float64[])
for (nm, f) in (("TLTL", E.run_tltl_solution), ("GL", E.run_gl_solution))
    sol = Base.invokelatest(f)
    names = Dict(string(s) => i for (i, s) in enumerate(ModelingToolkit.unknowns(sol.prob.f.sys)))
    obs = Dict(string(s.lhs) => s for s in ModelingToolkit.observed(sol.prob.f.sys))
    function series(nm2)
        for s in (nm2,)
            for (k, v) in obs
                k == s && return [Base.invokelatest(sol, t, idxs = v.lhs) for t in 1980:2100]
            end
            haskey(names, s) && return [sol(t)[names[s]] for t in 1980:2100]
        end
        error("variable $nm2 not found")
    end
    ep = series("ene₊EP(t)"); de = series("ene₊DE(t)")
    for (i, y) in enumerate(1980:2100)
        push!(out, (y, nm, ep[i], de[i]))
    end
end
CSV.write(ARGS[2], out)
println("wrote ", ARGS[2], " rows ", nrow(out))
