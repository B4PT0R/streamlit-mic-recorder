/// <reference types="react-scripts" />
declare module 'audiobuffer-to-wav';
declare module 'tinycolor2'

interface Window {
    webkitAudioContext: typeof AudioContext;
  }
