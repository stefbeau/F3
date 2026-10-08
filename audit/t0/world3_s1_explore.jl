# Step 1.4 helper: find how the population sector's external inputs (food per capita, service output per
# capita, industrial output per capita, pollution index) can be read from a WorldDynamics.jl World3 solution.
# Run: julia +1.10 --project=audit/env audit/t0/world3_s1_explore.jl   (pinned environment, D-017)
using WorldDynamics

const W3 = WorldDynamics.World3
sys = Base.invokelatest(W3.historicalrun)
MTK = parentmodule(typeof(sys))
sol = Base.invokelatest(WorldDynamics.solve, sys, (1900, 2100); saveat = 0.5)
println("retcode ", sol.retcode, ", points ", length(sol.t))
simp = sol.prob.f.sys
obs = Base.invokelatest(MTK.observed, simp)
println("observed equations: ", length(obs))
pat = r"(fpc|sopc|iopc|ppolx|₊le\(|₊tf\(|₊br\(|₊dr\()"
for e in obs
    s = string(e.lhs)
    occursin(pat, s) && println("  ", s, "  ~  ", first(string(e.rhs), 90))
end
println("unknowns matching: ", [string(u) for u in Base.invokelatest(MTK.unknowns, simp) if occursin(pat, string(u))])
# try reading one
for e in obs
    if string(e.lhs) == "dr₊fpc(t)" || string(e.lhs) == "dr₊iopc(t)"
        v = Base.invokelatest(getindex, sol, e.lhs)
        println(string(e.lhs), " first values: ", v[1:3], " last: ", v[end])
    end
end
