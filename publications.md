---
layout: page
title: Publications
description: Honey Lab publications - research papers on brain connectivity, temporal processing, and cognitive neuroscience
---

<section class="publications-section">
    <div class="container">
        <div class="pub-filters">
            <button class="pub-filter-btn active" data-filter="all">All</button>
            <button class="pub-filter-btn" data-filter="momentum">Cognitive Momentum</button>
            <button class="pub-filter-btn" data-filter="minds-machines">Minds &amp; Machines</button>
            <button class="pub-filter-btn" data-filter="temporal">Temporal Processing</button>
            <button class="pub-filter-btn" data-filter="memory-aging">Memory &amp; Aging</button>
            <button class="pub-filter-btn" data-filter="networks">Brain Networks</button>
            <button class="pub-filter-btn" data-filter="methods-other">Methods &amp; Other</button>
        </div>
        {% assign sorted_pubs = site.data.publications | sort: "year" | reverse %}
        <ul class="pub-list">
            {% for pub in sorted_pubs %}
                {% include publication-entry.html pub=pub %}
            {% endfor %}
        </ul>
    </div>
</section>
