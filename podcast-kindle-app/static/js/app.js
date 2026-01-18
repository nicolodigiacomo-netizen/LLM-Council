/**
 * Podcast to Kindle - Frontend Application
 */

(function() {
    'use strict';

    // Application state
    const state = {
        currentPodcast: null,
        selectedEpisodes: [],
        processedData: null,
        sessionStats: { processed_count: 0, remaining_quota: 5 }
    };

    // UI Elements
    const elements = {
        searchInput: null,
        searchBtn: null,
        filterButtons: null,
        resultsSection: null,
        resultsContainer: null,
        episodesSection: null,
        episodesContainer: null,
        previewSection: null,
        loadingOverlay: null
    };

    /**
     * Initialize the application
     */
    function init() {
        // Cache DOM elements
        cacheElements();

        // Attach event listeners
        attachEventListeners();

        // Load session stats
        loadSessionStats();

        console.log('Podcast to Kindle app initialized');
    }

    /**
     * Cache DOM elements
     */
    function cacheElements() {
        elements.searchInput = document.getElementById('search-input');
        elements.searchBtn = document.getElementById('search-btn');
        elements.filterButtons = document.querySelectorAll('.btn-filter');
        elements.resultsSection = document.getElementById('results-section');
        elements.resultsContainer = document.getElementById('results-container');
        elements.episodesSection = document.getElementById('episodes-section');
        elements.episodesContainer = document.getElementById('episodes-container');
        elements.previewSection = document.getElementById('preview-section');
        elements.loadingOverlay = document.getElementById('loading-overlay');
    }

    /**
     * Attach event listeners
     */
    function attachEventListeners() {
        // Search functionality
        elements.searchBtn.addEventListener('click', handleSearch);
        elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch();
        });

        // Quick filters
        elements.filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.dataset.query;
                elements.searchInput.value = query;
                handleSearch();
            });
        });

        // Navigation buttons
        document.getElementById('back-to-search').addEventListener('click', showSearchResults);
        document.getElementById('back-to-episodes').addEventListener('click', showEpisodes);

        // Episode selection
        document.getElementById('select-all').addEventListener('click', selectAllEpisodes);
        document.getElementById('deselect-all').addEventListener('click', deselectAllEpisodes);
        document.getElementById('process-btn').addEventListener('click', handleProcess);

        // Preview tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => switchTab(btn.dataset.tab));
        });

        // Download
        document.getElementById('download-btn').addEventListener('click', handleDownload);
    }

    /**
     * Handle search
     */
    async function handleSearch() {
        const query = elements.searchInput.value.trim();

        if (!query) {
            showToast('Please enter a search query', 'warning');
            return;
        }

        showLoading('Searching podcasts...');

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Search failed');
            }

            displaySearchResults(data.results);
            hideLoading();

        } catch (error) {
            hideLoading();
            showToast(error.message, 'error');
        }
    }

    /**
     * Display search results
     */
    function displaySearchResults(results) {
        if (!results || results.length === 0) {
            elements.resultsContainer.innerHTML = '<p class="text-center">No podcasts found. Try different keywords.</p>';
            elements.resultsSection.classList.remove('hidden');
            return;
        }

        elements.resultsContainer.innerHTML = results.map(podcast => `
            <div class="podcast-card" data-podcast='${JSON.stringify(podcast)}'>
                <img src="${podcast.image_url || '/static/images/placeholder.png'}"
                     alt="${podcast.title}"
                     class="podcast-image"
                     onerror="this.src='/static/images/placeholder.png'">
                <div class="podcast-details">
                    <h3 class="podcast-title">${podcast.title}</h3>
                    <p class="podcast-author">${podcast.author || 'Unknown Author'}</p>
                    <p class="podcast-description">${podcast.description || 'No description available'}</p>
                    ${podcast.genre ? `<span class="podcast-badge">${podcast.genre}</span>` : ''}
                </div>
            </div>
        `).join('');

        // Attach click handlers to podcast cards
        document.querySelectorAll('.podcast-card').forEach(card => {
            card.addEventListener('click', () => {
                const podcast = JSON.parse(card.dataset.podcast);
                handlePodcastSelect(podcast);
            });
        });

        elements.resultsSection.classList.remove('hidden');
        elements.episodesSection.classList.add('hidden');
        elements.previewSection.classList.add('hidden');
    }

    /**
     * Handle podcast selection
     */
    async function handlePodcastSelect(podcast) {
        state.currentPodcast = podcast;

        showLoading('Loading episodes...');

        try {
            const response = await fetch('/api/episodes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    feed_url: podcast.feed_url,
                    podcast_info: podcast
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to load episodes');
            }

            displayEpisodes(data.episodes, podcast);
            hideLoading();

        } catch (error) {
            hideLoading();
            showToast(error.message, 'error');
        }
    }

    /**
     * Display episodes
     */
    function displayEpisodes(episodes, podcast) {
        // Update podcast info
        document.getElementById('podcast-title').textContent = podcast.title;
        document.getElementById('podcast-info').innerHTML = `
            <strong>${podcast.title}</strong> by ${podcast.author}<br>
            <small>${episodes.length} episodes with transcripts available</small>
        `;

        document.getElementById('episodes-count').textContent =
            `${episodes.length} episodes available with transcripts`;

        // Display episodes
        if (episodes.length === 0) {
            elements.episodesContainer.innerHTML = `
                <p class="text-center">No episodes with transcripts found for this podcast.</p>
            `;
        } else {
            elements.episodesContainer.innerHTML = episodes.map((episode, index) => `
                <div class="episode-item ${!episode.has_transcript ? 'disabled' : ''}" data-index="${index}">
                    <input type="checkbox"
                           class="episode-checkbox"
                           data-episode='${JSON.stringify(episode)}'
                           ${!episode.has_transcript ? 'disabled' : ''}>
                    <div class="episode-content">
                        <div class="episode-title">${episode.title}</div>
                        <div class="episode-meta">
                            <span>${episode.duration || 'Unknown duration'}</span>
                            ${episode.published ? `<span>${new Date(episode.published).toLocaleDateString()}</span>` : ''}
                            <span class="transcript-badge ${episode.has_transcript ? 'available' : 'unavailable'}">
                                ${episode.has_transcript ? '✓ Transcript Available' : '✗ No Transcript'}
                            </span>
                        </div>
                    </div>
                </div>
            `).join('');

            // Attach checkbox listeners
            document.querySelectorAll('.episode-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', handleEpisodeSelection);
            });
        }

        // Reset selection
        state.selectedEpisodes = [];
        updateSelectionCount();

        // Show episodes section
        elements.resultsSection.classList.add('hidden');
        elements.episodesSection.classList.remove('hidden');
        elements.previewSection.classList.add('hidden');
    }

    /**
     * Handle episode selection
     */
    function handleEpisodeSelection(e) {
        const checkbox = e.target;
        const episode = JSON.parse(checkbox.dataset.episode);

        if (checkbox.checked) {
            state.selectedEpisodes.push(episode);
        } else {
            state.selectedEpisodes = state.selectedEpisodes.filter(ep => ep.guid !== episode.guid);
        }

        updateSelectionCount();
    }

    /**
     * Update selection count
     */
    function updateSelectionCount() {
        const count = state.selectedEpisodes.length;
        document.getElementById('selected-count').textContent = count;

        const processBtn = document.getElementById('process-btn');
        processBtn.disabled = count === 0;
    }

    /**
     * Select all episodes
     */
    function selectAllEpisodes() {
        const checkboxes = document.querySelectorAll('.episode-checkbox:not(:disabled)');
        checkboxes.forEach(cb => {
            if (!cb.checked) {
                cb.checked = true;
                cb.dispatchEvent(new Event('change'));
            }
        });
    }

    /**
     * Deselect all episodes
     */
    function deselectAllEpisodes() {
        const checkboxes = document.querySelectorAll('.episode-checkbox');
        checkboxes.forEach(cb => {
            if (cb.checked) {
                cb.checked = false;
                cb.dispatchEvent(new Event('change'));
            }
        });
    }

    /**
     * Handle process episodes
     */
    async function handleProcess() {
        if (state.selectedEpisodes.length === 0) {
            showToast('Please select at least one episode', 'warning');
            return;
        }

        showLoading('Processing transcripts...');

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ episodes: state.selectedEpisodes })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Processing failed');
            }

            state.processedData = data;
            displayPreview(data.preview);
            updateSessionStats({ processed_count: data.episode_count, remaining_quota: data.remaining_quota });
            hideLoading();

            showToast(`Successfully processed ${data.episode_count} episode(s)`, 'success');

        } catch (error) {
            hideLoading();
            showToast(error.message, 'error');
        }
    }

    /**
     * Display preview
     */
    function displayPreview(markdownContent) {
        // Convert markdown to HTML for preview (simple conversion)
        const html = markdownToHtml(markdownContent);
        document.getElementById('markdown-preview').innerHTML = html;

        // Show preview section
        elements.episodesSection.classList.add('hidden');
        elements.previewSection.classList.remove('hidden');
    }

    /**
     * Simple markdown to HTML converter
     */
    function markdownToHtml(markdown) {
        let html = markdown;

        // Headers
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

        // Bold
        html = html.replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*(.*)\*/gim, '<em>$1</em>');

        // Lists
        html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // Horizontal rule
        html = html.replace(/^---$/gim, '<hr>');

        // Paragraphs
        html = html.split('\n\n').map(p => {
            if (!p.match(/^<[h|u|o|l]/)) {
                return `<p>${p}</p>`;
            }
            return p;
        }).join('\n');

        // Line breaks
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    /**
     * Handle download
     */
    async function handleDownload() {
        const format = document.querySelector('input[name="format"]:checked').value;

        showLoading(`Generating ${format.toUpperCase()} file...`);

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ format })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Download generation failed');
            }

            // Display download link
            const downloadResult = document.getElementById('download-result');
            downloadResult.innerHTML = `
                <p>✓ Your file is ready!</p>
                <a href="${data.download_url}" class="btn btn-primary" download>
                    Download ${data.filename}
                </a>
            `;
            downloadResult.classList.remove('hidden');

            hideLoading();
            showToast('File generated successfully!', 'success');

        } catch (error) {
            hideLoading();
            showToast(error.message, 'error');
        }
    }

    /**
     * Switch tabs in preview section
     */
    function switchTab(tabName) {
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane.id === `${tabName}-tab`);
        });
    }

    /**
     * Navigation functions
     */
    function showSearchResults() {
        elements.resultsSection.classList.remove('hidden');
        elements.episodesSection.classList.add('hidden');
        elements.previewSection.classList.add('hidden');
    }

    function showEpisodes() {
        elements.resultsSection.classList.add('hidden');
        elements.episodesSection.classList.remove('hidden');
        elements.previewSection.classList.add('hidden');
    }

    /**
     * Load session stats
     */
    async function loadSessionStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            updateSessionStats(data);
        } catch (error) {
            console.error('Failed to load session stats:', error);
        }
    }

    /**
     * Update session stats display
     */
    function updateSessionStats(stats) {
        state.sessionStats = stats;
        const usageElement = document.getElementById('session-usage');
        if (usageElement) {
            usageElement.textContent = `${stats.processed_count}/${stats.processed_count + stats.remaining_quota}`;
        }
    }

    /**
     * Show loading overlay
     */
    function showLoading(message = 'Loading...') {
        elements.loadingOverlay.querySelector('.loading-text').textContent = message;
        elements.loadingOverlay.classList.remove('hidden');
    }

    /**
     * Hide loading overlay
     */
    function hideLoading() {
        elements.loadingOverlay.classList.add('hidden');
    }

    /**
     * Show toast notification
     */
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    // Export to global scope
    window.podcastApp = {
        init,
        showToast
    };

})();
