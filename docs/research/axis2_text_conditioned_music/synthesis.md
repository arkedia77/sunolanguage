# Axis 2 Synthesis: Text-Conditioned Music Generation and sunolanguage

> 2026-03-31 | sunolanguage project

## Current State of Text-to-Music AI

Text-conditioned music generation has advanced rapidly since 2022. The field follows two main architectural paths: (1) autoregressive token-based models (MusicLM, MusicGen) that treat music as a sequence of discrete codes and condition generation on text embeddings, and (2) diffusion-based models (Noise2Music, Mousai, Stable Audio, JEN-1) that denoise latent representations guided by text encoders. Both approaches have reached the point of generating coherent, multi-minute musical audio from natural language prompts. A 2025 survey (Zhao et al.) further categorizes these into traditional, hybrid, and LLM-centric frameworks, noting that LLM integration is accelerating.

## How These Models Process Text

The text-conditioning pipeline typically involves three stages. First, text is encoded by a pretrained language model -- either a contrastive audio-text encoder (MuLan, CLAP) or a general-purpose text encoder (T5, as used in MusicGen and Stable Audio). Second, these embeddings guide the generative process, either as conditioning tokens in an autoregressive decoder or as cross-attention inputs in a diffusion U-Net/DiT. Third, the model's actual responsiveness to text is bounded by its training data: the music-text pairs it was trained on determine which words and phrases reliably influence the output.

This creates a critical asymmetry. The text encoder can represent virtually any English sentence, but the generator only learned associations for vocabulary that appeared in its training metadata. Noise2Music explicitly demonstrates this by using LLMs to fabricate pseudo-captions for training data -- the generated captions define the model's effective vocabulary. LP-MusicCaps takes this further, creating 2.2M captions from music tags, revealing that the bridge between music and language is built on a relatively constrained set of descriptive terms (genre, mood, tempo, instrumentation, texture).

## The Vocabulary Opacity Gap

None of the surveyed models expose which words they actually understand. MuLan learns a joint embedding space where certain text clusters near certain audio -- but which text? CLAP maps 630K audio-text pairs into a shared space -- but which phrases carry weight? MusicGen conditions on T5 embeddings of free-text prompts -- but which tokens meaningfully steer generation versus being ignored? The answer is always locked inside the model weights, inaccessible to users.

This is the gap sunolanguage addresses. Rather than probing model internals or running ablation studies on open-source models, sunolanguage takes an empirical, black-box approach: feed real music into Suno, collect the prompts Suno generates to describe that music, and aggregate the vocabulary Suno actually uses. This produces a ground-truth inventory of the words Suno's system considers meaningful for music description and generation.

## Connection to sunolanguage's 3-Layer Vocabulary

The literature implicitly supports the existence of vocabulary layers. Training data for text-to-music models typically contains: (1) high-level style descriptors (genre, mood, era) -- corresponding to sunolanguage's Style Prompts layer; (2) instrument-specific cues that appear inline in captions ("distorted guitar riff," "pizzicato strings") -- matching the Inline Instrument Cues layer; and (3) production-level descriptors for individual stems or sonic textures ("reverb-heavy pad," "punchy kick") -- aligning with the Stem-level descriptors layer. MusicCaps annotations, LP-MusicCaps pseudo-captions, and LAION-Audio metadata all exhibit this layered structure, though no prior work has formalized it. Sunolanguage's contribution is making this hierarchy explicit and grounding it in empirical data extracted from a commercial system.
