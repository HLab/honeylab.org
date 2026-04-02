/**
 * Honey Lab - Main JavaScript
 * Enhances the CSS-only mobile nav with close-on-outside-click
 * and close-on-link-click. The menu works without JS via checkbox hack.
 */
document.addEventListener('DOMContentLoaded', function() {
    var check = document.getElementById('navCheck');
    if (!check) return;

    var siteNav = document.getElementById('siteNav');
    var toggle = document.querySelector('.nav-toggle');
    var isLanding = document.body.classList.contains('landing-page');

    // On landing page, if nav hasn't stuck yet (still at bottom of viewport),
    // scroll it to the top before opening the menu.
    if (toggle && isLanding && siteNav) {
        toggle.addEventListener('click', function(e) {
            if (!siteNav.classList.contains('stuck')) {
                e.preventDefault();
                siteNav.scrollIntoView({ behavior: 'smooth', block: 'start' });
                setTimeout(function() { check.checked = true; }, 350);
            }
        });
    }

    // Close menu when clicking a nav link
    document.querySelectorAll('.nav-links a').forEach(function(link) {
        link.addEventListener('click', function() { check.checked = false; });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (check.checked && !e.target.closest('.nav-inner')) {
            check.checked = false;
        }
    });
});

/**
 * People photo easter egg — click to reveal alt photo(s).
 * Single-alt: click toggles between primary and alt.
 * Multi-alt: each click advances to the next photo.
 * Mouseleave always resets to the primary image.
 */
(function() {
    document.querySelectorAll('.person-photo.has-alt').forEach(function(photo) {
        var primary = photo.querySelector('img:first-child');
        var alts = photo.querySelectorAll('.person-photo-alt');
        var current = -1; // -1 = primary visible

        function reset() {
            primary.style.opacity = '1';
            alts.forEach(function(a) { a.style.opacity = '0'; });
            current = -1;
        }

        photo.addEventListener('click', function() {
            if (alts.length === 1) {
                // Single alt: toggle
                if (current === -1) {
                    primary.style.opacity = '0';
                    alts[0].style.opacity = '1';
                    current = 0;
                } else {
                    reset();
                }
            } else {
                // Multi alt: advance to next
                if (current >= 0) alts[current].style.opacity = '0';
                current = (current + 1) % alts.length;
                primary.style.opacity = '0';
                alts[current].style.opacity = '1';
            }
        });

        photo.addEventListener('mouseleave', reset);
    });
})();
