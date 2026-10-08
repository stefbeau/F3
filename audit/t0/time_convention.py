"""Time-convention evidence (M0, review item 16): see docs/time-convention-evidence.md.
Run from the repository root:  uv run python audit/t0/time_convention.py <path to WPP2024_Population1JanuaryByAge5GroupSex_Medium.csv.gz>
The UN file is downloaded to a scratch folder outside the repository (population.un.org) and is not committed."""
import csv, gzip, sys, numpy as np
def load(p):
    r=list(csv.DictReader(open(p,encoding='utf-8-sig'))); return {k:np.array([float(x[k]) for x in r]) for k in r[0]}
# UN WPP 2024 5-year age file (1 January, World, Medium) -> totals and cohorts, 1 Jan values for years Y
f=gzip.open(sys.argv[1],'rt',encoding='utf-8-sig')
jan={}
for d in csv.DictReader(f):
    if d['Location']=='World' and d['Variant']=='Medium': jan[(int(d['Time']),int(d['AgeGrpStart']))]=float(d['PopTotal'])*1000
tot=lambda y: sum(v for (yy,a),v in jan.items() if yy==y)
jul=lambda y: 0.5*(tot(y)+tot(y+1))     # mid-year approximated by the mean of the two 1 January values
print('UN total, 1 Jan vs mid-year (mean of 1 Jan Y and Y+1), billions:')
for y in (1970,2000,2025): print('  ',y,'%.3f  %.3f  (%.2f%%)'%(tot(y)/1e9,jul(y)/1e9,100*(jul(y)-tot(y))/tot(y)))
print()
print('Model population against observed under the four possible readings (percent, model minus observed over observed):')
print('  reading A: model t=Y is 1 January Y, compare with UN 1 January Y')
print('  reading B: model t=Y is 1 January Y, compare with UN mid-year Y   (what D-015 Finding 3 and D-019 used, with the mid-year value from the UN spreadsheet)')
print('  reading C: model t=Y is mid-year Y (i.e. 1 Jan = t-0.5), compare with UN 1 January Y: model at t=Y+0.5 vs 1 Jan Y')
print('  reading D: model t=Y is mid-year Y, compare with UN mid-year Y: same model value as A but UN mid-year')
for tag,ps in (('world3_1974','1974'),('world3_2004','2004')):
    ref=load(f'tests/fixtures/s1_reference_{tag}_default.csv')
    pop=lambda t: sum(np.interp(t,ref['time'],ref[f'pop₊p{k}']) for k in (1,2,3,4))
    for y in (1970,2000,2025):
        A=100*(pop(y)-tot(y))/tot(y); B=100*(pop(y)-jul(y))/jul(y); C=100*(pop(y+.5)-tot(y))/tot(y); D=100*(pop(y+.5)-jul(y))/jul(y)
        print('  %s %d: A %+.2f  B %+.2f  C %+.2f  D %+.2f   spread %.2f points'%(ps,y,A,B,C,D,max(A,B,C,D)-min(A,B,C,D)))
print()
print('Flow quantities: model births per year at t=Y versus the mean over [Y, Y+1) (what a calendar-year total would be):')
for tag,ps in (('world3_1974','1974'),('world3_2004','2004')):
    ref=load(f'tests/fixtures/s1_reference_{tag}_default.csv')
    for y in (1970,2000,2025):
        m=(ref['time']>=y)&(ref['time']<=y+1)
        a=np.interp(y,ref['time'],ref['pop₊br']); b=np.interp(y,ref['time'],ref['pop₊br'])
        mean=np.trapezoid(ref['pop₊br'][m],ref['time'][m])/(ref['time'][m][-1]-ref['time'][m][0])
        print('  %s %d: births at t=Y %.4g, mean over [Y,Y+1] %.4g, difference %+.2f%%'%(ps,y,a,mean,100*(mean-a)/a))
