# Axis 1: Timbre Verbal Description — Paper Survey

> How humans describe timbre/sound-color in words: semantics, perceptual spaces, cross-modal metaphor.
> Compiled 2026-03-31 for the sunolanguage project.

---

### [1] Multidimensional Perceptual Scaling of Musical Timbres
- **Authors**: John M. Grey
- **Year**: 1977
- **Venue**: Journal of the Acoustical Society of America, 61(5), 1270-1277
- **Key Contribution**: Foundational study applying multidimensional scaling (MDS) to timbre. Using 16 synthesized instrument tones equalized for pitch, loudness, and duration, Grey identified a 3D perceptual timbre space: (1) spectral energy distribution, (2) synchronicity of harmonic transients / spectral fluctuation, (3) presence of high-frequency energy in the attack. Established MDS as the dominant method for timbre research.
- **Relevance to sunolanguage**: Grey's three axes are the ancestor of modern timbre-space models. Suno's prompt vocabulary (e.g., "bright", "warm", "punchy") implicitly maps onto descendants of these dimensions. Understanding which acoustic axes listeners actually use helps us predict which Suno keywords will be most effective.
- **Tags**: [timbre] [MDS] [perceptual-space] [foundational]

### [2] Perceptual Scaling of Synthesized Musical Timbres: Common Dimensions, Specificities, and Latent Subject Classes
- **Authors**: Stephen McAdams, Suzanne Winsberg, Sophie Donnadieu, Geert De Soete, Jochen Krimphoff
- **Year**: 1995
- **Venue**: Psychological Research, 58, 177-192
- **Key Contribution**: Extended Grey's MDS approach using the CLASCAL algorithm, which models common perceptual dimensions, instrument-specific "specificities" (unique attributes not captured by shared dimensions), and latent listener classes. Demonstrated that timbres possess idiosyncratic qualities beyond shared perceptual axes and that listener sub-populations weight dimensions differently.
- **Relevance to sunolanguage**: The concept of "specificities" is critical for sunolanguage — some Suno keywords may trigger instrument-specific qualities that fall outside general semantic dimensions (e.g., "Rhodes" triggers electric piano character not reducible to bright/warm). Latent listener classes also warn us that vocabulary effectiveness may differ across user populations.
- **Tags**: [timbre] [MDS] [CLASCAL] [listener-classes] [perceptual-space]

### [3] Acoustic Correlates of Timbre Space Dimensions: A Confirmatory Study Using Synthetic Tones
- **Authors**: Anne Caclin, Stephen McAdams, Bennett K. Smith, Suzanne Winsberg
- **Year**: 2005
- **Venue**: Journal of the Acoustical Society of America, 118(1), 471-482
- **Key Contribution**: Confirmatory study directly testing the perceptual relevance of four acoustic parameters: attack time, spectral centroid, spectral flux, and spectrum fine structure (even/odd harmonic ratio). Attack time, spectral centroid, and spectrum fine structure were robustly confirmed as timbre-space dimensions; spectral flux was less salient and context-dependent.
- **Relevance to sunolanguage**: Provides the acoustic-to-perceptual bridge. When Suno users say "bright," the underlying acoustic correlate is spectral centroid; "punchy" maps to attack time. This paper validates exactly which acoustic features anchor verbal descriptions, enabling us to build a grounded vocabulary-to-acoustics mapping.
- **Tags**: [timbre] [acoustic-correlates] [spectral-centroid] [attack-time] [confirmatory]

### [4] Exploring Perceptual and Acoustical Correlates of Polyphonic Timbre
- **Authors**: Vinoo Alluri, Petri Toiviainen
- **Year**: 2010
- **Venue**: Music Perception, 27(3), 223-242
- **Key Contribution**: Extended timbre semantics from isolated tones to polyphonic music (Indian popular music excerpts). Factor analysis of listener ratings revealed three perceptual dimensions — Activity, Brightness, and Fullness — which could be predicted from computationally extracted acoustic features. Demonstrated that semantic differential methods scale to real music, not just isolated tones.
- **Relevance to sunolanguage**: Suno generates polyphonic music, not isolated tones. This study validates that semantic timbre description applies to full mixes and that dimensions like "Activity" and "Fullness" are meaningful for complete tracks — directly relevant vocabulary for Suno prompts.
- **Tags**: [timbre] [polyphonic] [semantic-differential] [acoustic-features] [real-music]

### [5] The Timbre Toolbox: Extracting Audio Descriptors from Musical Signals
- **Authors**: Geoffroy Peeters, Bruno L. Giordano, Patrick Susini, Nicolas Misdariis, Stephen McAdams
- **Year**: 2011
- **Venue**: Journal of the Acoustical Society of America, 130(5), 2902-2916
- **Key Contribution**: Introduced a comprehensive MATLAB toolbox computing a large set of audio descriptors organized into temporal, spectral, spectrotemporal, and energetic categories. Factor analysis of descriptors revealed ~10 independent classes. Became a standard reference tool for timbre research and MIR.
- **Relevance to sunolanguage**: The Timbre Toolbox's descriptor taxonomy (spectral, temporal, spectrotemporal) directly aligns with the TOR 3-axis framework we already use. Its descriptor set provides candidate acoustic features for grounding Suno vocabulary terms in measurable signal properties.
- **Tags**: [timbre] [audio-descriptors] [toolbox] [spectral] [temporal] [MIR]

### [6] An Interlanguage Study of Musical Timbre Semantic Dimensions and Their Acoustic Correlates
- **Authors**: Asterios Zacharakis, Konstantinos Pastiadis, Joshua D. Reiss
- **Year**: 2014
- **Venue**: Music Perception, 31(4), 339-358 (earlier version); consolidated in 2015, Music Perception, 32(4), 394-417
- **Key Contribution**: Cross-linguistic study (Greek and English speakers) rating 23 instrument tones on 30 adjectives. Identified three universal semantic dimensions: Luminance (brilliant/sharp vs. deep), Texture (soft/warm vs. rough/harsh), and Mass (dense/rich/full vs. light). Showed these dimensions are language-independent and correlate strongly with perceptual dissimilarity spaces.
- **Relevance to sunolanguage**: The Luminance-Texture-Mass (LTM) model is the most actionable semantic framework for sunolanguage. It provides a compact, cross-linguistically validated vocabulary that we can map to Suno prompt terms. The fact that these dimensions are language-independent supports building a universal Suno vocabulary.
- **Tags**: [timbre] [semantics] [cross-linguistic] [luminance-texture-mass] [adjectives]

### [7] Saitis & Weinzierl — The Semantics of Timbre
- **Authors**: Charalampos Saitis, Stefan Weinzierl
- **Year**: 2019
- **Venue**: Chapter 5 in *Timbre: Acoustics, Perception, and Cognition* (Siedenburg, Saitis, McAdams, Popper, Fay, Eds.), Springer SHAR vol. 69, pp. 119-149
- **Key Contribution**: Comprehensive review chapter synthesizing decades of timbre semantics research. Catalogues how humans use cross-modal metaphors (bright, warm, sweet), onomatopoeia (buzzing, shrill), and abstract terms (rich, complex, harsh) to describe timbre. Reviews semantic differential methodology, factor-analytic results, and the acoustic grounding of verbal labels.
- **Relevance to sunolanguage**: The definitive overview connecting verbal timbre description to perception and acoustics. Its taxonomy of descriptor types (cross-modal, onomatopoeic, abstract) directly informs how we categorize Suno prompt vocabulary.
- **Tags**: [timbre] [semantics] [review] [cross-modal] [methodology]

### [8] Semantic Crosstalk in Timbre Perception
- **Authors**: Zachary Wallmark
- **Year**: 2019
- **Venue**: Music & Science, 2, 1-18
- **Key Contribution**: Used Stroop-type experiments to demonstrate that cross-modal semantic associations with timbre (e.g., "bright," "smooth") are at least partially automatic, not just deliberate metaphors. Found bidirectional interference between written adjectives and perceived timbral qualities, suggesting deep cognitive links between language and timbre processing. Corpus analysis of orchestration treatises showed ~20% of timbre descriptors are cross-modal metaphors.
- **Relevance to sunolanguage**: Demonstrates that timbre-language associations are cognitively robust, not arbitrary. This validates the premise that a systematic Suno vocabulary can reliably evoke timbral qualities — the mappings are grounded in human cognition, not just convention.
- **Tags**: [timbre] [cross-modal] [Stroop] [cognition] [metaphor]

### [9] Timbre: Acoustics, Perception, and Cognition (Edited Volume)
- **Authors**: Kai Siedenburg, Charalampos Saitis, Stephen McAdams, Arthur N. Popper, Richard R. Fay (Eds.)
- **Year**: 2019
- **Venue**: Springer Handbook of Auditory Research, vol. 69
- **Key Contribution**: First comprehensive modern volume on timbre research, covering perceptual/cognitive processes, timbre in voice perception, music, cochlear implants, sound design, and computational modeling. Establishes timbre research as a mature interdisciplinary field with convergent methods.
- **Relevance to sunolanguage**: The reference volume for the entire field. Chapters on semantics (Saitis & Weinzierl), perceptual representation (McAdams), and audio content descriptors provide the theoretical backbone for grounding sunolanguage's vocabulary mapping.
- **Tags**: [timbre] [handbook] [comprehensive] [reference]

### [10] Verbal Expression of Piano Timbre: Multidimensional Semantic Space of Adjectival Descriptors
- **Authors**: Asterios Zacharakis, Konstantinos Pastiadis
- **Year**: 2013 (conference presentation) / referenced in Zacharakis et al. 2014-2015
- **Venue**: Presented at Stockholm Music Acoustics Conference (SMAC) 2013; related findings in the 2014/2015 Music Perception papers
- **Key Contribution**: Focused specifically on piano timbre verbal description, proposing five adjectives to best represent a semantic space for piano timbre: bright, dry, dark, round, and velvety (based on two principal dimensions capturing 78% of variance). Demonstrated that even within a single instrument, semantic differential methods yield consistent, low-dimensional descriptor spaces.
- **Relevance to sunolanguage**: Piano is among Suno's most commonly prompted instruments. Knowing that piano timbre semantics reduces to ~5 core adjectives helps us build a compact, effective prompt vocabulary for piano-related Suno generations.
- **Tags**: [timbre] [semantics] [piano] [adjectives] [instrument-specific]
