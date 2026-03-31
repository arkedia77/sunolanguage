# Axis 4: Music Ontology - Synthesis

> How existing music ontologies inform the sunolanguage project.
> 2026-03-31

---

## The Landscape of Music Ontologies

Over the past two decades, the music research community has produced a rich ecosystem of formal knowledge representations for music. The foundational Music Ontology (Raimond et al., 2007) established the canonical RDF-based model for describing the music production workflow: works, performances, recordings, and their relationships. This was complemented by domain-specific efforts: MPEG-7 (ISO/IEC 15938) standardized 17 low-level audio descriptors for signal-level content description; the Audio Feature Ontology (Allik et al., 2016) addressed interoperability between MIR feature extraction tools; and the Audio Commons Ontology (Ceriani & Fazekas, 2018) modeled audio content ecosystems for programmatic access by software agents.

For metadata interoperability, DOREMUS (Achichi et al., 2018) demonstrated how institutional music catalogs can be linked through extensions of cultural heritage standards (CIDOC-CRM, FRBRoo). Most recently, the Polifonia Ontology Network (de Berardinis et al., 2023) introduced a modular architecture with dedicated modules for metadata, content representation, provenance, and instruments -- explicitly addressing the cultural biases embedded in earlier, Western-centric models.

## Categorization Strategies

These ontologies handle musical elements through distinct strategies. **Instruments** are classified either by physics (Hornbostel-Sachs's sound-production mechanism: idiophones, membranophones, etc.) or by cultural role (Polifonia's instrument module). **Genres** remain notoriously difficult to formalize; Pachet & Cazaly (2000) documented the inconsistencies across industry taxonomies and proposed principled guidelines, but no universal genre ontology has achieved consensus. **Audio features** are described at the signal level (MPEG-7 spectral descriptors) or the semantic level (mood, timbre labels), with Oramas et al. (2017) showing how knowledge graphs can bridge textual descriptions and structured feature representations.

## The Gap: Formal Description vs. AI Understanding

All of these ontologies share a critical assumption: their target consumer is a human researcher, librarian, or traditional software system. They describe music as it *is* (acoustically, culturally, bibliographically) but do not address what an AI music generation engine *actually understands* from text prompts. MPEG-7 can represent spectral centroid with precision, but Suno does not accept "spectral centroid: 3500 Hz" as input. The Music Ontology can model a performance event with full provenance, but Suno needs "dreamy lo-fi beat with warm Rhodes piano."

This is the fundamental gap that sunolanguage occupies. Existing ontologies provide the formal scaffolding -- the categories, relationships, and descriptive dimensions that music knowledge requires. But they stop at description. They do not answer: "Which of these descriptors actually produce the intended sonic result when fed to an AI engine?"

## Connection to leomusic-base and sunolanguage

**leomusic-base** organizes all musical elements into human-understandable language -- a comprehensive vocabulary of instruments, genres, moods, techniques, and production styles drawn from real music knowledge. It is, in effect, a practical music ontology built from production experience rather than academic formalism.

**sunolanguage** then filters this vocabulary through empirical testing against Suno's actual behavior. It asks: does Suno distinguish "nylon guitar" from "classical guitar"? Does "ethereal" produce different results from "dreamy"? Which genre combinations create coherent outputs vs. confused ones?

The existing ontology literature tells us *what dimensions matter* (instrument taxonomy, genre hierarchy, audio features, mood descriptors). leomusic-base captures *how musicians actually talk about these dimensions*. sunolanguage determines *which of these terms an AI engine can meaningfully act upon*. Together, they form a three-layer stack: formal ontology (academic) -> human music language (leomusic-base) -> AI-effective vocabulary (sunolanguage).

This positioning -- grounded in established ontological frameworks but oriented toward AI-engine pragmatics -- is, to our knowledge, unexplored in the existing literature.
