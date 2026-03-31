# Axis 4: Music Ontology - Paper Collection

> Systematic categorization and formal representation of musical elements in language.
> Collected: 2026-03-31

---

### [1] The Music Ontology
- **Authors**: Yves Raimond, Samer Abdallah, Mark Sandler, Frederick Giasson
- **Year**: 2007
- **Venue**: ISMIR 2007 (International Society for Music Information Retrieval Conference)
- **Key Contribution**: Foundational Semantic Web ontology for music, modeling the music production workflow (MusicalWork, MusicalManifestation, Performance). Built on RDF, defines editorial, cultural, and acoustic information structures. Used in DBTune and BBC Music.
- **Relevance to sunolanguage**: The MO defines the canonical entity model (work/performance/recording) that any music vocabulary must acknowledge. sunolanguage can map its AI-oriented vocabulary onto MO entities to maintain interoperability with existing metadata ecosystems.
- **URL**: https://ismir2007.ismir.net/proceedings/ISMIR2007_p417_raimond.pdf
- **Tags**: [ontology] [semantic-web] [RDF] [foundational]

---

### [2] MPEG-7 Multimedia Content Description Interface (Audio Part)
- **Authors**: ISO/IEC JTC 1/SC 29 (key contributors: Hyoung-Gook Kim et al. for audio signature work)
- **Year**: 2002 (standard); audio signature paper 2013
- **Venue**: ISO/IEC 15938 standard; related work in Sensors journal (2013)
- **Key Contribution**: International standard defining 17 low-level audio descriptors (spectral, timbral, harmonic) and high-level description schemes (audio signature, instrument timbre, sound recognition). Provides a formal vocabulary for acoustic feature description.
- **Relevance to sunolanguage**: MPEG-7's low-level descriptors (spectral centroid, harmonicity, etc.) map to the acoustic features Suno implicitly processes. The gap: MPEG-7 describes signal properties, not the natural-language tags (e.g., "warm," "punchy") that Suno's text encoder understands. sunolanguage bridges this signal-to-language gap.
- **URL**: https://en.wikipedia.org/wiki/MPEG-7 / https://pmc.ncbi.nlm.nih.gov/articles/PMC3606779/
- **Tags**: [standard] [audio-features] [low-level-descriptors] [signal]

---

### [3] Hornbostel-Sachs Classification of Musical Instruments
- **Authors**: Erich Moritz von Hornbostel, Curt Sachs
- **Year**: 1914 (original); English translation 1961; MIMO revision 2011
- **Venue**: Zeitschrift fur Ethnologie (1914); Galpin Society Journal (1961)
- **Key Contribution**: The most widely used instrument classification system in ethnomusicology. Hierarchical Dewey-like taxonomy with 5 top-level categories (idiophones, membranophones, chordophones, aerophones, electrophones) and 300+ subcategories based on sound production mechanism.
- **Relevance to sunolanguage**: H-S classifies by physics of sound production, which is orthogonal to how Suno categorizes instruments (by cultural role and sonic character, e.g., "acoustic guitar" vs. "nylon guitar"). sunolanguage needs a mapping between formal instrument taxonomies and the instrument tags Suno actually responds to.
- **URL**: https://en.wikipedia.org/wiki/Hornbostel%E2%80%93Sachs / https://www.isko.org/cyclo/hornbostel
- **Tags**: [taxonomy] [instruments] [ethnomusicology] [foundational]

---

### [4] A Taxonomy of Musical Genres
- **Authors**: Francois Pachet, Daniel Cazaly
- **Year**: 2000
- **Venue**: RIAO 2000 (Content-Based Multimedia Information Access), Paris
- **Key Contribution**: Analyzed inconsistencies in existing genre taxonomies from the music industry and Internet sources. Proposed a principled genre taxonomy where only terminal genres describe individual titles (not artists/albums). Used to annotate 5,000+ titles.
- **Relevance to sunolanguage**: Genre is the single most important tag dimension for Suno. Pachet's observation that existing genre taxonomies are inconsistent mirrors exactly the problem sunolanguage faces: Suno has its own implicit genre vocabulary that diverges from industry standards. This paper's methodology (principled taxonomy from messy real-world data) is directly applicable.
- **URL**: https://www.francoispachet.fr/wp-content/uploads/2021/01/pachet-00-RIAO.pdf
- **Tags**: [taxonomy] [genre] [classification] [methodology]

---

### [5] An Ontology for Audio Features
- **Authors**: Alo Allik, Gyorgy Fazekas, Mark B. Sandler
- **Year**: 2016
- **Venue**: ISMIR 2016
- **Key Contribution**: Proposed Semantic Web ontologies for (1) a common structure for audio feature data formats and (2) representing computational workflows of audio features. Addresses the interoperability problem between MIR feature extraction toolsets. Built on Event and Timeline ontologies.
- **Relevance to sunolanguage**: The AFO formalizes the relationship between audio features and their extraction context. sunolanguage could reference AFO concepts when documenting which acoustic features correlate with which Suno-understood text descriptors (e.g., "bright" correlates with high spectral centroid).
- **URL**: https://archives.ismir.net/ismir2016/paper/000077.pdf
- **Tags**: [ontology] [audio-features] [MIR] [interoperability]

---

### [6] Sound and Music Recommendation with Knowledge Graphs
- **Authors**: Sergio Oramas, Vito Claudio Ostuni, Tommaso Di Noia, Xavier Serra, Eugenio Di Sciascio
- **Year**: 2017
- **Venue**: ACM Transactions on Intelligent Systems and Technology
- **Key Contribution**: Created and exploited a knowledge graph for music/sound recommendation, extracting entities from textual descriptions and linking them to external graphs (WordNet, DBpedia). Demonstrated hybrid recommendation using structured knowledge + content features.
- **Relevance to sunolanguage**: Demonstrates how textual music descriptions can be mapped to structured knowledge. sunolanguage performs an analogous task: mapping human music language (leomusic-base) to a structured vocabulary that an AI engine (Suno) can interpret. The entity extraction and linking methodology is relevant.
- **URL**: https://dl.acm.org/doi/10.1145/2926718
- **Tags**: [knowledge-graph] [recommendation] [NLP] [entity-linking]

---

### [7] DOREMUS: A Graph of Linked Musical Works
- **Authors**: Manel Achichi, Pasquale Lisena, Konstantin Todorov, Raphael Troncy, Jean Delahousse
- **Year**: 2018
- **Venue**: ISWC 2018 (International Semantic Web Conference)
- **Key Contribution**: Linked knowledge graphs from three major French cultural institutions (BnF, Radio France, Philharmonie de Paris) for classical music. Extended CIDOC-CRM and FRBRoo ontologies to model musical works, performances, and catalog metadata.
- **Relevance to sunolanguage**: DOREMUS shows how different institutions' music vocabularies can be aligned through a shared ontology. sunolanguage faces a parallel challenge: aligning human music vocabulary (leomusic-base) with Suno's implicit vocabulary. The alignment methodology is instructive.
- **URL**: https://link.springer.com/chapter/10.1007/978-3-030-00668-6_1
- **Tags**: [knowledge-graph] [linked-data] [cultural-heritage] [alignment]

---

### [8] Audio Commons Ontology: A Data Model for an Audio Content Ecosystem
- **Authors**: Miguel Ceriani, Gyorgy Fazekas
- **Year**: 2018
- **Venue**: ISWC 2018
- **Key Contribution**: Data model for integrating multiple audio content repositories (music tracks, samples, loops, sound effects). Extends FRBR, relates to Music Ontology, EBU Core, and Creative Commons ontologies. Designed for programmatic access by software agents.
- **Relevance to sunolanguage**: The AC ontology's focus on making audio content accessible to software agents parallels sunolanguage's goal of making music descriptions accessible to an AI engine. The ontology's distinction between musical and non-musical audio content is relevant for understanding what categories of sound description Suno can process.
- **URL**: https://link.springer.com/chapter/10.1007/978-3-030-00668-6_2
- **Tags**: [ontology] [audio-content] [interoperability] [software-agents]

---

### [9] The Music Meta Ontology: A Flexible Semantic Model for the Interoperability of Music Metadata
- **Authors**: Jacopo de Berardinis, Valentina Anita Carriero, Nitisha Jain, Nicolas Lazzari, Albert Merono-Penuela, Andrea Poltronieri, Valentina Presutti
- **Year**: 2023
- **Venue**: ISMIR 2023
- **Key Contribution**: Core module of the Polifonia Ontology Network. Flexible semantic model for music metadata (artists, compositions, performances, recordings, links). Uses eXtreme Design methodology, provides alignments to Music Ontology, DOREMUS, and Wikidata. Addresses cultural and temporal diversity in music description.
- **Relevance to sunolanguage**: The most recent comprehensive music metadata ontology. Its emphasis on flexibility and cross-schema alignment directly informs how sunolanguage should structure its vocabulary to be both rigorous and adaptable. The acknowledgment of cultural bias in existing ontologies resonates with sunolanguage's need to capture diverse musical traditions.
- **URL**: https://archives.ismir.net/ismir2023/paper/000102.pdf
- **Tags**: [ontology] [metadata] [interoperability] [recent]

---

### [10] The Polifonia Ontology Network: Building a Semantic Backbone for Musical Heritage
- **Authors**: Jacopo de Berardinis, Albert Merono-Penuela, Andrea Poltronieri, Valentina Presutti et al.
- **Year**: 2023
- **Venue**: ISWC 2023
- **Key Contribution**: Modular ontology network for music cultural heritage with four core modules: Music Meta (metadata), Representation (content), Source (provenance), Instrument (cultural objects). Designed with stakeholder requirements and competency questions. Includes NLP toolkit for ontology engineering support.
- **Relevance to sunolanguage**: The modular architecture (separating metadata, content representation, instruments, provenance) offers a blueprint for how sunolanguage could organize its own vocabulary dimensions. The instrument module's cultural-heritage perspective complements Hornbostel-Sachs with cultural context.
- **URL**: https://link.springer.com/chapter/10.1007/978-3-031-47243-5_17
- **Tags**: [ontology-network] [modular] [cultural-heritage] [instruments]
