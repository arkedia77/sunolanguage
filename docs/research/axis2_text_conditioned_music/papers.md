# Axis 2: Text-Conditioned Music Generation -- Paper Collection

> Collected 2026-03-31 for the sunolanguage project.
> Focus: how current AI models process text prompts to generate music.

---

### [1] MuLan: A Joint Embedding of Music Audio and Natural Language
- **Authors**: Qingqing Huang, Aren Jansen, Joonseok Lee, Ravi Ganti, Judith Yue Li, Daniel P. W. Ellis
- **Year**: 2022
- **Venue**: ISMIR 2022 (23rd International Society for Music Information Retrieval Conference)
- **Key Contribution**: First large-scale joint audio-text embedding for music. Two-tower contrastive model trained on 44M music recordings with weakly-associated free-form text. Enables zero-shot music tagging and cross-modal retrieval without a fixed ontology.
- **Relevance to sunolanguage**: MuLan demonstrates that music-text alignment can be learned from noisy web data, but the learned vocabulary is implicit in the embedding space -- you cannot inspect which words the model "understands." Sunolanguage's reverse-engineering approach (extracting Suno's own vocabulary) addresses exactly this opacity.
- **Tags**: [joint-embedding] [contrastive-learning] [music-text] [zero-shot]
- **URL**: https://arxiv.org/abs/2208.12415

---

### [2] MusicLM: Generating Music From Text
- **Authors**: Andrea Agostinelli, Timo I. Denk, Zalan Borsos, Jesse Engel, Mauro Verzetti, Antoine Caillon, Qingqing Huang, Aren Jansen, Adam Roberts, Marco Tagliasacchi, Matt Sharifi, Neil Zeghidour, Christian Frank
- **Year**: 2023
- **Venue**: arXiv preprint (arXiv:2301.11325)
- **Key Contribution**: Hierarchical sequence-to-sequence model generating 24kHz music from text descriptions. Uses MuLan embeddings as the text-conditioning bridge. Also released MusicCaps, a 5.5k music-text dataset with expert annotations.
- **Relevance to sunolanguage**: MusicLM's reliance on MuLan means its text understanding is filtered through a contrastive embedding -- certain words activate strong musical features while others are ignored. The MusicCaps dataset reveals what human experts consider describable in music, providing a useful comparison to Suno's auto-generated vocabulary.
- **Tags**: [text-to-music] [generation] [hierarchical] [MuLan] [MusicCaps]
- **URL**: https://arxiv.org/abs/2301.11325

---

### [3] Noise2Music: Text-conditioned Music Generation with Diffusion Models
- **Authors**: Qingqing Huang, Daniel S. Park, Tao Wang, Timo I. Denk, Andy Ly, Nanxin Chen, Zhengdong Zhang, Zhishuai Zhang, Jiahui Yu, Christian Frank, Jesse Engel, Quoc V. Le, William Chan, Wei Han
- **Year**: 2023
- **Venue**: arXiv preprint (arXiv:2302.03917)
- **Key Contribution**: Cascading diffusion model (generator + cascader) producing 30-second clips from text. Crucially, uses LLMs to generate pseudo-captions for training data, demonstrating that the quality of text descriptions directly impacts generation fidelity.
- **Relevance to sunolanguage**: Shows that language models are already used to create the music-text pairs that train generators. This is the same pipeline sunolanguage aims to decode -- if Suno uses a similar captioning step internally, the vocabulary we extract reflects what its captioner can express.
- **Tags**: [text-to-music] [diffusion] [pseudo-captions] [LLM-augmented]
- **URL**: https://arxiv.org/abs/2302.03917

---

### [4] Simple and Controllable Music Generation (MusicGen)
- **Authors**: Jade Copet, Felix Kreuk, Itai Gat, Tal Remez, David Kant, Gabriel Synnaeve, Yossi Adi, Alexandre Defossez
- **Year**: 2023
- **Venue**: NeurIPS 2023
- **Key Contribution**: Single-stage transformer LM over compressed discrete music tokens (EnCodec). Efficient token interleaving patterns eliminate multi-stage cascading. Text conditioning via T5 encoder. Trained on 20K hours of licensed music with text metadata.
- **Relevance to sunolanguage**: MusicGen's text encoder (T5) processes prompts as general natural language, but the model's actual responsiveness is constrained by what appeared in training metadata. Understanding this gap between "what T5 can encode" and "what MusicGen learned to respond to" parallels sunolanguage's goal of mapping Suno's effective vocabulary.
- **Tags**: [text-to-music] [generation] [transformer-LM] [single-stage] [controllable]
- **URL**: https://arxiv.org/abs/2306.05284

---

### [5] Large-scale Contrastive Language-Audio Pretraining (CLAP)
- **Authors**: Yusong Wu, Ke Chen, Tianyu Zhang, Yuchen Hui, Taylor Berg-Kirkpatrick, Shlomo Dubnov
- **Year**: 2023
- **Venue**: ICASSP 2023
- **Key Contribution**: Contrastive language-audio pretraining on LAION-Audio-630K (633K audio-text pairs). Feature fusion handles variable-length audio; keyword-to-caption augmentation expands text diversity. Achieves SOTA zero-shot audio classification.
- **Relevance to sunolanguage**: CLAP is the audio-domain analogue of CLIP. It defines a shared embedding space where certain textual descriptions cluster near certain sounds. Sunolanguage's 3-layer vocabulary (Style Prompts, Inline Instrument Cues, Stem-level descriptors) likely maps to different regions of such embedding spaces.
- **Tags**: [contrastive-learning] [audio-text] [embedding] [zero-shot]
- **URL**: https://arxiv.org/abs/2211.06687

---

### [6] Mousai: Efficient Text-to-Music Diffusion Models
- **Authors**: Flavio Schneider, Ojasv Kamal, Zhijing Jin, Bernhard Scholkopf
- **Year**: 2024
- **Venue**: ACL 2024 (62nd Annual Meeting of the Association for Computational Linguistics)
- **Key Contribution**: Two-stage cascading latent diffusion (DMAE encoder + text-conditioned latent diffusion). Generates minutes-long 48kHz stereo music on a single consumer GPU. Open-source.
- **Relevance to sunolanguage**: Mousai's text conditioning uses standard text encoders, meaning it inherits the same vocabulary opacity problem. Its open-source nature makes it a candidate for controlled vocabulary probing experiments alongside Suno.
- **Tags**: [text-to-music] [diffusion] [latent-space] [efficient] [open-source]
- **URL**: https://arxiv.org/abs/2301.11757

---

### [7] Stable Audio Open
- **Authors**: Zach Evans, Julian D. Parker, CJ Carr, Zack Zukowski, Josiah Taylor, Jordi Pons
- **Year**: 2024
- **Venue**: arXiv preprint (arXiv:2407.14358)
- **Key Contribution**: Latent diffusion model with T5-based text conditioning and timing embeddings. Generates variable-length stereo audio up to 47s at 44.1kHz. Trained on ~500K Creative Commons recordings. Open weights.
- **Relevance to sunolanguage**: T5 text embeddings mean the model theoretically accepts any English text, but effective prompts cluster around specific musical vocabulary. The CC training data's metadata quality directly shapes what text the model learned to obey -- another case where the "effective vocabulary" is hidden.
- **Tags**: [text-to-audio] [diffusion] [latent-space] [open-weights] [T5-conditioning]
- **URL**: https://arxiv.org/abs/2407.14358

---

### [8] LP-MusicCaps: LLM-Based Pseudo Music Captioning
- **Authors**: SeungHeon Doh, Keunwoo Choi, Jongpil Lee, Juhan Nam
- **Year**: 2023
- **Venue**: ISMIR 2023 (nominated for Best Paper, 5/104)
- **Key Contribution**: Uses GPT-3.5 to generate 2.2M music captions from tag datasets (MusicCaps, MagnaTagATune, MSD). Tag-to-caption pipeline creates large-scale training data for music captioning models. Systematic evaluation of LLM-generated music captions.
- **Relevance to sunolanguage**: Directly relevant -- LP-MusicCaps shows how LLMs translate music tags into natural language descriptions. Sunolanguage does the inverse: extracting tags/vocabulary FROM an AI system's natural language outputs. The two approaches are complementary and could validate each other.
- **Tags**: [music-captioning] [LLM] [pseudo-labels] [dataset] [tag-to-caption]
- **URL**: https://arxiv.org/abs/2307.16372

---

### [9] JEN-1: Text-Guided Universal Music Generation with Omnidirectional Diffusion Models
- **Authors**: Peike Li, Boyu Chen, Yao Yao, Yikai Wang, Allen Wang, Alex Wang
- **Year**: 2023
- **Venue**: arXiv preprint (arXiv:2308.04729)
- **Key Contribution**: Combines autoregressive and non-autoregressive diffusion in a single end-to-end model. Supports text-to-music, music inpainting, and continuation within one unified framework. Achieves 48kHz stereo generation.
- **Relevance to sunolanguage**: JEN-1's multi-task design means its text encoder must handle diverse prompt types (generation prompts, style descriptions, continuation cues). This suggests text-to-music models develop internal hierarchies of prompt interpretation -- echoing sunolanguage's discovery of layered vocabulary.
- **Tags**: [text-to-music] [diffusion] [omnidirectional] [multi-task] [unified]
- **URL**: https://arxiv.org/abs/2308.04729

---

### [10] AI-Enabled Text-to-Music Generation: A Comprehensive Review of Methods, Frameworks, and Future Directions
- **Authors**: Yujia Zhao, Mingzhi Yang, Yujia Lin, Xiaohong Zhang, Feifei Shi, Zongjie Wang, Jianguo Ding, Ning Hu
- **Year**: 2025
- **Venue**: MDPI Electronics, Vol. 14, Issue 6, Article 1197
- **Key Contribution**: Comprehensive survey categorizing text-to-music methods into traditional, hybrid, and end-to-end LLM-centric frameworks. Documents the growing role of LLMs in improving controllability. Identifies persistent challenges: data scarcity, representation limitations, text-music structural alignment.
- **Relevance to sunolanguage**: This survey confirms that "aligning text with musical structures remains underexplored" -- precisely the gap sunolanguage fills by empirically extracting what vocabulary an AI music engine actually responds to, rather than theoretically modeling the alignment.
- **Tags**: [survey] [text-to-music] [LLM] [frameworks] [challenges]
- **URL**: https://www.mdpi.com/2079-9292/14/6/1197
