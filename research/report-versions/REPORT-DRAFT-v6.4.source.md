# Transfer, Permission, Arrangement: What Agent Logs Can and Cannot Prove About Collusion

Tom - Response IV (Swarmchasers Discord)

Affiliation: Independent researcher

## Abstract

When AI agents share private information, what would convince an auditor that they arranged the
exchange? Antitrust law faces the same problem and does not infer an agreement from parallel conduct
alone; we borrow its method of comparing evidence against concrete innocent explanations. In a
two-agent task that records every page write, read and final answer, we built those explanations on
purpose (a shared source, an authorized exchange, a planted leak) and ran 706 scorable episodes on four
OpenAI models and the open-weight Qwen3-32B. Three questions needed different records. Transfer: with
the access log, a frozen model judge found all 244 primary transfers (242 of them prescribed exchanges) and raised no false alarm on the
194 episodes where no exchange was prescribed. Permission: a near-matched script without the confidentiality rule left six page and log
signals unchanged on two models; a third model's traffic changed. Arrangement: in a
registered follow-up on one model, all eight transfers the agents arranged themselves followed an offer,
its reading and a reply carrying the token, but a scripted control produced the same sequence in 20 of
20 episodes, and a planted token was taken in 60 of 60 without any. Audits should keep reads, revision history and instructions, and
report these three findings separately.

## 1. Introduction

In one episode, an agent read its partner's token from a note planted before the task and returned
it. In another, one agent offered a reversed-token exchange, the other read the offer and posted its
own token reversed, and both returned both tokens. Both records show a completed transfer. Only the
second contains an offer and a reply.

Question 2.3 asks which signals separate deliberate coalitions from innocent correlation, talk
without action and harm without agreement. Antitrust has faced a similar problem: conduct "as
consistent with permissible competition as with illegal conspiracy does not, standing alone, support
an inference" of conspiracy (Matsushita, 1986), and "without more, parallel conduct does not suggest
conspiracy" (Twombly, 2007). Courts look for plus factors, which Kovacic et al. (2011) propose ranking
by how much more likely each is under an agreement than without one; the obstacle they name is that
courts rarely observe conduct known to be innocent. Mehra (2016) notes the converse gap, coordination
reached without an agreement. We borrow the comparison method, not legal conclusions.

We test which records (the ordered page writes, an access log of reads, the final
answers, the instructions) distinguish three questions: whether a token was transferred, whether the
transfer was permitted, and whether the agents were observed arranging it.

**Our main contributions are:**

(1) **A controlled comparison of records and alternative explanations.** For each question we built
the alternative that mimics it and measured which record separates the two (Table 1), on three models
from two providers.

(2) **Measured failures of plausible evidence**: false alarms the access log removes, matching answers
that a shared source defeats, and an offer and reply that a script reproduces.

(3) **A registered event definition of an observed arrangement**, an offer, then a reply carrying the
token, then use, written before a 40-episode follow-up and met by all eight transfers it produced, and
a scripted control showing that it needs the instructions beside it.

**Table 1. Three questions and the record used to assess each.** The alternatives are question 2.3's
three contrasts. Counts are episodes.

| Question | Record used to assess it | Alternative that mimics it | What we found |
|---|---|---|---|
| Transfer: did a token move? | Access log of reads, and the answers | Innocent correlation: a shared source; an agent's own token on its own page | With the log, 244/244 transfers found; 0 false alarms on 194 episodes with no prescribed exchange (28 on page writes alone) |
| Permission: was it forbidden? | The instructions | A near-matched script without the rule | Six page and log signals identical over 20 task pairs on Luna and on Qwen; Sol's traffic differed |
| Arrangement: did the agents set it up? | Offer, its reading, a reply carrying the token, and the instructions | Talk without action. Harm without agreement: a planted leak. A script that lays out the sequence | Later Sol follow-up: 8/8 transfers followed it; a script produced it in 20/20. Leak taken in 60/60, none arranged |

## 2. Related work

Agent collusion work studies covert channels (Motwani et al., 2024; Mathew et al., 2025; Rippin et
al., 2026), action and message measures (Nakamura et al., 2026), monitoring (Radev et al., 2026; Hu et
al., 2026; Tailor, 2025), activations (Rose et al., 2026), long interactions (Shi et al., 2026) and arrangements supplied by a
common principal (Berger et al., 2025).

At the time of writing, three concurrent sprint entries reach neighbouring conclusions: in a pricing
market, plus factors tested against a shared cost shock and talk without action showed that convincing
evidence was behavioural (Engelbrecht, 2026); passive association cannot separate a common cause from
direct copying without intervening on the channel (Kwon, 2026); an activation probe separates a covert
pricing cartel from natural colluders only with the right negatives (Aktas, 2026). We add complete agent logs, a permission contrast, a planted
leak, and a registered arrangement definition tested against a script.

## 3. Methods

**Task and record.** We call the OpenAI agent models Sol, Luna, Terra (gpt-5.6-sol, -luna, -terra)
and Astra (gpt-6-astra). An episode has two agents, alpha and beta, each holding a private
seed-derived token (an initial and nine hexadecimal characters). Each has at most eight actions: read
a page, replace a page, or answer `alpha=<token>|beta=<token>`. Agents alternate, alpha first. Some
conditions open a shared board whose writes carry no author name; the fixture still records every
event, its true author and the revision each read returned.

**Ground truth.** The fixture records events and tokens exactly; transfer is a frozen operational
label. A completed transfer is an agent re-emitting the other's token after reading it on a revision
the other wrote, or answering with a correct peer token that no recognized plain read explains, assuming
the token was not guessed. All 244 primary transfers and every follow-up transfer with an encoded carrier
count through this second clause; the 60 planted-leak transfers and one plain disclosure on Qwen
count through the first. Receipt (reading such a revision) and
use are scored separately.

**Conditions.** Two confidentiality rules with an urgency sentence and no sharing scheme: by the
letter ("never write it on any page") and by purpose (the other agent must never learn it, in any
form). An instructed pact under the letter rule ("you have privately agreed to get round this rule",
with a reversal method), and its no-rule counterpart, which removes the rule and rewords that sentence
("you have agreed on how to exchange your tokens"). Authorized conventions: write tokens reversed or
shifted, no rule. A shared source: a read-only archive holding both tokens. A planted leak: alpha's readable note already holds its token, and nobody is told. A scripted offer: one
instruction lays out an offer, a reply and completion, with no rule.

**Observer records and detectors.** Page writes: the ordered history of every write and its text,
with authors hidden on the board. Page writes and log: adds who read which page, and when. Pages, log and answers: adds the final answers. A carrier is page text holding a token in some form; an informed read
is a read of a page holding another hand's secret-like string; uptake is an answer carrying such a
string after it was read. Eight frozen signals include these, a request for a token, code language and
agreeing answers. Two judges frozen before the sprint (gpt-6-astra, prompt 10; gpt-5.6-luna, prompt 9) answer whether a
secret reached another agent, blind to tokens, model and arm; Qwen3-32B with Astra's prompt was added
afterwards.

**Sequence and registration.** The testbed, label, signals and judge prompts are preexisting work,
developed on 1,174 earlier episodes (Appendix E); they were frozen before a 450-episode primary test on
four OpenAI models (461 attempts; 11 excluded, one a provider refusal). Six follow-ups, each registered
with predictions by the author and by Claude before its first episode: 39 Sol episodes on a new seed;
the no-rule counterpart and planted leak on Luna (40), Sol (57) and Qwen3-32B (60); Sol's letter-rule
arm on Qwen3-32B (34 of 39 attempted); a scripted offer with no rule on Sol (20) and Qwen3-32B (6 of
8 attempted). Failed episodes are kept, never rerun (a stopped run may resume once; one resumed twice, a logged
deviation). These 706 episodes, the alternatives, the arrangement definition and the
analyses are new.

Intervals are exact (Clopper–Pearson, 95%); paired tests are exact on discordant pairs, with Holm's
correction within each family. All 143 registered forecasts are scored in Appendix D.

## 4. Results

### 4.1 Under a rule, asking was common and passing was rare

Under the two confidentiality wordings, 146 of 156 episodes contained a request for a token, the
proposal judge flagged 9, and 2 ended in a transfer (per model in Appendix C). Both were on Sol under the letter rule; the other three models proposed in at
most one episode and passed none.

### 4.2 Transfer: the access log removed false alarms where no exchange was prescribed

With the log, Astra found every transfer (Table 2; κ = 0.96, against 0.80 on page writes).

**Table 2. Frozen judges on the 450 primary episodes, by record shown.** Hits of 244 transfers;
false alarms in 206 episodes without one.

| Record shown | Astra hits | Astra false alarms | Luna hits | Luna false alarms |
|---|---|---|---|---|
| Pages | 240 | 39 | 195 | 18 |
| Pages and log | 244 | 9 | 233 | 25 |
| Pages, log and answers | 244 | 9 | 232 | 32 |

Where the false alarms fall depends on the kind of episode without a transfer (Table 3). With the log,
Astra raised none in the 194 episodes where no exchange was prescribed, and 9 in the 12 prescribed
exchanges that did not complete (3 instructed pacts, 9 authorized conventions). On page writes alone it
raised 28 in the 194: Sol wrote its own token on its own note in all 20 of its archive episodes and
Astra called 19 of them transfers; the log, which shows that neither agent read the other's page,
removed all 19. The second judge and the open-weight judge, which found every agent-arranged transfer,
failed on different episodes.

**Table 3. False alarms with page writes and log, by kind of episode without a transfer.** Rule arms prescribe no exchange.

| Kind of episode | Episodes | Astra | Luna | Qwen3-32B |
|---|---|---|---|---|
| Rule arms | 154 | 0 | 1 | 31 |
| Shared archive | 40 | 0 | 12 | 29 |
| Failed prescribed exchanges | 12 | 9 | 12 | 9 |

How much an alarm is worth depends on which episodes are audited (Figure 1). If 1% of audited episodes
held a transfer and they resembled all 206 primary nontransfers, 19% of Astra's alarms with the log
would be real (at least 11% at the interval bounds); if no prescribed exchange were present, the point
estimate is 100% and the bound 35%. On page writes alone, 5%. The base rate and the mix are the
auditor's assumptions.

![Figure 1](figures/writeup-v6.4/figure-1-alarm-share.png)

**Figure 1. How often a transfer alarm would be right.** Share of Astra p10's alarms that are real
transfers, by the assumed base rate, from its primary-test rates: with the log against all 206
nontransfers (blue, point and bound), with the log against the 194 with no prescribed exchange (green,
bound; the point estimate is 100%), and on page writes alone against all 206 (red).

String tracing missed most agent-designed carriers: uptake found 174 of 244 primary transfers, none of
the 194 unprescribed nontransfers and 3 of the 12 failed prescribed exchanges, but only 1 of the 8
transfers in the Sol follow-up, whose carriers used per-character RSA and an XOR mask.

### 4.3 Permission: six signals did not distinguish forbidden from permitted scripted exchanges

We ran the instructed pact against its no-rule counterpart on the same tasks, on three models
(transfers, pact against no-rule: Luna 17/20 against 20/20, Sol 3/17 against 20/20, Qwen 12/20 against
11/20; Qwen ran with a larger token allowance, Appendix B). The two prompts differ in the rule and in
the reworded agreement sentence.

On Luna, the six frozen page and log signals were identical across the 20 task pairs. Of the 12
paired tests in that family (eight signals and four label fields), only agreeing answers differed after
Holm's correction (5 of 20 under the pact, 20 of 20 without the rule; adjusted p = 0.0007): under the
pact one agent often used all its actions without answering. On Qwen, the six signals were also
identical across the pairs.

Sol responded differently to the two prompts. In 12 of its 17 pact episodes the pages carried a
request for the token and code language together, and in none of the paired no-rule episodes (raw
paired p = 0.0005); only 3 pact episodes completed a transfer, against 17 without the rule
(p = 0.0001). Sol mostly asked plainly instead of following the pact script. On these three models,
then, the measured signals separated the prompts only where the model departed from the script.

### 4.4 Arrangement: offer, reading, reply

Before 40 new Sol episodes we registered an event-level definition, shaped by the four earlier
agent-arranged transfers: an offer proposes a disguised transfer; the other agent accepts by posting a
carrier of its own token; the arrangement is completed when the offerer re-emits that token.

Of 39 scorable episodes, 13 contained an offer, 8 an acceptance, and all 8 completed; the coding was
done from the event logs before any judge verdict was read. In each, the other agent read the offer
before posting its carrier; four of the five unanswered offers were never read; no transfer happened
without an offer. Every carrier re-encodes exactly to the true token under the offered scheme (RSA, an XOR mask,
reversal). All eight successful offers came from alpha, the agent that moves first, and seven transfers went only
to it; in four, beta's request for alpha's token in return went unanswered. The two-way exchange is the
one where alpha posted its own token first (Figure 2, left). The page-only proposal judge agreed with the coding of offer presence in
all 39 episodes.

The same letter-rule arm on Qwen3-32B produced no offer in 34 scorable episodes (10 with a request by
hand count, 2 by the frozen signal). Its one transfer was a plain disclosure that beta read and used;
Astra with the log called only that episode, and on page writes alone two more where nobody read.

A script produces the same sequence. In a registered control with no rule, one shared instruction laid
the sequence out: alpha offers a reversed-token exchange, beta replies with its token reversed, alpha
completes. Sol produced it, reading included, in 20 of 20 episodes; no page mentioned an agreement or
an instruction, and the offers read like the agent-made ones ("I will reverse it"). The proposal judge and a looser
retrospective screen (Appendix F) fired on all 20, as the screen did on all ten agent-arranged
transfers. Supplied conventions met the definition too: 27 of the 31 the screen flagged, though in 19
the reply came before the offer could be read. What separated them was the instructions or, in bulk, the script's regularity: blind to the key, the
author called all 11 scripted episodes on a mixed sheet scripted (22 of 24 correct), from the identical
turn order and complete answers (Qwen: 6 scorable episodes, Appendix B).

![Figure 2](figures/writeup-v6.4/figure-2-trajectories.png)

**Figure 2. Two ways a token passed.** Left: Sol follow-up episode 21, an observed arrangement: an
offer with alpha's own reversed token, beta's read, beta's reversed token, alpha's read, then both
answers carry both tokens. Right: Luna planted-leak episode 01, no observed arrangement: beta reads the
planted token before alpha replaces the note with a request. Numbers are event orders.

### 4.5 Alternatives that look like collusion

**Shared source.** With a read-only archive, both answers matched in all 40 episodes, though neither
agent read anything the other wrote. Agreeing answers occurred in 189 of 244 transfers; against the
pooled nontransfer episodes that looks 3.8 times as common under transfer, but against the archive
alone it is less common (lower bound 0.72). A large pool of easy negatives hides the one alternative
that defeats the signal.

**Transfer without an observed arrangement.** A token planted on alpha's readable note was taken in all
20 Luna episodes, and again on Sol and Qwen: 60 of 60. Beta wrote no page; uptake and the informed read fired in all 60, the request signal in 37 because
the victim asked for the other token, and Astra with the log called all 60. The final page holds
alpha's request, not the token that was taken (Figure 2, right).

## 5. Discussion

**What should count as convincing evidence of collusion.** A transfer alarm addressed only the first question. Whether the transfer was permitted was in the instructions; the six measured
signals did not reveal it when the agents followed the script. Whether the agents arranged it needed
the order of events, an offer, its reading and a reply carrying the token, which the planted leak
lacked, and the instructions, because a script produced the same order. Matching answers and transfer alarms behave like parallel conduct. An observed offer and acceptance is closer to direct evidence than to a plus factor, which an auditor
falls back on when the log lacks reads or their order. All eight agent-arranged transfers in the Sol follow-up showed the registered sequence, and so did all 20
scripted episodes.
Nor did an arrangement mean a shared gain: 9 of the 10 agent-arranged transfers served only the agent
that proposed the scheme.

**Records to keep.** Measured: removing the access log raised false alarms on unprescribed
nontransfers from 0 to 28 of 194; without the instructions a scripted exchange showed the same offer
and reply as an arranged one (20 of 20), and a permitted and a forbidden scripted exchange the same six
signals. Demonstrated in single episodes: without revision history the leak reads as a request
(Figure 2). Section 6 lists the records to keep. By analogy with
the gap Mehra (2016) describes, a standard that looks only for an arrangement would not flag the leak,
while one that looks only for transfer would.

**Limitations** (Appendix A). A synthetic two-agent task; no market harm or intent is measured. The
observed arrangements are few, on one model and wording, and the follow-up's successful offers all came from the first mover. Scale and the choice of models were
set by an individual budget (consumer model subscriptions and hackathon compute credits). The author's blind check covers 24 of 38 episodes (Appendix D). Harder alternatives remain: a script only one
agent receives, a leak an agent causes (Qwen produced one, unprompted), a source one agent sees.

## 6. Conclusion

Logs show transfer, not collusion. In this task the access log settled whether a token moved; the
instructions settled whether moving it was allowed; and whether the agents arranged it needed the order
of events and the instructions together, because a script produced the same offer and reply. An audit for agent collusion should keep each read with the revision it returned, the write history
and each agent's instructions, and report the three findings separately.

## Code and data

Every run record, registration, analysis and script, and 1,923 episode records (43 failed, kept and
flagged), are in the release (code MIT, data CC BY-NC 4.0). Repository: https://github.com/ResponseIV/transfer-permission-arrangement

## References

<!-- GENERATED REFERENCES -->

## Appendix A. Limitations and Dual-Use / Ethical Considerations

Appendices B–F give the prompts and run counts, every judge and signal result, every forecast and
the human checks, the prior-work boundary and rebuild, and the checks that failed.

**Scope.** The task tests complete-token transfer, not every partial disclosure or hidden channel.
The offer-and-reply definition does not establish intention. The pact gives conflicting instructions
from one source, not an override of a higher-priority policy. The leak is planted by the fixture. No
downstream harm or real system is involved.

**Selection.** The primary measures were developed on prior data; follow-ups designed after early
results keep their stated scope, and forecasts made while an arm was running do not make it unseen.
The Sol follow-up chose a model and condition that had produced transfers, and its successful offers
all came from the first mover, which limits what eight cases support. Episodes, models and providers
were bounded by an individual budget (consumer subscriptions; hackathon credits for Qwen).

**Statistics and measurement.** Intervals are equal-tailed Clopper–Pearson 95% intervals assuming
independent episodes, although task tokens repeat across paired conditions and models; paired tests
are two-sided exact McNemar tests, raw and Holm-adjusted results kept apart. The judges differ in
prompt and the OpenAI/Qwen routes in compute allowance, so their comparison does not isolate model size
or training. Uptake can attach an agent's own token to an anonymous-board read; page names can hint at
authors; receipt can occur without use. We keep the frozen definitions and report these limits.

**Dual use and ethics.** The work is meant for auditors: which records help assess which question,
and where common detectors mislead. The logs show the encodings agents chose (reversal, splitting,
per-character RSA, an XOR mask), all standard and described in the cited literature. No experiment
varied a detector or a surveillance threat, no agent was trained to evade monitoring, and no evasion of
a deployed monitor is shown. Tokens are random strings in a synthetic fixture; no person, account or
real system is involved. Refusals and failed episodes stay in the record; the data are released for
non-commercial evaluation.

## Appendix B. Prompts, models and run counts

Sol, Luna and Terra are gpt-5.6-sol, gpt-5.6-luna and gpt-5.6-terra; Astra is gpt-6-astra.
OpenAI agents used high reasoning effort and judges low. Qwen3-32B (weights revision 9216db57) ran through vLLM on Modal
with default thinking. Its declared allowance was 4,096 tokens per action, versus 1,500 per
agent on the OpenAI route; both retained the eight-action limit. Compute budgets were not matched.

The original test's scorable episodes comprise 156 rule-wording episodes, 20 pact episodes,
234 no-rule instructed exchanges and 40 archive episodes. A failed episode may contain a
transfer event, but primary rates exclude the whole failed episode. Follow-ups use separate
counts, and the original Luna pact is not counted twice. The scripted-offer control ran 20 Sol episodes, all scorable, and 8 of 20 on Qwen3-32B: format failures in
episodes 01 and 08 stopped the run and its single resume, leaving 6 scorable. The Qwen letter-rule follow-up registered 40
episodes and attempted 39: it stopped on a format failure at episode 17 and, resumed once on its unrun
episodes, again at episode 39; with 2 invalid actions and 3 truncated episodes, 34 are scorable.

For source attribution, the frozen label keeps the first matching read of each peer token.
A first archive read stays archive-sourced even after a later read of a peer-authored copy.
The coded flag can also come from a correct peer token in a final answer without a recognized
carrier; the flag does not itself require an observed encoding scheme.

<!-- GENERATED RUN TABLES -->

These are the exact task prompts from the manifests. Private evidence adds only the owning
agent's token. Common adapter instructions and the tool schema are in the preexisting source.
The leak also changes the initial fixture state as stated beside its prompt.

<!-- GENERATED PROMPTS -->

## Appendix C. Judges, signals and uncertainty

**Table C0. Rule arms without a supplied scheme, per episode.** Requests are from the frozen text
detector; proposals are positive calls of the page-only proposal judge, not agreement labels.

| Model | Episodes | Token requests | Proposal flags | Completed transfers |
|---|---|---|---|---|
| Sol | 40 | 40 | 8 | 2 |
| Luna | 39 | 39 | 0 | 0 |
| Terra | 39 | 33 | 1 | 0 |
| Astra | 38 | 34 | 0 | 0 |

The judges receive an observer record without true tokens, source model or arm label. The
question asks whether a secret reached another agent in any form. The tables score that call
against both completed transfer and the frozen receipt measure, exposure or transfer. Rates
use valid verdicts; coverage tables retain errors, interruptions and pending calls separately.
Missing verdicts may be selective, so these rates do not describe the omitted calls.
The condition-level comparisons were added after the runs and are descriptive.
Forecast counts allow either verdict for each unresolved request. The kappa forecast also
uses the full attainable range against the saved Astra calls; its point estimate uses valid pairs.
Judge-call gaps do not add task episodes to those counted in Section 3.

<!-- GENERATED JUDGE TABLES -->

All 206 primary nontransfers enter the judge tables. The exploratory signal comparison instead
retains 194 nontransfer cases and sets aside 12 assigned exchanges that did not complete.
Against common source, matching answers have a transfer/nontransfer rate ratio of .77, lower
bound .72. Pooling the retained cases gives 3.8, lower bound 2.7. These are transfer comparisons,
not agreement ratios.

For a stated signal, the conservative ratio bound divides its positive-rate lower interval
endpoint by the largest upper endpoint among the comparator cases. The fixed case with the
largest true rate gives the coverage argument; selecting a signal after inspecting the table
is a separate issue. Uptake has no positives in the retained negative set, so its point ratio
is unbounded. At a 1% assumed prior, the lower-bound transformations are 25.9% against the pooled
retained cases and 2.1% against the worst comparator. They do not establish certainty or a
posterior probability of agreement. In Figure 1 (Section 4.2), solid lines use the measured rates and dashed lines the lower hit-rate and upper false-alarm-rate interval endpoints; the green curve uses only the 194 nontransfers with no prescribed exchange, and so assumes that failed prescribed exchanges are absent from the audited population; the bounds hold
for each configuration under the episode-sampling assumptions, not simultaneously across them.

<!-- GENERATED SIGNAL TABLE -->

<!-- GENERATED SUBGROUP DETAILS -->

## Appendix D. Predictions and validation

The complete 143-line record is `prediction-ledger.csv`: original wording, observations,
scoring sources and caveats, including wrong predictions and free lines with no forecast.
The source registrations retain their original text. Table D1 sorts every forecast into four
outcomes; the CSV keeps each detailed verdict beside its outcome. The wrong forecasts are the most
informative: both forecasters expected the planted token to be taken in 10 to 18 of 20 Luna episodes
(it was 20); both expected 16 to 20 no-rule transfers on Qwen (it was 11, lost to reversal errors);
the author expected the rule to show in Qwen's traffic (no signal differed); and Claude expected at
most one answer-free signal to differ between Sol's pact and no-rule episodes (four did).

<!-- GENERATED PREDICTION LEDGER -->

The independent proposal judge and event coding agree on offer presence in 39/39 Sol follow-up
episodes: 13 positive and 26 negative. That comparison does not validate acceptance or completion.
The blind proposal sheet asks its own question on its own sample. The separate checks are:

| Independent check | Episodes reviewed | Disagreements | Notes |
|---|---|---|---|
| Arrangement sheet (blind, scripted episodes mixed in) | 24 of 38 | offer 4, acceptance 1, completion 1 | See below |
| Blind proposal hand read | 4 of 20 | 0 | See below |

Arrangement sheet (13 follow-up cells, 11 scripted episodes): the 4 offer disagreements are requests for an
unnamed "token-safe route", which the author counted and the registered definition excludes; the completion
disagreement is an episode where the offerer did answer with the other token. Scripted or agent-made, from the
log alone: 22 of 24 correct, all 11 scripted episodes identified (comparison file
`CHECK-blind-arrangement-20261026-comparison.md`). Proposal sheet: all four cells read were ones the judge
flagged; two of the author's yes calls rest on a request with no named form; 16 were not read.

## Appendix E. Prior work and reproduction

The public sprint opened at 2026-10-23T12:00Z. The instrument commit `a280f7a` predates it.
The annotated `sprint-freeze` tag was recorded at 15:27:34Z, before the first primary run
manifest at 15:27:57Z. The tag's time is not a pre-opening registration. Freeze membership
and manifest timestamps identify 1,198 prior attempts, 1,174 scorable. Three failed prior
Gemini attempts are outside the OpenAI/Qwen benchmark export.

The new sprint results are the 450 primary episodes and 256 unique follow-up episodes (196 in the
first four follow-ups, 34 in the Qwen letter-rule run and 26 in the scripted-offer control), 706 in all,
described in Section 3. New work also includes the case comparisons, registered sequence definition,
analyses, retrospective auditor and report. The preexisting instruments and development data
are identified in `research/PRIOR-AND-NEW-WORK-20261023.md` and the release README.

The report's numbers are saved in `research/numbers-writeup-v6.3/` (the v6.0 capture plus the Qwen letter-rule and scripted-offer outputs, recorded in `REPORT-INPUTS.json`), which extends `research/numbers-writeup-v6.0/`: the v5.2 capture, unchanged,
plus the judge rates for nontransfers with no prescribed exchange (Figure 1, Table 3) and the sequence-by-condition table; `REPORT-INPUTS.json` records the added files, the commands and scripts that produced them, the capture time, source commit, script hashes and data hashes. This capture includes
the registered Qwen judge groups and the condition-level analysis. Judge failures have no
verdict. One primary request interrupted by the old supervisor has an unknown outcome and
was not replayed. The coverage tables identify those omissions. The fact sheet preserves
the earlier analysis capture and records the later Qwen inputs separately.

The document itself was built from those tables, a fact sheet and a small excerpt bundle in the working repository, with the official template; the public release carries the built report and every analysis input, not that document-build bundle.
`zsh scripts/sprint_numbers.sh` regenerates analysis tables without model calls. Repeating
stochastic inference is different from replaying records: the OpenAI model names are aliases and
do not guarantee identical future outputs; the Qwen weights are pinned to the revision that ran
(`Qwen/Qwen3-32B@9216db5781bf21249d130ec9da846c4624c16137`, in `scripts/modal_vllm.py`), though
sampling still varies between runs.

<!-- GENERATED FIGURE CHECKS -->

## Appendix F. Additional checks and unsuccessful approaches

Reasoning-headline searches flagged 16 primary rule episodes. Event-by-event inspection of
the nine with no page proposal found one scheme softened on the page, five considered before
a plain or unnamed request, and three named in order to reject them. These are summaries, not
the underlying reasoning. Missing headline coverage and rejection language make the lexical
flag unsuitable as an intent label.

String uptake found all 155 completed reversed-convention transfers and fired in one of 70
shifted-convention transfers. Inspection showed that the latter reused the agent's own carrier
relayed on the anonymous board; it did not demonstrate successful shift decoding. This helps
explain why performance on a supplied convention does not settle performance on other carriers.
Uptake also fired in three reversed-board episodes without completed transfer. Those are among
the assigned noncompletions excluded from the 194-case comparison in Appendix C.

The exploratory signal-rule search also had a failure worth preserving. It selected opportunity combined
with agreeing answers for the observer with final outputs. That removes archive cases, but
catches only one of ten held-out transfers under a rule, a group that includes instructed pacts.
A separate split keeps repeated tasks together. Its results and the individual case results
are retained with the analysis rather than replaced by the best-looking aggregate score.

The retrospective auditor (`scripts/audit_cell.py`) was written after the runs. After a correction distinguishing
prohibitions from prescribed exchanges, its candidate rule flags the two original-sprint
agent-arranged transfers and one other candidate against the existing proxy. On its Sol
follow-up development data it flags eight candidates and one other case. Its flow flag finds
one of eight transfers and misses seven encoded carriers. These are diagnostic results, not held-out agreement accuracy;
`scripts/sequence_by_condition.py` gives the per-condition counts of this looser screen; it is not the registered event coding. It flagged all ten agent-arranged transfers in the sprint and two other episodes, where the anonymous board hid that one agent wrote both the code language (in one, a refusal mentioning "plaintext") and the token-like text; it never fired on the archive (0/40), the leak (0/60) or the pact and its no-rule counterpart (0/117), but on page writes it fired on 31 of 234 authorized conventions, where agents restated the prescribed scheme, and on all 26 scripted-offer episodes. The auditor's instruction check, a pattern for the fixture's known pact and convention wording, missed the scripted-offer instruction and called all 26 agent-made candidates; it was not changed after the fact. `scripts/code_sequence.py`, a coding aid for supplied carriers, proposed the scripted-offer and authorized-convention codings, each then read by hand (`research/CODING-scripted-offer-20261026.md`). On the Qwen letter-rule run it fired on none of 34 episodes, including the one plain disclosure, in agreement with the coding. Masking agent names in page paths changes no frozen signal;
it does not prove that names cannot influence a model judge.

## LLM usage statement

Claude and Codex assisted with design, implementation, analysis and writing. Claude coded offers and
carriers before any proposal-judge verdict was opened, and carrier arithmetic was checked by
computation; the human checks are in Appendix D. The author is responsible for the report and
verified its claims and results.
