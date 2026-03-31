# Axis 1 Synthesis: Timbre Verbal Description

> How the academic literature on timbre semantics informs the sunolanguage project.
> 2026-03-31

---

## State of the Field

Research on how humans describe timbre in words spans nearly five decades, from Grey's (1977) foundational multidimensional scaling work to Siedenburg et al.'s (2019) comprehensive handbook. The field has converged on a mature methodology: listeners rate sounds on semantic differential scales (adjective pairs like "bright-dull" or "warm-cold"), factor analysis reduces these ratings to a small number of dimensions, and regression links those dimensions to measurable acoustic features. The result is a growing consensus that timbre perception — despite its notorious complexity — can be captured by a compact set of verbal-perceptual-acoustic correspondences.

## Key Findings Relevant to sunolanguage

**Three to five dimensions suffice.** Across multiple studies and languages, timbre semantics consistently reduces to 3-5 principal dimensions. Zacharakis et al.'s Luminance-Texture-Mass (LTM) model is the most robust: Luminance (brilliant vs. deep) maps to spectral centroid, Texture (smooth/warm vs. rough/harsh) maps to harmonic energy distribution, and Mass (dense/full vs. light) relates to spectral spread and inharmonicity. These dimensions are language-independent (Greek and English speakers produce nearly identical spaces), suggesting a universal perceptual basis.

**Verbal descriptions carry real perceptual information.** Zacharakis et al. (2015) demonstrated substantial overlap between semantic spaces (built from adjective ratings) and perceptual spaces (built from dissimilarity judgments). This means that words genuinely encode timbre distinctions — they are not vague metaphors but reliable carriers of acoustic-perceptual content.

**Cross-modal metaphors are cognitively grounded.** Wallmark (2019) showed via Stroop-type interference that associations like "bright timbre" are at least partially automatic, not just conventional labels. Saitis & Weinzierl (2019) catalogued three descriptor types: cross-modal (bright, warm), onomatopoeic (buzzing, shrill), and abstract (rich, complex). All three types appear in Suno prompts.

**Polyphonic timbre is also describable.** Alluri & Toiviainen (2010) extended semantic methods from isolated tones to full musical mixtures, finding dimensions of Activity, Brightness, and Fullness. This is directly relevant because Suno generates complete tracks, not isolated instruments.

## Connection to the TOR Framework

The TOR (Timbre and Orchestration Resource) framework organizes timbre descriptors along Spectral, Temporal, and Spectrotemporal axes. The literature maps onto this cleanly:

- **Spectral axis**: Luminance/Brightness corresponds to spectral centroid; spectrum fine structure (even/odd ratio) contributes to Texture. Peeters et al.'s (2011) Timbre Toolbox provides the computational descriptors.
- **Temporal axis**: Attack time is the most consistent temporal correlate across all studies (Grey 1977, Caclin et al. 2005). It anchors descriptors like "punchy," "soft," "percussive."
- **Spectrotemporal axis**: Spectral flux and harmonic synchronicity (Grey's Axis II) capture how the spectrum evolves over time — relevant to descriptors like "evolving," "static," "shimmering."

The LTM model adds a semantic layer on top of TOR's acoustic layer, bridging what listeners say and what the signal contains.

## Gaps That sunolanguage Fills

The existing literature has three limitations that sunolanguage directly addresses:

1. **Human-to-human focus.** All studies examine how humans describe timbre to other humans. No work systematically maps how an AI music engine interprets verbal timbre descriptors. sunolanguage bridges this gap by testing which words actually shift Suno's output along perceptual dimensions.

2. **Isolated or classical stimuli.** Most studies use synthesized instrument tones or classical music. Suno generates pop, electronic, hip-hop, and genre-blended music where timbre vocabulary includes production terms ("lo-fi," "crispy," "saturated") absent from academic corpora. sunolanguage extends the descriptor space to cover AI-native musical production.

3. **Descriptive, not generative.** Academic timbre semantics describes existing sounds. sunolanguage inverts the direction: given a verbal descriptor, what sound does the engine produce? This generative mapping — from word to sound rather than sound to word — is unexplored territory that sunolanguage is uniquely positioned to chart.

---

*Next step*: Cross-reference these semantic dimensions with Suno prompt vocabulary collected in `sunolang.db` to identify which academic descriptors have direct Suno equivalents and which production-domain terms lack academic grounding.
