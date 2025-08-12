// Application State
let currentPlaylist = null;
let currentJobId = null;
let progressInterval = null;

// DOM Elements
const elements = {
    // Navigation
    loginBtn: document.getElementById('loginBtn'),
    heroStartBtn: document.getElementById('heroStartBtn'),
    
    // App Interface
    appInterface: document.getElementById('appInterface'),
    
    // Step 1: Input
    inputStep: document.getElementById('inputStep'),
    playlistUrl: document.getElementById('playlistUrl'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    
    // Step 2: Preview
    previewStep: document.getElementById('previewStep'),
    playlistInfo: document.getElementById('playlistInfo'),
    trackList: document.getElementById('trackList'),
    backBtn: document.getElementById('backBtn'),
    convertBtn: document.getElementById('convertBtn'),
    
    // Step 3: Progress
    progressStep: document.getElementById('progressStep'),
    progressText: document.getElementById('progressText'),
    progressPercent: document.getElementById('progressPercent'),
    progressFill: document.getElementById('progressFill'),
    currentTrack: document.getElementById('currentTrack'),
    completedCount: document.getElementById('completedCount'),
    failedCount: document.getElementById('failedCount'),
    totalCount: document.getElementById('totalCount'),
    
    // Step 4: Download
    downloadStep: document.getElementById('downloadStep'),
    downloadMessage: document.getElementById('downloadMessage'),
    downloadBtn: document.getElementById('downloadBtn'),
    newConversionBtn: document.getElementById('newConversionBtn'),
    
    // Loading & Error
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    errorModal: document.getElementById('errorModal'),
    errorMessage: document.getElementById('errorMessage'),
    closeErrorModal: document.getElementById('closeErrorModal'),
    errorOkBtn: document.getElementById('errorOkBtn')
};

// API Base URL
const API_BASE = '/api';

// Utility Functions
function showLoading(message = 'Loading...') {
    elements.loadingText.textContent = message;
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorModal.style.display = 'flex';
}

function hideError() {
    elements.errorModal.style.display = 'none';
}

function showStep(stepElement) {
    // Hide all steps
    document.querySelectorAll('.step-card').forEach(step => {
        step.style.display = 'none';
    });
    
    // Show the specified step
    stepElement.style.display = 'block';
    
    // Show app interface if not already visible
    elements.appInterface.style.display = 'block';
    
    // Scroll to app interface
    elements.appInterface.scrollIntoView({ behavior: 'smooth' });
}

function formatDuration(ms) {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function isValidSpotifyUrl(url) {
    const spotifyRegex = /^https:\/\/open\.spotify\.com\/playlist\/[a-zA-Z0-9]+(\?.*)?$/;
    return spotifyRegex.test(url);
}

// API Functions
async function analyzePlaylist(playlistUrl) {
    const response = await fetch(`${API_BASE}/spotify/playlist`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ playlist_url: playlistUrl })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to analyze playlist');
    }
    
    return await response.json();
}

async function startConversion(tracks, playlistName) {
    const response = await fetch(`${API_BASE}/convert/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            tracks: tracks,
            playlist_name: playlistName
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to start conversion');
    }
    
    return await response.json();
}

async function getConversionStatus(jobId) {
    const response = await fetch(`${API_BASE}/convert/status/${jobId}`);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to get conversion status');
    }
    
    return await response.json();
}

async function downloadPlaylist(jobId) {
    const response = await fetch(`${API_BASE}/convert/download/${jobId}`);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to download playlist');
    }
    
    // Create download link
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `playlist_${jobId.substring(0, 8)}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Step Functions
function handleAnalyze() {
    const url = elements.playlistUrl.value.trim();
    
    if (!url) {
        showError('Please enter a Spotify playlist URL');
        return;
    }
    
    if (!isValidSpotifyUrl(url)) {
        showError('Please enter a valid Spotify playlist URL');
        return;
    }
    
    showLoading('Analyzing playlist...');
    
    analyzePlaylist(url)
        .then(playlist => {
            currentPlaylist = playlist;
            displayPlaylistPreview(playlist);
            showStep(elements.previewStep);
        })
        .catch(error => {
            showError(error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function displayPlaylistPreview(playlist) {
    // Playlist info
    elements.playlistInfo.innerHTML = `
        <div class="playlist-header">
            <div class="playlist-cover">
                <i class="fas fa-music"></i>
            </div>
            <div class="playlist-details">
                <h3>${playlist.name}</h3>
                <div class="playlist-meta">
                    <p>${playlist.total_tracks} tracks</p>
                    ${playlist.description ? `<p>${playlist.description}</p>` : ''}
                </div>
            </div>
        </div>
    `;
    
    // Track list
    const trackListHtml = playlist.tracks.map((track, index) => `
        <div class="track-item">
            <div class="track-number">${index + 1}</div>
            <div class="track-info">
                <div class="track-name">${track.name}</div>
                <div class="track-artist">${track.artists.join(', ')}</div>
            </div>
            <div class="track-duration">${formatDuration(track.duration_ms)}</div>
        </div>
    `).join('');
    
    elements.trackList.innerHTML = trackListHtml;
}

function handleConvert() {
    if (!currentPlaylist) {
        showError('No playlist selected');
        return;
    }
    
    showLoading('Starting conversion...');
    
    startConversion(currentPlaylist.tracks, currentPlaylist.name)
        .then(result => {
            currentJobId = result.job_id;
            showStep(elements.progressStep);
            startProgressMonitoring();
        })
        .catch(error => {
            showError(error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function startProgressMonitoring() {
    if (!currentJobId) return;
    
    // Initial setup
    elements.totalCount.textContent = currentPlaylist.total_tracks;
    elements.completedCount.textContent = '0';
    elements.failedCount.textContent = '0';
    elements.progressPercent.textContent = '0%';
    elements.progressFill.style.width = '0%';
    
    // Start polling
    progressInterval = setInterval(() => {
        getConversionStatus(currentJobId)
            .then(status => {
                updateProgress(status);
                
                if (status.status === 'completed') {
                    clearInterval(progressInterval);
                    showDownloadReady(status);
                } else if (status.status === 'failed') {
                    clearInterval(progressInterval);
                    showError(status.error || 'Conversion failed');
                }
            })
            .catch(error => {
                clearInterval(progressInterval);
                showError(error.message);
            });
    }, 2000); // Poll every 2 seconds
}

function updateProgress(status) {
    elements.completedCount.textContent = status.completed_tracks;
    elements.failedCount.textContent = status.failed_tracks;
    elements.progressPercent.textContent = `${status.progress}%`;
    elements.progressFill.style.width = `${status.progress}%`;
    
    if (status.current_track) {
        elements.currentTrack.innerHTML = `
            <i class="fas fa-music"></i>
            <span>Converting: ${status.current_track}</span>
        `;
    }
    
    // Update progress text
    if (status.status === 'processing') {
        elements.progressText.textContent = 'Converting tracks...';
    } else if (status.status === 'queued') {
        elements.progressText.textContent = 'Queued for processing...';
    }
}

function showDownloadReady(status) {
    let message = '';
    
    if (status.completed_tracks === status.total_tracks) {
        // Perfect success
        message = `🎉 Successfully converted all ${status.total_tracks} tracks!`;
    } else if (status.completed_tracks > 0) {
        // Partial success
        message = `✅ Successfully converted ${status.completed_tracks} out of ${status.total_tracks} tracks.`;
        if (status.failed_tracks > 0) {
            message += `\n⚠️ ${status.failed_tracks} tracks failed to convert.`;
        }
    } else {
        // No success
        message = `❌ Unable to convert any tracks from this playlist.`;
    }
    
    message += `\n\nA detailed report is included in your download.`;
    
    elements.downloadMessage.textContent = message;
    
    // Add detailed results if available
    if (status.failed_track_list && status.failed_track_list.length > 0) {
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'conversion-details';
        detailsDiv.innerHTML = `
            <h4>Failed Tracks:</h4>
            <ul class="failed-tracks-list">
                ${status.failed_track_list.map(track => 
                    `<li>❌ ${track.name} - ${track.artists.join(', ')}<br>
                     <small>Reason: ${track.reason}</small></li>`
                ).join('')}
            </ul>
        `;
        
        // Insert after the download message
        elements.downloadMessage.parentNode.insertBefore(detailsDiv, elements.downloadMessage.nextSibling);
    }
    
    showStep(elements.downloadStep);
}

function handleDownload() {
    if (!currentJobId) {
        showError('No download available');
        return;
    }
    
    showLoading('Preparing download...');
    
    downloadPlaylist(currentJobId)
        .then(() => {
            // Download started successfully
        })
        .catch(error => {
            showError(error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function handleNewConversion() {
    // Reset state
    currentPlaylist = null;
    currentJobId = null;
    
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    // Clear input
    elements.playlistUrl.value = '';
    
    // Show input step
    showStep(elements.inputStep);
}

function handleBack() {
    showStep(elements.inputStep);
}

function startApp() {
    // Hide hero section and show app interface
    document.querySelector('.hero').style.display = 'none';
    showStep(elements.inputStep);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    elements.loginBtn.addEventListener('click', startApp);
    elements.heroStartBtn.addEventListener('click', startApp);
    
    // Step 1: Input
    elements.analyzeBtn.addEventListener('click', handleAnalyze);
    elements.playlistUrl.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleAnalyze();
        }
    });
    
    // Step 2: Preview
    elements.backBtn.addEventListener('click', handleBack);
    elements.convertBtn.addEventListener('click', handleConvert);
    
    // Step 4: Download
    elements.downloadBtn.addEventListener('click', handleDownload);
    elements.newConversionBtn.addEventListener('click', handleNewConversion);
    
    // Error modal
    elements.closeErrorModal.addEventListener('click', hideError);
    elements.errorOkBtn.addEventListener('click', hideError);
    
    // Close modal on overlay click
    elements.errorModal.addEventListener('click', function(e) {
        if (e.target === elements.errorModal) {
            hideError();
        }
    });
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Handle page unload
window.addEventListener('beforeunload', function() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
});

// Export for debugging (optional)
if (typeof window !== 'undefined') {
    window.SpotifyConverter = {
        currentPlaylist,
        currentJobId,
        analyzePlaylist,
        startConversion,
        getConversionStatus
    };
}

