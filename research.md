---
layout: page
title: Research Areas
description: Honey Lab research - temporal processing, spontaneous thought, memory, brain networks, and AI
---

<section class="research-topic">
    <div class="container">
        <div class="research-summary">
            <div class="research-image">
                <img src="{{ '/assets/images/research/psychological-momentum.png' | relative_url }}" alt="Psychological Momentum">
            </div>
            <div class="research-intro">
                <h2>Momentum in our Thoughts</h2>
                <p>When we finish a book or leave a conversation, the experience does not simply stop. For some experiences, ideas and themes continue to surface in our thoughts for hours. We study how and why certain mental content persists beyond the experiences that produced it, and what this reveals about the organization of thought.</p>
                <details class="research-details">
                    <summary>Read more</summary>
                    <div class="research-expanded">
                        <p>People commonly report that an idea or past experience is "stuck in their head" or "on their minds." To investigate this process, we developed a paradigm for inducing lingering mental content and measuring its persistence. Participants generate chains of free associates ("word chains") that provide an index of their ongoing thought, both before and after engaging with a complex narrative. By comparing the word chains before and after reading, we can quantify the changes in thought induced by the story. We also measure activity in the brain before, during and after reading.</p>
                        <p>We find that both general story themes and specific narrative entities persist in spontaneous thought, and that this persistence is related to neural activity during the original experience. We call this phenomenon "psychological momentum," and we are investigating how it relates to memory formation and the brain's default mode network.</p>
                        <p class="research-papers">
                            <strong>Example papers:</strong>
                            <a href="https://www.nature.com/articles/s41467-022-32113-6">Bellana, Mahabal &amp; Honey (2022) <em>Nature Communications</em></a>;
                            <a href="https://journals.sagepub.com/doi/10.1177/09637214221143053">Honey, Mahabal &amp; Bellana (2023) <em>Current Directions in Psychological Science</em></a>
                        </p>
                    </div>
                </details>
            </div>
        </div>
    </div>
</section>

<section class="research-topic alt">
    <div class="container">
        <div class="research-summary">
            <div class="research-image research-image-hover" style="text-align: center">
                <img src="{{ '/assets/images/research/thinking-robot-bw.jpg' | relative_url }}" alt="Minds and Machines" style="max-width: 70%; margin: 0 auto">
                <img src="{{ '/assets/images/research/thinking-robot-amber.jpg' | relative_url }}" alt="Minds and Machines (amber highlight)" class="research-image-alt" style="max-width: 70%; margin: 0 auto">
            </div>
            <div class="research-intro">
                <h2>Minds &amp; Machines</h2>
                <p>Many of the principles that organize processing in the brain also appear in artificial neural networks. We study the parallels between biological and artificial learning systems, and we probe cognitive abilities in large language models.</p>
                <details class="research-details">
                    <summary>Read more</summary>
                    <div class="research-expanded">
                        <p>Our work on temporal integration in the human neocortex revealed a hierarchy of processing timescales, faster in early cortical regions and slower in deeper stages of the cortical hierarchy. We have identified a similar organization in recurrent neural networks and transformer models trained on language: early layers maintain short-lived representations while deeper layers integrate over longer spans of text.</p>
                        <p>We have also shown that providing learning systems with slowly changing internal states can boost learning, because it gives the system a "low-pass filter" on the world, enabling it to detect features that change gradually, such as the tone of a conversation. In parallel, we are investigating the cognitive capacities of large language models, including their ability to reason about other agents' mental states. By testing LLMs on tasks originally designed for human participants, we probe the boundaries of machine cognition and gain new perspective on what is distinctive about human thinking.</p>
                        <p class="research-papers">
                            <strong>Example papers:</strong>
                            <a href="{{ '/pdfs/honey_newman_schapiro_netneuro_2017.pdf' | relative_url }}">Honey, Newman &amp; Schapiro (2017) <em>Network Neuroscience</em></a>;
                            <a href="https://arxiv.org/abs/2012.06717">Chien, Zhang &amp; Honey (2021) <em>ICLR</em></a>;
                            <a href="https://arxiv.org/abs/2304.11490">Rahimi Moghaddam &amp; Honey (2023) <em>arXiv</em></a>
                        </p>
                    </div>
                </details>
            </div>
        </div>
    </div>
</section>

<section class="research-topic">
    <div class="container">
        <div class="research-summary">
            <div class="research-image">
                <img src="{{ '/assets/images/research/chien-2020-timescale-picture.jpg' | relative_url }}" alt="Timescale hierarchy in the cerebral cortex">
            </div>
            <div class="research-intro">
                <h2>Temporal Processing &amp; Context</h2>
                <p>Our world unfolds over time: hearing a fragment of sound, we perceive it as part of a melody; hearing one word, we understand it as part of a sentence. We study how the brain combines information across timescales to build an ongoing understanding of the world.</p>
                <details class="research-details">
                    <summary>Read more</summary>
                    <div class="research-expanded">
                        <p>Almost all regions of the human cerebral cortex can integrate information over time, producing a response at each moment that depends on what came before. Early sensory regions integrate over short periods (milliseconds to seconds) and pass information to higher-order regions, which integrate over longer periods (seconds to minutes). But information cannot be integrated indiscriminately: the subject of a new sentence is not necessarily related to the verb of the previous one. How do our brains flexibly integrate related information while separating unrelated information?</p>
                        <p>Our overarching hypothesis is that each cortical region maintains a local temporal context, which can be updated upon arrival of new input (leading to integration) or reset (leading to separation). We formalized this hypothesis via a computational model that we call HAT ("hierarchical autoencoders in time"). When two groups of participants heard the same sentence preceded by different contexts, we observed that their neural responses were initially different but gradually fell into alignment, with sensory cortices aligning most quickly and higher-order regions taking more than 10 seconds to converge. But when participants heard surprising context, we found that both sensory and higher-order regions would "reset" their context representations, as suggested by the HAT model.</p>
                        <p class="research-papers">
                            <strong>Example papers:</strong>
                            <a href="https://pubmed.ncbi.nlm.nih.gov/23083743/">Honey et al. (2012) <em>Neuron</em></a>;
                            <a href="https://pubmed.ncbi.nlm.nih.gov/32164874/">Chien &amp; Honey (2020) <em>Neuron</em></a>
                        </p>
                    </div>
                </details>
            </div>
        </div>
    </div>
</section>

<section class="research-topic alt">
    <div class="container">
        <div class="research-summary">
            <div class="research-image">
                <img src="{{ '/assets/images/research/real-world-memory.png' | relative_url }}" alt="Real-world autobiographical memory" style="max-width: 80%">
            </div>
            <div class="research-intro">
                <h2>Real-World Memory &amp; Aging</h2>
                <p>We remember thousands of experiences from our lives, and no two memories are quite alike. We study the structure of autobiographical memory and develop tools to strengthen it, especially in older adults.</p>
                <details class="research-details">
                    <summary>Read more</summary>
                    <div class="research-expanded">
                        <p>How are our real-world memories organized? When people recall experiences from their own lives and rate how similar those memories are to one another, we find a rich similarity structure that reflects the spatial, temporal, and emotional features of the original events. This structure is shared across individuals, suggesting common organizing principles for autobiographical memory.</p>
                        <p>In collaboration with Morgan Barense's group at the University of Toronto and Chris Martin at Florida State University, we have also developed smartphone-based interventions that can enhance real-world memory and promote healthy patterns of hippocampal activity. In a study of older adults, a brief daily photography exercise using a custom app (Hippocamera) led to improved memory for everyday events and increased differentiation of activity in the hippocampus, the brain region most critical for forming new memories.</p>
                        <p class="research-papers">
                            <strong>Example papers:</strong>
                            <a href="https://www.biorxiv.org/content/10.1101/2021.01.28.428278v1">Tomita, Barense &amp; Honey (2021) <em>bioRxiv</em></a>;
                            <a href="https://www.pnas.org/doi/abs/10.1073/pnas.2214285119">Martin et al. (2022) <em>PNAS</em></a>
                        </p>
                    </div>
                </details>
            </div>
        </div>
    </div>
</section>

<section class="research-topic">
    <div class="container">
        <div class="research-summary">
            <div class="research-image">
                <img src="{{ '/assets/images/research/brain-networks-image.png' | relative_url }}" alt="Brain network dynamics">
            </div>
            <div class="research-intro">
                <h2>Brain Network Dynamics</h2>
                <p>The brain is a network of densely interconnected regions. We study how the structure of this network shapes the flow of information, and how "hub" regions organize communication across the cortex.</p>
                <details class="research-details">
                    <summary>Read more</summary>
                    <div class="research-expanded">
                        <p>A typical brain region maintains reciprocal connections with more than a dozen others, so information can potentially flow in all directions. But some regions are especially effective in organizing and switching the flow of information, as occurs when we shift our attention from what somebody is saying to their facial expression. Using a combination of computational modeling and neuroimaging, we have shown that the brain's structural wiring can predict its patterns of functional connectivity at rest.</p>
                        <p>We have also mapped the moment-by-moment changes in signal flow across the cortical surface during narrative processing. The higher-order "hub" nodes in our cerebral cortices are either phase-leading their neighbors (acting as transmitters) or phase-lagging (acting as receivers). Changes in low-frequency oscillations predict these shifts, suggesting that synchronization patterns alter information flow to and from long-timescale hub regions.</p>
                        <p class="research-papers">
                            <strong>Example papers:</strong>
                            <a href="https://www.ncbi.nlm.nih.gov/pubmed/19188601">Honey et al. (2009) <em>PNAS</em></a>;
                            <a href="https://www.biorxiv.org/content/10.1101/2022.06.01.494224v1.abstract">Moon et al. (2022)</a>
                        </p>
                    </div>
                </details>
            </div>
        </div>
    </div>
</section>
