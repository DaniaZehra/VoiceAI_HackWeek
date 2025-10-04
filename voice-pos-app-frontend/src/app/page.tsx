'use client';

import { useState } from 'react';
import VoiceCommand from '@/components/VoiceCommand';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  const [transcription, setTranscription] = useState('');
  const [response, setResponse] = useState('');

  const handleVoiceResponse = (transcription: string, message: string) => {
    setTranscription(transcription);
    setResponse(message);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100" dir="ltr">
      {/* Navbar */}
      <nav className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-gray-800">
                  Hisaab Kitaab
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600" dir="rtl">
              آواز سے کنٹرول کریں
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Dashboard Section */}
          <div className="lg:col-span-2">
            <Dashboard />
          </div>

          {/* Voice Command Section */}
          <div className="lg:col-span-1">
            <VoiceCommand onVoiceResponse={handleVoiceResponse} />
            
            {/* Transcription Display */}
            {(transcription || response) && (
              <div className="mt-6 bg-white rounded-xl shadow-lg p-6 border border-gray-200 animate-fade-in-up">
                <h3 className="text-lg font-semibold text-gray-800 mb-4" dir="rtl">
                  ہساب کتاب کا جواب
                </h3>
                
                {transcription && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-600 mb-2" dir="rtl">
                      ٹرانسکرپشن:
                    </h4>
                    <p className="text-gray-800 bg-gray-50 p-3 rounded-lg border" dir="rtl">
                      {transcription}
                    </p>
                  </div>
                )}
                
                {response && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-600 mb-2" dir="rtl">
                      سسٹم کا جواب:
                    </h4>
                    <p className="text-gray-800 bg-blue-50 p-3 rounded-lg border border-blue-200" dir="rtl">
                      {response}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}