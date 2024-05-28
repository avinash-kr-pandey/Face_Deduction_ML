import React, { useEffect, useRef } from 'react';

function WebcamOverlay() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const startWebcam = () => {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        })
        .catch(err => console.error("Error accessing webcam: ", err));
    };

    const processFrame = async () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const frame = canvas.toDataURL('image/jpeg');

      const response = await fetch('http://localhost:5000/process-frame', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ frame: frame.split(',')[1] })
      });
      const data = await response.json();
      const img = new Image();
      img.src = 'data:image/jpeg;base64,' + data.frame;
      img.onload = () => {
        context.drawImage(img, 0, 0, canvas.width, canvas.height);
      };
    };

    startWebcam();

    const interval = setInterval(() => {
      processFrame();
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Live Webcam with Glasses Overlay</h1>
      <video ref={videoRef} style={{ display: 'none' }}></video>
      <canvas ref={canvasRef}></canvas>
    </div>
  );
}

export default WebcamOverlay;
