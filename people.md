---
layout: page
title: Lab Members
description: Honey Lab team members - current lab members and alumni
---

<section class="people-section">
    <div class="container">
        <div class="people-grid">
            {% assign active_members = site.data.people | where: "active", true %}
            {% for person in active_members %}
                {% include person-card.html person=person %}
            {% endfor %}
        </div>
    </div>
</section>

<section class="alumni-section">
    <div class="container">
        <h2>Alumni</h2>
        <div class="alumni-list">
            {% assign alumni = site.data.people | where: "active", false %}
            {% for person in alumni %}
            <div class="alumni-item">
                <strong>{{ person.name }}</strong>, {{ person.role }}{% if person.years %} ({{ person.years }}){% endif %}
                {% if person.now %}<br><em>Now:</em> {{ person.now }}{% endif %}
                {% if person.website %} <a href="{{ person.website }}">website</a>{% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</section>
