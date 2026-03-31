# Deep Dive: Axis 3 (Sensory-Language-AI) & Axis 4 (Music Ontology)

> Phase 2 literature survey for sunolanguage project
> Compiled: 2026-03-31
> Scope: New papers beyond the initial 20 (10 per axis) from Phase 1

---

## Axis 3: New Findings

### [A3-11] Pengi: An Audio Language Model for Audio Tasks
- **Authors**: Soham Deshmukh, Benjamin Elizalde, Rita Singh, Huaming Wang
- **Year**: 2023
- **Venue**: NeurIPS 2023
- **Key Contribution**: Frames ALL audio tasks as text-generation tasks. Takes audio + text input, generates free-form text output. A pre-trained frozen LLM receives audio embeddings (from an audio encoder) and text embeddings as a joint prefix. Evaluated on 22 downstream tasks, achieving SoTA on several without task-specific fine-tuning. This is the first "audio language model" in the GPT sense -- it can answer open-ended questions about audio.
- **Why it matters for sunolanguage**: Pengi demonstrates that audio understanding can be unified through language generation. When we feed Suno a recording and it returns a prompt, Suno is performing exactly this kind of audio-to-text task. Pengi's architecture validates that a single model can both "listen" and "describe" -- the inverse of what text-to-music models do. sunolanguage's vocabulary is the bridge vocabulary between these two directions.
- **URL**: https://arxiv.org/abs/2305.11834

---

### [A3-12] SALMONN: Towards Generic Hearing Abilities for Large Language Models
- **Authors**: Changli Tang, Wenyi Yu, Guangzhi Sun, Xianzhao Chen et al. (Tsinghua / ByteDance)
- **Year**: 2024
- **Venue**: ICLR 2024
- **Key Contribution**: Integrates a dual audio encoder (Whisper for speech + BEATs for general audio) into a pre-trained LLM (Vicuna) via a window-level Q-Former. Handles speech recognition, audio captioning, music captioning, emotion recognition, and speaker verification in one model. Exhibits emergent abilities not seen in training: speech translation to untrained languages, audio-based storytelling, and speech-audio co-reasoning.
- **Why it matters for sunolanguage**: SALMONN proves that a single model can process music, speech, and environmental sound through language. Its emergent co-reasoning ability (combining speech content with audio characteristics) parallels what sunolanguage needs: understanding that "warm jazz guitar" is not just tags but a coherent sensory-linguistic description. The dual-encoder design (specialized + general) suggests sunolanguage's vocabulary should span both precise acoustic terms and holistic descriptions.
- **URL**: https://arxiv.org/abs/2310.13289

---

### [A3-13] Qwen-Audio: Advancing Universal Audio Understanding via Unified Large-Scale Audio-Language Models
- **Authors**: Yunfei Chu, Jin Xu, Xiaohuan Zhou et al. (Alibaba)
- **Year**: 2023
- **Venue**: arXiv (Alibaba Cloud)
- **Key Contribution**: Extends Qwen-7B LLM with a single Whisper-large-v2 audio encoder to handle 30+ audio tasks across speech, natural sounds, music, and songs. Uses a single encoder for all audio types (unlike SALMONN's dual encoder). Achieves SoTA on diverse benchmarks without task-specific fine-tuning. Demonstrates that scaling audio-language pre-training across task types improves universality.
- **Why it matters for sunolanguage**: Qwen-Audio's single-encoder approach to all audio types is significant -- it suggests that the boundary between "music description" and "sound description" is artificial from the model's perspective. For sunolanguage, this implies that Suno's internal vocabulary likely does not cleanly separate musical from non-musical sonic descriptors. Terms like "atmospheric," "ambient," or "crisp" may carry the same meaning whether describing music or environmental sound.
- **URL**: https://arxiv.org/abs/2311.07919

---

### [A3-14] MusiLingo: Bridging Music and Text with Pre-trained Language Models for Music Captioning and Query Response
- **Authors**: Zihao Deng, Yinghao Ma, Yudong Liu et al.
- **Year**: 2024
- **Venue**: Findings of NAACL 2024
- **Key Contribution**: Aligns music representations from MERT (a pre-trained music audio model) with a frozen LLM via a single projection layer. Trained on music captions and fine-tuned with instructional data. Created the MusicInstruct (MI) dataset from MusicCaps captions for open-ended music Q&A. Enables both music captioning and conversational music understanding.
- **Why it matters for sunolanguage**: MusiLingo is the closest existing system to what sunolanguage envisions as a downstream application. It can answer questions like "What instruments are in this track?" or "Describe the mood." The quality of its answers is bounded by the vocabulary in its training data -- exactly the gap sunolanguage fills. A MusiLingo-like system trained on sunolanguage's curated Suno-native vocabulary would produce descriptions that are both accurate AND actionable for music generation.
- **URL**: https://aclanthology.org/2024.findings-naacl.231/

---

### [A3-15] The Vector Grounding Problem
- **Authors**: Dimitri Coelho Mollo, Raphael Milliere
- **Year**: 2023
- **Venue**: arXiv / Philosophy and the Mind Sciences
- **Key Contribution**: Reformulates Harnad's (1990) symbol grounding problem for the era of neural networks that compute over continuous vectors, not discrete symbols. Distinguishes five types of grounding (referential, sensorimotor, relational, communicative, epistemic) and argues that referential grounding is the core issue. Provocatively argues that RLHF-tuned LLMs may already possess referential grounding through causal-historical selection, and that multimodality/embodiment are neither necessary nor sufficient for grounding.
- **Why it matters for sunolanguage**: This paper directly challenges the assumption that AI needs sensory experience to ground language. If Mollo & Milliere are right, then Suno may already have a form of referential grounding for music terms through its training process. sunolanguage's empirical approach (testing which words Suno actually responds to) is effectively a grounding verification protocol -- we are measuring whether Suno's internal representations are grounded in acoustic reality.
- **URL**: https://arxiv.org/abs/2304.01481

---

### [A3-16] WavCaps: A ChatGPT-Assisted Weakly-Labelled Audio Captioning Dataset for Audio-Language Multimodal Research
- **Authors**: Xinhao Mei, Chutong Meng, Haoyan Liu et al.
- **Year**: 2023
- **Venue**: IEEE/ACM Transactions on Audio, Speech and Language Processing (2024)
- **Key Contribution**: First large-scale weakly-labelled audio captioning dataset (~400K audio clips with captions). Sourced from FreeSound, BBC Sound Effects, SoundBible, and AudioSet. Used ChatGPT in a three-stage pipeline to filter noisy web-scraped descriptions and generate high-quality captions. Models trained on WavCaps significantly outperform previous SoTA in audio captioning, retrieval, and zero-shot classification.
- **Why it matters for sunolanguage**: WavCaps' methodology is directly transferable to sunolanguage. They used an LLM to clean and standardize noisy sensory descriptions -- we can do the same with Suno's raw prompt outputs. Their three-stage pipeline (filter noise, standardize format, generate consistent captions) is a blueprint for our data processing pipeline. The key difference: WavCaps covers general audio; sunolanguage focuses specifically on music production vocabulary.
- **URL**: https://arxiv.org/abs/2303.17395

---

### [A3-17] M2UGen: Multi-modal Music Understanding and Generation with the Power of Large Language Models
- **Authors**: Hussain, Liu et al.
- **Year**: 2024
- **Venue**: arXiv (AAAI 2024 submission)
- **Key Contribution**: Unified framework for both music understanding AND generation within a single LLM (LLaMA 2). Uses MERT for music encoding, ViT for images, ViViT for video, and MusicGen/AudioLDM2 as decoders. Can answer questions about music, generate music from text/image/video, and edit existing music -- all through natural language interaction.
- **Why it matters for sunolanguage**: M2UGen represents the convergence point: a system that both understands and generates music through language. This is precisely the cycle sunolanguage aims to optimize. When the system's understanding vocabulary and generation vocabulary are aligned (our core hypothesis), the quality of both tasks improves. sunolanguage's Suno-native vocabulary is the missing alignment layer.
- **URL**: https://arxiv.org/abs/2311.11255

---

### [A3-18] A Roadmap for Embodied and Social Grounding in LLMs
- **Authors**: Sara Ansari, Guilherme Bessa et al.
- **Year**: 2024
- **Venue**: arXiv
- **Key Contribution**: Proposes a roadmap for grounding LLMs through three elements: (1) an active bodily system as reference point, (2) temporally structured experience, and (3) social skills for common-grounded shared experience. Argues that meaning is always socially and culturally shaped, not just sensorily grounded. Distinguishes between "optimistic" approaches (adding perceptual data to LLMs) and "skeptical" approaches (arguing LLMs can never truly understand).
- **Why it matters for sunolanguage**: The social grounding dimension is particularly relevant. Music vocabulary is inherently social -- terms like "funky," "soulful," or "anthemic" carry cultural meaning that goes beyond acoustic features. sunolanguage must capture not just acoustic-linguistic mappings but also the cultural conventions embedded in music description. The roadmap's framework helps us understand why some Suno vocabulary is culturally specific.
- **URL**: https://arxiv.org/abs/2409.16900

---

## Axis 4: New Findings

### [A4-11] MusicCaps: A High-Quality Music Captioning Dataset
- **Authors**: Andrea Agostinelli et al. (Google Research)
- **Year**: 2023
- **Venue**: Released alongside MusicLM (arXiv)
- **Key Contribution**: 5,521 music clips from AudioSet, each annotated by professional musicians with (1) a free-text caption (avg. 4 sentences) and (2) an aspect list covering genre, mood, tempo, vocals, instrumentation, rhythm, etc. (avg. 11 aspects per clip). The aspect list effectively constitutes a de facto controlled vocabulary for music description, with terms like "tinny wide hi hats," "mellow piano melody," "high pitched female vocal melody."
- **Why it matters for sunolanguage**: MusicCaps is the closest existing dataset to what sunolanguage produces, but from the opposite direction. MusicCaps = humans describing music for AI evaluation. sunolanguage = AI (Suno) describing music for human understanding. Comparing the two vocabularies would reveal where human and AI music description diverge -- a core research question. MusicCaps' aspect list format (tag-like phrases) closely mirrors Suno's prompt structure.
- **URL**: https://huggingface.co/datasets/google/MusicCaps

---

### [A4-12] LP-MusicCaps: LLM-Based Pseudo Music Captioning
- **Authors**: SeungHeon Doh, Keunwoo Choi, Jongpil Lee, Juhan Nam
- **Year**: 2023
- **Venue**: ISMIR 2023 (Best Paper Nominee)
- **Key Contribution**: Scaled music captioning from 5.5K (MusicCaps) to 2.2M captions / 0.5M audio clips by using LLMs to convert existing tag datasets into natural language descriptions. Used diverse task instructions (writing, summary, paraphrase, attribute prediction) to generate varied captions. The pseudo-captioned dataset, when used for training, outperforms models trained on human-annotated data alone.
- **Why it matters for sunolanguage**: LP-MusicCaps demonstrates that structured music tags can be reliably expanded into natural language via LLMs -- and that this expansion IMPROVES downstream performance. This directly validates sunolanguage's approach: collect Suno's structured tag vocabulary, then use LLMs to expand it into rich, contextual descriptions for the RAG system. The "pseudo" in "pseudo-captioning" is essentially what sunolanguage does in reverse (AI-generated descriptions treated as ground truth).
- **URL**: https://arxiv.org/abs/2307.16372

---

### [A4-13] Musical Word Embedding for Music Tagging and Retrieval
- **Authors**: SeungHeon Doh, Minz Won, Keunwoo Choi, Juhan Nam
- **Year**: 2024
- **Venue**: IEEE/ACM Transactions on Audio, Speech and Language Processing
- **Key Contribution**: Trained domain-specific word embeddings on music text data (Amazon reviews, music biographies, Wikipedia music pages). Showed that general-purpose embeddings (Word2Vec, GloVe) miss music-specific semantic relationships (e.g., "deep_house" and "western_swing" as compound concepts). Integrated Musical Word Embedding (MWE) into audio-word joint representation for tagging and retrieval, outperforming generic embeddings.
- **Why it matters for sunolanguage**: This is perhaps the most directly relevant paper for sunolanguage's core mission. It proves that music has its own semantic space that generic language models miss. sunolanguage goes further: we are building not just domain-specific embeddings but a domain-specific vocabulary verified against a specific AI engine (Suno). The MWE methodology (training on music-domain text) could be applied to Suno's collected prompts to create Suno-specific word embeddings.
- **URL**: https://arxiv.org/abs/2404.13569

---

### [A4-14] COMUS: Ontological and Rule-Based Reasoning for Music Recommendation
- **Authors**: Rho, Song, Hwang, Kim
- **Year**: 2009
- **Venue**: ICDS 2009 / IEEE DEXA 2008
- **Key Contribution**: OWL ontology extending the Music Ontology with domain-specific classes for mood and situation. Models relationships between low-level features (pitch, duration), musical factors (tempo, rhythm), moods, and listening situations. 18 classes, 32 properties. Enables rule-based reasoning: "if tempo > 120 AND major key THEN mood = energetic."
- **Why it matters for sunolanguage**: COMUS provides a formal framework for the mood/situation dimension of music vocabulary -- something missing from the technical ontologies (MO, MPEG-7, AFO). For sunolanguage, COMUS's approach of linking acoustic features to mood labels through rules is analogous to our mapping of Suno's acoustic processing to its vocabulary choices. However, COMUS uses hand-crafted rules; sunolanguage discovers these mappings empirically.
- **URL**: https://ieeexplore.ieee.org/document/4782893

---

### [A4-15] The Song Describer Dataset: A Corpus of Audio Captions for Music-and-Language Evaluation
- **Authors**: Ilaria Manco, Benno Weck, SeungHeon Doh et al.
- **Year**: 2023
- **Venue**: ML for Audio Workshop @ NeurIPS 2023
- **Key Contribution**: 1,100 human-written natural language descriptions of 706 music recordings, all under Creative Commons licenses. Designed specifically as an evaluation benchmark for music-language models (captioning, text-to-music generation, retrieval). Benchmarks popular models on three M&L tasks and highlights the importance of cross-dataset evaluation.
- **Why it matters for sunolanguage**: SDD provides a clean, copyright-free benchmark for evaluating whether sunolanguage's vocabulary improves music-language alignment. We could compare: (1) how well Suno's auto-generated prompts match SDD human descriptions, (2) whether sunolanguage-informed prompts generate music closer to SDD reference recordings. The Creative Commons licensing also makes it practically usable.
- **URL**: https://arxiv.org/abs/2311.10057

---

### [A4-16] MARBLE: Music Audio Representation Benchmark for Universal Evaluation
- **Authors**: Ruibin Yuan, Yinghao Ma, Yizhi Li et al.
- **Year**: 2023
- **Venue**: NeurIPS 2023 (Datasets and Benchmarks Track)
- **Key Contribution**: Comprehensive benchmark for music audio representations with 18 tasks across 12 datasets. Defines a four-level taxonomy: acoustic (pitch, beat), performance (technique, expression), score (key, chord, structure), and high-level description (genre, mood, instrumentation). Provides unified evaluation protocol for all open-source pre-trained music models.
- **Why it matters for sunolanguage**: MARBLE's four-level taxonomy (acoustic / performance / score / high-level) is an excellent framework for organizing sunolanguage's vocabulary. Suno's prompts likely span all four levels -- from acoustic descriptions ("reverb-heavy") to high-level tags ("indie rock"). MARBLE's hierarchy could serve as the backbone for sunolanguage's RAG index structure, ensuring coverage across all description levels.
- **URL**: https://arxiv.org/abs/2306.10548

---

### [A4-17] Hevner Adjective Checklist (Updated) + Russell Circumplex Model for Music Emotion
- **Authors**: Kate Hevner (1936, original); Emery Schubert (2003, update); James Russell (1980, circumplex model)
- **Year**: 1936 / 1980 / 2003
- **Venue**: Various (American Journal of Psychology / Journal of Personality and Social Psychology / Perceptual and Motor Skills)
- **Key Contribution**: Hevner's original 66-adjective checklist organized emotions in 8 circular clusters for music description. Russell's circumplex model mapped all affect onto two dimensions: arousal (calm-excited) and valence (unpleasant-pleasant). Schubert's 2003 update surveyed 133 musicians, refining to 46 adjectives in 9 clusters mapped onto Russell's arousal-valence space. This is the most established controlled vocabulary for music emotion.
- **Why it matters for sunolanguage**: The Hevner-Russell framework is the gold standard for music emotion vocabulary. Suno almost certainly uses mood/emotion tags internally. Mapping Suno's collected mood vocabulary onto the Hevner-Russell arousal-valence space would reveal: (a) which emotional regions Suno covers well, (b) which are underrepresented, and (c) whether Suno's mood categories align with established music psychology. This mapping is essential for the mood dimension of sunolanguage's RAG.
- **URL**: https://journals.sagepub.com/doi/10.2466/pms.2003.96.3c.1117

---

### [A4-18] DCASE 2024 Task 6: Automated Audio Captioning
- **Authors**: Various (DCASE community challenge)
- **Year**: 2024
- **Venue**: DCASE Challenge 2024
- **Key Contribution**: Annual benchmark challenge for automated audio captioning on the Clotho V2 dataset. Top 2024 systems achieved FENSE scores of 0.54+ using encoder-decoder architectures with BEATs/CLAP audio encoders and BART/LLaMA decoders. Key innovations: CLAP-based beam search filtering (selecting descriptions that best match input audio), nucleus sampling, hybrid re-ranking, and LLM-based caption summarization.
- **Why it matters for sunolanguage**: DCASE 2024 represents the SoTA in "audio to text" -- the exact inverse of text-to-music generation. The top systems' approach of using CLAP to filter generated captions (keeping only those that align well with the audio) is directly applicable to sunolanguage: we could use the same technique to validate whether Suno's auto-generated prompts are actually good descriptions of the input music. This would give us a quality metric for our collected vocabulary.
- **URL**: https://dcase.community/challenge2024/task-automated-audio-captioning-results

---

## Experimental Design References

Papers with methodology directly adaptable for sunolanguage:

### 1. Vocabulary Extraction Pipeline (from WavCaps)
WavCaps' three-stage pipeline for converting noisy web descriptions into clean captions:
1. **Filter**: Remove irrelevant/noisy raw descriptions
2. **Standardize**: Normalize format and terminology
3. **Generate**: Use LLM to produce consistent, high-quality captions

Adaptation for sunolanguage: Apply to Suno's raw prompt outputs. Stage 1 removes malformed prompts; Stage 2 normalizes instrument names and genre tags; Stage 3 uses LLM to expand abbreviated tags into full descriptions for the RAG.

### 2. Domain-Specific Embedding Training (from Musical Word Embedding)
Train word embeddings on music-specific corpora to capture semantic relationships that general embeddings miss.

Adaptation for sunolanguage: Once we have ~1000+ Suno prompts, train Suno-specific word embeddings. This would reveal Suno's internal semantic structure -- e.g., which instruments Suno considers "similar," which genre terms cluster together.

### 3. Cross-Dataset Vocabulary Comparison (from MusicCaps vs. SDD vs. LP-MusicCaps)
Compare the vocabulary distributions across different music description sources.

Adaptation for sunolanguage: Compare Suno's auto-generated vocabulary against MusicCaps (expert human), LP-MusicCaps (LLM-expanded), and SDD (crowdsourced human). This triangulation would reveal Suno's unique vocabulary fingerprint.

### 4. Grounding Verification Protocol (from DCASE + CLAP)
Use contrastive audio-language models to verify whether text descriptions actually match their corresponding audio.

Adaptation for sunolanguage: Feed Suno's auto-generated prompt + the original audio into CLAP. High CLAP similarity = Suno understood the audio well. Low similarity = the prompt is noise. This provides an objective quality filter for our vocabulary collection.

### 5. Emotion Vocabulary Mapping (from Hevner-Russell + COMUS)
Map collected mood/emotion terms onto the established arousal-valence space.

Adaptation for sunolanguage: Plot all mood-related terms from Suno prompts onto the Russell circumplex. Identify coverage gaps and over-represented regions. Cross-reference with COMUS's rule-based mood-feature associations.

---

## Updated Gaps Analysis

### Refined White Space for sunolanguage

Based on Phase 1 (40 papers) + Phase 2 (16 new papers), here is our updated understanding of sunolanguage's unique position:

#### Gap 1: Reverse-Engineering an AI Music Engine's Vocabulary (STILL UNIQUE)
No paper in our survey attempts to systematically extract and catalog the vocabulary that a specific AI music engine actually uses to describe music. All existing work goes in the other direction: designing vocabularies FOR AI systems (MusicCaps, LP-MusicCaps, SDD) or training AI to use human vocabularies (CLAP, MuLan, SALMONN). sunolanguage is the first to ask: "What vocabulary does the AI itself choose?"

#### Gap 2: Production-Aware Sensory Vocabulary (PARTIALLY ADDRESSED)
Musical Word Embedding (A4-13) showed that domain-specific text captures music semantics better than generic text. But MWE trained on human-written music text (reviews, biographies), not on AI-generated descriptions. sunolanguage uniquely targets the AI-native production vocabulary -- terms like "punchy kick," "lo-fi tape hiss," or "sidechained bass" that exist at the intersection of production technique and sonic description.

#### Gap 3: Bidirectional Vocabulary Alignment (STILL UNIQUE)
M2UGen (A3-17) showed that unified understanding+generation improves both tasks. But no one has proposed that the VOCABULARY itself should be bidirectionally aligned -- that the terms used to describe music should be the same terms that optimally generate it. sunolanguage's core insight remains: Suno's auto-generated prompts are the Rosetta Stone because they represent what Suno "thinks" when it "hears" music.

#### Gap 4: Grounded Evaluation of AI Music Vocabulary (NOW FEASIBLE)
Phase 2 revealed tools that make sunolanguage's evaluation tractable:
- CLAP for measuring prompt-audio alignment
- MARBLE's taxonomy for organizing vocabulary dimensions
- MusicCaps/SDD for cross-referencing against human descriptions
- Hevner-Russell for validating emotion vocabulary coverage
- DCASE methodology for quality-filtering collected prompts

#### Gap 5: Cultural and Social Dimensions (NEWLY IDENTIFIED)
The embodied grounding roadmap (A3-18) highlighted that language meaning is socially and culturally shaped. Music vocabulary carries heavy cultural baggage ("jazz," "K-pop," "reggaeton" are not just sonic categories but cultural identifiers). No existing ontology adequately captures how cultural context affects music description vocabulary. sunolanguage could contribute here by analyzing how Suno's vocabulary reflects (or misrepresents) cultural music categories.

### Priority Research Questions (Updated)

1. **Vocabulary overlap**: What percentage of Suno's auto-generated terms appear in MusicCaps/LP-MusicCaps? (Measures how "standard" vs. "unique" Suno's vocabulary is)
2. **Grounding quality**: Do Suno's prompts score higher on CLAP similarity than random descriptions? (Validates that Suno's vocabulary is genuinely grounded)
3. **Bidirectional fidelity**: If we feed Suno's auto-generated prompt back into Suno as a generation prompt, how similar is the output to the original recording? (The ultimate round-trip test)
4. **Taxonomy coverage**: Mapping Suno vocabulary onto MARBLE's four-level hierarchy -- which levels are well-covered? (Reveals Suno's description granularity)
5. **Emotion calibration**: Mapping Suno mood terms onto Hevner-Russell space -- is the coverage balanced? (Reveals emotional bias in Suno's vocabulary)

---

## Summary Statistics

| Category | Phase 1 | Phase 2 | Total |
|----------|---------|---------|-------|
| Axis 3 papers | 10 | 8 | 18 |
| Axis 4 papers | 10 | 8 | 18 |
| **All axes total** | **40** | **16** | **56** |

### Phase 2 Paper Timeline
| Year | Count | Papers |
|------|-------|--------|
| 2003 | 1 | Schubert (Hevner update) |
| 2009 | 1 | COMUS |
| 2023 | 8 | Pengi, Qwen-Audio, WavCaps, MusicCaps, LP-MusicCaps, SDD, MARBLE, Vector Grounding |
| 2024 | 6 | SALMONN, MusiLingo, M2UGen, MWE, DCASE, Embodied Grounding Roadmap |
