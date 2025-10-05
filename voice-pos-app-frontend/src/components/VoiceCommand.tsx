'use client';

import { useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface VoiceCommandProps {
  onVoiceResponse: (transcription: string, message: string) => void;
}

export default function VoiceCommand({ onVoiceResponse }: VoiceCommandProps) {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'https://voiceaihackweek-production.up.railway.app';
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');
        setAudioChunks(chunks);
        uploadAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
        
        const audioURL = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioURL);
        audio.play(); 

      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('مائیکروفون تک رسائی نہیں مل سکی۔ براہ کرم اجازت دیں۔');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const uploadAudio = async (audioBlob: Blob) => {
    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.wav');

      const response = await fetch(`${API_BASE}/voice-command`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        console.error('Server response:', errText);
        throw new Error('API call failed');
      }      

      const result = await response.json();
      onVoiceResponse(result.transcription, result.message);
    } catch (error) {
      console.error('Error uploading audio:', error);
      alert('آڈیو اپ لوڈ کرنے میں خرابی ہوئی۔ دوبارہ کوشش کریں۔');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/voice-command`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('API call failed');
      }

      const result = await response.json();
      onVoiceResponse(result.transcription, result.message);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('فائل اپ لوڈ کرنے میں خرابی ہوئی۔ دوبارہ کوشش کریں۔');
    } finally {
      setIsUploading(false);
      setIsProcessing(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const isAnyActionInProgress = isRecording || isUploading || isProcessing;

  const pulseVariants = useMemo(() => ({
    idle: { scale: 1 },
    recording: { scale: [1, 1.08, 1], boxShadow: [
      '0 0 0 0 rgba(239,68,68,0.6)',
      '0 0 0 16px rgba(239,68,68,0)',
      '0 0 0 0 rgba(239,68,68,0)'
    ], transition: { duration: 1.4, repeat: Infinity } },
  }), []);

  return (
    <div className="bg-white rounded-xl shadow-soft-lg p-6 border border-gray-200 animate-fade-in-up">
      <h2 className="text-xl font-bold text-gray-800 mb-6" dir="rtl">
        آواز کمانڈ
      </h2>

      {/* Recording Section */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4" dir="rtl">
          ریکارڈنگ
        </h3>
        
        <div className="flex flex-col items-center space-y-4">
        <motion.button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isUploading || isProcessing}
          variants={pulseVariants}
          animate={isRecording ? 'recording' : 'idle'}
          className={`
            w-24 h-24 rounded-full flex items-center justify-center text-3xl
            transition-all duration-300 transform hover:scale-105
            ${isRecording ? 'bg-red-500 hover:bg-red-600 text-white' : 'text-white'}
            ${!isRecording ? 'accent-gradient' : ''}
            ${(isUploading || isProcessing) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            accent-ring
          `}
        >
          {isRecording ? '⏹️' : '🎙️'}
        </motion.button>
          
          <p className="text-sm text-gray-600 text-center" dir="rtl">
            {isRecording ? 'ریکارڈنگ جاری ہے... کلک کرکے روکیں' : 'ریکارڈنگ شروع کرنے کے لیے کلک کریں'}
          </p>
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-gray-200 my-6">
        <div className="text-center -mt-3">
          <span className="bg-white px-4 text-gray-500 text-sm rounded-full">یا</span>
        </div>
      </div>

      {/* File Upload Section */}
      <div>
        <h3 className="text-lg font-semibold text-gray-700 mb-4" dir="rtl">
          فائل اپ لوڈ
        </h3>
        
        <div className="space-y-4">
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*,.wav"
            onChange={handleFileUpload}
            disabled={isAnyActionInProgress}
            className="hidden"
          />
          
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isAnyActionInProgress}
            className={`
              w-full py-3 px-4 rounded-lg border-2 border-dashed border-gray-300 glass
              hover:border-blue-400 hover:bg-blue-50/40 transition-all duration-300
              flex items-center justify-center space-x-2
              ${isAnyActionInProgress ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <span className="text-2xl">📁</span>
            <span className="text-gray-700 font-medium" dir="rtl">
              WAV فائل اپ لوڈ کریں
            </span>
          </button>
          
          <p className="text-xs text-gray-500 text-center" dir="rtl">
            WAV, MP3, یا کوئی بھی آڈیو فائل
          </p>
        </div>
      </div>

      {/* Loading Spinner */}
      {isProcessing && (
        <div className="mt-6 flex items-center justify-center space-x-3">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
          </span>
          <span className="text-sm text-gray-600" dir="rtl">
            ٹرانسکرپشن ہو رہا ہے...
          </span>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="text-sm font-semibold text-blue-800 mb-2" dir="rtl">
          استعمال کی ہدایات:
        </h4>
        <ul className="text-xs text-blue-700 space-y-1" dir="rtl">
          <li>• &quot;سیلز&quot; کہیں سیلز رپورٹ کے لیے</li>
          <li>• &quot;پروڈکٹ&quot; کہیں پروڈکٹ لسٹ کے لیے</li>
          <li>• &quot;بل&quot; کہیں بلنگ کے لیے</li>
        </ul>
      </div>
    </div>
  );
}