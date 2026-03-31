# Deep Dive: Axis 1 (Timbre) & Axis 2 (Text-to-Music)

> Phase 2 literature survey for sunolanguage project
> Compiled: 2026-03-31
> Total new papers: 17 (8 Axis 1, 9 Axis 2)

---

## Axis 1: New Findings (Timbre Verbal Description)

### [1] Deng, Pardo & Pappas — Do Joint Language-Audio Embeddings Encode Perceptual Timbre Semantics? (2025)

- **Authors**: Qixin Deng, Bryan Pardo, Thrasyvoulos N. Pappas
- **Year**: 2025
- **Venue**: arXiv:2510.14249 (cs.SD)
- **Key Contribution**: First systematic evaluation of whether multimodal embedding models (MS-CLAP, LAION-CLAP, MuQ-MuLan) actually capture human-perceived timbre semantics like brightness, roughness, and warmth. Used the CCMusic-Database-Instrument-Timbre dataset with 37 Chinese and 24 Western instruments rated on 16 descriptors by musically trained listeners.
- **Key Finding**: LAION-CLAP consistently provides the most reliable alignment with human-perceived timbre semantics across both instrumental sounds and audio effects.
- **Why it matters for sunolanguage**: Directly validates our core thesis — that language-audio embedding spaces DO encode perceptual timbre semantics, meaning Suno's internal text encoder likely maps timbre words to meaningful acoustic regions. Also provides a cross-cultural (Chinese + Western) instrument set, relevant to our multi-language ambitions.

### [2] Reymore & Lindsey — Color and Tone Color: Audiovisual Crossmodal Correspondences with Musical Instrument Timbre (2025)

- **Authors**: Lindsey Reymore, Delwin T. Lindsey
- **Year**: 2025
- **Venue**: Frontiers in Psychology (PMC11747214)
- **Key Contribution**: Two experiments examining color-timbre crossmodal correspondences. Participants rated instrument timbres on 12 semantic scales (bright, dark, warm, cool, high, low, heavy, light, big, small, happy, sad) and matched them to colors. Tested keyboard instruments (piano, harpsichord, lautenwerk) and orchestral instruments (flute, oboe, clarinet, trumpet, violin, viola).
- **Key Finding**: Semantic ratings on bright/dark/warm/cool predicted lightness and saturation of matched colors. Effects were larger when both pitch register and instrument type varied. The warm-cool dimension showed weaker but significant correspondence.
- **Why it matters for sunolanguage**: Confirms that crossmodal descriptors (bright, dark, warm) carry real perceptual weight in timbre description. These are exactly the kinds of words Suno uses in its auto-generated prompts. The semantic scales used (12 terms) could serve as a validation framework for our Suno vocabulary extraction.

### [3] Reymore — Timbre Semantic Associations Vary Both Between and Within Instruments (2023)

- **Authors**: Lindsey Reymore
- **Year**: 2023
- **Venue**: Music Perception, Vol. 40, No. 3, pp. 253+
- **Key Contribution**: 540 participants rated single sustained notes from 8 Western orchestral instruments across 3 registers on 20 semantic scales (from the Reymore & Huron 2020 model). Found that timbre semantic associations vary systematically with register and pitch height — e.g., deep/thick/heavy rated highest in low register, sparkling/brilliant/bright highest in high register.
- **Key Finding**: Timbre semantics are NOT fixed per instrument — they shift with register. The same trumpet can be "bright" in the high register and "warm" in the low register.
- **Why it matters for sunolanguage**: Critical insight for our vocabulary extraction. When Suno describes a sound as "bright," it may be encoding register information, not just instrument identity. Our RAG should track pitch-register context alongside timbre descriptors.

### [4] Reymore & Huron — Characterizing Prototypical Musical Instrument Timbres with Timbre Trait Profiles (2022)

- **Authors**: Lindsey Reymore, David Huron
- **Year**: 2022
- **Venue**: Musicae Scientiae (SAGE)
- **Key Contribution**: Created a 20-dimensional timbre trait model and generated Timbre Trait Profiles for 34 musical instruments common in Western orchestras and wind ensembles. Visualized as radar plots providing timbral-linguistic fingerprints for each instrument.
- **Key Finding**: 243 musician participants rated instruments on 20 semantic dimensions. Produced the most comprehensive mapping of instrument-to-language timbre descriptions available.
- **Why it matters for sunolanguage**: The 20-dimension model and 34-instrument profiles provide a gold-standard reference for comparing against Suno's auto-generated timbre vocabulary. We can check whether Suno's native descriptors align with, or deviate from, these empirically validated trait profiles.

### [5] Venkatesh, Moffat & Miranda — Word Embeddings for Automatic Equalization in Audio Mixing (2022)

- **Authors**: Satvik Venkatesh, David Moffat, Eduardo Reck Miranda
- **Year**: 2022
- **Venue**: Journal of the Audio Engineering Society (JAES), Vol. 70, No. 9, pp. 753-763
- **Key Contribution**: Used pre-trained word embeddings (Tok2Vec) to map semantic audio descriptors (e.g., "warm," "bright," "muddy") to EQ parameter settings. The embedding layer enables a neural network to translate studio vocabulary into concrete DSP parameter adjustments — even for descriptors not seen during training.
- **Key Finding**: Word embeddings can generalize to unseen semantic descriptors. Models with embedding layers outperformed those without (0.76 vs 0.836 error), though still below human-label accuracy.
- **Why it matters for sunolanguage**: Demonstrates that production/studio vocabulary has learnable semantic structure in embedding space. The same principle likely applies to Suno's text encoder — terms like "warm," "punchy," "crisp" occupy meaningful positions in its latent space. Our vocabulary RAG could leverage this for SP optimization.

### [6] Stables, Enderby, De Man, Fazekas & Reiss — SAFE: Semantic Audio Feature Extraction (2014)

- **Authors**: Ryan Stables, Sean Enderby, Brecht De Man, Gyorgy Fazekas, Joshua D. Reiss
- **Year**: 2014
- **Venue**: ISMIR 2014, Taipei
- **Key Contribution**: Built DAW plugins (EQ, compressor, distortion, reverb) that crowdsource semantic descriptors from audio engineers during their actual workflow. Created a database mapping subjective terms to objective audio parameters. Addressed the fundamental problem: there is no standardized transferable semantic vocabulary in music production.
- **Key Finding**: Semantic terms hold varied meanings across genres, production settings, and geographical regions. The system collected thousands of descriptor-parameter pairs from real production sessions.
- **Why it matters for sunolanguage**: Methodological gold mine. SAFE's approach of collecting vocabulary in-situ (during actual production) parallels our approach of collecting Suno's vocabulary in-situ (during actual music recognition). Their finding about vocabulary instability across contexts warns us that Suno's vocabulary may also be context-dependent.

### [7] Zhang, Lin & Chen — Timbre Perception, Representation, and its Neuroscientific Exploration: A Comprehensive Review (2024)

- **Authors**: Hong Zhang, Jie Lin, Shengxuan Chen
- **Year**: 2024
- **Venue**: arXiv:2405.13661
- **Key Contribution**: Comprehensive review covering how musicians verbally describe timbre (relying on emotional/sensory metaphors like "bright red" for trumpet, "deep brown" for cello), machine learning integration for timbre analysis, disentangled representations (separating loudness from timbral features), and perception-based notation systems.
- **Key Finding**: Musicians lack explicit vocabulary for timbre and rely heavily on synesthetic metaphors. ML-based approaches using joint embeddings or deep style features show that nuanced, multi-level, context-sensitive representations are needed — simple one-adjective-one-feature mappings fail.
- **Why it matters for sunolanguage**: Reinforces that timbre vocabulary is inherently metaphorical and context-sensitive. Suno's auto-generated prompts likely use similar metaphorical vocabulary. Our analysis should categorize Suno descriptors into: literal (e.g., "guitar"), metaphorical-sensory (e.g., "warm"), metaphorical-emotional (e.g., "melancholic"), and technical (e.g., "reverb-heavy").

### [8] Yuan, Khan & Golkov — Generation of Musical Timbres using a Text-Guided Diffusion Model (2025)

- **Authors**: Weixuan Yuan, Qadeer Khan, Vladimir Golkov
- **Year**: 2025
- **Venue**: arXiv:2504.09219
- **Key Contribution**: Text-guided synthesis of individual musical note timbres (not full songs) using latent diffusion + CLIP-style contrastive learning. Generates magnitude and phase simultaneously, eliminating the need for phase retrieval. Designed for DAW/electronic instrument integration.
- **Key Finding**: Natural language descriptions can effectively control timbral properties at the single-note level, bridging text prompts to fine-grained acoustic characteristics.
- **Why it matters for sunolanguage**: Shows text-to-timbre mapping is feasible at granular level. If text descriptions can generate specific timbres, then Suno's recognition prompts should reversibly encode timbral information. Validates our approach of extracting timbre vocabulary from Suno's auto-descriptions.

---

## Axis 2: New Findings (Text-to-Music AI)

### [9] Casini, Cros Vila, Dalmazzo, Kaila & Sturm — Data-Driven Analysis of Text-Conditioned AI-Generated Music: A Case Study with Suno and Udio (2025)

- **Authors**: Luca Casini, Laura Cros Vila, David Dalmazzo, Anna-Kaisa Kaila, Bob L.T. Sturm
- **Year**: 2025
- **Venue**: arXiv:2509.11824 / submitted to TISMIR
- **Key Contribution**: Analyzed 100,000+ songs generated by Suno and Udio users (May-October 2024). Used text embedding models, dimensionality reduction, and clustering to analyze prompts, tags, and lyrics. Identified 26 macro-categories in lyrics and mapped prompt vocabulary patterns.
- **Key Findings**:
  - Two primary prompting strategies: comma-separated qualifiers ("modern country, introspective, melodic") and narrative descriptions ("A jazz ballad with trumpet...")
  - Structural metatags in square brackets: [Verse] (88,270x), [Chorus] (65,342x), [Bridge] (22,491x), [Guitar solo], [Instrumental intro]
  - Advanced metatags for chord progressions, duration, dynamics, tempo — but long metatag sequences tend to get ignored
  - 80.7% of unique tags appeared only once — vast long tail of experimental vocabulary
  - Core vocabulary dominated by established genres + standard musical descriptors
  - Voice specifications (male/female) formed distinct compact clusters
- **Why it matters for sunolanguage**: THE most directly relevant paper for our project. Provides a large-scale empirical map of what vocabulary Suno users actually employ and what the model responds to. Our approach is complementary — they study user input vocabulary, we study Suno's output vocabulary when it describes music. Combining both perspectives gives a complete picture of Suno's "native language."

### [10] Grotschla, Solak, Lanzendorfer & Wattenhofer — Benchmarking Music Generation Models and Metrics via Human Preference Studies (2025)

- **Authors**: Florian Grotschla, Ahmet Solak, Luca A. Lanzendorfer, Roger Wattenhofer
- **Year**: 2025
- **Venue**: ICASSP 2025
- **Key Contribution**: Generated 6,000 songs using 12 state-of-the-art models, conducted 15,600 pairwise comparisons with 2,500+ human participants. First large-scale human-preference benchmark for music generation.
- **Key Finding**: Commercial models (particularly Suno v3.5) achieved highest human preference for both music quality AND text-audio alignment, surpassing even reference datasets. For metrics: FAD with CLAP-MA embeddings best correlates with quality; LAION-CLAP models best correlate with text-audio alignment.
- **Why it matters for sunolanguage**: Confirms Suno's SOTA status in text-audio alignment — meaning Suno's text encoder is genuinely effective at mapping vocabulary to music. Also identifies which embedding models best capture human perception of text-music correspondence, informing our choice of evaluation tools.

### [11] Wang et al. — Generative Music Models' Alignment with Professional and Amateur Users' Expectations (2025)

- **Authors**: Zihao Wang, Jiaxing Yu, Haoxuan Liu, Zehui Zheng, Yuhang Jin, Shuyu Li, Shulei Ji, Kejun Zhang
- **Year**: 2025
- **Venue**: ACL 2025 Findings, pp. 6909-6920
- **Key Contribution**: Introduced the task of Professional and Amateur Description-to-Song Generation. Used the MuChin dataset (Chinese music annotations from both professionals and amateurs). Pre-trained on 1.5M+ songs. Proposed MuDiT/MuSiT framework for better human-machine alignment.
- **Key Finding**: Professionals and amateurs describe music differently, and models need to accommodate both description styles. MuDiT/MuSiT outperforms baselines in alignment with both user types.
- **Why it matters for sunolanguage**: Highlights that music description vocabulary differs by expertise level. Suno's auto-generated descriptions represent a third perspective — the machine's own vocabulary. Understanding how this "AI native" vocabulary relates to both professional and amateur human descriptions is central to sunolanguage.

### [12] Wang et al. — MuChin: A Chinese Colloquial Description Benchmark for Evaluating Language Models in the Field of Music (2024)

- **Authors**: Zihao Wang et al.
- **Year**: 2024
- **Venue**: IJCAI 2024
- **Key Contribution**: First open-source Chinese-language music description benchmark. Built the CaiMAP annotation platform with multi-person, multi-stage quality assurance. Contains professional and amateur annotations for 6,066 songs (1,000 high-quality test set).
- **Key Finding**: Significant discrepancies exist between professional and amateur music descriptions in Chinese. The colloquial/everyday language people use to describe music diverges substantially from technical vocabulary.
- **Why it matters for sunolanguage**: Cross-cultural validation that music description vocabulary varies by language and expertise. When we expand sunolanguage beyond English prompts, this dataset provides a reference for Chinese music description patterns. Also methodologically relevant — their multi-annotator platform design could inform our data collection.

### [13] Melechovsky et al. — Mustango: Toward Controllable Text-to-Music Generation (2024)

- **Authors**: Jan Melechovsky, Zixun Guo, Deepanway Ghosal, Navonil Majumder, Dorien Herremans, Soujanya Poria
- **Year**: 2024
- **Venue**: NAACL 2024
- **Key Contribution**: Music-domain-knowledge-informed text-to-music system. Core innovation: MuNet, a UNet guidance module that extracts music-specific conditions (chords, beats, tempo, key) from text prompts and injects them during diffusion. Created MusicBench dataset (52K+ instances) with music-theory-based captions via data augmentation.
- **Key Finding**: Knowledge-aware prompts with specific music-theory terms (chord names, time signatures, key signatures) produce significantly more controllable output than generic descriptive prompts. Greatly outperforms MusicGen and AudioLDM2 in controllability.
- **Why it matters for sunolanguage**: Demonstrates that music-theory vocabulary is a distinct "channel" of control beyond general descriptors. If Suno similarly encodes music-theory terms, our vocabulary RAG should distinguish between: (1) descriptive vocabulary (genre, mood) and (2) technical vocabulary (chords, tempo, key) as separate control dimensions.

### [14] Sienkiewicz, Neumann & Modrzejewski — ConceptCaps: A Distilled Concept Dataset for Interpretability in Music Models (2026)

- **Authors**: Bruno Sienkiewicz, Lukasz Neumann, Mateusz Modrzejewski
- **Year**: 2026
- **Venue**: arXiv:2601.14157
- **Key Contribution**: Created a 200-attribute taxonomy for musical concepts and generated 23,815 music-caption-audio triplets using a pipeline: VAE learns attribute co-occurrence patterns -> LLM converts attribute lists to professional descriptions -> MusicGen synthesizes audio. Enables concept-based interpretability via TCAV (Testing with Concept Activation Vectors).
- **Key Finding**: By separating semantic modeling from text generation, the approach achieves higher coherence and controllability than end-to-end methods. Provides clean positive/negative examples for probing what music models actually "understand."
- **Why it matters for sunolanguage**: The 200-attribute taxonomy is directly comparable to the vocabulary we're extracting from Suno. Their approach of using TCAV to probe model understanding is a methodology we could adapt — instead of generating synthetic data, we use Suno's own recognition output as "ground truth" concept labels.

### [15] Singh, Cherep & Maes — Discovering and Steering Interpretable Concepts in Large Generative Music Models (2025)

- **Authors**: Nikhil Singh, Manuel Cherep, Pattie Maes
- **Year**: 2025
- **Venue**: arXiv:2505.18186 (accepted to ICLR 2026)
- **Key Contribution**: Applied sparse autoencoders to the residual stream of transformer-based music generators (MusicGen-Large). Discovered both familiar musical concepts AND "coherent but uncodified patterns lacking clear counterparts in theory or language." These concepts can be used to steer generation.
- **Key Finding**: Music generation models contain interpretable concepts that go beyond what language can currently describe — some patterns are real and consistent but have no established vocabulary.
- **Why it matters for sunolanguage**: Profound implication — there may be a vocabulary gap. Suno may "understand" musical patterns that human language hasn't named yet. Our project could potentially identify these gaps by finding cases where Suno's recognition produces unusual or compound descriptors that don't match standard terminology.

### [16] Roy, Liu, Lu & Herremans — JamendoMaxCaps: A Large Scale Music-caption Dataset with Imputed Metadata (2025)

- **Authors**: Abhinaba Roy, Renhang Liu, Tongyu Lu, Dorien Herremans
- **Year**: 2025
- **Venue**: arXiv:2502.07461
- **Key Contribution**: 362,000 freely-licensed instrumental tracks from Jamendo, captioned using Qwen2-Audio with imputed metadata via retrieval-based similarity matching and local LLM. Massive expansion over MusicCaps (5,521 clips).
- **Key Finding**: Large-scale captioning with metadata imputation produces usable training data for music-language understanding tasks.
- **Why it matters for sunolanguage**: Scale reference point — our Suno recognition data is complementary to JamendoMaxCaps. They use AI captioning on real music (like us), but with a general-purpose model. We use Suno's own recognition, which reveals what Suno-specifically understands. Both datasets serve the music-language alignment problem from different angles.

### [17] Ronchini, Comanducci, Marcucci & Antonacci — AI-Assisted Music Production: A User Study on Text-to-Music Models (2025)

- **Authors**: Francesca Ronchini, Luca Comanducci, Simone Marcucci, Fabio Antonacci
- **Year**: 2025
- **Venue**: CMMR 2025 (Computer Music Multidisciplinary Research), London
- **Key Contribution**: User study with 17 music producers of varying experience levels. Evaluated how TTM models impact productivity, usability as creative collaborators, and integration into real workflows. Combined TTM with source separation tools.
- **Key Finding**: TTM models still struggle to interpret musicians' controls. Significant gap between what producers want to express and what text prompts can convey. Highlights the need for focused research on creator-AI interaction vocabulary.
- **Why it matters for sunolanguage**: Confirms the "vocabulary gap" from the production side. Producers have intentions they can't express in prompts. sunolanguage's reverse approach (learning what Suno CAN understand) addresses exactly this gap — by building a vocabulary of "what works" rather than "what we wish worked."

---

## Experimental Design References

Papers with methodology directly adaptable for sunolanguage:

### From Axis 1

1. **Deng et al. [1]** — Their protocol for evaluating whether embeddings encode timbre semantics (comparing embedding distances to human perceptual ratings) could be applied to evaluate Suno's internal text encoder. We could test: do Suno's embeddings for "bright" and "warm" relate to acoustic features the way human perception does?

2. **Reymore [3, 4]** — The 20-dimensional Timbre Trait Profile methodology and the 34-instrument radar plots provide a template for building "Suno Trait Profiles" — what descriptors does Suno consistently associate with each instrument?

3. **SAFE [6]** — The in-situ vocabulary collection methodology (collecting terms during actual use) directly parallels our approach. Their DAW plugin approach could inspire a Suno-side collection tool.

### From Axis 2

4. **Casini et al. [9]** — Their clustering and dimensionality reduction approach on 100K+ prompts is directly applicable to our collected Suno recognition outputs. We should replicate their analysis pipeline on our data.

5. **ConceptCaps [14]** — The 200-attribute taxonomy and TCAV probing method could be adapted to test which concepts Suno's recognition actually activates. We generate music -> Suno recognizes it -> check if the recognized concepts align with the taxonomy.

6. **Singh et al. [15]** — Sparse autoencoder probing of MusicGen could be applied to understand Suno's internal representations, if we can access intermediate layers (unlikely for commercial API, but the methodology is instructive for open-source alternatives).

---

## Updated Gaps Analysis

### How these findings refine sunolanguage's white space

**1. Vocabulary Structure Gap (CONFIRMED + REFINED)**
- Casini et al. [9] showed 80.7% of user tags appear only once — massive long-tail vocabulary with a small core.
- Reymore [3, 4] showed timbre semantics vary by register and context.
- **Implication**: Suno's "native vocabulary" likely has a similar structure: a small core of reliable descriptors + a long tail of context-dependent terms. Our RAG should weight core vocabulary higher.

**2. Input vs. Output Vocabulary Gap (NEW)**
- Casini et al. [9] mapped USER INPUT vocabulary to Suno/Udio.
- sunolanguage maps Suno's OUTPUT vocabulary (what Suno says about music).
- **Nobody has systematically compared these two**: what Suno is told vs. what Suno says.
- **This is our unique contribution**: the input-output vocabulary alignment study.

**3. Cross-Cultural Vocabulary Gap (STILL OPEN)**
- Deng et al. [1] used Chinese + Western instruments.
- MuChin [12] provides Chinese-language music descriptions.
- But NO study has examined how Suno's recognition vocabulary differs across languages or musical traditions.
- **Opportunity**: Feed Suno traditional East Asian music and compare its descriptors to those for Western music.

**4. Expertise-Level Vocabulary Gap (PARTIALLY ADDRESSED)**
- Wang et al. [11, 12] showed professional vs. amateur descriptions diverge significantly.
- Suno's auto-generated descriptions represent a THIRD vocabulary type: "machine native."
- **Question**: Is Suno's vocabulary closer to professional or amateur descriptions? This reveals its training data bias.

**5. Beyond-Language Concepts (NEW GAP)**
- Singh et al. [15] found that generative music models contain "coherent but uncodified patterns lacking clear counterparts in theory or language."
- **Implication**: There may be aspects of music that Suno "understands" but cannot name. These would show up as novel compound descriptors, unusual adjective combinations, or hedging language in Suno's recognition output.

**6. Controllability Hierarchy (REFINED)**
- Mustango [13] showed music-theory terms control different aspects than mood/genre terms.
- Casini et al. [9] showed metatags (structural) operate differently from descriptive tags.
- **Implication**: Suno's vocabulary likely has multiple "channels": structural ([Verse], [Chorus]), descriptive (genre, mood), technical (BPM, key), timbral (bright, warm). Our RAG should organize vocabulary by channel, not just alphabetically.

**7. Timbre-Text Mapping Validation (NOW FEASIBLE)**
- Deng et al. [1] showed LAION-CLAP best captures timbre semantics.
- **Implication**: We can use LAION-CLAP to validate whether Suno's timbre descriptors actually correspond to the acoustic features they claim to describe. This gives us a quantitative quality metric for our vocabulary entries.

---

## Summary Statistics

| Category | Count | Notes |
|----------|-------|-------|
| New Axis 1 papers | 8 | Timbre semantics, crossmodal, production vocab, computational |
| New Axis 2 papers | 9 | Suno/Udio analysis, benchmarks, controllability, captioning |
| Papers post-2024 | 12 | 70% of findings are from 2024-2026 |
| Directly about Suno/Udio | 2 | [9] Casini et al., [10] Grotschla et al. |
| Cross-cultural scope | 3 | [1] Chinese+Western, [11][12] Chinese music descriptions |
| Methodology templates | 6 | See Experimental Design References section |
| New gaps identified | 3 | Input-output vocab, beyond-language concepts, multi-channel hierarchy |
