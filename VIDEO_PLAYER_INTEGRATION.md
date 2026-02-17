# Video Player Integration Guide - Videoflix

## HLS Video Player Implementation

This guide shows how to integrate a video player in the frontend for HLS streaming.

## 📺 Recommended Players

### 1. Video.js (Recommended)
- ✅ Open Source
- ✅ HLS Support via plugin
- ✅ Customizable
- ✅ Mobile-friendly
- ✅ Full documentation

### 2. hls.js
- ✅ Lightweight
- ✅ Pure JavaScript
- ✅ Works with HTML5 video

### 3. Plyr
- ✅ Modern UI
- ✅ HLS Support
- ✅ Beautiful design

---

## 🎬 Implementation with Video.js

### Installation

```bash
npm install video.js @videojs/http-streaming
```

### React Component

```javascript
import React, { useEffect, useRef, useState } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import '@videojs/http-streaming';

const VideoPlayer = ({ videoId }) => {
  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const [videoData, setVideoData] = useState(null);
  const [selectedQuality, setSelectedQuality] = useState('720p');

  useEffect(() => {
    // Load video stream data
    fetch(`/api/video/${videoId}/stream/`, {
      credentials: 'include'
    })
    .then(res => res.json())
    .then(data => {
      setVideoData(data);
      initializePlayer(data);
    });

    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
      }
    };
  }, [videoId]);

  const initializePlayer = (data) => {
    if (!videoRef.current) return;

    const player = videojs(videoRef.current, {
      controls: true,
      autoplay: false,
      preload: 'auto',
      fluid: true,
      responsive: true,
      poster: data.thumbnail_url,
      sources: [{
        src: data.hls_streams[selectedQuality],
        type: 'application/x-mpegURL'
      }]
    });

    playerRef.current = player;

    // Event Listeners
    player.on('play', () => console.log('Video started'));
    player.on('pause', () => console.log('Video paused'));
    player.on('ended', () => console.log('Video ended'));
  };

  const changeQuality = (quality) => {
    if (playerRef.current && videoData) {
      const currentTime = playerRef.current.currentTime();
      const isPaused = playerRef.current.paused();
      
      // Change source
      playerRef.current.src({
        src: videoData.hls_streams[quality],
        type: 'application/x-mpegURL'
      });
      
      // Restore playback state
      playerRef.current.currentTime(currentTime);
      if (!isPaused) {
        playerRef.current.play();
      }
      
      setSelectedQuality(quality);
    }
  };

  return (
    <div className="video-player-container">
      {/* Quality Selector */}
      <div className="quality-selector">
        {videoData?.available_qualities.map(quality => (
          <button
            key={quality}
            onClick={() => changeQuality(quality)}
            className={selectedQuality === quality ? 'active' : ''}
          >
            {quality}
          </button>
        ))}
      </div>

      {/* Video Player */}
      <div data-vjs-player>
        <video
          ref={videoRef}
          className="video-js vjs-default-skin vjs-big-play-centered"
        />
      </div>

      {/* Video Info */}
      {videoData && (
        <div className="video-info">
          <h2>{videoData.title}</h2>
          <p>{videoData.description}</p>
          <span>Dauer: {videoData.formatted_duration}</span>
        </div>
      )}
    </div>
  );
};

export default VideoPlayer;
```

### Styling

```css
.video-player-container {
  width: 100%;
  max-width: 1920px;
  margin: 0 auto;
  background: #000;
}

.quality-selector {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  display: flex;
  gap: 10px;
}

.quality-selector button {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  border: 1px solid #666;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.quality-selector button.active {
  background: #e50914;
  border-color: #e50914;
}

.video-js {
  width: 100%;
  height: 600px;
}

.video-js .vjs-big-play-button {
  border-color: #e50914;
  background-color: rgba(229, 9, 20, 0.8);
}

.video-js .vjs-control-bar {
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
}
```

---

## 🎬 Implementation with hls.js

### Installation

```bash
npm install hls.js
```

### React Component

```javascript
import React, { useEffect, useRef, useState } from 'react';
import Hls from 'hls.js';

const HLSPlayer = ({ videoId }) => {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [videoData, setVideoData] = useState(null);
  const [selectedQuality, setSelectedQuality] = useState('720p');

  useEffect(() => {
    // Load video data
    fetch(`/api/video/${videoId}/stream/`, {
      credentials: 'include'
    })
    .then(res => res.json())
    .then(data => {
      setVideoData(data);
      loadVideo(data.hls_streams[selectedQuality]);
    });

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
      }
    };
  }, [videoId]);

  const loadVideo = (streamUrl) => {
    if (!videoRef.current) return;

    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 90
      });

      hls.loadSource(streamUrl);
      hls.attachMedia(videoRef.current);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log('HLS manifest loaded');
      });

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error('HLS error:', data);
      });

      hlsRef.current = hls;
    } 
    // Fallback for Safari (native HLS support)
    else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
      videoRef.current.src = streamUrl;
    }
  };

  const changeQuality = (quality) => {
    if (videoData) {
      const currentTime = videoRef.current.currentTime;
      loadVideo(videoData.hls_streams[quality]);
      videoRef.current.currentTime = currentTime;
      setSelectedQuality(quality);
    }
  };

  return (
    <div className="hls-player">
      {/* Quality Selector */}
      <div className="quality-buttons">
        {videoData?.available_qualities.map(q => (
          <button 
            key={q}
            onClick={() => changeQuality(q)}
            className={selectedQuality === q ? 'active' : ''}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Video Element */}
      <video
        ref={videoRef}
        controls
        poster={videoData?.thumbnail_url}
        width="100%"
      >
        Your browser does not support HLS video.
      </video>
    </div>
  );
};

export default HLSPlayer;
```

---

## 🎮 Player Controls

### Required Controls (User Story 6)

#### 1. Play/Pause ✅
```javascript
// Built-in HTML5 controls
<video controls />

// Custom controls
const togglePlay = () => {
  if (videoRef.current.paused) {
    videoRef.current.play();
  } else {
    videoRef.current.pause();
  }
};
```

#### 2. Seek (Vor/Zurückspulen) ✅
```javascript
// Built-in seekbar
<video controls />

// Custom seek
const seek = (seconds) => {
  videoRef.current.currentTime += seconds;
};

// Keyboard shortcuts
useEffect(() => {
  const handleKeyPress = (e) => {
    if (e.key === 'ArrowLeft') seek(-10);   // 10s zurück
    if (e.key === 'ArrowRight') seek(10);   // 10s vor
    if (e.key === ' ') togglePlay();         // Play/Pause
  };
  
  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, []);
```

#### 3. Fullscreen ✅
```javascript
// Built-in fullscreen button
<video controls />

// Custom fullscreen
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    videoRef.current.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

<button onClick={toggleFullscreen}>
  {isFullscreen ? '⛶ Exit' : '⛶ Fullscreen'}
</button>
```

#### 4. Volume Control ✅
```javascript
// Built-in volume control
<video controls />

// Custom volume
const changeVolume = (value) => {
  videoRef.current.volume = value / 100;
};

<input 
  type="range" 
  min="0" 
  max="100" 
  onChange={(e) => changeVolume(e.target.value)}
/>
```

---

## 🔧 API Endpoints for Playback

### Get Stream URLs

**Request:**
```http
GET /api/video/{id}/stream/
Authorization: Bearer <token>
Cookie: access_token=xxx
```

**Response:**
```json
{
  "id": 1,
  "title": "Breaking Bad - Season 1",
  "description": "...",
  "thumbnail_url": "http://localhost:8000/media/thumbnails/1/thumbnail.jpg",
  "duration": 2940,
  "formatted_duration": "49:00",
  "available_qualities": ["360p", "480p", "720p", "1080p"],
  "hls_streams": {
    "360p": "http://localhost:8000/api/video/1/360p/index.m3u8",
    "480p": "http://localhost:8000/api/video/1/480p/index.m3u8",
    "720p": "http://localhost:8000/api/video/1/720p/index.m3u8",
    "1080p": "http://localhost:8000/api/video/1/1080p/index.m3u8"
  }
}
```

### Get HLS Playlist

**Request:**
```http
GET /api/video/{id}/{resolution}/index.m3u8
Authorization: Bearer <token>
```

**Response (M3U8 Playlist):**
```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
segment_000.ts
#EXTINF:10.0,
segment_001.ts
#EXTINF:10.0,
segment_002.ts
#EXT-X-ENDLIST
```

### Get Video Segment

**Request:**
```http
GET /api/video/{id}/{resolution}/segment_000.ts
Authorization: Bearer <token>
```

**Response:** Binary TS file

---

## 🎨 Complete Video Player Component

```javascript
import React, { useEffect, useRef, useState } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

const VideoflixPlayer = ({ videoId, onClose }) => {
  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const [videoData, setVideoData] = useState(null);
  const [selectedQuality, setSelectedQuality] = useState('720p');
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    loadVideoData();
    return () => cleanup();
  }, [videoId]);

  const loadVideoData = async () => {
    const response = await fetch(`/api/video/${videoId}/stream/`, {
      credentials: 'include'
    });
    const data = await response.json();
    setVideoData(data);
    initializePlayer(data);
  };

  const initializePlayer = (data) => {
    if (!videoRef.current) return;

    const player = videojs(videoRef.current, {
      controls: true,
      autoplay: false,
      preload: 'auto',
      fluid: true,
      poster: data.thumbnail_url,
      controlBar: {
        children: [
          'playToggle',
          'volumePanel',
          'currentTimeDisplay',
          'timeDivider',
          'durationDisplay',
          'progressControl',
          'remainingTimeDisplay',
          'playbackRateMenuButton',
          'fullscreenToggle'
        ]
      },
      sources: [{
        src: data.hls_streams[selectedQuality],
        type: 'application/x-mpegURL'
      }]
    });

    // Custom hotkeys
    player.on('keydown', (e) => {
      if (e.key === 'f') player.requestFullscreen();
      if (e.key === ' ') player.paused() ? player.play() : player.pause();
    });

    playerRef.current = player;
  };

  const changeQuality = (quality) => {
    if (!playerRef.current || !videoData) return;
    
    const currentTime = playerRef.current.currentTime();
    const isPaused = playerRef.current.paused();
    
    playerRef.current.src({
      src: videoData.hls_streams[quality],
      type: 'application/x-mpegURL'
    });
    
    playerRef.current.one('loadedmetadata', () => {
      playerRef.current.currentTime(currentTime);
      if (!isPaused) playerRef.current.play();
    });
    
    setSelectedQuality(quality);
  };

  const cleanup = () => {
    if (playerRef.current) {
      playerRef.current.dispose();
      playerRef.current = null;
    }
  };

  if (!videoData) return <div>Loading...</div>;

  return (
    <div className="videoflix-player">
      {/* Close Button */}
      <button className="close-btn" onClick={onClose}>
        ✕
      </button>

      {/* Quality Selector */}
      <div className="quality-selector">
        <label>Qualität:</label>
        {videoData.available_qualities.map(quality => (
          <button
            key={quality}
            onClick={() => changeQuality(quality)}
            className={selectedQuality === quality ? 'active' : ''}
          >
            {quality}
          </button>
        ))}
      </div>

      {/* Video Player */}
      <div data-vjs-player>
        <video
          ref={videoRef}
          className="video-js vjs-theme-videoflix"
        />
      </div>

      {/* Video Metadata */}
      <div className="video-metadata">
        <h2>{videoData.title}</h2>
        <p>{videoData.description}</p>
        <span className="duration">
          🕐 {videoData.formatted_duration}
        </span>
      </div>
    </div>
  );
};

export default VideoflixPlayer;
```

---

## 🎨 Custom Video.js Theme

```css
/* Videoflix Theme for Video.js */
.vjs-theme-videoflix {
  font-family: Arial, sans-serif;
}

/* Big Play Button */
.vjs-theme-videoflix .vjs-big-play-button {
  border-color: #e50914;
  background-color: rgba(229, 9, 20, 0.9);
  border-radius: 50%;
  width: 80px;
  height: 80px;
  line-height: 80px;
  font-size: 48px;
  border-width: 2px;
}

.vjs-theme-videoflix .vjs-big-play-button:hover {
  background-color: #e50914;
}

/* Control Bar */
.vjs-theme-videoflix .vjs-control-bar {
  background: linear-gradient(transparent, rgba(0,0,0,0.9));
  height: 60px;
}

/* Progress Bar */
.vjs-theme-videoflix .vjs-play-progress {
  background-color: #e50914;
}

.vjs-theme-videoflix .vjs-load-progress {
  background: rgba(255, 255, 255, 0.3);
}

/* Volume */
.vjs-theme-videoflix .vjs-volume-level {
  background-color: #e50914;
}

/* Buttons */
.vjs-theme-videoflix .vjs-button:hover {
  color: #e50914;
}
```

---

## 🔧 Player Features Implementation

### 1. Multiple Quality Selection ✅

```javascript
const QualityMenu = ({ qualities, selected, onChange }) => {
  return (
    <div className="quality-menu">
      <select value={selected} onChange={(e) => onChange(e.target.value)}>
        {qualities.map(q => (
          <option key={q} value={q}>{q}</option>
        ))}
      </select>
    </div>
  );
};
```

### 2. Play/Pause Controls ✅

```javascript
// Video.js automatically provides:
// - Play button
// - Pause button
// - Spacebar for toggle
// - Click on video for toggle

// Custom implementation:
const [isPlaying, setIsPlaying] = useState(false);

const togglePlay = () => {
  if (videoRef.current.paused) {
    videoRef.current.play();
    setIsPlaying(true);
  } else {
    videoRef.current.pause();
    setIsPlaying(false);
  }
};

<button onClick={togglePlay}>
  {isPlaying ? '⏸ Pause' : '▶ Play'}
</button>
```

### 3. Seek Controls (Vor/Zurückspulen) ✅

```javascript
// Video.js automatically provides:
// - Progress bar (seekbar)
// - Click to seek
// - Drag to seek
// - Arrow keys for +/- 5s

// Custom seek buttons:
const seekBackward = () => {
  videoRef.current.currentTime -= 10;
};

const seekForward = () => {
  videoRef.current.currentTime += 10;
};

<button onClick={seekBackward}>⏪ -10s</button>
<button onClick={seekForward}>⏩ +10s</button>

// Keyboard shortcuts:
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft') seekBackward();
  if (e.key === 'ArrowRight') seekForward();
});
```

### 4. Fullscreen Option ✅

```javascript
// Video.js automatically provides:
// - Fullscreen button
// - ESC to exit
// - F key for fullscreen

// Custom fullscreen:
const toggleFullscreen = () => {
  const container = videoRef.current.parentElement;
  
  if (!document.fullscreenElement) {
    container.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

// Listen for fullscreen changes
useEffect(() => {
  const handleFullscreenChange = () => {
    setIsFullscreen(!!document.fullscreenElement);
  };
  
  document.addEventListener('fullscreenchange', handleFullscreenChange);
  return () => {
    document.removeEventListener('fullscreenchange', handleFullscreenChange);
  };
}, []);
```

---

## 📱 Responsive Player

```css
/* Desktop */
.video-player-container {
  max-width: 1920px;
  margin: 0 auto;
}

.video-js {
  width: 100%;
  height: 600px;
}

/* Tablet */
@media (max-width: 1024px) {
  .video-js {
    height: 500px;
  }
  
  .quality-selector {
    font-size: 14px;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .video-js {
    height: 400px;
  }
  
  .quality-selector {
    top: 10px;
    right: 10px;
  }
  
  .quality-selector button {
    padding: 6px 12px;
    font-size: 12px;
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .video-js {
    height: 250px;
  }
}
```

---

## ⚡ Performance Optimization

### Lazy Loading
```javascript
import { lazy, Suspense } from 'react';

const VideoPlayer = lazy(() => import('./VideoPlayer'));

<Suspense fallback={<LoadingSkeleton />}>
  <VideoPlayer videoId={id} />
</Suspense>
```

### Preload Strategy
```javascript
// Don't preload on mobile (save bandwidth)
const isMobile = window.innerWidth < 768;

<video 
  preload={isMobile ? 'metadata' : 'auto'}
  controls
/>
```

---

## 🧪 Testing

```javascript
// Test video playback
describe('VideoPlayer', () => {
  it('should load video with selected quality', async () => {
    render(<VideoPlayer videoId={1} />);
    
    await waitFor(() => {
      expect(screen.getByText('720p')).toHaveClass('active');
    });
  });
  
  it('should change quality', async () => {
    render(<VideoPlayer videoId={1} />);
    
    fireEvent.click(screen.getByText('1080p'));
    
    await waitFor(() => {
      expect(screen.getByText('1080p')).toHaveClass('active');
    });
  });
  
  it('should toggle fullscreen', () => {
    render(<VideoPlayer videoId={1} />);
    
    const fullscreenBtn = screen.getByText('Fullscreen');
    fireEvent.click(fullscreenBtn);
    
    expect(document.fullscreenElement).toBeTruthy();
  });
});
```

---

## 📚 Resources

- **Video.js:** https://videojs.com/
- **hls.js:** https://github.com/video-dev/hls.js/
- **HLS Specification:** https://datatracker.ietf.org/doc/html/rfc8216
- **MDN Video Element:** https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video
