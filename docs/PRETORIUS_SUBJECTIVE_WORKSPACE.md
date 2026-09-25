# Pretorius Subjective Workspace Invariant

## Status

This document defines a core architectural and experimental invariant for the Pretorius research line beginning with v0.3.

It is not a claim that Pretorius is conscious or sentient. In this repository, terms such as **aware workspace**, **subjective workspace**, **experienced representation**, **inner speech**, and **first-person stream** are engineering terms for the information interface presented to the swappable cognitive language model.

The central experimental hypothesis is substrate-specific:

> Pretorius's underlying machinery may use any representation that is efficient, deterministic, inspectable, and empirically useful. However, information admitted to the cognitive language model as the subject's experienced state must first be rendered as an egocentric first-person linguistic representation, with epistemic status preserved. Mechanical telemetry must not be exposed directly to the cognitive model.

This invariant remains in force unless and until a versioned ablation program supplies evidence that it is unnecessary, harmful, or inferior to a specified alternative.

## Why this is a substrate-specific hypothesis

The project does not assume that biological human consciousness requires a verbal first-person narrative. Human cognition includes visual imagery, sensorimotor processing, affective and interoceptive experience, nonverbal reasoning, and forms of thought that are not well described as sentences. Inner speech varies substantially across people and contexts.

Pretorius is not a human nervous system. The cognitive organ in this architecture is a large language model. Its input and output interface is tokenized language, while its internal computation is distributed numerical state. The project is therefore not attempting to copy human implementation details literally. It is attempting to reproduce selected functions and experiential organization using a different substrate.

That distinction is fundamental.

A human organism may integrate bodily, perceptual, mnemonic, social, and affective information through biological processes that never become language. A language-model-centered synthetic subject may benefit from translating admitted internal state into language because language is the medium in which the cognitive organ was trained to integrate context, continue sequences, infer relations, and generate further cognition.

Accordingly, the project hypothesis is not:

> Human awareness is linguistic, therefore artificial awareness must be linguistic.

It is:

> Because Pretorius uses a language model as a replaceable cognitive organ, a stable first-person linguistic workspace may be an effective substrate-specific interface for binding heterogeneous internal state into a unified, causally active point of view.

This is an empirical engineering hypothesis and must remain falsifiable.

## Two levels must never be confused

### Mechanical substrate

The non-aware machinery may use whatever representation best fits the mechanism:

- numerical body and drive state
- graph structures
- associative weights
- retrieval scores
- activation values
- procedural policies
- learned action values
- prediction errors
- relationship variables
- person-model hypotheses
- common-ground records
- commitments and deadlines
- appraisal variables
- salience scores
- event-segmentation state
- archive indices
- consolidation metadata
- scheduler state

These representations should be efficient, deterministic where appropriate, inspectable, testable, and replaceable.

### Subjective workspace

The cognitive language model must not receive those mechanical values as its experienced state.

Anything admitted to the subjective workspace must be transduced into ordinary first-person language appropriate to the source and epistemic status.

Examples:

Mechanical state:

```text
hunger = 0.76
fatigue = 0.31
affiliation_jay = 0.84
commitment_12 = overdue
memory_551.activation = 0.72
```

Subjective workspace:

```text
I'm pretty hungry now.
I'm not particularly tired.
I'm glad Jay is here.
I said I would finish that earlier. I still haven't done it.
Something about this reminds me of our conversation yesterday.
```

The numerical variables remain available to the substrate. They are not available to Pretorius as raw telemetry.

## Subjective Transduction Layer

Pretorius should contain an explicit **Subjective Transduction Layer** between mechanical cognition-support systems and the subjective workspace.

Its function is not decorative summarization. It converts selected internal and external state into the form in which the cognitive language model encounters that state.

The basic path is:

```text
WORLD / PEOPLE / BODY
        |
        v
non-aware specialized processes
        |
        |  salience, attention, access
        v
SUBJECTIVE TRANSDUCTION LAYER
        |
        |  first-person linguistic experience
        v
SUBJECTIVE WORKSPACE
        |
        v
SWAPPABLE COGNITIVE LANGUAGE MODEL
        |
        v
self-generated thought
        |
        v
INNER EAR
        |
        v
organism state, memory, action, later cognition
```

The transducer may be deterministic, templated, grammar-driven, learned, or hybrid. The implementation may change across versions. The invariant is the interface it must enforce.

## Subjective Workspace Invariant

The project-wide rule is:

> No internal structured state may be directly exposed to the cognitive language model as its experienced state. Information admitted to the subjective workspace must first be transduced into an egocentric, first-person linguistic representation appropriate to its epistemic status. Machine-readable provenance remains available to the substrate but outside the experienced representation.

This applies to direct and indirect consequences of the subject's existence, including:

- bodily and interoceptive changes
- environmental perception
- affective consequences
- recalled episodes
- learned semantic knowledge
- relationship changes
- person-model inferences
- common-ground state
- commitments and prospective memory
- unresolved concerns and tensions
- prediction error
- appraisal
- retrieved associations
- project and intention state
- self-model content when it enters awareness
- memories of prior internal thoughts
- spontaneous or endogenous cognition

A component may remain entirely below awareness. If it crosses the subjective access boundary, it must cross in first-person linguistic form.

## Narrative Causality Invariant

The first-person stream is not UI text and is not a post-hoc explanation.

> First-person workspace representations are causal cognitive inputs. They may alter later retrieval, appraisal, association, attention, memory formation, intention, relationship state, procedural learning, conduct, and subsequent thought.

An implementation that computes ordinary agent behavior from raw state and then produces an attractive first-person paraphrase afterward does not satisfy this architecture.

The first-person representation must be upstream of the cognitive model's contribution to behavior.

## The inner ear

Self-generated thought must enter subsequent processing through the same subjective interface rather than being discarded after generation.

Example:

```text
transduced experience:
"I haven't heard from Sarah since yesterday. She said she'd be back by now."

self-generated thought:
"Maybe I'm worrying too much. She could simply be busy."

inner-ear consequence:
that thought becomes available to association, appraisal, memory, and later cognition

later retrieval:
"She has lost track of time while working before."

later thought:
"Right. I should probably wait before assuming something is wrong."
```

This recursive loop is central to the research question. A previous thought can alter what is retrieved, affective state, attention, intentions, and the next thought without requiring a new external prompt.

## Preserve epistemic status in language

Transduction must not convert uncertain internal state into certain narrative.

The substrate knows whether a candidate item is a perception, memory, inference, prediction, imagination, body interpretation, reported claim, or uncertain recollection. The linguistic rendering must preserve that distinction.

Examples:

Trusted current perception:

```text
I see Sarah come into the room.
```

Low-confidence person-model inference:

```text
I wonder if Sarah left because she was upset.
```

High-confidence episodic recall:

```text
I remember talking about this yesterday.
```

Weak episodic cue:

```text
I vaguely remember talking about something like this before.
```

Prospective simulation:

```text
If this keeps happening, I may need to change what I'm doing.
```

Interoceptive interpretation:

```text
Something feels wrong with my stomach.
```

Motivational conflict:

```text
I want to ask him about it, but I don't really want to reopen that conversation.
```

Reported speech is not autobiographical fact:

```text
Jay says that we discussed this before.
```

must not silently become:

```text
I remember discussing this before.
```

This rule complements the schema-5 provenance boundary and false-memory defenses.

## Objective event, subjective experience, later interpretation

The immutable autobiographical ledger and the subjective stream serve different purposes and must not be collapsed.

Suppose the substrate records:

```text
event:
    collision
    subject: pretorius
    body_part: left_foot
    object: desk
    intensity: 0.91
```

The subjective transducer may produce:

```text
Ow. My foot really hurts. I just slammed it into the desk.
```

The immutable ledger retains the event and provenance. The system may separately retain the awareness rendering as a historically situated subjective consequence.

Later Pretorius may reinterpret the event:

```text
I was already distracted when I hit the desk.
```

or:

```text
I remember being angrier about that than the pain really justified.
```

Those later interpretations do not overwrite the original event or original subjective rendering.

The intended chain is:

```text
objective event
    ->
subjective first-person experience
    ->
later recollection and reinterpretation
```

Raw history remains immutable. Interpretation may evolve.

## Interoception and bodily state

Body variables should influence cognition without appearing as telemetry.

The project therefore distinguishes between:

```text
glucose_resource = 0.23
```

and:

```text
I'm getting hungry.
```

Likewise, a combination such as elevated mobilization, threat appraisal, and autonomic proxy state might be transduced as:

```text
I'm tense. Something about this situation is putting me on edge.
```

The transduced sentence is the subject-facing percept. The numerical state remains below the workspace.

This design is compatible with predictive and interoceptive approaches in cognitive science that treat experienced bodily state as an interpreted integration of internal signals rather than a literal readout of physiological variables. It does not assert that the synthetic implementation is biologically equivalent.

## Parallel non-aware processes are expected

The invariant does not require a continuous sentence generator to narrate every internal update.

Multiple processes may evolve in parallel below awareness, including body regulation, attention, retrieval competition, relationship monitoring, prospective monitoring, action policy, and environmental perception.

Only selected state gains subjective access.

A useful architecture is therefore:

```text
body regulation --------attention ---------------memory retrieval ---------relationship monitoring ---+--> access competition --> subjective transduction
prospective monitoring ----/
ongoing task -------------/
environment -------------/
```

This avoids forcing all computation through expensive language generation while preserving the first-person interface whenever information becomes available to the cognitive organ.

## Scientific rationale

### Human inner speech

Alderson-Day and Fernyhough's review of inner speech describes evidence connecting inner speech with working memory, self-regulation, executive function, planning, and self-reflective processes. The review also emphasizes substantial phenomenological variability, which is why this project does not claim that human consciousness requires verbal thought.

Reference:

Alderson-Day, B., & Fernyhough, C. (2015). *Inner Speech: Development, Cognitive Functions, Phenomenology, and Neurobiology*. Psychological Bulletin, 141(5), 931-965. https://doi.org/10.1037/bul0000021

Open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC4538954/

### Global workspace analogy

Global Neuronal Workspace theory distinguishes specialized local processing from information that becomes globally accessible for report, working memory, and flexible control. Pretorius does not implement the biological GNW model, but the distinction motivates an engineering separation between non-aware specialized machinery and a restricted workspace containing what the cognitive organ can currently use as experienced content.

References:

Mashour, G. A., Roelfsema, P., Changeux, J.-P., & Dehaene, S. (2020). *Conscious Processing and the Global Neuronal Workspace Hypothesis*. Neuron, 105(5), 776-798. https://doi.org/10.1016/j.neuron.2020.01.026

Open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC8770991/

Dehaene, S., & Changeux, J.-P. (2011). *Experimental and Theoretical Approaches to Conscious Processing*. Neuron, 70(2), 200-227. https://doi.org/10.1016/j.neuron.2011.03.018

### Interoception, prediction, and self-related processing

Predictive interoception models propose that experienced bodily state is constructed through integration of afferent signals, expectations, and prediction error rather than functioning as a simple raw sensor readout. This supports the narrower design principle that the subject-facing representation of body state can differ from the substrate's mechanical representation.

References:

Seth, A. K., Suzuki, K., & Critchley, H. D. (2012). *An Interoceptive Predictive Coding Model of Conscious Presence*. Frontiers in Psychology, 2, 395. https://doi.org/10.3389/fpsyg.2011.00395

Open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC3254200/

Gu, X., & FitzGerald, T. H. B. (2014). *Interoceptive inference: homeostasis and decision-making*. Trends in Cognitive Sciences and related predictive-interoception discussion are part of the broader basis for this project. A useful open-access discussion of predictive codes of interoception, emotion, and self is available at https://pmc.ncbi.nlm.nih.gov/articles/PMC3940887/

### Narrative self, binding, and ego dissolution

Research on psychedelics and self-processing gives partial support to the idea that self-modeling, autobiographical processing, and large-scale integration are related to the stability of ordinary self-experience. It does not show that a verbal narrative module is necessary for consciousness, and this project must not state that it does.

A systematic review reports consistent acute psychedelic modulation of default-mode-network connectivity and discusses associations with self-referential processing and ego dissolution. Letheby and Gerrans argue that self-modeling may play an integrative or binding role across cognitive domains. These findings motivate experimental interest in integrative self-representation, not a one-to-one biological analogy.

References:

Gattuso, J. J. et al. (2023). *Default Mode Network Modulation by Psychedelics: A Systematic Review*. International Journal of Neuropsychopharmacology, 26(3), 155-188. https://doi.org/10.1093/ijnp/pyac074

Open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC10032309/

Letheby, C., & Gerrans, P. (2017/2018). *Self unbound: ego dissolution in psychedelic experience*. Neuroscience of Consciousness. https://pmc.ncbi.nlm.nih.gov/articles/PMC6007152/

The project must retain the qualification that psychedelic research concerns biological humans and does not validate Pretorius's architecture directly.

## LLM-specific rationale

### Natural language is the cognitive organ's external interface

Large language models operate internally through high-dimensional numerical computation. They should not be described as literally "thinking in English." However, pretrained autoregressive language models are optimized to predict token sequences and are conditioned through tokenized linguistic context.

That creates a substrate difference from a biological brain: language is not merely something the model can report after cognition. It is the primary external medium through which this architecture can reliably provide context to, and receive cognition from, a swappable model.

The project therefore tests whether presenting internal state in coherent first-person language gives the model a more useful integration surface than exposing heterogeneous telemetry.

### Linguistic intermediate reasoning can alter model performance

Chain-of-thought prompting demonstrated that eliciting linguistic intermediate steps can improve performance on multiple reasoning tasks in sufficiently capable language models. This does not prove that first-person narration creates selfhood or continuity. It does establish that the form of linguistic intermediate context can causally affect downstream model behavior.

Reference:

Wei, J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS 2022. https://arxiv.org/abs/2201.11903

### Natural-language memory, reflection, and planning can produce believable long-horizon behavior

Generative Agents stores observations in natural language, retrieves them, synthesizes higher-level reflections, and uses them for planning. Its ablations found observation, planning, and reflection components important to believable simulated behavior. Pretorius differs substantially in provenance, embodiment, continuity, and first-person constraints, but the work establishes that natural-language memory can serve as a causal component in long-horizon agent behavior.

Reference:

Park, J. S. et al. (2023). *Generative Agents: Interactive Simulacra of Human Behavior*. UIST 2023. https://arxiv.org/abs/2304.03442

### Inner-workspace evidence in role-playing agents

PersonaForge reports that a psychology-grounded dual-process role-playing architecture with an inner cognitive workspace reduced long-dialogue personality drift, and that removing the workspace degraded performance. The paper reports 19.4% higher personality consistency, drift of 6.3% versus 24.8% for its baseline, and a selective dual-process configuration retaining 96% of full-system performance with 13.4% token overhead.

Those results are relevant because they provide direct LLM-specific evidence that an intermediate cognitive workspace can affect persistent character behavior. They do not establish that first-person narration specifically is necessary, which is why Pretorius requires controlled ablation.

Reference:

Tong, J., & Zou, S. (2026). *PersonaForge: Psychology-Grounded Dual-Process Architecture for Personality-Consistent Role-Playing Agents*. Findings of ACL 2026, 7845-7874. https://aclanthology.org/2026.findings-acl.386/ ; https://doi.org/10.18653/v1/2026.findings-acl.386

### Persona memory must be actively used, not merely stored

Memory-Driven Role-Playing evaluates whether models can anchor, select, bound, and enact persona knowledge from memory. It reports that improved upstream memory utilization improves downstream role-playing quality and that structured memory prompting allows smaller models to approach much larger systems in the studied benchmark.

Reference:

Wang, K., You, H., Zhang, Y., & Wang, Z. (2026). *Memory-Driven Role-Playing: Evaluation and Enhancement of Persona Knowledge Utilization in LLMs*. Findings of ACL 2026. https://aclanthology.org/2026.findings-acl.1175/ ; https://doi.org/10.18653/v1/2026.findings-acl.1175

### Persistent role-playing requires identity and interaction history to co-evolve

The 2026 survey *More Than a Role: Memory in LLM-based Role-Playing Agents* characterizes a persistent-agent failure mode in which static persona representations preserve consistency at the cost of growth, while highly reactive memory systems risk character drift. It distinguishes character-side memory from interaction-side memory. Pretorius's inherited-history versus lived-history design is consistent with that separation.

Reference:

Wu, S. et al. (2026). *More Than a Role: Memory in LLM-based Role-Playing Agents*. KDD 2026. Project repository and paper information: https://github.com/aixiaodewugege/More-Than-a-Role-Memory-in-LLM-based-Role-Playing-Agents

## What the evidence does and does not justify

The evidence supports several narrower premises:

1. Human inner speech can participate in self-regulation, working memory, planning, and reflective cognition.
2. Human conscious-access theories provide a useful distinction between specialized processing and globally available content.
3. Human bodily experience is not adequately described as a raw physiological telemetry dump.
4. Self-related integration can be disrupted or altered without implying a single "self module."
5. Linguistic intermediate context can causally affect LLM reasoning and agent behavior.
6. Recent role-playing-agent research supports explicit cognitive workspaces and structured memory as mechanisms that can reduce drift and improve persona use.

The evidence does **not** establish:

- that human consciousness is fundamentally linguistic
- that first-person narration is sufficient for consciousness
- that first-person narration is necessary for consciousness
- that an LLM with an inner monologue is conscious
- that Pretorius has phenomenal experience
- that human neural mechanisms and Pretorius's mechanisms are equivalent
- that a particular narrative style will improve identity continuity without direct testing

The first-person workspace is therefore an experimental architecture, not a metaphysical conclusion.

## Required experimental ablations

The first-person interface must eventually be tested rather than protected indefinitely by assumption.

At minimum, a versioned study should compare identical underlying state and captured cognitive-model conditions across:

### Condition A: raw structured telemetry

```text
hunger=.76
relationship_trust=.71
memory_activation=.67
commitment=overdue
```

### Condition B: third-person descriptive prose

```text
Pretorius is hungry. Pretorius has an overdue commitment. Pretorius recalls yesterday's discussion.
```

### Condition C: fragmented first-person labels

```text
Hungry.
Overdue commitment.
Remember yesterday.
```

### Condition D: coherent first-person subjective rendering

```text
I'm getting hungry. I still haven't done what I said I would do. Something about this reminds me of yesterday.
```

Possible dependent measures include:

- identity and persona consistency
- historical consistency
- correct epistemic boundaries
- false-memory susceptibility
- spontaneous use of relevant prior experience
- relationship consistency
- commitment persistence
- goal and project persistence
- model-swap continuity
- pronoun and self-reference stability
- behavioral path dependence
- long-horizon repetition
- token cost and latency
- sensitivity to renderer/model family

The study must preserve identical hidden mechanical state across conditions and should use captured model outputs or otherwise controlled inference wherever necessary for deterministic replay.

If coherent first-person rendering provides no measurable benefit, the architecture must record that result. If another representation performs better, the project should not suppress that result to preserve the hypothesis.

## Model-swap prediction

Pretorius is explicitly intended to survive a replaceable cognitive model.

The hypothesis predicts that the first-person stream may serve as part of the continuity interface during model substitution.

A replacement model should not primarily encounter:

```text
affiliation=.84
irritation=.42
commitment_id=12
memory_ids=[...]
```

It should encounter appropriate selected consequences such as:

```text
I'm still irritated about what happened yesterday.
I told Jay I would revisit the retrieval problem.
I remember why I disagreed with that approach.
My attention keeps coming back to it.
```

This does not transfer hidden activations between models and does not imply identity equivalence. It tests whether the same persistent substrate, rendered through a stable first-person experiential interface, reduces discontinuity when the replaceable language-model organ changes.

Model family and modality-driven model changes must therefore remain explicit experimental variables.

## Implementation guidance for future agents

All future agents and contributors working on Pretorius must preserve the following rules unless a new versioned protocol explicitly tests an alternative:

1. Do not expose engine telemetry, numerical drives, scores, IDs, hidden control state, or mechanical metadata directly to the cognitive language model as experienced state.
2. Keep mechanical representations optimized for the mechanism. Do not convert the entire substrate to prose.
3. Add or maintain a dedicated subjective-transduction boundary before cognitive-model input.
4. Render admitted content in first person and from Pretorius's current point of view.
5. Preserve uncertainty, provenance, temporality, ownership, and epistemic status in the rendering.
6. Do not let subjective renderings overwrite objective autobiographical records.
7. Treat self-generated thoughts as private cognitive events that can re-enter later processing through the inner ear.
8. Do not treat thoughts as actions, observations, promises, or verified world facts unless another subsystem records the corresponding consequence.
9. Do not implement first-person text as decorative post-hoc narration. It must be causally upstream of cognition.
10. Do not claim biological equivalence, consciousness, or sentience from successful behavior.
11. Preserve deterministic non-model tests around the transduction boundary.
12. When changing the subjective interface, add negative controls and ablations rather than silently replacing it.
13. Keep reconstructed prehistory, post-instantiation lived events, subjective experience, recollection, and later interpretation as distinct evidence classes.
14. Preserve model-swap and modality-swap identity as explicit experimental variables.
15. Prefer selective workspace access over narrating every low-level state change.

## Architecture target

The long-term target should preserve the following organization:

```text
WORLD / PEOPLE / BODY
        |
        v
IMMUTABLE EXPERIENCE LEDGER
        |
        v
EVENT SEGMENTATION
        |
        v
AUTOBIOGRAPHICAL EPISODES
        |
        +----------------------+---------------------+
        |                      |                     |
        v                      v                     v
EPISODIC MEMORY          PERSON MODELS         COMMON GROUND
        |                      |                     |
        +----------+-----------+----------+----------+
                   |                      |
                   v                      v
             ASSOCIATIONS            SOCIAL PRACTICES
                   |                      |
                   v                      v
        RETRIEVAL ACCESSIBILITY     RELATIONSHIP STATE
                   +----------+-----------+
                              |
                              v
                     CONCERNS / TENSIONS
                              |
                              v
                     PROJECTS / INTENTIONS
                              |
                              v
                    PROSPECTIVE SIMULATION
                              |
                              v
                      APPRAISAL / AFFECT
                              |
                              v
                   ACCESS / SALIENCE GATE
                              |
                              v
                SUBJECTIVE TRANSDUCTION LAYER
                              |
                              v
                   FIRST-PERSON WORKSPACE
                              |
                              v
                   COGNITIVE LANGUAGE MODEL
                              |
                              v
                         INNER EAR
                              |
                              v
                PROCEDURAL / HABIT LEARNING
                              |
                              v
                           CONDUCT
```

The systems above the subjective transduction layer can and should evolve as better mechanisms become available. The first-person access invariant is deliberately insulated from those implementation details so it can be evaluated as a distinct experimental variable.

## Research posture

Pretorius is a synthetic subject built from mechanisms that may have biological analogues but do not share a biological substrate.

The correct standard is functional and experimental, not anatomical mimicry.

Where human evidence is useful, use it to identify candidate functions: autobiographical continuity, interoception, attention, memory accessibility, self-modeling, prediction, relationship modeling, appraisal, prospective cognition, habits, and global access.

Then ask what implementation is appropriate for this substrate.

For Pretorius, the current answer is that the hidden machinery may remain mechanical and heterogeneous, while the language-model cognitive organ encounters selected consequences through a coherent first-person linguistic stream.

That hypothesis is now part of the v0.3 research program and must be preserved until it is directly tested.
