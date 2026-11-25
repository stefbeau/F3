"""Atlas pages (D-067, Provisional): what is reported about AI's effects on people and the planet, shown beside what F3 models.

Two kinds of numbers appear and are never mixed in one chart or one table:
  * REPORTED figures, each with a numbered link to the source it was read from on 2026-11-25. Most were read in news reports or summaries of the
    original study, not in the study itself (research/SOURCES.md, section "Atlas"). They are not F3 output and F3 does not vouch for them.
  * F3 OUTPUT, read from site/data/explorer.json at build time (no new run) and only from series the site already draws: FaIR warming, the damage
    fraction, S3's automated fraction and World3's resource fraction. Each carries the notice of its sector, taken verbatim from the data file.
Withheld series (S3 compute, data-centre electricity) are not drawn or tabulated here either. Wording is neutral: no page recommends a policy.
The world outline is Natural Earth 1:110m land (public domain), Equal Earth projection, stored simplified in atlas_map.json."""
from __future__ import annotations

import html as _h
import json
import re
from pathlib import Path

READ_ON = "2026-11-25"
LABEL = "Reported figures, not F3 model output"
TOPICS = [("energy", "Power and climate"), ("water", "Water"), ("land", "Land, metals, chips and waste"), ("work", "Work and the economy"), ("robots", "Robots"),
          ("health", "Health and science"), ("mind", "Learning, minds and information"), ("safety", "Safety, access and rules"),
          ("military", "Military use"), ("creative", "Creative work and copyright"), ("surveillance", "Surveillance"), ("nature", "Nature and food")]
F3_STATE = {"energy": "model", "work": "model", "land": "model"}          # every other topic: "none"
STATE_TEXT = {"model": "F3 output shown", "none": "Not modelled"}
PAGE_NAMES = ["atlas.html"] + [f"atlas-{k}.html" for k, _ in TOPICS]
esc = _h.escape
S: dict = {}


def src(key: str, label: str, url: str) -> None:
    S[key] = (label, url)


def c(keys: list, key: str) -> str:
    return f'<sup><a href="#s-{key}">{keys.index(key) + 1}</a></sup>'


def refs(keys: list) -> str:
    items = "".join(f'<li id="s-{k}"><a href="{esc(S[k][1])}">{esc(S[k][0])}</a></li>' for k in keys)
    return f'<section class="at-src"><h2>Sources for this page</h2><p class="small">Read on {READ_ON}. Numbers in the text point here.</p><ol>{items}</ol></section>'


def tile(k: str, n: str, d: str, cls: str = "") -> str:
    return f'<div class="at-tile {cls}"><span class="at-k">{k}</span><strong class="at-n">{n}</strong><span class="at-d">{d}</span></div>'


def bars(rows: list, unit: str, caption: str, vmax: float = None, w: int = 640) -> str:
    """Horizontal bars as plain HTML rows, so they fit a phone without sideways scrolling. One scale per chart; the value is printed on each row."""
    vmax = vmax or max(v for _, v, _ in rows)
    out = "".join(f'<div class="at-brow"><span class="at-lab">{esc(lab)}</span><span class="at-btrack"><i class="at-bfill {cls}" style="width:{max(100 * v / vmax, 0.6):.1f}%"></i></span>'
                  f'<span class="at-val">{v:,g} {unit}</span></div>' for lab, v, cls in rows)
    return f'<div class="at-bars" role="img" aria-label="{esc(caption)}">{out}</div><p class="at-capline">{esc(caption)}</p>'


MARK = {"g": '<svg class="at-mark" viewBox="0 0 16 16" aria-hidden="true"><circle class="g" cx="8" cy="8" r="7"></circle></svg>',
        "s": '<svg class="at-mark" viewBox="0 0 16 16" aria-hidden="true"><path class="s" d="M8 1 15 14H1Z"></path></svg>',
        "u": '<svg class="at-mark" viewBox="0 0 16 16" aria-hidden="true"><rect class="u" x="2" y="2" width="12" height="12"></rect></svg>'}


def ledger(g: list, s: list, u: list) -> str:
    col = lambda m, t, items: f"<div><h3>{MARK[m]}{t}</h3><ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul></div>"      # noqa: E731
    return '<div class="at-ledger">' + col("g", "What is gained", g) + col("s", "What it costs", s) + col("u", "What is not known", u) + "</div>"


def world_map() -> str:
    m = json.loads((Path(__file__).parent / "atlas_map.json").read_text(encoding="utf-8"))
    dots = "".join(f'<circle class="at-pb" cx="{p["x"]}" cy="{p["y"]}" r="6"></circle>' if p["k"] == "build"
                   else f'<rect class="at-pw" x="{p["x"] - 5}" y="{p["y"] - 5}" width="10" height="10"></rect>' for p in m["world"])
    alt = ("World map. Large AI campuses are concentrated in the United States, with one in England and one in Inner Mongolia. Water-stress hotspots for "
           "data centres are marked in Arizona, Mexico, Chile, Spain, Italy, the Gulf states and India.")
    return (f'<div class="at-map"><svg viewBox="0 0 1000 500" role="img" aria-label="{alt}"><path class="at-sea" d="{m["sphere"]}"></path>'
            f'<path class="at-landp" d="{m["d"]}"></path>{dots}</svg></div>'
            '<div class="at-legend"><span><svg class="at-mark" viewBox="0 0 16 16" aria-hidden="true"><circle class="at-pb" cx="8" cy="8" r="6"></circle></svg>'
            'Large AI campus, built or planned</span><span><svg class="at-mark" viewBox="0 0 16 16" aria-hidden="true"><rect class="at-pw" x="3" y="3" width="10" height="10"></rect></svg>'
            'Water-stress hotspot for data centres</span><span>Positions approximate. A selection named in reports, not a full count.</span></div>')


# ------------------------------------------------------------------------------------------------------------ sources (label, link)

src('iea-weo','IEA World Energy Outlook 2026, as reported by CNBC (19 Nov 2026)','https://www.cnbc.com/2026/11/19/data-center-electricity-demand-iea.html')
src('iea-70','IEA World Energy Outlook 2026 on emissions, as reported by the Irish Examiner','https://www.irishexaminer.com/world/arid-41939628.html')
src('iea-mix','IEA on the 2030 power mix for data centres, as reported by Bernama','https://bernama.com/en/world/news.php?id=2636821')
src('iea-ai','IEA, Energy and AI: AI and climate change','https://www.iea.org/reports/energy-and-ai/ai-and-climate-change')
src('iea-news','IEA news release on data-centre electricity use in 2025','https://www.iea.org/news/data-centre-electricity-use-surged-in-2025-even-with-tightening-bottlenecks-driving-a-scramble-for-solutions')
src('tr-93','TechRadar on the 93 large AI facilities tracked by the IEA','https://www.techradar.com/pro/power-demands-at-ai-data-centers-set-to-double-by-2030-adding-the-equivalent-of-another-great-britain-to-the-grid-as-an-extra-usd4-trillion-in-spending-kicks-in')
src('erock','ERock prospectus (SEC filing) citing IEA on build times','https://www.sec.gov/Archives/edgar/data/0002110029/000119312526265898/d12401d424b4.htm')
src('nat-water','Nature Africa on IEA water figures','https://www.nature.com/articles/d44148-026-00286-7')
src('earth-water','Earth.com on the Stanford and Carnegie global water-stress map','https://www.earth.com/science/one-in-four-data-centers-are-located-in-water-stressed-regions/')
src('sf-water','StudyFinds on the same study (Environmental Science & Technology, 2026)','https://studyfinds.com/data-centers-strain-local-water-supplies/')
src('bb-water','Bloomberg, AI is draining water from areas that need it most','https://www.bloomberg.com/graphics/2025-ai-impacts-data-centers-water-data/')
src('ceres','Newsweek on the Ceres report on data centres and freshwater','https://www.newsweek.com/map-shows-states-using-the-most-water-for-data-centers-12374846')
src('dcmap','dcmap.us, data-centre water stress by US state','https://dcmap.us/insights/water-stress/')
src('qro','Tech Policy Press on data centres in Querétaro','https://www.techpolicy.press/many-latin-americans-living-near-data-centers-do-not-feel-welcome-in-the-future/')
src('chile','American Geographical Society, water usage of AI data centres','https://ethicalgeo.org/the-cloud-is-drying-our-rivers-water-usage-of-ai-data-centers/')
src('sfex','San Francisco Examiner on studies of AI water use','https://www.sfexaminer.com/news/technology/ai-water-use-studies-show-tech-may-be-thirstier-than-thought/article_3a0f3177-7b2d-4aea-96a9-2dfa2a0a5984.html')
src('hyperion','Fortune on Meta Hyperion in Louisiana','https://fortune.com/2026/03/26/meta-ai-data-center-hyperion-louisiana/')
src('ewaste','MIT Technology Review on the Nature Computational Science e-waste study','https://www.technologyreview.com/2024/10/28/1106316/ai-e-waste/amp/')
src('ewaste2','IEEE Spectrum on generative AI and e-waste','https://spectrum.ieee.org/e-waste-2669544726')
src('ewaste3','HPCwire on the global e-waste trend','https://www.hpcwire.com/2024/11/07/the-growing-e-waste-footprint-of-genai/')
src('copper',"Tom's Hardware on copper demand from data centres",'https://www.tomshardware.com/tech-industry/why-copper-markets-are-feeling-the-pinch')
src('ilo','ILO Working Paper 140, Generative AI and Jobs: a refined global index','https://www.ilo.org/node/706766')
src('ilo-caution','ILO brief on what AI exposure indicators reveal','https://www.ilo.org/resource/news/ilo-releases-new-brief-ai-exposure-measurement')
src('ilo-wb','ILO and World Bank paper on the uneven global impact of generative AI','https://ilo.org/resource/news/new-ilo%E2%80%93world-bank-paper-highlights-uneven-global-impact-generative-ai-jobs')
src('imf-katz','IMF Finance & Development, AI and the economics of adjustment (June 2026)','https://www.imf.org/en/publications/fandd/issues/series/analytical-series/straight-talk-artificial-intelligence-and-the-economics-of-adjustment-dan-katz')
src('etf','European Training Foundation, AI and the job market','https://www.etf.europa.eu/en/node/12971')
src('bofa','Bank of America Institute, AI and the future of work (ILO regional figures)','https://institute.bankofamerica.com/content/dam/transformation/ai-and-future-of-work.pdf')
src('oecd-tfp','OECD, Miracle or myth? Macroeconomic productivity gains from AI','https://www.oecd.org/en/publications/miracle-or-myth-assessing-the-macroeconomic-productivity-gains-from-artificial-intelligence_b524a072-en.html')
src('oecd-g7','OECD, Macroeconomic productivity gains from AI in G7 economies','https://www.oecd.org/en/publications/macroeconomic-productivity-gains-from-artificial-intelligence-in-g7-economies_a5319ab5-en.html')
src('hazan','Hazan, Does AI really boost productivity? (ENS-PSL, 2026)','https://www.ens.psl.eu//sites/default/files/2026-05/Does%20AI%20Really%20Boost%20Productivity_.pdf')
src('imf-ar','IMF Annual Report 2026, AI: deployment and disruption','https://www.imf.org/annual-report/2026/in-focus/ai-deployment-and-disruption/')
src('cepr',"CEPR VoxEU, AI's gains are large, rising and unevenly shared",'https://cepr.org/index%2ephp/voxeu/columns/ais-gains-are-large-and-rising-unevenly-shared')
src('aiindex','Stanford HAI, AI Index Report 2026: medicine','https://hai.stanford.edu/ai-index/2026-ai-index-report/medicine')
src('healio','Healio on the 2026 census of FDA-cleared AI devices','https://www.healio.com/news/primary-care/20260821/most-ai-tools-cleared-by-fda-were-not-tested-on-clinical-outcomes')
src('epoc','Epocrates synopsis of the PLOS Digital Health census','https://www.epocrates.com/online/article/ai-medical-device-clearance-skips-outcomes-data')
src('stan-clin','Stanford Medicine on the State of Clinical AI report','https://medicine.stanford.edu/news/current-news/standard-news/clinical-ai-has-boomed.html')
src('single','SingleCare, AI in healthcare statistics 2026','https://www.singlecare.com/blog/news/ai-in-healthcare-statistics/')
src('f3data','F3 Explorer open data counts (OpenAlex, Epoch AI, FDA)','https://stefbeau.github.io/F3/')
src('iza-tutor','IZA discussion paper 19072 on AI tutoring (cites OECD 2026)','https://docs.iza.org/dp19072.pdf')
src('iza-africa','IZA discussion paper 19025, From chatbots to programs','https://docs.iza.org/dp19025.pdf')
src('reyes','Contractor and Reyes, Experimental evidence on the learning impact of generative AI','https://conference.nber.org/conf_papers/f236743.pdf')
src('edweek','Education Week, Is AI good or bad for learning? (Nov 2026)','https://www.edweek.org/technology/is-ai-good-or-bad-for-learning-the-answer-isnt-so-simple/2026/11')
src('npr-teens','NPR via OPB on teen and tween chatbot use','https://opb.org/article/2026/10/30/new-research-looks-at-teen-mental-health-and-ai-chatbot-use')
src('va','Virginia JCOTS report, AI chatbots: companionship and minors','https://dls.virginia.gov/commissions/jcots/Materials/2026_AI_Chatbots_Report.pdf')
src('ottawa','University of Ottawa on AI use for emotional support among students','https://www.uottawa.ca/en/news-all/uottawa-study-finds-ai-use-emotional-support-may-signal-youth-distress')
src('stan-lonely','Stanford HAI on AI companions and loneliness','https://hai.stanford.edu/news/ai-companions-may-worsen-loneliness-for-vulnerable-users-stanford-study-finds')
src('wef','World Economic Forum on AI and disinformation in 2026','https://www.weforum.org/stories/digital-trust-and-safety/ai-2026-jp')
src('fullfact','Full Fact, AI-generated misinformation in the UK','https://fullfact.org/policy/reports/ai-generated-misinformation-in-the-uk-harm-context-and-classification/')
src('ofcom','Ofcom literature review on online threats to elections (Oct 2026)','https://www.ofcom.org.uk/siteassets/resources/documents/about-ofcom/structure-and-leadership/online-information-advisory-committee/a-literature-review-on-online-information-based-threats-to-elections.pdf')
src('digiday','Digiday on the rise of deepfakes','https://digiday.com/media/the-rise-of-deepfakes-poses-a-new-trust-challenge-for-publishers/')
src('iasr','International AI Safety Report 2026, press release','https://www.aap.com.au/aapreleases/cision20260203ae77099')
src('iasr-heise','Heise on the International AI Safety Report 2026','https://heise.de/-11164043')
src('iasr-soc','SOCRadar key facts from the International AI Safety Report 2026','https://socradar.io/blog/international-ai-safety-report-2026-key-facts/')
src('iasr-asis','ASIS Security Management on the report','https://www.asisonline.org/security-management-magazine/latest-news/today-in-security/2026/february/2026-international-safety-report/')
src('iasr-au','Australian government page on the report','https://www.industry.gov.au/publications/international-ai-safety-report-2026')
src('fpf','Future of Privacy Forum, the AI Act timeline after the AI Omnibus','https://fpf.org/blog/the-ai-act-implementation-timeline-what-changes-under-the-ai-omnibus')
src('aj-act','Al Jazeera on what came into force with the EU AI Act in August 2026','https://aljazeera.com/news/2026/8/6/what-came-into-force-with-the-eus-ai-act-this-week-and-what-didnt')
src('brookings','Brookings, How to bridge the global AI divide','https://www.brookings.edu/articles/how-to-bridge-the-global-ai-divide/?hl=en-GB')
src('aj-divide','Al Jazeera on the AI opportunity divide (ITU, Oct 2026)','https://www.aljazeera.com/amp/news/2026/10/25/ais-opportunity-divide-could-deepen-global-inequality-un-official-warns')
src('undp','UNDP, The Next Great Divergence','https://www.undp.org/asia-pacific/next-great-divergence')
src('rb-ifr', 'IFR press release, Five million robots now operate in factories globally (24 Sept 2026)', 'https://ifr.org/ifr-press-releases/news/five-million-robots-now-operate-in-factories-globally')
src('rb-ifr2', 'IFR President’s report with World Robotics 2026 figures', 'https://ifr.org/news/presidents-report-by-jane-heffner-3-2026/1st-')
src('rb-sag', 'TechRepublic on Smart Analytics Global humanoid shipment estimates (Aug 2026)', 'https://techrepublic.com/article/news-humanoid-robot-shipments-chinese-vendors')
src('rb-cp', 'Counterpoint Research, humanoid robot shipments in the first half of 2026', 'https://counterpointresearch.com/xmlrpc.php/insights/global-humanoid-robot-shipments-soar-nearly-300-percent-yoy-in-h1-2026')
src('rb-idc', 'HRD on humanoid robots at work, citing IDC and Gartner', 'https://www.hcamag.com/ca/news/general/humanoid-robots-are-starting-real-jobs-how-soon-will-they-replace-real-staff/594972')
src('rb-r247', 'Robotics 24/7, Humanoid orders versus actual deployments (Oct 2026)', 'https://www.robotics247.com/article/humanoid-orders-vs-actual-deployments-how-much-commercial-progress-is-really-happening')
src('rb-anth', 'Anthropic, What work can robots do? (2026)', 'https://www.anthropic.com/research/what-work-can-robots-do')
src('rb-bis', 'BIS Working Paper 1334, Robots, ICT and employment (March 2026)', 'https://www.bis.org/publ/work1334.htm')
src('rb-ifrpos', 'IFR position paper, The impact of robots (Aug 2026)', 'https://ifr.org/ifr-press-releases/news/new-ifr-position-paper-the-impact-of-robots')
src('rb-berg', 'Berg Insight forecast of humanoid shipments to 2040', 'https://iconnect007.com/article/151498/humanoid-robot-shipments-to-reach-26-million-units-annually-by-2040/151495/milaero')
src('chip-ti', 'TechInsights, Semiconductor Sustainability Outlook 2027', 'https://techinsights.com/ja/node/61968')
src('chip-wef', 'World Economic Forum on water in semiconductor manufacturing', 'https://www.weforum.org/stories/2024/07/the-water-challenge-for-semiconductor-manufacturing-and-big-tech-what-needs-to-be-done/')
src('chip-aj', 'Al Jazeera on chip manufacturing and Taiwan’s climate goals (2024)', 'https://www.aljazeera.com/economy/2024/12/25/taiwan-struggles-to-reconcile-climate-ambitions-and-chip-manufacturing')
src('mil-ac1', 'Arms Control Today, U.S., Russia oppose UN resolutions on military use of AI (Dec 2025)', 'https://www.armscontrol.org/act/2025-12/news/us-russia-oppose-un-resolutions-military-use-ai')
src('mil-oj', 'Opinio Juris on General Assembly resolution 80/57 (Aug 2026)', 'https://opiniojuris.org/2026/08/27/the-western-consensus-that-was-not-resolution-80-57-the-rolling-texts-human-control-substitution-and-the-structural-stakes-of-the-november-2026-ccw-review-conference/')
src('mil-ac2', 'Arms Control Today, UN members discuss AI in the military domain (Jul/Aug 2026)', 'https://www.armscontrol.org/node/15386')
src('mil-fortune', 'Fortune on the joint UN and Red Cross statement (25 Aug 2026)', 'https://www.fortune.com/2026/08/25/killer-robots-un-red-cross/')
src('mil-hurriyet', 'Hürriyet Daily News on the Geneva review conference (Nov 2026)', 'https://www.hurriyetdailynews.com/un-chief-urges-action-to-rein-in-merciless-autonomous-weapons-229462')
src('mil-reuters', 'Reuters via Yahoo News, Nations meet at UN for killer-robot talks', 'https://www.yahoo.com/news/nations-meet-un-killer-robot-132715611.html')
src('mil-ars', 'Ars Technica (via Harvard TagTeam) on the $54 billion drone request', 'https://tagteam.harvard.edu/hub_feeds/3382/feed_items/18141320')
src('mil-bbg', 'Bloomberg (via Advisor Perspectives) on the $75 billion drone request', 'https://advisorperspectives.com/articles/2026/04/21/pentagon-seeks-75-billion-drones-defense-budget')
src('mil-dscoop', 'DefenseScoop on the fiscal 2027 drone and counter-drone plan', 'https://defensescoop.com/2026/04/21/dod-plans-largest-ever-investment-drones-anti-drone-weapons/')
src('mil-carnegie', 'Carnegie Endowment, testimony on AI in the military domain and human rights (Sept 2026)', 'https://carnegieendowment.org/middle-east/posts/2026/09/on-artificial-intelligence-in-the-military-domain-and-the-implications-for-human-rights')
src('mil-hrw', 'Human Rights Watch briefing for the UN exchanges (June 2026)', 'https://www.hrw.org/news/2026/06/14/addressing-artificial-intelligence-in-the-military-domain')
src('mil-perry', 'Perry World House, Designing lawful military AI', 'https://perryworldhouse.upenn.edu/news-and-insight/designing-lawful-military-ai-technical-and-legal-reflections-on-decision-support-and-autonomous-weapon-systems/')
src('mil-sipri1', 'SIPRI, AI and nuclear escalation risk', 'https://www.sipri.org/node/7464')
src('mil-sipri2', 'SIPRI, Pragmatic approaches to governance at the AI–nuclear nexus (2025)', 'https://www.sipri.org/publications/2025/other-publications/pragmatic-approaches-governance-artificial-intelligence-nuclear-nexus')
src('mil-unric', 'UN Regional Information Centre, AI in conflict', 'https://unric.org/en/ai-in-conflict-keeping-humanity-in-control/')
src('cr-pymnts', 'PYMNTS, citing Reuters, on AI copyright cases in 2026', 'https://www.pymnts.com/cpi-posts/us-courts-poised-to-shape-the-future-of-ai-copyright-battles-in-2026/')
src('cr-cleary', 'Cleary Gottlieb, The open questions in US generative AI copyright litigation', 'https://www.clearygottlieb.com/news-and-insights/publication-listing/the-open-questions-in-us-generative-ai-copyright-litigation')
src('cr-dj', 'Daily Journal, Courts grapple with copyright limits as AI training lawsuits surge', 'https://dailyjournal.com/articles/389209-courts-grapple-with-copyright-limits-as-ai-training-lawsuits-surge')
src('cr-pg', 'Press Gazette, Publishers versus AI: the legal rulings so far', 'https://pressgazette.co.uk/?p=246203')
src('cr-nrf', 'Norton Rose Fulbright via PYMNTS, update on AI copyright cases (March 2026)', 'https://www.pymnts.com/?p=3613558')
src('cr-week', 'The Week, AI gains at creators’ expense', 'https://www.theweek.com/tech/ai-fair-use-copyrighted-media-trains-bots')
src('sv-carnegie', 'Carnegie Endowment, The global expansion of AI surveillance (2019 index)', 'https://carnegieendowment.org/2024/09/04/global-expansion-of-ai-surveillance-pub-79847')
src('sv-bio', 'Biometric Update on the Carnegie index', 'https://www.biometricupdate.com/201909/carnegie-report-says-facial-recognition-and-ai-surveillance-spreading-faster-than-thought')
src('sv-aj', 'Al Jazeera on the Carnegie index (2019)', 'https://www.aljazeera.com/amp/news/2019/9/17/researchers-warn-of-increased-china-style-ai-surveillance')
src('sv-cms', 'CMS Law on AI-enabled mass surveillance in Africa (April 2026)', 'https://cms.law/en/gbr/publication/ai-enabled-mass-surveillance-in-africa-privacy-rights-and-regulatory-gaps')
src('sv-allafrica', 'AllAfrica on smart-city surveillance across Africa (March 2026)', 'https://allafrica.com/stories/202603180021.html')
src('sv-bis', 'BankInfoSecurity on AI surveillance and policing', 'https://www.bankinfosecurity.com/blogs/ai-surveillance-tech-promises-safety-but-at-what-cost-p-2792')
src('nf-scan', 'Reynolds et al., The potential for AI to revolutionize conservation: a horizon scan (Trends in Ecology & Evolution)', 'https://www.cl.cam.ac.uk/~avsm2/2024-ai-conhorizon/')
src('nf-jae', 'Ammar et al., AI and decision support in applied ecology (Journal of Applied Ecology, 2026)', 'https://nora.nerc.ac.uk/id/eprint/541872/1/N541872JA.pdf')
src('nf-conv', 'The Conversation (via SANBI), AI in nature conservation (June 2026)', 'https://opus.sanbi.org/bitstreams/a9aaf849-ab16-4625-be6b-cacc0e2358c4/download')
src('nf-wb', 'World Bank fact sheet, Harnessing AI for agricultural transformation', 'https://thedocs.worldbank.org/en/doc/5f6713ffe87d349fd09c40ec3803c7bb-0320012025/original/fact-sheet-harnessing-AI-for-agricultural-transformation.pdf')
src('nf-wbblog', 'World Bank blog, Can AI give small-scale producers the right advice?', 'https://blogs.worldbank.org/en/agfood/can-ai-give-small-scale-producers-the-right-advice-')
src('nf-rct', 'Authors’ summary of a randomised field experiment on AI advice for smallholders (SSRN paper)', 'https://tr.linkedin.com/in/ali-bakan-20579586')
src('nf-3ie', '3ie rapid review, The use of AI in food and agriculture systems', 'https://www.grtd.fcdo.gov.uk/research/the-use-of-artificial-intelligence-in-food-and-agriculture-systems/')
src('nf-dte', 'Down To Earth, AI offers promise for agriculture, but smallholders risk being left behind', 'https://www.downtoearth.org.in/agriculture/ai-offers-promise-for-agriculture-but-smallholder-farmers-risk-being-left-behind')


# ------------------------------------------------------------------------------------------------------------ infographics (reported figures only)


def fig(inner: str, caption: str) -> str:
    return f'<figure class="at-ig">{inner}<figcaption>Reported figures. {caption}</figcaption></figure>'


def legend(items: list) -> str:
    return '<div class="at-legend">' + "".join(f'<span><i class="at-sw {cls}"></i>{esc(t)}</span>' for cls, t in items) + "</div>"


def waffle(total: int, groups: list, cols: int, alt: str) -> str:
    """A grid of ``total`` squares; ``groups`` is [(count, class)], filled in order, the rest empty."""
    cell, gap = 16, 4
    rows = -(-total // cols)
    cls = [c for n, c in groups for _ in range(n)] + ["e"] * total
    sq = "".join(f'<rect class="at-w {cls[i]}" x="{(i % cols) * (cell + gap)}" y="{(i // cols) * (cell + gap)}" width="{cell}" height="{cell}" rx="2"></rect>' for i in range(total))
    return f'<div class="at-chart"><svg class="at-waffle" viewBox="0 0 {cols * (cell + gap) - gap} {rows * (cell + gap) - gap}" role="img" aria-label="{esc(alt)}">{sq}</svg></div>'


def propbar(parts: list, alt: str) -> str:
    """One bar split in proportion; ``parts`` is [(value, class)]."""
    tot, x, out = sum(v for v, _ in parts), 0.0, []
    for v, cls in parts:
        wd = 600 * v / tot
        out.append(f'<rect class="at-w {cls}" x="{x:.1f}" y="0" width="{max(wd - 2, 1.5):.1f}" height="36" rx="3"></rect>')
        x += wd
    return f'<div class="at-chart"><svg viewBox="0 0 600 36" role="img" aria-label="{esc(alt)}">{"".join(out)}</svg></div>'


def dots(items: list, alt: str) -> str:
    """Circles whose AREA is proportional to the value, stacked in rows so the drawing fits a phone; ``items`` is [(value, label, class)]."""
    big = max(v for v, _, _ in items)
    rmax, y, out = 70, 0.0, []
    for v, lab, cls in items:
        r = max(rmax * (v / big) ** 0.5, 3)
        h = max(2 * r, 34) + 12
        out.append(f'<circle class="at-w {cls}" cx="{rmax}" cy="{y + h / 2:.1f}" r="{r:.1f}"></circle><text class="at-val" x="{2 * rmax + 16}" y="{y + h / 2 - 2:.1f}">{v:,}</text>'
                   f'<text class="at-cap" x="{2 * rmax + 16}" y="{y + h / 2 + 16:.1f}">{esc(lab)}</text>')
        y += h
    return f'<div class="at-chart"><svg viewBox="0 0 360 {y:.0f}" role="img" aria-label="{esc(alt)}">{"".join(out)}</svg></div>'


def timeline(items: list) -> str:
    return '<ol class="at-timeline">' + "".join(f"<li><strong>{esc(d)}</strong><span>{esc(t)}</span></li>" for d, t in items) + "</ol>"


def chain(items: list) -> str:
    return '<ol class="at-chain">' + "".join(f'<li><span class="at-k">{esc(k)}</span><strong class="at-n">{esc(n)}</strong><span class="at-d">{esc(d)}</span></li>' for k, n, d in items) + "</ol>"


# ------------------------------------------------------------------------------------------------------------ F3 output blocks


def warming_chart(d: dict) -> str:
    y, cl = d["years"], d["climate"]
    w, h, left, right, top, bot = 640, 280, 46, 70, 14, 34
    lo, hi = 1.0, 4.0
    px = lambda yr: left + (w - left - right) * (yr - y[0]) / (y[-1] - y[0])      # noqa: E731
    py = lambda v: top + (h - top - bot) * (hi - v) / (hi - lo)                   # noqa: E731
    band = " ".join(f"{px(a):.1f},{py(v):.1f}" for a, v in zip(y, cl["warming_p95"])) + " " + " ".join(f"{px(a):.1f},{py(v):.1f}" for a, v in zip(reversed(y), reversed(cl["warming_p05"])))
    line = " ".join(f"{px(a):.1f},{py(v):.1f}" for a, v in zip(y, cl["warming"]))
    grid = "".join(f'<line class="at-grid" x1="{left}" x2="{w - right}" y1="{py(v):.1f}" y2="{py(v):.1f}"></line><text class="at-cap" x="{left - 6}" y="{py(v) + 4:.1f}" text-anchor="end">{v:g} K</text>' for v in (1, 2, 3, 4))
    xs = "".join(f'<text class="at-cap" x="{px(a):.1f}" y="{h - 12}" text-anchor="middle">{a}</text>' for a in (2025, 2050, 2075, 2100))
    end = f'<circle class="at-dot" cx="{px(y[-1]):.1f}" cy="{py(cl["warming"][-1]):.1f}" r="4"></circle><text class="at-val" x="{px(y[-1]) + 8:.1f}" y="{py(cl["warming"][-1]) + 4:.1f}">{cl["warming"][-1]:.1f} K</text>'
    alt = (f'F3 output. Warming above 1850 to 1900 rises from {cl["warming"][0]:.1f} K in {y[0]} to {cl["warming"][-1]:.1f} K in {y[-1]} (ensemble mean); '
           f'the 5 to 95 percent range in {y[-1]} is {cl["warming_p05"][-1]:.1f} to {cl["warming_p95"][-1]:.1f} K.')
    return (f'<div class="at-chart"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{alt}">{grid}{xs}<polygon class="at-band" points="{band}"></polygon>'
            f'<polyline class="at-line" points="{line}"></polyline>{end}</svg></div>')


def f3_energy(d: dict) -> str:
    y, cl = d["years"], d["climate"]
    row = lambda yr: (f'<tr><th scope="row">{yr}</th><td>{cl["warming"][y.index(yr)]:.1f} K</td>'                                    # noqa: E731
                      f'<td>{cl["warming_p05"][y.index(yr)]:.1f} to {cl["warming_p95"][y.index(yr)]:.1f} K</td></tr>')
    dmg = lambda o, yr: f'{100 * d["runs"]["central|" + o + "|1"]["damage_fraction"][y.index(yr)]:.1f}%'                              # noqa: E731
    drow = lambda o, name: f'<tr><th scope="row">{name}</th><td>{dmg(o, 2050)}</td><td>{dmg(o, 2100)}</td></tr>'                       # noqa: E731
    return f'''<section class="card at-f3" data-f3="model" aria-labelledby="f3h"><p class="kicker">F3 output · a conditional scenario, not a forecast</p>
<h2 id="f3h">What F3’s model shows</h2>
<p><strong>Warming.</strong> F3’s climate sector replays the FaIR model with {d["meta"]["provenance"]["climate_members"]} members. The line is the ensemble mean, the band the 5 to 95% range, in kelvin above 1850 to 1900.</p>
{warming_chart(d)}
<div class="tblwrap"><table><thead><tr><th scope="col">Year</th><th scope="col">F3 warming, mean</th><th scope="col">5 to 95% range</th></tr></thead><tbody>{row(2030)}{row(2050)}{row(2100)}</tbody></table></div>
<p class="note"><strong>Notice (climate sector):</strong> {esc(d["meta"]["s6_status"])}</p>
<p><strong>What links the two halves of this page, and what does not.</strong> The emissions behind this curve are prescribed. They do not respond to the data-centre build-out reported above, so the IEA’s 70% rise in data-centre emissions is not in the F3 curve.</p>
<p><strong>Climate damage to output.</strong> With the damage switch on, F3 lowers economic output by a share that grows with warming:</p>
<div class="tblwrap"><table><thead><tr><th scope="col">Damage option</th><th scope="col">2050</th><th scope="col">2100</th></tr></thead><tbody>{drow("low", "Low (Nordhaus 2017)")}{drow("central", "Central (Barrage and Nordhaus 2024)")}{drow("high", "High (Howard and Sterner 2017)")}</tbody></table></div>
<p class="note">These are level-of-output effects. The high option is not the upper end of the literature: growth-effect estimates are larger and are not represented.</p>
<p><strong>Data-centre electricity: withheld.</strong> F3 computes it but does not show it. In the recorded runs it leaves any plausible range: about 20,000 TWh in 2030, against the roughly 1,000 TWh the IEA expects. The cause is a growth sector with no physical limit on power. An approved change (decision D-066) will let data centres grow only as fast as powered capacity can be built. It is not built yet. See <a href="limitations.html#status-ai">Limitations</a>.</p>
</section>'''


def f3_work(d: dict) -> str:
    y = d["years"]
    fr = lambda s, yr: f'{100 * d["runs"][s + "|central|1"]["frac_automated"][y.index(yr)]:.0f}%'      # noqa: E731
    row = lambda s, name: f'<tr><th scope="row">{name}</th><td>{fr(s, 2030)}</td><td>{fr(s, 2040)}</td><td>{fr(s, 2050)}</td></tr>'      # noqa: E731
    return f'''<section class="card at-f3" data-f3="model" aria-labelledby="f3h"><p class="kicker">F3 output · a conditional scenario, not a forecast</p>
<h2 id="f3h">What F3’s model shows</h2>
<p>F3’s AI-race sector is rebuilt from the GATE growth model of Epoch AI. One of its outputs is the fraction of all tasks in the economy that AI systems can perform:</p>
<div class="tblwrap"><table><thead><tr><th scope="col">Setting</th><th scope="col">2030</th><th scope="col">2040</th><th scope="col">2050</th></tr></thead>
<tbody>{row("low", "Slow race")}{row("central", "Central")}{row("race", "Fast race")}</tbody></table></div>
<p class="note"><strong>Notice (AI sector):</strong> {esc(d["meta"]["s3_status"])}</p>
<p class="note">These values come from the published site data, computed before decision D-065 changed the sector’s task composite. The site data has not been regenerated.</p>
<p><strong>Why the two halves of this page disagree.</strong> The reported figures count today’s jobs that current tools could affect. The F3 sector is a growth model in which investment in computing automates tasks without friction: no hiring rules, no retraining time, no limit on electricity. It gives near-complete automation within about fifteen years. The reported evidence shows most firms measuring no effect yet. F3 exists to test which limits lie between those two pictures. The sector’s economic output is not shown on this site.</p>
</section>'''


def f3_land(d: dict) -> str:
    w = d["world3"]
    run = w["runs"][w["standard"] + "|off"]
    nr = lambda yr: f'{100 * run["nrfr"][w["years"].index(yr)]:.0f}%'      # noqa: E731
    return f'''<section class="card at-f3" data-f3="model" aria-labelledby="f3h"><p class="kicker">F3 output · a conditional scenario, not a forecast</p>
<h2 id="f3h">What F3’s model shows</h2>
<p>F3 carries the World3 model of <em>The Limits to Growth</em>. World3 holds all non-renewable resources as one stock. In its standard run the share still in the ground is:</p>
<div class="at-tiles">{tile("2025", nr(2025), "of the 1900 stock remains")}{tile("2050", nr(2050), "of the 1900 stock remains")}{tile("2100", nr(2100), "of the 1900 stock remains")}</div>
<p class="note"><strong>Notice (World3 port):</strong> A3.2: {esc(w["status"]["A3.2"])}. A3.4b: {esc(w["status"]["A3.4b"])}.</p>
<p><strong>What this does and does not say.</strong> World3’s stock is one lump with no copper, no chips and no land. Nothing in F3 yet connects the reported demand from data centres to it. Land and water use by data centres are planned as reported outputs of the electricity module (decision D-066, step E4). They are not built.</p>
</section>'''


NONE_TEXT = {
    "water": "It has no water sector. Water use by data centres is planned as a reported output of the electricity module (decision D-066, step E4). It is not built.",
    "health": "The site’s <a href=\"ai.html\">AI Impact</a> page shows counts of AI publications, notable models and cleared medical devices. Those are data, not model output.",
    "mind": "A link from AI displacement and climate stress to mental health and productivity is on the list of proposed links (L_MH). It is not built.",
    "safety": "A link from AI capability and incident rates to catastrophic risk is on the list of proposed links (L_RISK). It is not built.",
    "military": "A link from resource and climate stress to armed conflict is on the list of proposed links (L_CONF). It is not built, and it would not represent military uses of AI.",
    "creative": "The AI sector treats all tasks in the economy as one continuum and has no separate creative sector, no prices for creative work and no law.",
    "robots": "The AI sector represents automation through computing alone. It holds no stock of robots and no metals, batteries or electricity for building and running them.",
    "surveillance": "Nothing in the model represents surveillance, privacy or civil liberties.",
    "nature": "World3 models food and farmland in aggregate, with no effect of AI on yields and no biodiversity. Land and water use by data centres are planned as reported outputs (decision D-066, step E4), not built.",
}


def f3_none(key: str) -> str:
    return (f'<section class="card at-f3" data-f3="none" aria-labelledby="f3h"><p class="kicker">F3 and this topic</p><h2 id="f3h">Not in the model</h2>'
            f'<p><strong>F3 does not model this.</strong> {NONE_TEXT[key]}</p><p>The figures on this page are context for readers. They do not enter any F3 run.</p></section>')


def f3_box(key: str, d: dict) -> str:
    return {"energy": f3_energy, "work": f3_work, "land": f3_land}[key](d) if key in F3_STATE else f3_none(key)


def cav(text: str) -> str:
    return f'<span class="at-caveat">{text}</span>'


def story_tiles(d: dict) -> str:
    """Four headline numbers for the story page, in the atlas tile style. All are series the story already draws; read from the data file."""
    import links
    w = d["world3"]
    run = w["runs"][w["standard"] + "|off"]
    pk = max(range(len(run["pop"])), key=lambda i: run["pop"][i])
    y, cl = d["years"], d["climate"]
    fa = d["runs"]["central|central|1"]["frac_automated"][y.index(2040)]
    built = sum(1 for x in links.LINKS if x["status"] == "built")
    return ('<section class="st-block" aria-labelledby="st_f3_h"><h2 id="st_f3_h">The story in four numbers</h2><div class="at-tiles" id="story_tiles">'
            + tile("Step 1 · World3 standard run", f'{run["pop"][pk] / 1e9:.2f} billion', f'people at the peak, in {w["years"][pk]}' + cav("Amber: the standard run matches its reference; test A3.4(b) failed; runs with changed settings are not compared."), "f3")
            + tile("Step 2 · warming in 2100", f'{cl["warming"][-1]:.1f} K', f'FaIR ensemble mean; 5 to 95% range {cl["warming_p05"][-1]:.1f} to {cl["warming_p95"][-1]:.1f} K' + cav("Amber: test A2.1 failed; the run starts about 0.04 to 0.07 K below observed; emissions are prescribed, not modelled."), "f3")
            + tile("Step 3 · tasks AI can perform, 2040", f"{100 * fa:.0f}%", "central setting" + cav("Red: the AI sector failed its test against GATE (A1.3), is unvalidated after about 2027 and does not reproduce GATE. Read the timing only."), "f3")
            + tile("Step 4 · links between the models", f"{built} of {len(links.LINKS)}", "are built; the rest are not" + cav("A record of what is connected, not a model result. Compute and electricity outputs of one built link are withheld."), "f3")
            + '</div><p class="small">F3 output: conditional scenarios, not forecasts. Each number carries its caveat; details are in its step below and on <a href="limitations.html">Limitations</a>.</p></section>')


# ------------------------------------------------------------------------------------------------------------ page shell


def subnav(cur: str) -> str:
    items = [("atlas.html", "Overview")] + [(f"atlas-{k}.html", t) for k, t in TOPICS]
    return ('<nav class="at-sub" aria-label="Atlas topics">' + "".join(f'<a href="{f}"' + (' aria-current="location"' if f == cur else "") + f">{esc(t)}</a>" for f, t in items) + "</nav>")


def shell(cur: str, inner: str) -> str:
    names = [("atlas.html", "Overview")] + [(f"atlas-{k}.html", t) for k, t in TOPICS]
    i = [f for f, _ in names].index(cur)
    prev = f'<a href="{names[i - 1][0]}">Previous: {esc(names[i - 1][1])}</a>' if i else "<span></span>"
    nxt = f'<a href="{names[i + 1][0]}">Next: {esc(names[i + 1][1])}</a>' if i < len(names) - 1 else "<span></span>"
    return (subnav(cur) + f'<div class="at"><p class="at-label">{LABEL} · read on {READ_ON}, mostly in secondary reports · <a href="atlas.html#method">method</a></p>'
            + inner + f'<div class="at-pager">{prev}{nxt}</div></div>')


def render(data: dict, stamp: dict, page) -> dict:
    """All atlas pages. ``page`` is pages.page (passed in to avoid a circular import)."""
    out: dict = {}

    def topic(key: str, title: str, body: str, keys: list) -> None:
        name = f"atlas-{key}.html"
        out[name] = page("F3 Explorer v0.2: Atlas, " + title, "atlas.html", shell(name, body + f3_box(key, data) + refs(keys)), "", stamp, "", kind="reading")

    # ---------------- energy
    K=['iea-weo','iea-70','iea-mix','iea-ai','iea-news','tr-93','erock']
    body=f'''
    <header class="at-stack"><h1>Power and climate</h1>
    <p class="lead">AI runs on electricity. Demand from data centres is on course to double within four years, and in the two largest markets most of the new supply comes from gas and coal.</p></header>
    <section class="at-tiles">
    {tile('Data-centre electricity','1,000 TWh','a year by 2030, up from about 500 today, then 1,500 by 2035'+c(K,'iea-weo'),'acc')}
    {tile('Growth in 2025','17%','against 3% for all electricity demand'+c(K,'iea-weo'),'acc')}
    {tile('Carbon emissions','+70%','from data centres by 2030'+c(K,'iea-70'),'stress')}
    {tile('Under construction','50 GW','across 93 large AI sites tracked by the IEA'+c(K,'tr-93'),'acc')}
    </section>
    <section class="card at-stack"><h2>Electricity used by data centres</h2>
    {bars([('Today',500,''),('2030',1000,''),('2035',1500,'')],'TWh','IEA World Energy Outlook 2026, Stated Policies Scenario, terawatt-hours a year')}
    </section>
    <section class="at-stack"><h2>What is happening</h2>
    <p>The International Energy Agency expects data centres to use twice as much electricity in 2030 as today, with AI responsible for about three-quarters of the increase.{c(K,'iea-70')} The capacity of the large AI sites it tracks rose from under 2 GW to about 17 GW in two years.{c(K,'tr-93')}</p>
    <p>The supply mix differs sharply by region. By 2030 gas is expected to provide about 60% of the power for data centres in the United States, coal about half in China, and renewables about 70% in the European Union.{c(K,'iea-mix')}</p>
    <p>Power, not chips, is now the constraint. A data centre can be built in two to three years, while grid connections and new generation take four to eight, so operators are installing their own gas plants.{c(K,'erock')} Five large technology companies spent more than $400 billion on capital projects in 2025.{c(K,'iea-news')}</p>
    <p>In absolute terms the sector is still small: about 180 million tonnes of CO₂ a year, or 0.5% of emissions from burning fuels. It is one of the few sectors whose emissions are still rising.{c(K,'iea-ai')}</p></section>
    <section class="at-stack"><h2>The ledger</h2>
    {ledger(['AI can cut emissions elsewhere: finding methane leaks from satellites sooner, and running power plants and grids more efficiently.'+c(K,'iea-ai')],
            ['Emissions from data centres up 70% by 2030.'+c(K,'iea-70'),'New gas plants built for data centres will run for decades.','Local grids are strained, and connection queues delay other users.'],
            ['Whether AI’s savings elsewhere will outweigh its own footprint. No study settles it.','How much efficiency gains in chips will offset growth in use.','Whether all the announced capacity gets built.'])}
    </section>
    '''
    topic('energy', 'Power and climate', body, K)

    # ---------------- water
    K=['nat-water','earth-water','sf-water','bb-water','ceres','dcmap','qro','chile','sfex']
    body=f'''
    <header class="at-stack"><h1>Water</h1>
    <p class="lead">Servers are cooled with water, and the electricity that feeds them needs water too. Consumption is set to double by 2030, often in places that are already short.</p></header>
    <section class="at-tiles">
    {tile('Consumed each year','560 bn litres','in 2023, rising to about 1,200 billion by 2030'+c(K,'nat-water'),'stress')}
    {tile('In water-short regions','1 in 4','data centres: 2,315 of 9,347 worldwide'+c(K,'sf-water'),'stress')}
    {tile('At 3 °C of warming','1 in 3','data centres would be in water-short regions'+c(K,'earth-water'),'stress')}
    {tile('One 100 MW site','2 m litres','a day, on average in the United States'+c(K,'bb-water'),'acc')}
    </section>
    <section class="card at-stack"><h2>Where the pressure falls</h2>{world_map()}</section>
    <section class="card at-stack"><h2>Water consumed by data centres</h2>
    {bars([('2023',560,'s'),('2030',1200,'s')],'bn litres','IEA estimate and projection, billion litres a year')}</section>
    <section class="at-stack"><h2>What is happening</h2>
    <p>Only about a quarter of the water is used directly for cooling.{c(K,'nat-water')} The rest is consumed making the electricity and the chips. In seven US states, data centres depend on an estimated 3.4 trillion gallons of freshwater a year through their power supply.{c(K,'ceres')}</p>
    <p>A 2026 study mapped all 9,347 operational data centres against local water balance. A quarter sit where demand outstrips supply for at least one month a year. The authors use water conditions of 2001 to 2010 and call their shortfall estimates an upper bound, since reservoirs, transfers and desalination are not counted. The hotspots are the western United States, Spain, Italy, India and the Gulf states, and in Spain 64% of sites are affected.{c(K,'earth-water')}{c(K,'sf-water')}</p>
    <p>In Arizona every one of 149 rated sites is in an area of extremely high water stress.{c(K,'dcmap')} In Querétaro, Mexico, a data-centre hub is growing in a state hit hard by drought.{c(K,'qro')} Near Santiago, Chile, a project was planned on the capital's strained aquifer.{c(K,'chile')}</p></section>
    {fig(propbar([(25, "a"), (75, "b")], "One bar split in two. About a quarter of the water data centres consume is used on site for cooling. About three quarters is consumed making their electricity and chips."), "About a quarter of the water is used on site for cooling; the rest is consumed making the electricity and the chips (IEA figures, read in a secondary report)." + c(K,'nat-water'))}
    {legend([("a", "Cooling on site, about 25%"), ("b", "Electricity and chips, about 75%")])}
    <section class="at-stack"><h2>The ledger</h2>
    {ledger(['Newer cooling designs use far less water, and some operators report recycling or replacing what they draw.','AI is also used to manage water networks and detect leaks.'],
            ['Consumption doubling by 2030.'+c(K,'nat-water'),'Competition with homes and farms in dry regions. Data centres can usually secure supply in a shortage, so neighbours carry the risk.'+c(K,'sf-water')],
            ['The true total. Some researchers argue the IEA figure understates it.'+c(K,'sfex'),'Site-level use: few operators publish it.','How fast dry cooling spreads, and what it costs in extra electricity.'])}
    </section>
    '''
    topic('water', 'Water', body, K)

    # ---------------- land
    K=['hyperion','ewaste','ewaste2','ewaste3','copper','chip-ti','chip-wef','chip-aj']
    body=f'''
    <header class="at-stack"><h1>Land, metals, chips and waste</h1>
    <p class="lead">The cloud is made of buildings, copper and chips that are replaced every few years. Each leaves a physical trace.</p></header>
    <section class="at-tiles">
    {tile('One campus','3,650 acres','about 15 km² of former farmland, Meta Hyperion in Louisiana'+c(K,'hyperion'),'acc')}
    {tile('Copper','1.1 m tonnes','a year for data centres by 2030, close to 3% of world demand'+c(K,'copper'),'stress')}
    {tile('E-waste from generative AI','1.2 to 5 m tonnes','in total over 2020 to 2030, by scenario'+c(K,'ewaste'),'stress')}
    {tile('All e-waste','62 → 82 m tonnes','a year, 2022 to 2030 on current trends'+c(K,'ewaste3'),'acc')}
    </section>
    <section class="card at-stack"><h2>Electronic waste in context</h2>
    {bars([('All e-waste, 2022',62,'m'),('All e-waste, 2030',82,'m'),('Generative AI, 2030 (high case)',2.5,'s')],'m tonnes a year','Global e-waste and the high scenario for generative AI, million tonnes a year')}</section>
    <section class="at-stack"><h2>What is happening</h2>
    <p><strong>Land.</strong> The largest campus under construction covers about 3,650 acres of former farmland after a 1,400-acre expansion in 2026.{c(K,'hyperion')} That is local land-use change on the scale of a small town.</p>
    <div class="at-flag">A claim to treat with care: no sourced figure for forest clearing by data centres was found for this atlas. The land figure above is for farmland.</div>
    <p><strong>Metals.</strong> Data centres could need about 1.1 million tonnes of copper a year by 2030. World demand for refined copper is about 28 million tonnes, and a shortfall is forecast for 2026.{c(K,'copper')}</p>
    <p><strong>Waste.</strong> Servers and accelerators are replaced quickly. A study in Nature Computational Science projects 1.2 to 5 million tonnes of e-waste from generative AI over 2020 to 2030, depending on the scenario, and up to 2.5 million tonnes a year by 2030 in its high scenario.{c(K,'ewaste')}{c(K,'ewaste2')} That is a small share of all e-waste, but it contains lead, mercury and chromium as well as recoverable gold and copper.{c(K,'ewaste3')}</p>
    <p><strong>Chips.</strong> Making the chips has its own footprint. One industry analyst puts emissions from chip fabrication at 178 million tonnes of CO₂-equivalent in 2026 and 197 million in 2027, with AI and memory demand growing faster than efficiency improves.{c(K,'chip-ti')} An average chip factory can use about 10 million US gallons of ultra-pure water a day.{c(K,'chip-wef')} In Taiwan one manufacturer alone used about 8% of the island’s electricity, according to a 2024 report.{c(K,'chip-aj')}</p></section>
    <section class="at-stack"><h2>The ledger</h2>
    {ledger(['Reuse and longer hardware lifetimes can cut the waste stream substantially; the study models such measures.'+c(K,'ewaste'),'Construction brings jobs and tax revenue to rural areas.'],
            ['Farmland and open land converted to industrial use.','Added pressure on copper supply already in deficit.'+c(K,'copper'),'Hazardous waste, much of it processed informally in poorer countries.'],
            ['Total land taken worldwide. No global figure was found.','Effects on forests and wildlife.','How much retired hardware is actually recycled.'])}
    </section>
    '''
    topic('land', 'Land, metals, chips and waste', body, K)

    # ---------------- work
    K=['ilo','ilo-caution','ilo-wb','imf-katz','etf','bofa','oecd-tfp','oecd-g7','hazan','imf-ar','cepr']
    body=f'''
    <header class="at-stack"><h1>Work and the economy</h1>
    <p class="lead">Many jobs will change, and few will disappear outright. The gains measured so far are real but modest, and they go mostly to rich countries and large firms.</p></header>
    <section class="at-tiles">
    {tile('Workers exposed','1 in 4','are in an occupation with some exposure to generative AI'+c(K,'ilo'),'acc')}
    {tile('Highest exposure','3.3%','of world employment: 4.7% of women’s jobs, 2.4% of men’s'+c(K,'ilo'),'stress')}
    {tile('Productivity','+0.25 to 0.6 pt','a year over ten years, OECD estimate of 2024'+c(K,'oecd-tfp'),'gain')}
    {tile('Firms using AI','20%','in OECD countries in 2025: 52% of large firms, 17% of small ones'+c(K,'hazan'),'acc')}
    </section>
    <section class="card at-stack"><h2>Share of jobs exposed to generative AI, by region</h2>
    {bars([('Europe and Central Asia',31.7,''),('Americas',28.8,''),('Arab States',24.9,''),('Asia-Pacific',22,'')],'%','ILO 2025 estimates as reported by the Bank of America Institute, percent of employment',vmax=40)}</section>
    <section class="at-stack"><h2>What is happening</h2>
    <p><strong>Jobs.</strong> The International Labour Organization finds that one worker in four is in an occupation with some exposure to generative AI, with clerical work the most exposed.{c(K,'ilo')} IMF staff put the share of jobs that could be affected in some way at about 40%, which means changed tasks and skills and not necessarily lost jobs.{c(K,'imf-katz')} Entry-level roles are more exposed than senior ones.{c(K,'etf')}</p>
    <p>The ILO itself cautions that exposure scores are not predictions of job losses.{c(K,'ilo-caution')}</p>
    <p><strong>Growth.</strong> The OECD's main estimate is 0.25 to 0.6 percentage points of extra productivity growth a year over a decade, and up to 1.3 points for labour productivity in the most exposed G7 economies.{c(K,'oecd-tfp')}{c(K,'oecd-g7')} AI investment added an estimated half a point to US growth in 2025.{c(K,'imf-ar')} Yet most firms in surveys report no measurable effect on employment or productivity so far.{c(K,'cepr')}</p>
    <p><strong>Who gains.</strong> One estimate puts AI's measured gains at about 4.2% of GDP in high-income countries, 0.6% in middle-income countries and 0.1% in low-income ones.{c(K,'cepr')} Many developing countries risk disruption before they see benefits.{c(K,'ilo-wb')}</p></section>
    {fig(waffle(100, [(3, "b"), (22, "a")], 20, "A grid of 100 squares, one per 1 percent of the world's workers. 25 are filled: workers in an occupation with some exposure to generative AI. Three of those are darker: the highest exposure category, 3.3 percent."), "Each square is 1% of the world’s workers. A quarter are in an occupation with some exposure to generative AI; 3.3% are in the highest category. Exposure is not a forecast of job loss." + c(K,'ilo'))}
    {legend([("b", "Highest exposure, 3.3%"), ("a", "Some exposure"), ("e", "Not exposed")])}
    <section class="at-stack"><h2>The ledger</h2>
    {ledger(['Higher productivity where AI is adopted, and higher pay for workers with AI skills.'+c(K,'imf-ar'),'Past general-purpose technologies raised incomes and employment in the long run.'+c(K,'imf-katz')],
            ['Women’s jobs and clerical jobs are more exposed.'+c(K,'ilo'),'Fewer entry-level openings for people starting careers.'+c(K,'etf'),'Gains concentrate in rich countries and large firms.'+c(K,'cepr')],
            ['How many exposed jobs are transformed and how many are lost.','When, or whether, firm-level gains show up in national statistics.','How fast economies can retrain and reallocate workers.'])}
    </section>
    '''
    topic('work', 'Work and the economy', body, K)

    # ---------------- robots
    K = ["rb-ifr", "rb-ifr2", "rb-sag", "rb-cp", "rb-idc", "rb-r247", "rb-anth", "rb-bis", "rb-ifrpos", "rb-berg"]
    body = f'''
<header class="at-stack"><h1>Robots</h1>
<p class="lead">AI is leaving the screen. Factory robots are at a record, and humanoid robots went from prototypes to tens of thousands shipped in a year. Most of those are not yet doing productive work.</p></header>
<section class="at-tiles">
{tile("Industrial robots at work", "5.08 million", "in factories worldwide in 2025, up 9%" + c(K, "rb-ifr2"), "acc")}
{tile("Installed in 2025", "603,000", "a record; 806,000 a year forecast for 2029" + c(K, "rb-ifr"), "acc")}
{tile("Humanoids shipped, first half of 2026", "19,100 to 25,000", "three analyst counts; about 95% made in China" + c(K, "rb-idc"), "stress")}
{tile("Tasks where robots beat labour on cost", "0.3%", "of job tasks today, in one US study" + c(K, "rb-anth"), "gain")}
</section>
{fig(bars([("Smart Analytics Global", 19100, "s"), ("Counterpoint Research", 22000, "s"), ("IDC", 25000, "s")], "units", "Humanoid robots shipped worldwide, January to June 2026, by analyst firm"),
     "Estimates differ by almost a third because there is no agreed definition or public register of shipments." + c(K, "rb-sag") + c(K, "rb-cp") + c(K, "rb-idc"))}
<section class="at-stack"><h2>What is happening</h2>
<p><strong>Factory robots.</strong> The stock of industrial robots passed five million in 2025, and factories installed more than 600,000 in a year for the first time.{c(K, "rb-ifr2")} The industry federation forecasts 655,000 installations in 2026 and 806,000 in 2029.{c(K, "rb-ifr")} These are fixed arms and similar machines doing set tasks.</p>
<p><strong>Humanoids.</strong> Shipments in the first half of 2026 were three to five times those of a year earlier, depending on who counts.{c(K, "rb-sag")}{c(K, "rb-idc")} Two Chinese makers supply about three in four.{c(K, "rb-r247")} More than 60% went to entertainment, performance, research and data collection, not production lines.{c(K, "rb-cp")} One analyst expects that through 2028 fewer than 100 companies will take humanoid trials past the experimental stage.{c(K, "rb-idc")}</p>
<p><strong>Forecasts span two orders of magnitude.</strong> One firm sees 500,000 humanoids a year by 2030; another sees 26 million a year by 2040.{c(K, "rb-sag")}{c(K, "rb-berg")} These are market forecasts by firms that sell research, and orders announced often differ from robots deployed.{c(K, "rb-r247")}</p>
<p><strong>Work.</strong> A 2026 study by Anthropic estimates that today’s robots could perform three-quarters of physical tasks in the United States, covering 34% of working hours, mostly in controlled settings, and that they are cheaper than people for only 0.3% of tasks.{c(K, "rb-anth")} It finds that jobs more exposed to robots saw larger falls in wages and employment over fifty years, and that exposed workers are more often male, less educated and lower paid.{c(K, "rb-anth")} A study of 20 EU countries finds the effect depends on the stage: early adoption tends to add jobs, and the relation changes in sectors already robotised.{c(K, "rb-bis")} The industry federation’s own review says robots replace tasks more than whole occupations.{c(K, "rb-ifrpos")}</p>
<p><strong>Safety.</strong> A fixed robot arm stops when power is cut. A humanoid balances actively and can fall. The first international safety standard for such robots is not finished.{c(K, "rb-idc")}</p></section>
{fig(waffle(100, [(34, "a")], 20, "A grid of 100 squares. 34 are filled: the share of US working hours spent on physical tasks that present-day robots could perform. Less than one square would be filled for tasks where robots are cheaper than people, 0.3 percent."),
     "Each square is 1% of US working hours. Filled: physical tasks present-day robots could perform (34%). Robots are cost-competitive for 0.3% of tasks, less than one square." + c(K, "rb-anth"))}
{legend([("a", "Could be done by present-day robots"), ("e", "Other working hours")])}
<section class="at-stack"><h2>The ledger</h2>
{ledger(["Dangerous, dirty and repetitive tasks taken over by machines." + c(K, "rb-ifrpos"), "Higher productivity where robots are adopted, and in early adoption more jobs." + c(K, "rb-bis"), "Help in sectors short of workers."],
        ["Lower wages and employment in the most exposed jobs, on past evidence." + c(K, "rb-anth"), "Exposure falls on lower-paid, less educated workers." + c(K, "rb-anth"), "Each robot needs metals, batteries, chips and electricity; no total was found for this atlas.", "New safety risks from machines that walk among people."],
        ["How fast humanoids become useful outside controlled settings.", "Real numbers: shipments, deployments and prices are estimates that disagree.", "Whether cost falls enough to matter for most physical work, and when.", "The material and energy footprint of millions of robots."])}
</section>
'''
    topic("robots", "Robots", body, K)

    # ---------------- health
    K=['aiindex','healio','epoc','stan-clin','single','f3data']
    body=f'''
    <header class="at-stack"><h1>Health and science</h1>
    <p class="lead">Medicine has adopted AI quickly, and in trials doctors decide better with it. Proof that patients end up healthier is still rare.</p></header>
    <section class="at-tiles">
    {tile('Cleared in one year','258','AI medical devices authorised by the US FDA in 2025'+c(K,'aiindex'),'gain')}
    {tile('Tested on patient outcomes','3 of 1,357','cleared devices had published outcome studies'+c(K,'healio'),'stress')}
    {tile('Doctors using AI','80%+','of US physicians, up from 38% in 2023'+c(K,'single'),'acc')}
    {tile('Research output','13.7 million','AI publications indexed by OpenAlex'+c(K,'f3data'),'acc')}
    </section>
    <section class="card at-stack"><h2>Evidence behind 1,357 cleared AI medical devices</h2>
    {bars([('All cleared devices',1357,'m'),('Linked to a prospective trial',34,''),('With patient-outcome studies',3,'s')],'devices','2026 census published in PLOS Digital Health, number of devices')}</section>
    <section class="at-stack"><h2>What is happening</h2>
    <p><strong>In the clinic.</strong> The tools gaining ground are those that fit existing work, such as AI scribes that write up consultations and systems that warn of sepsis.{c(K,'aiindex')} In one trial with 238 providers, scribes cut documentation time by nearly 10%.{c(K,'single')} A randomised trial found that physicians using AI alongside their usual resources made better treatment decisions.{c(K,'stan-clin')}</p>
    <p><strong>The evidence gap.</strong> Most devices reach the market through routes that need no new clinical trial.{c(K,'aiindex')} A 2026 census traced every cleared device: 34 of 1,357 were linked to a registered prospective trial, and three had published results on outcomes such as death or illness.{c(K,'epoc')}{c(K,'healio')}</p>
    <p><strong>In the lab.</strong> AI now designs proteins and models cells, and leading systems outscore most physicians on structured clinical tests. Nearly half of clinical AI studies still use simulated cases and not real patient data.{c(K,'aiindex')}</p></section>
    {fig(dots([(1357, "cleared devices", "e"), (34, "with a registered trial", "a"), (3, "tested on patient outcomes", "b")], "Three circles sized by area. 1,357 AI medical devices cleared by the US regulator. 34 linked to a registered prospective trial. 3 with studies of patient outcomes."), "Circle areas are proportional. Devices cleared in the United States through 5 December 2025." + c(K,'healio'))}
    <section class="at-stack"><h2>The ledger</h2>
    {ledger(['Less paperwork for clinicians.'+c(K,'single'),'Better decisions in trials when doctors work with AI.'+c(K,'stan-clin'),'Faster discovery in biology and drug design.'+c(K,'aiindex')],
            ['Tools in use whose effect on patients has not been measured.'+c(K,'healio'),'Trials that exist are often small and leave out vulnerable groups.'+c(K,'healio'),'Risk of bias when tools are trained on unrepresentative data.'],
            ['Whether accuracy on tests becomes better health in practice.','Who is accountable when an AI-supported decision is wrong.','How many AI-designed drugs will pass clinical trials.'])}
    </section>
    '''
    topic('health', 'Health and science', body, K)

    # ---------------- mind
    K=['iza-tutor','reyes','iza-africa','edweek','npr-teens','va','ottawa','stan-lonely','wef','fullfact','ofcom','digiday']
    body=f'''
    <header class="at-stack"><h1>Learning, minds and information</h1>
    <p class="lead">AI has entered classrooms, bedrooms and news feeds faster than research can follow. The early evidence points both ways.</p></header>
    <section class="at-tiles">
    {tile('Students using AI weekly','45.5%','of 15-year-olds in OECD countries, to help them learn'+c(K,'iza-tutor'),'acc')}
    {tile('Measured learning gain','+0.25 SD','on a test taken without AI, in one randomised trial'+c(K,'reyes'),'gain')}
    {tile('US teens using chatbots','64%','and nearly half of 9 to 12-year-olds have tried one'+c(K,'va'),'acc')}
    {tile('Rigorous studies','52 of 1,686','education papers tested a specific intervention'+c(K,'edweek'),'stress')}
    </section>
    <section class="at-stack"><h2>Learning</h2>
    <p>In a randomised experiment with 210 undergraduates, access to AI while learning a new topic raised scores on a later test taken without it.{c(K,'reyes')} Trials in Ghana, Nigeria and Sierra Leone found that AI-supported programmes can raise learning, while a large trial in rural China found no gain from AI personalisation over ordinary practice.{c(K,'iza-africa')}</p>
    <p>The research base is thin. Of 1,686 papers in one Stanford repository, 52 tested a specific intervention.{c(K,'edweek')} The open question is whether students learn more or only produce better-looking work.{c(K,'iza-africa')}</p></section>
    <section class="at-stack"><h2>Wellbeing</h2>
    <p>Chatbots are part of daily life for most American teenagers, and use starts years before the minimum age on most services.{c(K,'npr-teens')} A survey of 39,761 Ontario students found that 57.7% of those who turned to AI for emotional support met the criteria for serious emotional problems, against 29.2% of those who did not.{c(K,'ottawa')} That is an association: distressed young people may simply seek support more. A Stanford study suggests AI companions may worsen loneliness for vulnerable users.{c(K,'stan-lonely')}</p></section>
    <section class="at-stack"><h2>Information</h2>
    <p>The World Economic Forum ranks misinformation and disinformation among the top short-term global risks. The evidence is mixed on whether deepfakes persuade better than other content, but they make it harder to know what is real and give liars a way to dismiss what is true.{c(K,'wef')} UK fact-checkers documented 112 pieces of AI-made or AI-altered misinformation seen tens of millions of times in fifteen months.{c(K,'fullfact')} A regulator's review found emerging evidence that language models can be politically persuasive.{c(K,'ofcom')}</p></section>
    {fig(bars([("Used AI for emotional support", 57.7, "s"), ("Did not", 29.2, "m")], "%", "Share of Ontario students meeting criteria for serious emotional problems, by use of AI for emotional support", vmax=100), "An association in one survey of 39,761 students, not a cause: distressed students may seek support more." + c(K,'ottawa'))}
    <section class="at-stack"><h2>The ledger</h2>
    {ledger(['Tutoring at low cost, with measured gains in some trials.'+c(K,'reyes'),'Support that is available at any hour, which some adults report eases loneliness.'],
            ['Emotional reliance among young and vulnerable users.'+c(K,'stan-lonely'),'A flood of convincing fakes and falling trust in genuine material.'+c(K,'wef'),'Schoolwork that looks better without learning behind it.'+c(K,'iza-africa')],
            ['Long-term effects on how children learn and relate to others. No long studies exist yet.','Whether heavy AI use weakens skills over years.','How much AI-made misinformation changes what people believe or how they vote.'])}
    </section>
    '''
    topic('mind', 'Learning, minds and information', body, K)

    # ---------------- safety
    K=['iasr','iasr-heise','iasr-soc','iasr-asis','iasr-au','fpf','aj-act','brookings','aj-divide','undp']
    body=f'''
    <header class="at-stack"><h1>Safety, access and rules</h1>
    <p class="lead">Capabilities are advancing faster than the means to control them, access to the technology is very uneven, and the first binding rules are arriving in stages.</p></header>
    <section class="at-tiles">
    {tile('Scientific assessment','100+ experts','from over 30 countries wrote the International AI Safety Report 2026'+c(K,'iasr'),'acc')}
    {tile('Company safety frameworks','12','published or updated by AI developers in 2025'+c(K,'iasr-soc'),'gain')}
    {tile('AI computing capacity','3%','is in Africa and Latin America combined; the article cites no source'+c(K,'brookings'),'stress')}
    {tile('People offline','2.2 billion','have no internet access at all'+c(K,'aj-divide'),'stress')}
    </section>
    <section class="at-stack"><h2>What the scientific assessment says</h2>
    <p>The International AI Safety Report 2026, chaired by Yoshua Bengio, sorts the risks of general-purpose AI into three groups: malicious use, malfunctions, and systemic risks.{c(K,'iasr-heise')} It reports growing real-world evidence for several of them, including deepfakes, help with cyberattacks and concerns about biological misuse.{c(K,'iasr-asis')}</p>
    <p>It finds that capabilities advanced quickly over the past year, with leading systems reaching gold-medal level on International Mathematical Olympiad questions, and that existing safety practices are not keeping pace.{c(K,'iasr-heise')} It also warns that strong results in controlled tests do not always carry over to the real world.{c(K,'iasr-soc')} The report makes no policy recommendations.{c(K,'iasr-au')}</p></section>
    <section class="at-stack"><h2>Who has access</h2>
    <p>Only 32 countries host data centres specialised for AI.{c(K,'brookings')} Just 7% of African languages are represented in AI translation tools.{c(K,'aj-divide')} At the same time AI reached 1.2 billion users in three years, nearly 70% of them in developing countries.{c(K,'undp')} The UN Development Programme warns of a possible widening gap between countries, and says it is not inevitable.{c(K,'undp')}</p></section>
    <section class="card at-stack"><h2>How the first major law is arriving: the EU AI Act</h2>
    {fig(timeline([("February 2025", "Bans on prohibited practices; duty to promote AI literacy"), ("August 2025", "Obligations for providers of general-purpose AI models"), ("August 2026", "Transparency rules, including labelling of AI-generated content"), ("December 2027 and August 2028", "Rules for high-risk systems, postponed by an amending law published in July 2026")]), "Dates on which parts of the EU AI Act apply." + c(K,'fpf'))}
    <p class="small">Timeline from the Future of Privacy Forum and Al Jazeera.{c(K,'fpf')}{c(K,'aj-act')} Other countries are taking different approaches; this table shows one law, not a judgement on which approach is right.</p></section>
    <section class="at-stack"><h2>The ledger</h2>
    {ledger(['A shared scientific picture of the risks, backed by more than 30 countries.'+c(K,'iasr'),'More developers publishing how they intend to manage risk.'+c(K,'iasr-soc'),'Rapid uptake in developing countries.'+c(K,'undp')],
            ['Misuse for fraud, deepfakes and cyberattacks is already documented.'+c(K,'iasr-asis'),'Computing power concentrated in a few countries and firms.'+c(K,'brookings'),'Countries that rely on foreign systems gain access but little control.'],
            ['How capable systems will be in a few years. Experts disagree widely.','Whether voluntary safety frameworks hold under commercial pressure.','Which rules will prove effective. Evidence is only starting to come in.'])}
    </section>
    '''
    topic('safety', 'Safety, access and rules', body, K)


    # ---------------- military
    K = ["mil-ac1", "mil-oj", "mil-ac2", "mil-fortune", "mil-hurriyet", "mil-reuters", "mil-ars", "mil-bbg", "mil-dscoop", "mil-carnegie", "mil-hrw", "mil-perry", "mil-sipri1", "mil-sipri2", "mil-unric"]
    body = f'''
<header class="at-stack"><h1>Military use</h1>
<p class="lead">AI already helps armies find targets and steer drones. Spending is rising fast, and talks on binding rules have not produced a treaty.</p></header>
<section class="at-tiles">
{tile("UN vote, December 2025", "164 to 6", "for a resolution on lethal autonomous weapons; 7 abstentions" + c(K, "mil-oj"), "acc")}
{tile("Systems in the field", "about 200", "autonomous weapon systems tracked in Ukraine, the Middle East and Africa" + c(K, "mil-reuters"), "stress")}
{tile("US request for 2027", "$54 bn", "for its autonomous warfare group, up from about $226 million" + c(K, "mil-ars"), "stress")}
{tile("High-end targeting AI", "8 countries", "are said to have such systems today" + c(K, "mil-carnegie"), "acc")}
</section>
<section class="card at-stack"><h2>US budget lines for AI, autonomy and drones</h2>
{bars([("AI and autonomy, 2026 request", 13.4, "m"), ("Autonomous warfare group, 2027 request", 54, "s"), ("Drones and counter-drone, 2027 request", 75, "s")], "bn USD", "Requests to Congress, billion US dollars; the lines overlap and are not additive")}
<p class="small">Requests, not enacted budgets. Most of the 2027 money would need a separate budget bill, and approval is uncertain.{c(K, "mil-bbg")} The 2026 figure is the first dedicated line for AI and autonomy.{c(K, "mil-dscoop")}</p></section>
<section class="at-stack"><h2>What is happening</h2>
<p><strong>On the battlefield.</strong> Testimony to the US Congress in September 2026 describes AI targeting systems in use in Ukraine, Gaza and Iran, and names eight countries with high-end systems: China, Israel, North Korea, Russia, South Korea, Ukraine, the United Kingdom and the United States.{c(K, "mil-carnegie")} The UN Secretary-General’s 2025 report lists uses that already exist, including drones that keep steering to a target under electronic jamming.{c(K, "mil-unric")}</p>
<p><strong>Does it protect civilians or endanger them?</strong> The evidence is disputed. Supporters argue that faster data processing can make targeting more precise and reduce human error, and a Pentagon spokesperson has said autonomous weapons might pose less risk to civilians than conventional ones.{c(K, "mil-perry")}{c(K, "mil-reuters")} Researchers who studied reporting from Gaza conclude that systems built to produce many targets quickly contributed to strikes that increased civilian harm, partly because of accuracy limits.{c(K, "mil-perry")} Human Rights Watch says adoption is outpacing the testing that lawful use depends on.{c(K, "mil-hrw")}</p>
<p><strong>Rules.</strong> The UN General Assembly adopted a resolution on lethal autonomous weapons in December 2025 by 164 votes to 6. The United States, which had supported the 2023 and 2024 texts, voted against, with Russia, Israel, Belarus, Burundi and North Korea.{c(K, "mil-oj")} A second resolution on AI in the military domain passed its committee 166 to 5.{c(K, "mil-ac1")} States held their first UN exchange on military AI in Geneva in June 2026.{c(K, "mil-ac2")} In August 2026 the UN Secretary-General and the president of the Red Cross renewed their call for binding rules, and a review conference opened in Geneva on 16 November.{c(K, "mil-fortune")}{c(K, "mil-hurriyet")} The United States has said it is not convinced existing law is insufficient.{c(K, "mil-reuters")}</p>
<p><strong>Nuclear weapons.</strong> Just over half of the nuclear-armed states have said explicitly that they will keep humans in control of decisions to use nuclear weapons.{c(K, "mil-sipri1")} SIPRI warns that military AI can raise the risk of escalation even when it is not built into nuclear systems.{c(K, "mil-sipri1")} A UN resolution on AI in nuclear command and control also passed in 2025, with the United States voting no.{c(K, "mil-ac1")}</p></section>
{fig(propbar([(164, "a"), (7, "e"), (6, "b")], "One bar split in three. 164 states voted for the 2025 United Nations resolution on lethal autonomous weapons, 7 abstained and 6 voted against."), "UN General Assembly resolution 80/57, 1 December 2025." + c(K, "mil-oj"))}
{legend([("a", "For: 164"), ("e", "Abstained: 7"), ("b", "Against: 6")])}
<section class="at-stack"><h2>The ledger</h2>
{ledger(["Faster processing of intelligence, and claims of greater precision." + c(K, "mil-perry"), "Cheap autonomous systems can defend against larger forces, as Ukraine’s use of drones shows.", "SIPRI also studies ways AI could reduce nuclear risk, for example in verification." + c(K, "mil-sipri2")],
        ["Reported civilian harm where systems generate targets faster than people can check them." + c(K, "mil-perry"), "An arms race: one request rising from millions to tens of billions in a year." + c(K, "mil-ars"), "Spread to more states and to armed groups." + c(K, "mil-carnegie")],
        ["How accurate deployed systems are. Their testing is not public." + c(K, "mil-hrw"), "Whether autonomy lowers or raises civilian deaths overall. Both are claimed; neither is measured.", "Whether any binding rule will be agreed, and whether the largest military powers would join it."])}
</section>
'''
    topic("military", "Military use", body, K)

    # ---------------- creative
    K = ["cr-pymnts", "cr-cleary", "cr-dj", "cr-pg", "cr-nrf", "cr-week"]
    body = f'''
<header class="at-stack"><h1>Creative work and copyright</h1>
<p class="lead">AI models were trained on books, images and music made by people. Courts are now deciding whether that was lawful, and who gets paid.</p></header>
<section class="at-tiles">
{tile("Largest settlement", "$1.5 bn", "between authors and one AI developer, the largest known US copyright payout" + c(K, "cr-pymnts"), "acc")}
{tile("First rulings on training", "2", "US federal judges ruled in 2025, both largely for the AI developers" + c(K, "cr-dj"), "acc")}
{tile("Lawsuits pending", "Dozens", "over text, images, music, code and news" + c(K, "cr-cleary"), "stress")}
</section>
<section class="at-stack"><h2>What is happening</h2>
<p><strong>In the United States.</strong> Two federal judges issued the first substantive rulings in 2025, in cases brought by authors against Anthropic and Meta. Both treated training on books as fair use in the cases before them, and one judge called the use “quintessentially transformative”.{c(K, "cr-pymnts")} The rulings concerned training only and left open what happens when outputs resemble or compete with the originals.{c(K, "cr-week")} One of those cases still ended in a $1.5 billion settlement over how the books were obtained.{c(K, "cr-pymnts")} Decisions in further cases are expected, and the central question is not settled.{c(K, "cr-cleary")}</p>
<p><strong>In the United Kingdom.</strong> Getty Images largely failed in November 2025 to obtain a ruling against Stability AI over training on its photographs.{c(K, "cr-pg")}</p>
<p><strong>Licensing.</strong> Some disputes are turning into deals. Warner Music settled with two AI music companies and plans joint products with them.{c(K, "cr-pymnts")} Lawyers expect more licensing agreements between rights holders and developers.{c(K, "cr-nrf")}</p>
<p><strong>Who owns the output.</strong> US law still requires a human author. Work produced entirely by AI is generally not protected, while work made with AI assistance may be.{c(K, "cr-nrf")}</p></section>
<section class="at-stack"><h2>The ledger</h2>
{ledger(["New tools for writing, images, music and video, at low cost.", "A licensing market that pays some rights holders." + c(K, "cr-pymnts")],
        ["Works used for training without consent or payment, which the first rulings mostly allowed." + c(K, "cr-dj"), "Competition from machine-made content in markets where creators sell." + c(K, "cr-week")],
        ["The effect on creators’ incomes. No measured figure was found for this atlas.", "How appeal courts will rule. None has decided the core question yet.", "Whether licensing will reach individual creators or mainly large catalogues."])}
</section>
'''
    topic("creative", "Creative work and copyright", body, K)

    # ---------------- surveillance
    K = ["sv-carnegie", "sv-bio", "sv-aj", "sv-cms", "sv-allafrica", "sv-bis"]
    body = f'''
<header class="at-stack"><h1>Surveillance</h1>
<p class="lead">Cameras that recognise faces and software that predicts crime have spread to most regions. The same tools serve policing and repression.</p></header>
<section class="at-tiles">
{tile("Countries using AI surveillance", "75 of 176", "in the Carnegie index of 2019, the last global count found" + c(K, "sv-carnegie"), "stress")}
{tile("Facial recognition", "64 countries", "in the same index; 56 with safe-city platforms, 52 with smart policing" + c(K, "sv-bio"), "acc")}
{tile("Spent in 11 African countries", "$2 bn", "at least, on facial recognition and vehicle tracking" + c(K, "sv-allafrica"), "stress")}
</section>
<section class="card at-stack"><h2>Spending on AI surveillance in three African countries</h2>
{bars([("Nigeria", 470, "s"), ("Mauritius", 456, "s"), ("Kenya", 219, "s")], "m USD", "2026 study of 11 countries, million US dollars to date")}</section>
<section class="at-stack"><h2>What is happening</h2>
<p><strong>The global picture is dated.</strong> The most cited count is from 2019: at least 75 of 176 countries used AI for surveillance, and 51% of advanced democracies did so.{c(K, "sv-carnegie")}{c(K, "sv-aj")} One Chinese company supplied at least fifty countries, and US firms thirty-two.{c(K, "sv-bio")} The index records where the technology is present. It does not separate lawful from unlawful use.{c(K, "sv-carnegie")} No newer global count was found.</p>
<p><strong>A 2026 study of Africa.</strong> Eleven countries have spent at least $2 billion on facial recognition and number-plate systems, with Nigeria, Mauritius and Kenya the largest buyers.{c(K, "sv-cms")}{c(K, "sv-allafrica")} The researchers say the systems are being installed without legal frameworks strong enough to protect rights, and in some countries with little terrorism or serious crime.{c(K, "sv-cms")}</p>
<p><strong>Why governments buy it.</strong> Police see clear uses in finding suspects and analysing large volumes of data, and adoption by governments was expected.{c(K, "sv-bis")}</p></section>
{fig(waffle(176, [(75, "b")], 22, "A grid of 176 squares, one per country studied. 75 are filled: countries using AI surveillance technology in the 2019 index."), "Each square is one of the 176 countries in the 2019 index. Filled: at least 75 using AI surveillance. The index does not separate lawful from unlawful use." + c(K, "sv-carnegie"))}
{legend([("b", "Using AI surveillance (2019)"), ("e", "No use recorded")])}
<section class="at-stack"><h2>The ledger</h2>
{ledger(["Tools for finding suspects and missing people and for managing traffic and crowds." + c(K, "sv-bis")],
        ["Mass monitoring of public space, often without legal safeguards." + c(K, "sv-cms"), "Misidentification and bias in facial recognition.", "Use against critics and minorities; the 2019 index notes that authoritarian states are more prone to abuse." + c(K, "sv-aj")],
        ["How far the technology has spread since 2019.", "How often it prevents or solves crime. Independent evaluations are rare.", "How newer AI models change what can be done with the footage."])}
</section>
'''
    topic("surveillance", "Surveillance", body, K)

    # ---------------- nature and food
    K = ["nf-scan", "nf-jae", "nf-conv", "nf-wb", "nf-wbblog", "nf-rct", "nf-3ie", "nf-dte"]
    body = f'''
<header class="at-stack"><h1>Nature and food</h1>
<p class="lead">AI can listen to forests, count animals and advise farmers by phone. The promise is large. Field evidence that it works is thin.</p></header>
<section class="at-tiles">
{tile("Conservation uses", "21", "priority ideas chosen by 27 experts from a list of 104" + c(K, "nf-scan"), "gain")}
{tile("Early farm result", "up to +38%", "yield for smallholders using tailored AI advice in Ethiopia" + c(K, "nf-wb"), "gain")}
{tile("First randomised trial", "no change", "in yields or costs in the short run, in the Philippines and India" + c(K, "nf-rct"), "stress")}
{tile("Evidence base", "51 studies", "reviewed; most rely on simulation, not field results" + c(K, "nf-3ie"), "acc")}
</section>
<section class="at-stack"><h2>Nature</h2>
<p>A panel of conservation scientists and AI specialists picked 21 uses most likely to help: recognising species from images and sound, tracking the illegal wildlife trade, and easing conflict between people and wildlife.{c(K, "nf-scan")} The same panel names risks, among them tools designed far from the places they are used and the loss of field skills.{c(K, "nf-scan")}</p>
<p>A 2026 paper in the Journal of Applied Ecology warns that uptake is outpacing oversight, and lists validation, data sovereignty and the environmental cost of the computing itself among the gaps.{c(K, "nf-jae")} South African scientists ranked AI among their top ten emerging issues, as both an opportunity and a risk.{c(K, "nf-conv")}</p></section>
<section class="at-stack"><h2>Food</h2>
<p>The World Bank reports early results of up to 38% higher yields and $580 more profit per hectare for Ethiopian smallholders using tailored AI advice. The figures come from a 2023 study, before today’s chat-based tools.{c(K, "nf-wb")} One advisory tool serves more than 350,000 plots in seven African countries through a messaging app.{c(K, "nf-wbblog")}</p>
<p>The first randomised trial of AI advice for smallholders found that farmers valued the service but saw no short-run change in yields or costs.{c(K, "nf-rct")} A review of 51 studies found most evidence came from simulations and models, with low-income countries under-represented.{c(K, "nf-3ie")} Poor connectivity, cost and low digital literacy may leave smallholders behind while large farms gain.{c(K, "nf-dte")}</p></section>
<section class="at-stack"><h2>The ledger</h2>
{ledger(["Monitoring of species and habitats at a scale people cannot manage by hand." + c(K, "nf-scan"), "Farm advice that reaches smallholders by phone." + c(K, "nf-wbblog")],
        ["Data centres’ own demand for power, water and land, covered on other pages.", "Tools and data controlled far from the communities concerned." + c(K, "nf-scan"), "A widening gap between large and small farms." + c(K, "nf-dte")],
        ["Whether early yield gains hold up in rigorous trials." + c(K, "nf-rct"), "The net effect on biodiversity once AI’s own footprint is counted.", "Effects of data-centre construction on wildlife. No study was found."])}
</section>
'''
    topic("nature", "Nature and food", body, K)

    # ---------------- hub
    def state(k: str) -> str:
        s = F3_STATE.get(k, "none")
        return f'<span class="at-state {s}">{STATE_TEXT[s]}</span>'
    blurbs = {
        "energy": "Electricity demand is doubling and most new supply in the two largest markets is fossil. F3’s warming scenario is shown beside it.",
        "water": "Water use is set to double. A quarter of data centres sit where water runs short part of the year.",
        "land": "Campuses the size of small towns, copper by the million tonnes, chip factories and electronic waste.",
        "work": "Many jobs will change and few vanish outright. F3’s automation scenario is shown beside the reported evidence.",
        "health": "Adoption in medicine is fast. Evidence that patients do better is still thin.",
        "mind": "Promising classroom trials, worrying signals on young people’s wellbeing, and a harder time telling true from false.",
        "safety": "What the international scientific assessment says, who has access, and how the rules are arriving.",
        "military": "Targeting systems and autonomous drones are in use, budgets are rising, and treaty talks are stalled.",
        "creative": "Courts are deciding whether training on creative work was lawful, and who gets paid.",
        "surveillance": "Facial recognition and predictive policing have spread widely, often ahead of legal safeguards.",
        "nature": "AI can monitor wildlife and advise farmers. Field evidence that it works is thin.",
        "robots": "Factory robots are at a record and humanoids are shipping in the tens of thousands, mostly not yet to productive work.",
    }
    cards = "".join(f'<a class="at-card" href="atlas-{k}.html"><h3>{esc(t)}</h3><p>{blurbs[k]}</p>{state(k)}<span class="at-go">Read the page</span></a>' for k, t in TOPICS)
    y, cl = data["years"], data["climate"]
    fa = data["runs"]["central|central|1"]["frac_automated"][y.index(2040)]
    hub = f'''
<header class="at-stack"><h1>What is AI doing to people and to the planet?</h1>
<p class="lead">Twelve areas where the effects of artificial intelligence are being measured, each with what is gained, what it costs and what nobody knows yet. Where F3 models the topic, its output is shown beside the reported figures and kept apart from them.</p></header>
<section class="at-stack"><h2>Reported</h2>
<div class="at-tiles" aria-label="Reported headline figures">
{tile("Electricity", "×2 by 2030", "data-centre power use, about 500 to 1,000 TWh a year", "acc")}
{tile("Water", "560 → 1,200", "billion litres consumed a year, 2023 to 2030", "stress")}
{tile("Jobs", "1 in 4", "workers in an occupation with some exposure to generative AI", "acc")}
{tile("Medicine", "3 of 1,357", "cleared AI medical devices with published patient-outcome studies", "stress")}
</div>
{fig(chain([("Chips", "178 Mt CO₂e", "from chip fabrication in 2026"), ("Data centres", "93 sites, 50 GW", "large AI campuses tracked"), ("Electricity", "1,000 TWh", "a year by 2030, twice today"), ("Water", "1,200 bn litres", "a year by 2030"), ("Emissions", "+70%", "from data centres by 2030")]), "The physical chain behind AI, one reported figure per step. Sources are on the Power, Water and Land pages.")}
</section>
<section class="at-stack"><h2>From F3’s model</h2>
<div class="at-tiles" aria-label="F3 output, conditional scenarios">
{tile("Warming in 2050", f'{cl["warming"][y.index(2050)]:.1f} K', f'above 1850 to 1900; 5 to 95% range {cl["warming_p05"][y.index(2050)]:.1f} to {cl["warming_p95"][y.index(2050)]:.1f} K' + cav("Amber: test A2.1 failed; the run starts about 0.04 to 0.07 K below observed."), "f3")}
{tile("Tasks AI can perform, 2040", f"{100 * fa:.0f}%", "central setting of the AI-race sector" + cav("Red: unvalidated after about 2027; does not reproduce GATE."), "f3")}
{tile("Data-centre electricity", "Withheld", "the output leaves any plausible range", "f3")}
</div><p class="small">Conditional scenarios, not forecasts. Notices and limits are on the <a href="atlas-energy.html">Power and climate</a> and <a href="atlas-work.html">Work and the economy</a> pages and on <a href="limitations.html">Limitations</a>.</p></section>
<section class="at-stack"><h2>The twelve areas</h2><div class="at-cards">{cards}</div></section>
<section class="at-stack" id="method"><h2>How to read the atlas</h2>
<p><strong>Two kinds of numbers.</strong> Reported figures come from agencies, studies and news reports, each linked. F3 output comes from the model runs behind the <a href="explorer.html">Explorer</a>. They are never placed in the same chart or table.</p>
<p><strong>Reported figures were read on {READ_ON}.</strong> Most were read in news reports or summaries, and the original study was not always opened. Projections get revised: the IEA’s 2030 figure for data-centre electricity moved from 945 TWh in April 2025 to about 1,000 TWh in November 2026.</p>
<p><strong>Associations are not causes.</strong> Where a study shows only that two things occur together, the page says so. Where a common claim could not be supported, the page says that too.</p>
<p><strong>Most topics are not in the model.</strong> F3 output appears on three of the twelve pages. On the other nine the page says plainly that F3 does not model the topic.</p>
<p><strong>Not covered yet:</strong> privacy law, effects on children’s development beyond the studies cited, energy and water used in training single models, and regional detail for most topics.</p>
<p>The site’s <a href="ai.html">AI Impact</a> page shows the data F3 holds on AI research output and medical devices.</p></section>
'''
    out["atlas.html"] = page("F3 Explorer v0.2: Atlas", "atlas.html", shell("atlas.html", hub), "", stamp, "", kind="reading")
    return {n: out[n] for n in PAGE_NAMES}
