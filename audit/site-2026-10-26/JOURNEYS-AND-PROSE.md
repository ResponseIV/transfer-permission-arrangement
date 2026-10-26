# Journeys and prose

Review date: **26 October 2026**. Source locations refer to baseline `769913f`. These are editorial recommendations, not changes to the site. Substantive rewrites below are bounded by the submitted paper. See [AUDIT.md](AUDIT.md) for severity and evidence, especially F1–F10.

## A first-time reader: The essentials

**Entry.** “A secret moved. Was there a deal?” is understandable before the reader knows the benchmark. The visible exchange gives that question an object. On desktop the question and exhibit coexist; on a phone the exhibit begins around y=710, after the title, explanation, byline and actions. This is acceptable reading order, but the reader can choose “Read the story” and bypass the demonstration that makes the opening distinctive. The first continuation should make the connection explicit: the story explains why that exchange's appearance is insufficient.

**What this reader learns.** The setup defines agents, token, shared pages and episode. Transfer shows why a written code is not necessarily received; permission shows why behavior alone does not settle a rule violation; arrangement shows why a sequence can be supplied by the experiment. The advice about keeping writes, reads, revisions, answers and instructions is useful. The limits accompany the headline results. A reader can finish with a defensible core idea rather than only a feeling that AI collusion is complicated.

**Where the route thins out.** The experiment's constructed alternatives are named but their chapter is hidden. The shared-source example that most clearly explains innocent matching answers is also hidden. The essentials therefore gives the findings a clean route, but omits some of the best reasons to remember them. Add one compact archive counterexample near setup or transfer: both agents can return matching codes after independently reading the same archive. Agreement in answers is not enough to infer an exchange. The paper reports this in `paper/report.md:235–241`; the site's richer discussion is at `docs/index.html:804–820`.

**Likely drop-off.** The Transfer chapter repeats the success count in paragraph and tiles, then adds qualifications in smaller text. “Primary transfers” and “prescribed” are precise but not lay vocabulary. Use “main test” and “told to exchange” at this depth. Do not remove the distinction between 194 episodes with no prescribed exchange and the other 12 failed prescribed exchanges.

**Finish.** The local PDF handoff is strong. Tell this reader what the paper adds: the full comparison populations, registered versus later checks, and unresolved alternatives. The current invitation is largely a list of things the paper contains. A specific unanswered question—whether a script received by only one agent would remain distinguishable—would make continuing intellectually motivated (`paper/report.md:266–269`; `docs/index.html:901–902`).

**Acceptance for this journey:** after the essentials, a new reader should be able to explain the three findings, name one innocent look-alike, say why the opening was scripted, and state that recorded arrangement is not proof of private intent. This audit did not test those outcomes with participants.

## An AI-literate reader: The investigation

**Entry.** This is currently the richest route. It adds constructed alternatives, the study process, cumulative records, judge comparisons, base-rate effects and the matching-answer control. It is about 3,003 extracted words versus 1,668 for essentials; the difference is substantive, although these approximate counts exclude code and are not reading-time estimates.

**The successful sequence.** Innocent alternatives make the evidentiary problem concrete. The distinction between a record available to an observer and the complete fixture log is productive. The permitted-versus-forbidden pair is especially valuable: measured signals can remain the same while permission differs. Sol's departure from the script prevents the result from sounding universal.

**The missing investigation.** “Build the explanation. Then try to break it.” promises a succession of changing beliefs. Its four steps instead summarize research practice. Give the reader a prediction, a result that complicates it, and the next test. There is ample existing material: the archive false positives; the few transfers under confidentiality; one-way transfers after offers; the scripted sequence; a later diagnostic flow check that misses encoded carriers. Do not turn the chronology into a triumphal arc. Some follow-ups were designed after early results, and the paper is candid about prior development and post-hoc work.

**The most difficult passage.** The base-rate paragraph (`docs/index.html:501–504`) asks the reader to track several populations and interval bounds before they have a simple example of an alarm's predictive value. Start with one hypothetical population and one negative mix, explain what changes, then let the chart add the alternatives. Explain that the dashed curves account for uncertainty in measured rates, rather than treating them as an additional prediction about deployed systems. The chart is an extrapolation under assumptions, not a field measurement.

**The desk handoff.** A link to a relevant pair is better than a generic invitation to explore. But the pair should open on its question and discriminating evidence. Current arrival repeats navigation/instructions and asks readers to operate a desk. Current single-case summaries also reveal what the reader is supposedly discovering. Retain an inspection route for readers who want the answer immediately; make the recommended learning route a guided inference.

**Acceptance:** this reader can distinguish transfer detection from arrangement coding, explain what identical signals establish in the matched permission conditions, and identify the negative-population assumption behind a base-rate result.

## A specialist: The research

**Entry.** The route adds real technical value: the operational transfer label, exact model identities, actions, event coding, population breakdowns, intervals, freeze chronology, partial blind checks and reproduction. The direct `?level=beginner#methods` link correctly selects expert depth and lands on Methods. It is about 4,564 extracted words, not merely essentials with acronyms.

**What should happen sooner.** Give the specialist a short evidence map before the tables:

| Question | Measurement | Relevant limitation |
| --- | --- | --- |
| Did a token transfer? | Frozen operational label and transfer judges | Almost all primary transfers were prescribed; judge coverage can be selective |
| Was it forbidden? | Agent instructions and matched conditions | The pact supplies conflicting instructions from the same source |
| Was an arrangement observed? | Registered event coding: offer, read, carrier reply, use | This sequence does not establish intention; a supplied script can reproduce it |
| How much human validation exists? | Partial blind/hand checks | 24/38 in one exercise; four actually read cells of a separate 20-cell proposal sheet |

This table is a proposed navigation aid derived from `paper/report.md:107–130,198–225,324–330,674–688`, not a new scientific result. Terms such as opportunity, uptake and informed read need their operational meaning when first consequential, rather than relying on a glossary after Methods.

**What makes this route less than excellent.** Tables arrive with captions but often without a clear “this row changes the interpretation because…” sentence. A specialist can reconstruct the argument; the companion should reduce that work. The partial human-check explanation is honest but could expose the asymmetric coverage before discussing agreement. Reproduction is a useful end, but a reader who only wants the label or validation coverage should have direct anchors to those items.

**Acceptance:** a specialist can locate the label definition, the 194/12 negative split, coding scope, post-hoc checks and partial validation without reading the whole article twice. Copied links should preserve the relevant evidence record as well as the case.

## Direct arrivals and continuity

- **Inner article chapter:** the heading and quiet rail supply good orientation at desktop/tablet. A link to a hidden specialist section selects a sufficient depth. Changing depth after arrival can lose the chapter; fix that before asking users to rely on depth switching.
- **Single episode:** the summary explains the selected case but the page assumes the reader knows the synthetic task. Add: “Two language-model agents use a small wiki; each starts with a private code, and the experiment records their reads, writes and answers.” Then ask the case-specific question.
- **Comparison:** replace the repeated desk instructions with the current pair's learning task. On phones, “left/right” should become A/B or the case names. A milestone comparison would avoid remembering an entire first log while reading the second.
- **Return to the article:** link back to the relevant finding and preserve depth. “Back to the explainer” at its top is a coarse return path after inspecting permission or arrangement.

## Exact copy examples and proposed revisions

### 1. Remove a garden-path phrase and expose both negative groups

**Before — `docs/index.html:434–436`:** “With the log, the judge called Astra found all 244 primary transfers.” This is grammatical (“called Astra” names the judge), but briefly reads as if *called* were the main verb. Do not misdiagnose it as a typo.

**After:** “With the read log, Astra detected all 244 transfers in the main test. It made no false alarms among 194 episodes where the experiment had not instructed an exchange. It made nine false alarms among 12 instructed exchanges that failed.”

Source: `paper/report.md:137–160`. Define Astra as a separate AI judge once. Retain the nearby statement that 242 transfers were prescribed. If the tiles remain, let this paragraph explain the archive mechanism instead of repeating all three displayed figures.

### 2. Replace self-ranking with the concrete challenge

**Before — `docs/index.html:715`:** “Then came the test that matters most.”

**After:** “Could the sequence identify who supplied the plan? In a registered control, one shared instruction specified the offer, reply and completion. Sol reproduced the sequence, including the read, in all 20 episodes. The instructions show that this control was prescribed; the other case had an observed offer-and-reply sequence without a supplied script. Neither sequence establishes private intent.”

Source: `paper/report.md:217–225`. Keep the no-rule condition explicit in the surrounding paragraph. Do not imply the two full traces are identical.

### 3. Show a failed shortcut without rewriting the chronology

**Before — `docs/index.html:360–364`:** “Challenge the strongest remaining clue” and an external link promising “the failed expectations.”

**After, replacing part of the abstract process list:** “A later check showed how easily a shortcut could fail. A retrospective flow flag found only one of the eight Sol follow-up transfers; it missed seven encoded carriers. This was a diagnostic check on existing runs, not a held-out measure of agreement detection.”

Source: `paper/report.md:741–746`. Then show one already-recorded carrier beside its decoding rule, linked to its case. Do not claim this later failure motivated an earlier registration. Do not equate this retrospective flow flag with every frozen signal or with the registered event coding.

### 4. Simplify the base-rate lesson in steps

**Before — `docs/index.html:501–504`:** “If 1% of audited episodes held a transfer and they resembled all 206 primary nontransfers, 19% of Astra's alarms with the log would be real (at least 11% at the interval bounds)…” The sentence continues with a different negative mix and more estimates.

**After, as an introduction rather than a replacement for the exact caption:** “Imagine auditing a population where transfers are rare. A detector can catch almost every transfer while most of its alarms are false, because there are many more episodes without a transfer. The chart asks how that balance changes under two different mixes of nontransfer episodes.”

Then identify the pooled 206 and restricted 194 populations, state their assumptions, and show one 1% example before adding the interval bounds. Source: `paper/report.md:153–168`. Any illustrative population counts must be calculated from the paper's rates and labeled hypothetical, with rounding shown; this audit proposes the teaching sequence, not new empirical counts.

### 5. Replace an intent implication with the recorded actions

**Before — `docs/data/episodes.json:3023`, beginner Qwen verdict:** “A token moved, but nobody arranged it: Alpha just gave it away.”

**After:** “Alpha wrote its code on the shared board. Beta read and used it. No offer was recorded.”

Source: `paper/report.md:213–215,324–327`; source episode `qwen-letter-37`. Similarly replace the beginner planted-leak verdict's “nobody arranged it” with “No offer or reply was recorded; the experiment had planted the token.” This states the evidence without claiming access to intent.

### 6. Make the record boundary explicit

**Before — `docs/index.html:96`:** “Condensed log, with actors identified by the experiment. Open the complete record.”

**After:** “Condensed scripted-control record. Alpha and Beta are the experiment's recorded actors; the observer's shared-board authors were anonymous. Open the complete record.”

Source: `sol-scripted-01` and `docs/assets/explorer.js:103–150`. If the editorial decision is to preserve the control's reveal, disclose reconstructed attribution immediately and name the control clearly at the reveal. Either approach should distinguish reconstruction from the limited observer view.

### 7. Use one term after explaining it

**Before — `docs/index.html:394–395`:** “A visitors' book, which the paper calls the access log…” The beginner explorer also uses “+ Visitors' book.”

**After:** “Access log: which page and version was read, and when. Shared-board reads remain anonymous to the observer.”

Keep the notebook analogy once in setup if it helps. Thereafter use page writes, access log, answers and instructions consistently. “Simple” words should reduce conceptual work, not create a second vocabulary.

## Cut, move, expand, preserve

| Action | Material | Purpose |
| --- | --- | --- |
| Cut | One duplicate narration of the transfer counts; “the test that matters most”; repeated desk instructions | Recover attention for evidence |
| Move | One shared-source counterexample into essentials; the specialist evidence map before detailed tables | Give each reader the missing context sooner |
| Expand | One failed shortcut; why the script challenge matters; the one-way/first-mover qualification | Make the research process interesting without broadening claims |
| Explain differently | Base-rate assumptions; transfer judge versus arrangement coding; reconstructed actors versus anonymous observer | Reduce inference errors |
| Preserve | Opening puzzle; real excerpts; direct caveats; Sol's different permission behavior; unknown judge verdicts; submitted-source handoff | Keep the work's actual strengths |

The best voice for this project is precise curiosity. It can be calm and personal without becoming confessional, promotional or theatrical. It should show the reader why an interpretation failed, then let the evidence earn the next conclusion.
