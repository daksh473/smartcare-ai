import React, { useRef, useState, useEffect } from 'react';

export default function FadingVideo({ src, className, style }) {
  const videoRef = useRef(null);
  const [opacity, setOpacity] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);

  const sources = Array.isArray(src) ? src : [src];
  const currentSrc = sources[currentIndex];

  useEffect(() => {
    // Reset opacity when source changes
    setOpacity(0);
  }, [currentSrc]);

  const handleLoadedData = () => {
    // Fade in over 500ms
    let start = null;
    const duration = 500;
    
    const animateFadeIn = (timestamp) => {
      if (!start) start = timestamp;
      const progress = timestamp - start;
      const newOpacity = Math.min(progress / duration, 1);
      setOpacity(newOpacity);
      if (progress < duration) {
        requestAnimationFrame(animateFadeIn);
      }
    };
    requestAnimationFrame(animateFadeIn);
  };

  const handleTimeUpdate = () => {
    const video = videoRef.current;
    if (!video) return;

    const remaining = video.duration - video.currentTime;
    // When 0.55s left, fade out over 550ms
    if (remaining <= 0.55 && opacity === 1) {
      let start = null;
      const duration = 550;
      
      const animateFadeOut = (timestamp) => {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        const newOpacity = Math.max(1 - (progress / duration), 0);
        setOpacity(newOpacity);
        if (progress < duration) {
          requestAnimationFrame(animateFadeOut);
        }
      };
      requestAnimationFrame(animateFadeOut);
    }
  };

  const handleEnded = () => {
    if (sources.length > 1) {
      setCurrentIndex((prev) => (prev + 1) % sources.length);
    } else {
      const video = videoRef.current;
      if (video) {
        video.currentTime = 0;
        video.play();
        handleLoadedData();
      }
    }
  };

  return (
    <video
      ref={videoRef}
      src={currentSrc}
      className={className}
      style={{ ...style, opacity, transition: 'opacity 0.1s linear' }}
      autoPlay
      muted
      playsInline
      preload="auto"
      onLoadedData={handleLoadedData}
      onTimeUpdate={handleTimeUpdate}
      onEnded={handleEnded}
    />
  );
}
