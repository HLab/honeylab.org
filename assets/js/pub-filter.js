/**
 * Publication filter — show/hide papers by category tag.
 * Only initializes if .pub-filter-btn elements are present.
 */
(function() {
    var buttons = document.querySelectorAll('.pub-filter-btn');
    if (!buttons.length) return;

    var items = document.querySelectorAll('.pub-list li');

    buttons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var filter = this.getAttribute('data-filter');

            buttons.forEach(function(b) { b.classList.remove('active'); });
            this.classList.add('active');

            items.forEach(function(item) {
                if (filter === 'all') {
                    item.style.display = '';
                } else if (filter === 'methods-other') {
                    var tags = item.getAttribute('data-tags').split(' ');
                    var match = tags.indexOf('methods') !== -1 || tags.indexOf('other') !== -1;
                    item.style.display = match ? '' : 'none';
                } else {
                    var tags = item.getAttribute('data-tags').split(' ');
                    item.style.display = tags.indexOf(filter) !== -1 ? '' : 'none';
                }
            });
        });
    });
})();
