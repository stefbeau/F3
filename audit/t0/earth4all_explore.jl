# Exploration helper for the Earth4All audit (D-010, T1b-T4): finds the names the audit script needs.
# Run: julia --project=<Earth4All.jl clone> audit/t0/earth4all_explore.jl <clone>
# Nothing is modified; output goes to stdout.

using ModelingToolkit
const CLONE = ARGS[1]
include(joinpath(CLONE, "src", "Earth4All.jl"))
const E = Earth4All

sys = Base.invokelatest(E.run_tltl)
eqs = Base.invokelatest(ModelingToolkit.equations, sys)
println("composed system: ", length(eqs), " equations; type ", typeof(sys))
println("first 5 equations:")
foreach(e -> println("  ", string(e)[1:min(end, 160)]), eqs[1:5])

pat = r"(?i)wellbeing|social tension|inequality|observed warming|gdp per person|^population|aged|working age|workforce"
sa = Base.invokelatest(getfield(E, :system_array))
sn = Base.invokelatest(getfield(E, :sector_name))
for (s, sector) in enumerate(sn)
    for v in Base.invokelatest(ModelingToolkit.namespace_variables, sa[s])
        d = Base.invokelatest(ModelingToolkit.getdescription, v)
        occursin(pat, d) && println(sector, " | ", v, " | ", d)
    end
end
