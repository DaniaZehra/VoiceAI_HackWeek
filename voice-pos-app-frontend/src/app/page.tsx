'use client';

import { useState } from 'react';
import VoiceCommand from '@/components/VoiceCommand';
import Dashboard from '@/components/Dashboard';
import { motion, AnimatePresence } from 'framer-motion';

interface Transaction {
  id: number;
  description: string;
  amount: number;
  payment_method: string;
  created_at: string;
}

interface ResponseData {
  date: string;
  total_transactions: number;
  total_sales: number;
  payment_breakdown: { [key: string]: number };
  transactions: Transaction[];
}

export default function Home() {
  const [transcription, setTranscription] = useState('');
  const [response, setResponse] = useState<ResponseData | string>('');

  const handleVoiceResponse = (transcription: string, message: ResponseData | string) => {
    setTranscription(transcription);
    console.log(typeof message)
    setResponse(message);
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key="home"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="min-h-screen"
        dir="ltr"
      >
      {/* Navbar */}
      <nav className="bg-white rounded-xl shadow-soft-lg mt-2 border border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg accent-gradient" />
                  <h1 className="text-2xl font-bold text-gray-800">
                    Hisaab Kitaab
                  </h1>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3"> 
              <div className="text-sm text-gray-800" dir="rtl">
              آواز سے کنٹرول کریں
              </div>
              <div className="hidden sm:block">
                <span className="inline-flex items-center rounded-lg px-3 py-1 text-sm text-white accent-gradient shadow-glow">
                  POS
                </span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Dashboard Section */}
          <div className="w-full">
            <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
              <Dashboard />
            </motion.div>
          </div>

          {/* Voice Command Section */}
          <div className="w-full">
            <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5, delay: 0.05 }}>
              <VoiceCommand onVoiceResponse={handleVoiceResponse} />
            </motion.div>
            
            {/* Transcription Display */}
            {(transcription || response) && (
              <div className="mt-6 glass gradient-border rounded-xl shadow-soft-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4" dir="rtl">
                  ہساب کتاب کا جواب
                </h3>
                
                {transcription && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-600 mb-2" dir="rtl">
                      ٹرانسکرپشن:
                    </h4>
                    <p className="text-gray-800 bg-white/60 p-3 rounded-lg border" dir="rtl">
                      {transcription}
                    </p>
                  </div>
                )}
                
               {response && (
  <div>
    <h4 className="text-sm font-medium text-gray-600 mb-2" dir="rtl">
      سسٹم کا جواب:
    </h4>

    {/* If it's a string, just show it */}
    {typeof response === "string" ? (
      <p className="text-gray-800 bg-blue-50/70 p-3 rounded-lg border border-blue-200" dir="rtl">
        {response}
      </p>
    ) : (
      response && (
        <div className="p-4 bg-blue-50/70 rounded-lg border border-blue-200">
          {/* Date and summary */}
          <div className="bg-white/80 shadow rounded-lg p-4 border mb-4" dir="rtl">
            <p className="text-sm text-blue-700"><strong>تاریخ:</strong> {response.date}</p>
            <p className="text-sm text-blue-700"><strong>کل لین دین:</strong> {response.total_transactions}</p>
            <p className="text-sm text-blue-700"><strong>کل فروخت:</strong> {response.total_sales}</p>
          </div>

          {/* Payment breakdown */}
          <div className="bg-white/80 shadow rounded-lg p-4 border mb-4" dir="rtl">
            <h5 className="text-sm font-semibold text-blue-800 mb-2">ادائیگی کی تفصیل:</h5>
            <ul className="text-xs text-blue-700 space-y-1 list-disc pr-5">
              {Object.entries(response.payment_breakdown).map(([method, amount]) => (
                <li key={method}>
                  {method}: {amount}
                </li>
              ))}
            </ul>
          </div>

          {/* Transactions */}
          <div className="bg-white/80 shadow rounded-lg p-4 border" dir="rtl">
            <h5 className="text-sm font-semibold text-blue-800 mb-2">لین دین کی فہرست:</h5>
            <table className="w-full border-collapse text-xs text-blue-700">
              <thead>
                <tr className="bg-blue-100 text-right">
                  <th className="p-2 border border-blue-200">ID</th>
                  <th className="p-2 border border-blue-200">تفصیل</th>
                  <th className="p-2 border border-blue-200">رقم</th>
                  <th className="p-2 border border-blue-200">ادائیگی کا طریقہ</th>
                  <th className="p-2 border border-blue-200">تاریخ</th>
                </tr>
              </thead>
              <tbody>
                {response.transactions.map((tx: Transaction) => (
                  <tr key={tx.id} className="hover:bg-blue-50">
                    <td className="p-2 border border-blue-200 text-xs">{tx.id}</td>
                    <td className="p-2 border border-blue-200">{tx.description}</td>
                    <td className="p-2 border border-blue-200">{tx.amount}</td>
                    <td className="p-2 border border-blue-200">{tx.payment_method || "نامعلوم"}</td>
                    <td className="p-2 border border-blue-200">{tx.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )
    )}
  </div>
)}

              </div>
            )}
          </div>
        </div>
      </main>
      </motion.div>
    </AnimatePresence>
  );
}