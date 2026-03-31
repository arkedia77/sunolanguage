# Axis 3: Sensory-Language-AI Framework -- Paper Collection

> Cross-modal mappings between sensory experience and language, and how AI leverages these.
> Collected: 2026-03-31

---

### [1] Learning Transferable Visual Models From Natural Language Supervision (CLIP)
- **Authors**: Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, Ilya Sutskever
- **Year**: 2021
- **Venue**: ICML 2021
- **Key Contribution**: Demonstrated that contrastive pretraining on 400M (image, text) pairs produces visual representations that transfer to downstream tasks via natural language, achieving zero-shot ImageNet performance matching supervised ResNet-50. Established that language supervision alone can ground visual understanding.
- **Relevance to sunolanguage**: The foundational template. CLIP proved that language can serve as the bridge between sensory data (vision) and semantic understanding. sunolanguage applies the same logic to audio: if music-descriptive language is rich enough, AI can learn music through language.
- **Tags**: [multimodal] [vision-language] [contrastive-learning] [zero-shot] [foundational]
- **URL**: https://arxiv.org/abs/2103.00020

---

### [2] AudioCLIP: Extending CLIP to Image, Text and Audio
- **Authors**: Andrey Guzhov, Federico Raue, Jorn Hees, Andreas Dengel
- **Year**: 2022
- **Venue**: ICASSP 2022
- **Key Contribution**: Extended CLIP to a trimodal (image, text, audio) embedding space by adding an ESResNeXt audio encoder trained on AudioSet. Achieved 97.15% on ESC-50 and enabled zero-shot audio classification (68.78% ESC-50) without task-specific training.
- **Relevance to sunolanguage**: First direct proof that CLIP's vision-language paradigm transfers to audio. However, AudioCLIP focuses on environmental sounds, not music. sunolanguage targets the music-specific vocabulary gap that AudioCLIP does not address.
- **Tags**: [multimodal] [audio-language] [contrastive-learning] [zero-shot]
- **URL**: https://arxiv.org/abs/2106.13043

---

### [3] CLAP: Learning Audio Concepts From Natural Language Supervision
- **Authors**: Benjamin Elizalde, Soham Deshmukh, Mahmoud Al Ismail, Huaming Wang
- **Year**: 2023
- **Venue**: ICASSP 2023
- **Key Contribution**: Trained contrastive audio-language model on 128K audio-text pairs and evaluated across 26 downstream tasks spanning sound events, music, and speech. Established SoTA zero-shot performance in multiple audio domains with significantly less paired data than vision counterparts.
- **Relevance to sunolanguage**: CLAP demonstrates that even modest-scale audio-language pairing produces strong generalization, validating the core thesis that language supervision scales to audio. The gap: CLAP uses generic audio descriptions, not the specialized music production vocabulary sunolanguage aims to codify.
- **Tags**: [audio-language] [contrastive-learning] [zero-shot] [general-audio]
- **URL**: https://arxiv.org/abs/2206.04769

---

### [4] ImageBind: One Embedding Space To Bind Them All
- **Authors**: Rohit Girdhar, Alaaeldin El-Nouby, Zhuang Liu, Mannat Singh, Kalyan Vasudev Alwala, Armand Joulin, Ishan Misra
- **Year**: 2023
- **Venue**: CVPR 2023
- **Key Contribution**: Learned a joint embedding across six modalities (images, text, audio, depth, thermal, IMU) using only image-paired data. Showed that image-text alignment (from CLIP) can bootstrap alignment for other modalities transitively -- audio binds to images, images bind to text, therefore audio binds to text.
- **Relevance to sunolanguage**: ImageBind's transitive binding principle is key: language can serve as the universal anchor modality. For sunolanguage, this means a well-constructed music vocabulary could enable grounding across production parameters, listener perception, and generative AI simultaneously.
- **Tags**: [multimodal] [six-modalities] [transitive-binding] [embedding-space]
- **URL**: https://arxiv.org/abs/2305.05665

---

### [5] MuLan: A Joint Embedding of Music Audio and Natural Language
- **Authors**: Qingqing Huang, Aren Jansen, Joonseok Lee, Ravi Ganti, Judith Yue Li, Daniel P. W. Ellis
- **Year**: 2022
- **Venue**: ISMIR 2022
- **Key Contribution**: First large-scale music-language joint embedding model, trained on 44M music recordings (370K hours) with weakly-associated free-form text annotations. Subsumes existing ontologies (tags, genres) and enables true zero-shot music understanding through natural language.
- **Relevance to sunolanguage**: Most directly relevant prior work. MuLan proves music-language alignment works at scale but relies on noisy web-scraped text. sunolanguage's contribution is the vocabulary itself -- curating precise, production-aware terms that MuLan-like models could leverage for better grounding.
- **Tags**: [music-language] [contrastive-learning] [zero-shot] [large-scale] [directly-relevant]
- **URL**: https://arxiv.org/abs/2208.12415

---

### [6] Contrastive Audio-Language Learning for Music (MusCALL)
- **Authors**: Ilaria Manco, Emmanouil Benetos, Elio Quinton, Gyorgy Fazekas
- **Year**: 2022
- **Venue**: ISMIR 2022
- **Key Contribution**: Dual-encoder framework learning alignment between music audio and descriptive sentences. Demonstrated that contrastive music-text learning enables zero-shot genre classification and auto-tagging, significantly outperforming baselines in cross-modal retrieval.
- **Relevance to sunolanguage**: MusCALL operates at a smaller scale than MuLan but explores the same music-language alignment space. Its reliance on descriptive sentences highlights the importance of text quality -- exactly the problem sunolanguage addresses by building a structured, expert-level music vocabulary.
- **Tags**: [music-language] [contrastive-learning] [zero-shot] [retrieval]
- **URL**: https://arxiv.org/abs/2208.12208

---

### [7] MusicLM: Generating Music From Text
- **Authors**: Andrea Agostinelli, Timo I. Denk, Zalan Borsos, Jesse Engel, Mauro Verzetti, Antoine Caillon, Qingqing Huang, Aren Jansen, Adam Roberts, Marco Tagliasacchi, Matt Sharifi, Neil Zeghidour, Christian Frank
- **Year**: 2023
- **Venue**: arXiv (Google Research)
- **Key Contribution**: Hierarchical sequence-to-sequence model generating high-fidelity 24kHz music from text descriptions, conditioned on MuLan embeddings. Demonstrated that music-language alignment (via MuLan) enables coherent multi-minute generation from natural language prompts.
- **Relevance to sunolanguage**: MusicLM is downstream proof that better music-language grounding (MuLan) directly improves generation quality. sunolanguage's vocabulary refinement could improve the precision of text-to-music generation by providing richer, more discriminative language inputs.
- **Tags**: [music-generation] [text-to-music] [language-conditioned] [hierarchical]
- **URL**: https://arxiv.org/abs/2301.11325

---

### [8] The Symbol Grounding Problem
- **Authors**: Stevan Harnad
- **Year**: 1990
- **Venue**: Physica D: Nonlinear Phenomena, 42(1-3), 335-346
- **Key Contribution**: Posed the foundational question: how can formal symbols acquire intrinsic meaning rather than remaining parasitic on external interpretation? Proposed that symbols must be grounded bottom-up in nonsymbolic representations -- iconic (sensory analogs) and categorical (learned feature detectors).
- **Relevance to sunolanguage**: Harnad's framework explains why sunolanguage matters theoretically. Music AI terms like "warm" or "bright" are ungrounded symbols until connected to actual acoustic features. sunolanguage's mapping of terms to audio properties is precisely the grounding operation Harnad described.
- **Tags**: [grounding] [theoretical] [cognitive-science] [foundational]
- **URL**: https://arxiv.org/abs/cs/9906002

---

### [9] Perceptual Symbol Systems
- **Authors**: Lawrence W. Barsalou
- **Year**: 1999
- **Venue**: Behavioral and Brain Sciences, 22(4), 577-609
- **Key Contribution**: Proposed that cognitive representations are not amodal tokens but grounded in perceptual-motor experience. Sensory fragments are captured as "perceptual symbols" that can be recombined into simulators supporting categorization, inference, and abstract thought.
- **Relevance to sunolanguage**: Barsalou provides the cognitive-science basis for why sensory-grounded language works. When a producer says "crunchy guitar tone," they activate a perceptual simulator. sunolanguage's vocabulary captures these perceptual symbols in text form, making them accessible to AI.
- **Tags**: [grounding] [theoretical] [cognitive-science] [perceptual-symbols]
- **URL**: https://pubmed.ncbi.nlm.nih.gov/11301525/

---

### [10] Crossmodal Correspondences: A Tutorial Review
- **Authors**: Charles Spence
- **Year**: 2011
- **Venue**: Attention, Perception, & Psychophysics, 73, 971-995
- **Key Contribution**: Comprehensive review of systematic mappings between stimulus features across modalities (e.g., high pitch mapped to small, bright, elevated objects). Demonstrated that crossmodal correspondences are robust, consistent across individuals, and constrain perceptual binding.
- **Relevance to sunolanguage**: Explains why certain language-sound mappings are universal (e.g., "bright" for high-frequency sounds). sunolanguage's vocabulary exploits these natural crossmodal correspondences -- they are not arbitrary metaphors but reflect deep perceptual structure that AI can learn.
- **Tags**: [crossmodal] [psychophysics] [perception] [sound-symbolism]
- **URL**: https://link.springer.com/article/10.3758/s13414-010-0073-7
