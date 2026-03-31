# Axis 3 Synthesis: The Sensory-Language-AI Framework

> How language bridges sensory experience and artificial intelligence, and why sunolanguage matters.

## The CLIP Template: Vision Proved It First

CLIP (Radford et al., 2021) established the paradigm: train two encoders -- one for images, one for text -- via contrastive learning on 400 million image-text pairs, and the resulting model understands visual concepts through language alone. No labeled datasets, no hand-designed ontologies. The key insight was that natural language is expressive enough to capture visual semantics, enabling zero-shot transfer to tasks the model never explicitly trained on. CLIP did not just match images to captions; it demonstrated that language supervision can replace traditional sensory-domain supervision entirely.

## Audio-Language Models: Extending the Paradigm

The CLIP template rapidly propagated to audio. AudioCLIP (Guzhov et al., 2022) added an audio encoder to CLIP's framework, achieving strong zero-shot environmental sound classification. CLAP (Elizalde et al., 2023) scaled this to 26 downstream tasks. In the music domain specifically, MuLan (Huang et al., 2022) trained on 44 million recordings with free-form text, and MusCALL (Manco et al., 2022) demonstrated music-text alignment at smaller scale. ImageBind (Girdhar et al., 2023) showed that modalities can be transitively bound through a shared anchor -- images bridge to text, audio bridges to images, therefore audio bridges to text. MusicLM (Agostinelli et al., 2023) then proved that music-language grounding enables high-fidelity text-to-music generation, closing the loop from understanding to creation.

## Theoretical Grounding: Why Language Works

The success of these models is not accidental. Harnad (1990) identified the symbol grounding problem: formal symbols are meaningless until connected to sensory experience. Barsalou (1999) proposed that human concepts are themselves perceptual symbols -- fragments of sensory-motor experience stored and recombined for cognition. Spence (2011) documented that crossmodal correspondences (e.g., high pitch perceived as "bright" or "small") are robust and systematic, not arbitrary. Together, these theories explain why language can encode sensory experience: human language already carries grounded perceptual content. When someone describes a sound as "warm" or "gritty," they are externalizing a perceptual symbol that is systematically linked to acoustic features.

## The Gap: Embeddings Without Vocabulary

Existing multimodal models learn dense, opaque embedding spaces. MuLan aligns music and text in a shared vector space, but cannot tell you which specific terms best describe a given sound. CLAP generalizes across audio domains but does not reveal an interpretable vocabulary. These models answer "are this audio and this text related?" but not "what words should a human use to precisely describe this audio?" The vocabulary itself -- the set of terms, their definitions, their acoustic correlates -- remains unexamined.

## sunolanguage: Extracting the Explicit Bridge

sunolanguage addresses this gap. Rather than learning implicit embeddings, it extracts and curates the explicit, human-readable vocabulary that bridges music perception and language. This vocabulary is grounded in the sense Harnad described (terms mapped to acoustic features), leverages the crossmodal correspondences Spence documented (systematic sound-word mappings), and can serve as higher-quality input to the contrastive models that CLIP's lineage produced. The framework generalizes: for any sensory domain where (1) humans have developed descriptive language and (2) AI can process the sensory signal, the sensory-language-AI pipeline applies. Vision had it naturally through web-scale image-caption data. Music needs it built deliberately -- and that is what sunolanguage does.
