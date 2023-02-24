document.addEventListener('alpine:init', () => {
    /**
     * Global state for toggling search modal.
     */
    Alpine.store('search', {
        isOpen: false,
        toggle() { this.isOpen = !this.isOpen },
        close() { this.isOpen = false }
    })

    /**
     * Capture keyboard events to toggle search modal.
     */
    document.addEventListener('keydown', (event) => {
      if (event.metaKey && event.key === 'k') {
          Alpine.store('search').toggle()
      } else if (event.key === 'Escape') {
          Alpine.store('search').close()
      }
    });

    /**
     * Appends an 's' if the count is not one.
     */
    function pluralise(word, count) {
        return `${count} ${word}${count !== 1 ? 's' : ''}`
    }

    /**
     * State/functions for performing searches.
     */
    Alpine.data('siteSearch', () => {
        const minChars = 2;
        const resultsEmpty = { apps: [] };

        return {
            /**
             * Value inputted into search box.
             */
            value: '',
            /**
             * Help text, updated before/during search.
             */
            helpText: `Enter ${minChars} or more characters...`,
            /**
             * Text displaying number of results.
             */
            countText: '',
            /**
             * Results array, updated on value change.
             */
            results: resultsEmpty,
            /**
             * Fetch search results from /admin/search/.
             */
            async fetchResults() {
                const response = await fetch(`/admin/search/?q=${this.value}`);
                return await response.json();
            },
            /**
             * Perform a search, if the min number of chars are entered, and update loading/error helpText.
             * This should be debounced/throttled to avoid excessive requests.
             */
            async onInputDebounce() {
                if (this.value.length < minChars) {
                    this.results = resultsEmpty;
                } else {
                    this.helpText = 'Searching...'
                    try {
                        const data = await this.fetchResults();
                        this.results = data.results;

                        const countApps = data.counts.apps;
                        const countModels = data.counts.models;
                        const countObjects = data.counts.objects;

                        if (countApps > 0 || countModels > 0 || countObjects > 0) {
                            this.helpText = `Showing ${pluralise('app', countApps)}, 
                            ${pluralise('model', countModels)}, 
                            and ${pluralise('object', countObjects)}`;
                        } else {
                            this.helpText = `No results for "${this.value}"`;
                        }
                    } catch (e) {
                        this.helpText = 'An unexpected error occurred'
                        console.error(e);
                    }
                }
            },
            /**
             * Updates the helpText value, based on the number of chars inputted.
             */
            onInputInstant() {
                this.results = resultsEmpty;
                if (this.value.length > 0) {
                    if (this.value.length < minChars) {
                        this.helpText = `Enter ${minChars} or more characters...`
                    } else {
                        this.helpText = "Searching..."
                    }
                }
            },
            /**
             * Returns an array of link/result elements inside the search results.
             */
            linkElements() {
                return Array.from(document.getElementById('search-site-results').querySelectorAll('a'));
            },
            /**
             * Moves focus to the search input.
             */
            focusOnInput() {
                document.getElementById('search-site-input').focus();
            },
            /**
             * Moves focus to the link with the given index (can be 'last').
             */
            focusOnLink({ index }) {
                const linkElements = this.linkElements();
                if (linkElements.length > 0) {
                    if (index === 'last') {
                        index = linkElements.length - 1;
                    }
                    linkElements[index].focus();
                }
            },
            /**
             * Moves focus to the next/previous link if arrow down/up, or moves focus to input
             * if a non-navigation character pressed.
             */
            onKeyDown(event) {
                const el = event.currentTarget;
                const key = event.key;

                if (["ArrowDown", "ArrowUp"].includes(key)) {
                    event.preventDefault();
                    const linkElements = this.linkElements();
                    let goToIndex;

                    if (key === "ArrowDown") {
                        // move to next result, or the first if we're at the end
                        goToIndex = (linkElements.indexOf(el) + 1) % linkElements.length;
                    } else {
                        // move to the previous result, or the last if we're at the start
                        const previous = linkElements.indexOf(el) - 1;
                        goToIndex = previous === -1 ? linkElements.length - 1 : previous;
                    }

                    linkElements[goToIndex].focus();
                } else if (!["Tab", "Shift", "Enter"].includes(key)) {
                    event.preventDefault();
                    // move focus back to input if user starts typing
                    this.focusOnInput();
                }
            },
        }
    })
})