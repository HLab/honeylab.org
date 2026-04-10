---
layout: page
title: Publications
hide_title: true
description: Honey Lab publications - research papers on brain connectivity, temporal processing, and cognitive neuroscience
---

<section class="publications-section">
    <div class="container">
        <svg viewBox="-3 -3 959 181" class="pub-filters-svg" aria-label="Publication filter honeycomb">
          <!-- decorative hex outlines with subtle amber fill -->
          <polygon class="hex-decorative" points="173.21,0 216.51,25 216.51,75 173.21,100 129.90,75 129.90,25" fill-opacity="0.08" />
          <polygon class="hex-decorative" points="259.81,0 303.11,25 303.11,75 259.81,100 216.51,75 216.51,25" fill-opacity="0.18" />
          <polygon class="hex-decorative" points="433.01,0 476.31,25 476.31,75 433.01,100 389.71,75 389.71,25" fill-opacity="0.12" />
          <polygon class="hex-decorative" points="519.62,0 562.92,25 562.92,75 519.62,100 476.31,75 476.31,25" fill-opacity="0.22" />
          <polygon class="hex-decorative" points="692.82,0 736.12,25 736.12,75 692.82,100 649.52,75 649.52,25" fill-opacity="0.1" />
          <polygon class="hex-decorative" points="779.42,0 822.72,25 822.72,75 779.42,100 736.12,75 736.12,25" fill-opacity="0.2" />
          <polygon class="hex-decorative" points="43.30,75 86.60,100 86.60,150 43.30,175 0,150 0,100" fill-opacity="0.08" />
          <polygon class="hex-decorative" points="129.90,75 173.21,100 173.21,150 129.90,175 86.60,150 86.60,100" fill-opacity="0.15" />
          <polygon class="hex-decorative" points="303.11,75 346.41,100 346.41,150 303.11,175 259.81,150 259.81,100" fill-opacity="0.12" />
          <polygon class="hex-decorative" points="389.71,75 433.01,100 433.01,150 389.71,175 346.41,150 346.41,100" fill-opacity="0.18" />
          <polygon class="hex-decorative" points="562.92,75 606.22,100 606.22,150 562.92,175 519.62,150 519.62,100" fill-opacity="0.1" />
          <polygon class="hex-decorative" points="649.52,75 692.82,100 692.82,150 649.52,175 606.22,150 606.22,100" fill-opacity="0.16" />
          <polygon class="hex-decorative" points="822.72,75 866.03,100 866.03,150 822.72,175 779.42,150 779.42,100" fill-opacity="0.2" />
          <polygon class="hex-decorative" points="909.33,75 952.63,100 952.63,150 909.33,175 866.03,150 866.03,100" fill-opacity="0.1" />
          <!-- filter buttons -->
          <g class="pub-filter-btn active" data-filter="all" role="button" tabindex="0">
            <polygon points="86.60,0 129.90,25 129.90,75 86.60,100 43.30,75 43.30,25" />
            <text x="86.60" y="50" text-anchor="middle" dominant-baseline="central">All Topics</text>
          </g>
          <g class="pub-filter-btn" data-filter="momentum" role="button" tabindex="0">
            <polygon points="346.41,0 389.71,25 389.71,75 346.41,100 303.11,75 303.11,25" />
            <text x="346.41" y="50" text-anchor="middle">
              <tspan x="346.41" y="41" dominant-baseline="central">Cognitive</tspan>
              <tspan x="346.41" y="59" dominant-baseline="central">Momentum</tspan>
            </text>
          </g>
          <g class="pub-filter-btn" data-filter="minds-machines" role="button" tabindex="0">
            <polygon points="606.22,0 649.52,25 649.52,75 606.22,100 562.92,75 562.92,25" />
            <text x="606.22" y="50" text-anchor="middle">
              <tspan x="606.22" y="41" dominant-baseline="central">Minds &amp;</tspan>
              <tspan x="606.22" y="59" dominant-baseline="central">Machines</tspan>
            </text>
          </g>
          <g class="pub-filter-btn" data-filter="memory-aging" role="button" tabindex="0">
            <polygon points="866.03,0 909.33,25 909.33,75 866.03,100 822.72,75 822.72,25" />
            <text x="866.03" y="50" text-anchor="middle">
              <tspan x="866.03" y="41" dominant-baseline="central">Memory</tspan>
              <tspan x="866.03" y="59" dominant-baseline="central">&amp; Aging</tspan>
            </text>
          </g>
          <g class="pub-filter-btn" data-filter="temporal" role="button" tabindex="0">
            <polygon points="216.51,75 259.81,100 259.81,150 216.51,175 173.21,150 173.21,100" />
            <text x="216.51" y="125" text-anchor="middle">
              <tspan x="216.51" y="116" dominant-baseline="central">Temporal</tspan>
              <tspan x="216.51" y="134" dominant-baseline="central">Processing</tspan>
            </text>
          </g>
          <g class="pub-filter-btn" data-filter="networks" role="button" tabindex="0">
            <polygon points="476.31,75 519.62,100 519.62,150 476.31,175 433.01,150 433.01,100" />
            <text x="476.31" y="125" text-anchor="middle">
              <tspan x="476.31" y="116" dominant-baseline="central">Brain</tspan>
              <tspan x="476.31" y="134" dominant-baseline="central">Networks</tspan>
            </text>
          </g>
          <g class="pub-filter-btn" data-filter="methods-other" role="button" tabindex="0">
            <polygon points="736.12,75 779.42,100 779.42,150 736.12,175 692.82,150 692.82,100" />
            <text x="736.12" y="125" text-anchor="middle">
              <tspan x="736.12" y="116" dominant-baseline="central">Methods</tspan>
              <tspan x="736.12" y="134" dominant-baseline="central">&amp; Other</tspan>
            </text>
          </g>
        </svg>
        {% assign sorted_pubs = site.data.publications | sort: "year" | reverse %}
        <ul class="pub-list">
            {% for pub in sorted_pubs %}
                {% include publication-entry.html pub=pub %}
            {% endfor %}
        </ul>
    </div>
</section>
