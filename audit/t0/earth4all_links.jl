# M0 evidence for decision N4: which variables cross between the Earth4All.jl sectors that D-016 replaces
# (population, climate, foodland, wellbeing) and the sectors it reuses (output, demand, inventory, finance, public, energy,
# labour market, other)? Read from the package's own connection equations of the composed scenario.
#
# Run from the repository root in the pinned environment, with the Earth4All.jl clone outside the repository:
#   julia +1.10 --project=audit/env-earth4all audit/t0/earth4all_links.jl <clone> <output csv>
# Nothing is modified. Variable names are the package's own; each connection is "target sector variable ~ source sector variable".

using ModelingToolkit, DifferentialEquations
include(joinpath(ARGS[1], "src", "Earth4All.jl"))
const E = Earth4All

sys = Base.invokelatest(E.run_tltl)
eqs = Base.invokelatest(ModelingToolkit.equations, sys)
SECT = Dict("pop" => "population", "cli" => "climate", "foo" => "foodland", "wel" => "wellbeing", "out" => "output",
            "dem" => "demand", "inv" => "inventory", "fin" => "finance", "pub" => "public", "ene" => "energy",
            "lab" => "labourmarket", "oth" => "other")
REPLACED = Set(["population", "climate", "foodland", "wellbeing"])
parts(v) = begin
    s = string(v)
    m = match(r"^([a-z]{3})₊([^(]+)\(t\)$", s)
    m === nothing ? nothing : (SECT[m.captures[1]], String(m.captures[2]))
end
open(ARGS[2], "w") do io
    println(io, "target_sector,target_variable,source_sector,source_variable,direction")
    for e in eqs
        l, r = parts(e.lhs), parts(e.rhs)
        (l === nothing || r === nothing) && continue
        l[1] == r[1] && continue
        dir = (l[1] in REPLACED) == (r[1] in REPLACED) ? "same-group" :
              (r[1] in REPLACED ? "replaced->reused" : "reused->replaced")
        println(io, join([l[1], l[2], r[1], r[2], dir], ","))
    end
end
println("connections written to ", ARGS[2])
