"""Markup of the "Average or spread?" page (spread.html, D-062, Proposed). Three inline SVG infographics and their text.

Honesty rule for this page: NOTHING here is an output of the F3 model. It states a hypothesis (AI narrows gaps between strong and weak performers on short,
supervised tasks and widens them on long, delegated ones) and labels it untested. Solid = measured in published field studies; dashed = predicted, not tested.
The figures about other systems come from published studies listed in SOURCES below; they were read from search extracts on 2026-11-12 and the primary
pages were not opened (research/SOURCES.md says the same). Same drawing rules as ig.py: viewBox 310 wide, text set at 13, colours from the stylesheet tokens.
"""
from ig import box

HYPOTHESIS = (
    '<svg id="ig_spread_h" viewBox="0 0 310 258" role="img" aria-labelledby="ig_spread_h_t ig_spread_h_d" class="ig">'
    '<title id="ig_spread_h_t">The hypothesis: AI narrows gaps on short tasks and may widen them on long ones</title>'
    '<desc id="ig_spread_h_d">A schematic curve, not drawn from data. Horizontal: from short tasks with a person in every step to long tasks delegated to agents. '
    'Vertical: the effect of AI on the gap between strong and weak performers, from narrower at the bottom to wider at the top. '
    'On the left, a solid line below the no-change line: published field studies of AI assistants found the gap narrowing. '
    'On the right, a dashed line above it: the prediction that the gap widens on long delegated tasks, which has not been tested.</desc>'
    '<rect x="12" y="32" width="138" height="178" class="zone"/>'
    '<text x="12" y="24" font-size="13" class="svgt b">Evidence so far</text>'
    '<text x="300" y="24" font-size="13" text-anchor="end" class="svgt b">Predicted, untested</text>'
    '<path d="M 12 32 L 12 210" class="axis"/>'
    '<path d="M 12 120 L 300 120" class="axis zero"/>'
    '<text x="18" y="48" font-size="13" class="svgm">gap widens</text>'
    '<text x="90" y="204" font-size="13" class="svgm">gap narrows</text>'
    '<text x="300" y="114" font-size="13" text-anchor="end" class="svgm">no change</text>'
    '<path d="M 22 190 C 70 186, 115 165, 160 120" class="cv measured" data-status="measured"/>'
    '<path d="M 160 120 C 205 78, 250 56, 296 50" class="cv untested" data-status="untested"/>'
    '<circle cx="160" cy="120" r="5" class="dot"/>'
    '<text x="168" y="140" font-size="13" class="svgt">tipping point</text>'
    '<text x="12" y="230" font-size="13" class="svgt b">short tasks,</text>'
    '<text x="12" y="246" font-size="13" class="svgt">person in every step</text>'
    '<text x="300" y="230" font-size="13" text-anchor="end" class="svgt b">long tasks,</text>'
    '<text x="300" y="246" font-size="13" text-anchor="end" class="svgt">delegated to agents</text>'
    '</svg>'
)

KINDS = (
    '<svg id="ig_spread_k" viewBox="0 0 310 162" role="img" aria-labelledby="ig_spread_k_t ig_spread_k_d" class="ig">'
    '<title id="ig_spread_k_t">Four kinds of spread that should not be confused</title>'
    '<desc id="ig_spread_k_d">Four boxes. Output spread: one model, many runs. Capability spread: one model, many tasks. Outcome spread: many people or firms; '
    'this is the one the hypothesis is about and its box is drawn with a heavier outline. Systemic spread: everyone at once.</desc>'
    + box(0, 4, 150, 72, ["Output spread", "one model, many runs"])
    + box(160, 4, 150, 72, ["Capability spread", "many kinds of task"])
    + box(0, 86, 150, 72, ["Outcome spread", "many people or firms", "the hypothesis"], "nodebox hl")
    + box(160, 86, 150, 72, ["Systemic spread", "everyone at once"])
    + '</svg>'
)

SYSTEMS = (
    '<svg id="ig_spread_s" viewBox="0 0 310 276" role="img" aria-labelledby="ig_spread_s_t ig_spread_s_d" class="ig">'
    '<title id="ig_spread_s_t">The pattern holds in some systems, not all</title>'
    '<desc id="ig_spread_s_d">Six systems in three groups. Fits, spread has widened: rainfall, more variable on about 75 percent of land; firm productivity, leaders pull away from the rest. '
    'Mixed, varies by place: incomes, gaps across countries down and within countries mixed; political polarization, up in 6 of 12 OECD countries and down in 6. '
    'Different, a shift or a rise and drawn with dashed outlines: heat extremes, a shifted average and not a wider spread; armed conflict, a rising count, 65 state-based conflicts in 2025.</desc>'
    '<text x="0" y="16" font-size="13" class="svgt b">Fits: spread has widened</text>'
    + box(0, 24, 150, 60, ["Rainfall", "more variable on", "75% of land"])
    + box(160, 24, 150, 60, ["Firm productivity", "leaders pull away", "from the rest"])
    + '<text x="0" y="108" font-size="13" class="svgt b">Mixed: varies by place</text>'
    + box(0, 116, 150, 60, ["Incomes", "gaps between nations", "down; within, mixed"])
    + box(160, 116, 150, 60, ["Polarization", "up in 6 of 12 OECD", "countries, down in 6"])
    + '<text x="0" y="200" font-size="13" class="svgt b">Different: a shift or a rise</text>'
    + box(0, 208, 150, 60, ["Heat extremes", "a shifted average,", "not a wider spread"], "nodebox notbuilt")
    + box(160, 208, 150, 60, ["Armed conflict", "a rising count:", "65 in 2025"], "nodebox notbuilt")
    + '</svg>'
)

# (label, what the source reports, fit, link text, url). Read from search extracts on 2026-11-12; primary pages not opened.
SOURCES = [
    ("Rainfall", "Variability has grown over about 75% of land since 1900; daily variability up 1.2% per decade.", "fits",
     "Zhang, Zhou and Wu, Science, 2024 (AAAS summary)", "https://www.eurekalert.org/news-releases/1052174"),
    ("Firm productivity", "In manufacturing, frontier firms gained 2.8% a year from 2001 to 2013; all other firms gained 0.6%.", "fits",
     "Andrews, Criscuolo and Gal, OECD (authors' summary)", "https://voxeu.org/article/productivity-slowdown-s-dirty-secret-growing-performance-gap"),
    ("Incomes", "Gaps between countries have narrowed; gaps within countries have stayed roughly constant on average since 2000.", "mixed",
     "Brookings, The present and future of global inequality", "https://www.brookings.edu/articles/the-present-and-future-of-global-inequality"),
    ("Political polarization", "Among twelve OECD countries since the 1980s, hostility between party supporters rose most in the United States, rose less in five others and fell in six.", "mixed",
     "Boxell, Gentzkow and Shapiro, NBER working paper 26669", "https://www.nber.org/papers/w26669"),
    ("Heat extremes", "Hot extremes have become more frequent and more intense since the 1950s; cold extremes less frequent and less severe.", "different",
     "IPCC AR6 findings, as summarised by the Hong Kong Observatory", "https://www.hko.gov.hk/en/climate_change/obs_global_extreme_weather.htm"),
    ("Armed conflict", "65 conflicts involving a state in 2025, the most since records began in 1946; 31 in 2010.", "different",
     "UCDP, Journal of Peace Research", "https://academic.oup.com/jpr/advance-article/doi/10.1093/jopres/xjag046/8703754"),
]
STUDIES = [
    ("Gap narrowed: customer support", "Productivity up 14% on average and 34% for novice and low-skilled workers.",
     "Brynjolfsson, Li and Raymond, Generative AI at Work", "https://www.nber.org/papers/w31161"),
    ("Gap narrowed: consulting", "Below-average performers improved by 43%, above-average by 17%.",
     "Dell'Acqua and colleagues, Navigating the Jagged Technological Frontier", "https://ssrn.com/abstract=4573321"),
    ("Gap widened: small businesses in Kenya", "No average effect; low performers did nearly 10% worse, high performers may have gained over 15%.",
     "Otis and colleagues, Management Science", "https://pubsonline.informs.org/doi/10.1287/mnsc.2024.06909"),
]

FIT = {"fits": "fits", "mixed": "mixed", "different": "does not fit"}

HYPOTHESIS_NOTICE = ('<div class="notice" role="note" id="spread-status"><strong>A hypothesis, not a result of the F3 model.</strong> Nothing on this page is computed by F3 and nothing here is built into it. '
                     'The claim that AI widens gaps on long, delegated tasks is <strong>untested</strong>; most published evidence so far shows gaps narrowing. '
                     'The figures about other systems come from the published studies listed at the foot of the page. They were read from search extracts on 2026-11-12; the primary pages were not opened.</div>')


def li(rows, with_fit: bool) -> str:
    out = ""
    for r in rows:
        if with_fit:
            label, what, fit, name, url = r
            out += f'<li><strong>{label}</strong> ({FIT[fit]}). {what} <a href="{url}">{name}</a>.</li>'
        else:
            label, what, name, url = r
            out += f'<li><strong>{label}.</strong> {what} <a href="{url}">{name}</a>.</li>'
    return out


def body(banner: str) -> str:
    return f"""
<h1>Average or spread?</h1>
{banner}
{HYPOTHESIS_NOTICE}
<section class="card"><h2>Why this question is on the F3 site</h2>
<p class="lead"><strong>An average can hide what matters.</strong> F3 already reports bands instead of single lines. This page asks a related question about AI: does it pull people and firms toward the average, or push them apart?</p>
<p>The page states one hypothesis, shows what would count against it, and checks whether the same pattern appears in six other systems. It is background for a possible extension of F3, described at the end. It is not part of the model.</p>
</section>
<section class="card"><h2>The hypothesis: the effect of AI on gaps depends on task length</h2>
{HYPOTHESIS}
<p class="note">Schematic, not drawn from data. Solid: found in published field studies. Dashed: predicted, not tested.</p>
<p>On short tasks with a person in every step, AI assistants have lifted weaker performers most, so the gap between strong and weak narrowed. The hypothesis is that on long tasks delegated to AI agents the effect reverses: differences in judgment are multiplied and the gap widens.</p>
<ul>{li(STUDIES, False)}</ul>
<p><strong>What would count against it:</strong> controlled studies of multi-day delegated tasks that also show the gap narrowing.</p>
</section>
<section class="card"><h2>Four kinds of spread, kept apart</h2>
{KINDS}
<p>"More variance" can mean four different things. The hypothesis is about the third: the spread of outcomes between people and firms. Evidence for one kind is not evidence for another.</p>
</section>
<section class="card"><h2>The same question in six other systems: it fits two</h2>
{SYSTEMS}
<p class="note">Solid outline: the spread itself has widened, or the picture is mixed. Dashed outline: the change is a shifted average or a rising count, not a wider spread.</p>
<ul>{li(SOURCES, True)}</ul>
<p><strong>A shifted average and a wider spread look alike from the tail.</strong> Heat extremes are more common while cold extremes retreat, which points to a moved average; rainfall is different, its spread itself has widened. Each system has its own cause, and none of these changes was caused by AI. The reading of heat extremes as mostly a shifted average is this page's inference, not a statement quoted from the source.</p>
</section>
<section class="card"><h2>What this could mean for F3 (proposed, not built)</h2>
<ul>
<li><strong>Show spread wherever the model produces it.</strong> The climate panel already draws the 841-member band. Other panels show single runs.</li>
<li><strong>A switchable assumption, not a fact.</strong> If an AI link to inequality between firms or workers is ever added, it would need both settings: gaps narrow, gaps widen.</li>
<li><strong>Tag indicators.</strong> For each observed series, say whether its spread is widening or its average is shifting.</li>
</ul>
<p class="note">None of this is built or decided. It is recorded as a proposal in decision D-062 for the editor.</p>
</section>
"""
