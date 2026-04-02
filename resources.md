---
layout: page
title: Resources
description: Honey Lab resources - datasets, code, and tools from our research
---

<section class="resources-section">
    <div class="container">

        {% assign datasets = site.data.resources | where: "type", "dataset" %}
        {% if datasets.size > 0 %}
        <div class="resource-group">
            <h2>Datasets</h2>
            <div class="resource-list">
                {% for item in datasets %}
                <div class="resource-card">
                    <h3><a href="{{ item.url }}">{{ item.name }}</a></h3>
                    <p>{{ item.description }}</p>
                    <div class="resource-meta">
                        <span class="resource-badge">Dataset</span>
                        {% if item.paper %}<span class="resource-paper">{{ item.paper }}</span>{% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% assign code = site.data.resources | where: "type", "code" %}
        {% if code.size > 0 %}
        <div class="resource-group">
            <h2>Code</h2>
            <div class="resource-list">
                {% for item in code %}
                <div class="resource-card">
                    <h3><a href="{{ item.url }}">{{ item.name }}</a></h3>
                    <p>{{ item.description }}</p>
                    <div class="resource-meta">
                        <span class="resource-badge">Code</span>
                        {% if item.paper %}<span class="resource-paper">{{ item.paper }}</span>{% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% assign tools = site.data.resources | where: "type", "tool" %}
        {% if tools.size > 0 %}
        <div class="resource-group">
            <h2>Tools</h2>
            <div class="resource-list">
                {% for item in tools %}
                <div class="resource-card">
                    <h3><a href="{{ item.url }}">{{ item.name }}</a></h3>
                    <p>{{ item.description }}</p>
                    <div class="resource-meta">
                        <span class="resource-badge">Tool</span>
                        {% if item.paper %}<span class="resource-paper">{{ item.paper }}</span>{% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</section>

<section class="resources-section resources-external">
    <div class="container">
        <h2>From the Community</h2>

        {% assign ext_tools = site.data.external_resources | where: "category", "tools" %}
        {% if ext_tools.size > 0 %}
        <div class="resource-group">
            <h3>Related Tools</h3>
            <div class="resource-list">
                {% for item in ext_tools %}
                <div class="resource-card resource-card-external">
                    <h3><a href="{{ item.url }}">{{ item.name }}</a></h3>
                    <p>{{ item.description }}</p>
                    {% if item.group %}<span class="resource-paper">{{ item.group }}</span>{% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% assign ext_data = site.data.external_resources | where: "category", "data" %}
        {% if ext_data.size > 0 %}
        <div class="resource-group">
            <h3>Open Datasets</h3>
            <div class="resource-list">
                {% for item in ext_data %}
                <div class="resource-card resource-card-external">
                    <h3><a href="{{ item.url }}">{{ item.name }}</a></h3>
                    <p>{{ item.description }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% assign ext_learning = site.data.external_resources | where: "category", "learning" %}
        {% if ext_learning.size > 0 %}
        <div class="resource-group">
            <h3>Books &amp; Courses</h3>
            <div class="resource-list">
                {% for item in ext_learning %}
                <div class="resource-card resource-card-external">
                    <h3><a href="{{ item.url }}">{{ item.name }}</a></h3>
                    <p>{{ item.description }}</p>
                    {% if item.group %}<span class="resource-paper">{{ item.group }}</span>{% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% assign ext_labs = site.data.external_resources | where: "category", "labs" %}
        {% if ext_labs.size > 0 %}
        <div class="resource-group">
            <h3>Collaborators &amp; Related Labs</h3>
            <div class="resource-list">
                {% for item in ext_labs %}
                <div class="resource-card resource-card-external">
                    <h3><a href="{{ item.url }}">{{ item.name }}</a></h3>
                    <p>{{ item.description }}</p>
                    {% if item.group %}<span class="resource-paper">{{ item.group }}</span>{% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% assign ext_community = site.data.external_resources | where: "category", "community" %}
        {% if ext_community.size > 0 %}
        <div class="resource-group">
            <h3>Community</h3>
            <div class="resource-list">
                {% for item in ext_community %}
                <div class="resource-card resource-card-external">
                    <h3><a href="{{ item.url }}">{{ item.name }}</a></h3>
                    <p>{{ item.description }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</section>
