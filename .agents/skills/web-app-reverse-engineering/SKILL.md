---
name: web-app-reverse-engineering
description: Use when asked how a web app works or predicts.
---

# Web App Reverse Engineering

Answer "how does this site/app work (predict/score/rank)" by reading the code it ships, not by clicking through the UI.

## Procedure

1. **Fetch raw HTML first.** `curl -sS -A "<real browser UA>" <url> -o index.html`. Most modern sites (Astro, Next, SvelteKit, Remix) are SSR — the HTML already contains the app shell and every JS bundle reference. If the HTML is an empty root div, the app is client-rendered: render once with a browser (browser_exec or crawl4ai) to collect bundle URLs, then go back to curl.
2. **Collect bundle URLs.** `grep -oE 'src="[^"]*\.js[^"]*"' index.html | sort -u`. Download each with curl.
3. **Map the code before reading.** Grep domain keywords and rank by frequency: `grep -oiE '(predict|seed|hash|random|shuffle|score|draw|fortune)[a-zA-Z_]*' bundle.js | sort | uniq -c | sort -rn`. This tells you which subsystems exist before you read anything.
4. **Extract function bodies with character-offset context windows.** Minified bundles are one line — line-based grep is useless. Use Python:
   ```python
   import re
   js = open('bundle.js', encoding='utf-8', errors='replace').read()
   def show(term, before=50, after=1200, n=1):
       for i, m in enumerate(re.finditer(term, js)):
           if i >= n: break
           print(js[max(0, m.start()-before):m.end()+after])
   show(r'function fe\(', 30, 400)
   ```
5. **Trace the pipeline end-to-end:** RNG → shuffle → selection → text/scoring → API calls. Find every `fetch('/api/...')` to mark the client/server boundary — anything behind those endpoints is server-side and not inspectable from the bundle.
6. **Report the predictability split.** For "how does it predict" questions the answer has three buckets: genuinely random (CSPRNG, user choice), deterministic (hashes, templates, per-day keys — reproducible offline), and server-side (API/LLM). Name which is which.
7. **For "what does it write / how does it interpret" questions, fetch /terms (and /privacy, /about).** The generation mechanism (AI/LLM vs static templates) and its inputs (card meanings + position, etc.) are usually disclosed there — that disclosure is the core of the answer. Pair it with one representative content page (e.g. a single card's page) to document the exact output structure.

## Pitfalls

- Don't burn retries on crawl4ai wait conditions: `wait_for="networkidle"` times out on apps that keep polling, and even `domcontentloaded` can time out in its proxy layer. The working escape hatch is `wait_until="commit"` + `delay_before_return_html=N` (seconds for client JS to settle) — it crawls pages that hang on late resources. If the page is SSR, curl + static bundles is still all you need and far faster.
- crawl4ai 0.9.x `CrawlerRunConfig` has no `wait_for_delay` — the wait knobs are `wait_until`, `wait_for`, `wait_for_timeout`, `delay_before_return_html`. When a parameter name is rejected, check `inspect.signature(CrawlerRunConfig.__init__)` instead of guessing.
- crawl4ai 0.9.x extracted text mangles Thai (drops vowels, shifts tone marks) — for Thai pages treat raw HTML (crawl4ai `result.html` or a curl fetch) as the source of truth for wording, and use the markdown only for structure and links. Working Thai text extraction: `curl -sL <url> | python -c` with `re.sub` stripping `<script>/<style>`, tags replaced by newlines, then `html.unescape` — preserves Thai text exactly and is fast enough to skip the browser entirely on SSR pages.
- Check `pip show crawl4ai` Location before running scripts — on this machine it lives in the Boom project venv (`E:\Boom Project\.venv`; install with `pip install crawl4ai` then `python -m playwright install chromium`) and the Hermes venv; use the matching interpreter. The execute_code kernel uses Hermes venv, not project venv, so import errors for crawl4ai occur there.
- Minified code mangles function names to 2-3 chars. Anchor on string literals, API paths, and regex patterns — those survive minification — and follow references outward from them.
- Seasonal/feature flags are usually plain date-string pairs (`from`/`until`) or a `seasonal` marker in the bundle; grep for those to find which mode is currently active.
- Deterministic outputs often hide in hash-of-(id|key) % length picks and per-day key strings (`date|spread|category|question` joined) — those are the parts a user can actually reproduce or predict; say so explicitly.
- Next.js apps expose all client code under `/_next/static/immutable/chunks/*.js`. Collect bundle URLs from the initial HTML with `script src` grep, dedupe, then download with aiohttp/ curl. The computation logic is in those chunks, not in inline scripts except theme bootstraps.
- Thai astrology bundles embed domain keywords and base labels as string arrays. Search for Thai base names `อัตตะ|หินะ|ธนัง|ปิตา|มาตา|โภคา|มัชฌิมา|ตนุ|กดุมพะ|สหัชชะ|พันธุ|ปุตตะ|อริ|ปัตนิ|มรณะ|ศุภะ|กัมมะ|ลาภะ|พยายะ|ทาสา|ทาสี` to locate the mapping tables and rule sets quickly. Use offset context windows rather than line grep because bundles are minified single-line files.
- Astro sites ship server-rendered HTML with client bundles under `/_astro/*.js`. Entry scripts are named like `/_astro/Base.astro_astro_type_script_index_0_lang.<hash>.js` and `/_astro/index.astro_astro_type_script_index_0_lang.<hash>.js`; they import site-specific bundles e.g. `/_astro/site.<hash>.js` and `/_astro/chinese.<hash>.js`. Collect `script src` from the initial HTML with curl first — browser_exec often times out on these pages, while the SSR HTML already contains all bundle URLs.
- For Thai content sites built with Astro, calculation logic is typically server-side; client bundles only handle navigation, today-sync fetches, and small interactive checks. If the bundle only contains lookup tables for branches/elements/colors and relation functions, the heavy lunisolar conversion is server-rendered, not inspectable in JS.
- When reverse-engineering a Thai Chinese almanac site such as tarot.loveiseveryday.com/chinese-calendar, the client bundles contain only static lookup tables for Heavenly Stems/Earthly Branches, Wu Xing colors, and clash/relation functions. The lunisolar conversion and do/don't lists are server-rendered. Reproduce the client logic with: branch resolver `d(e)=t[((e-4)%12+12)%12]`, relation function `l(e,n)` returning self/clash/punish/harm/break, and color tables per element. Use curl to fetch HTML, grep `src="/_astro/.*\.js"`, download each bundle, and show context windows around string literals for Thai branch names.
