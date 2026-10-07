---
title: "Style Patterns"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "style-patterns"
tags: [skill-reference, humanizer]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/creative/humanizer/SKILL.md"
summary: "**Problem:** LLMs use em dashes (—) more than humans, mimicking 'punchy' sales writing. In practice, most of these can be rewritten more cleanly with "
---

# Style Patterns

_Moved verbatim out of SKILL.md so the trigger body stays small._

## STYLE PATTERNS

### 14. Em Dash Overuse

**Problem:** LLMs use em dashes (—) more than humans, mimicking "punchy" sales writing. In practice, most of these can be rewritten more cleanly with commas, periods, or parentheses.

**Before:**
> The term is primarily promoted by Dutch institutions—not by the people themselves. You don't say "Netherlands, Europe" as an address—yet this mislabeling continues—even in official documents.

**After:**
> The term is primarily promoted by Dutch institutions, not by the people themselves. You don't say "Netherlands, Europe" as an address, yet this mislabeling continues in official documents.


### 15. Overuse of Boldface

**Problem:** AI chatbots emphasize phrases in boldface mechanically.

**Before:**
> It blends **OKRs (Objectives and Key Results)**, **KPIs (Key Performance Indicators)**, and visual strategy tools such as the **Business Model Canvas (BMC)** and **Balanced Scorecard (BSC)**.

**After:**
> It blends OKRs, KPIs, and visual strategy tools like the Business Model Canvas and Balanced Scorecard.


### 16. Inline-Header Vertical Lists

**Problem:** AI outputs lists where items start with bolded headers followed by colons.

**Before:**
> - **User Experience:** The user experience has been significantly improved with a new interface.
> - **Performance:** Performance has been enhanced through optimized algorithms.
> - **Security:** Security has been strengthened with end-to-end encryption.

**After:**
> The update improves the interface, speeds up load times through optimized algorithms, and adds end-to-end encryption.


### 17. Title Case in Headings

**Problem:** AI chatbots capitalize all main words in headings.

**Before:**
> ## Strategic Negotiations And Global Partnerships

**After:**
> ## Strategic negotiations and global partnerships


### 18. Emojis

**Problem:** AI chatbots often decorate headings or bullet points with emojis.

**Before:**
> 🚀 **Launch Phase:** The product launches in Q3
> 💡 **Key Insight:** Users prefer simplicity
> ✅ **Next Steps:** Schedule follow-up meeting

**After:**
> The product launches in Q3. User research showed a preference for simplicity. Next step: schedule a follow-up meeting.


### 19. Curly Quotation Marks

**Problem:** ChatGPT uses curly quotes ("...") instead of straight quotes ("...").

**Before:**
> He said "the project is on track" but others disagreed.

**After:**
> He said "the project is on track" but others disagreed.


## COMMUNICATION PATTERNS

### 20. Collaborative Communication Artifacts

**Words to watch:** I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like..., let me know, here is a...

**Problem:** Text meant as chatbot correspondence gets pasted as content.

**Before:**
> Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand on any section.

**After:**
> The French Revolution began in 1789 when financial crisis and food shortages led to widespread unrest.


### 21. Knowledge-Cutoff Disclaimers

**Words to watch:** as of [date], Up to my last training update, While specific details are limited/scarce..., based on available information...

**Problem:** AI disclaimers about incomplete information get left in text.

**Before:**
> While specific details about the company's founding are not extensively documented in readily available sources, it appears to have been established sometime in the 1990s.

**After:**
> The company was founded in 1994, according to its registration documents.


### 22. Sycophantic/Servile Tone

**Problem:** Overly positive, people-pleasing language.

**Before:**
> Great question! You're absolutely right that this is a complex topic. That's an excellent point about the economic factors.

**After:**
> The economic factors you mentioned are relevant here.


## STYLE, RHYTHM, AND RHETORIC PATTERNS

### 30. Forced Metaphors and Figurative Overwriting

**Signs to watch:** original but strained metaphors, mixed metaphors, figurative substitutions where a plain word is clearer, a metaphor that gets explained right after it is used

**Problem:** Beyond the stock figurative words flagged in patterns 4 and 7, LLMs invent decorative metaphors that add imagery without adding meaning, then often explain them. Plain description is usually clearer and more honest. If the metaphor does not earn its place, cut it and say the literal thing.

**Before:**
> The codebase is a garden we must tend, pruning dead branches and planting seeds of innovation so the whole ecosystem can flourish. In other words, delete unused code and add features.

**After:**
> Delete unused code and add the features users are asking for.


### 31. Dramatic Fragmentation and Punchy Kickers

**Signs to watch:** two- or three-word subjectless sentences used for drama, staccato "X. And Y. And Z." runs, a short quotable line ending every paragraph or section, cutesy appositive fragments ("the catalog, honestly priced")

**Problem:** LLMs chop sentences into fragments for false emphasis and end sections with a quotable "mic-drop" line. It reads like ad copy or a motivational poster. If a line sounds like it belongs on a poster, cut it or fold it back into a real sentence with a subject. This is distinct from pattern 13 (which is about grammatical passive voice); here the tell is rhythm and showmanship, not a hidden actor.

**Before:**
> The catalog, honestly priced. Pay for what it does. Not promises. It just works. Every time.

**After:**
> The catalog is priced by usage, so you pay for the calls you actually make rather than a flat monthly fee.


### 32. Rhetorical Questions Answered Immediately

**Signs to watch:** "What if...?", "The question is...", "Ever wondered...?", a question immediately followed by its own answer, "Think about it."

**Problem:** LLMs pose a question only to answer it a beat later. The question adds no information and stalls the sentence. State the point directly.

**Before:**
> What makes an API good? It comes down to predictability. Think about it: developers want to know exactly what they will get back.

**After:**
> A good API is predictable, so developers know exactly what they will get back.


### 33. Sentence-Opener Tics

**Words to watch:** So..., Look,, habitual sentence-initial And/But, "I think"/"I believe" when stating a fact, adverb openers (Interestingly, Importantly, Notably, Crucially, Essentially, Ultimately)

**Problem:** LLMs lean on a small set of openers. Adverb openers tell the reader how to feel instead of earning it, and "So" or "Look" fake conversational warmth. Drop the opener and start with the substance.

**Before:**
> So, the results were mixed. Interestingly, adoption went up. Importantly, churn went up too. I think that means the feature still needs work.

**After:**
> The results were mixed: adoption rose, but churn rose alongside it, so the feature still needs work.


### 34. Reassurance Kickers

**Signs to watch:** And that's okay., And that's fine., There's nothing wrong with that., no shame in..., you're not alone, it's completely normal

**Problem:** LLMs tack on reassurance the reader never asked for. It softens the writing and assumes the reader needs comforting. Trust the reader: make the point and stop.

**Before:**
> You might not have a testing setup yet. And that's okay. Plenty of teams start without one, and there's nothing wrong with that.

**After:**
> Many teams start without a testing setup and add one once regressions begin costing real time.

---

