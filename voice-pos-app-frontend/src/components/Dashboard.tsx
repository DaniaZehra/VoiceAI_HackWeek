'use client';

import { useState } from 'react';
import { FaChartBar, FaBoxOpen, FaReceipt, FaBoxes } from 'react-icons/fa';
import { ReactNode } from 'react';

interface DashboardCardProps {
  title: string;
  subtitle: string;
  icon: ReactNode;
  onClick: () => void;
}

const DashboardCard = ({ title, subtitle, icon, onClick }: DashboardCardProps) => (
  <div 
    onClick={onClick}
    className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 cursor-pointer border border-gray-200 hover:border-blue-300 group"
  >
    <div className="flex items-center justify-between">
      <div>
        <h3 className="text-lg font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">
          {title}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          {subtitle}
        </p>
      </div>
      <div className="text-3xl group-hover:scale-110 transition-transform">
        {icon}
      </div>
    </div>
  </div>
);

export default function Dashboard() {
  const [salesData] = useState({
    today: 125000,
    yesterday: 98000,
    thisWeek: 750000,
    thisMonth: 2100000
  });

  const handleCardClick = (cardType: string) => {
    console.log(`${cardType} clicked`);
  };

  return (
    <div className="space-y-6">
      {/* Sales Summary */}
      <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-200 animate-fade-in-up">
        <h2 className="text-xl font-bold text-gray-800 mb-3" dir="rtl">
          آج کی فروخت کا خلاصہ
        </h2>
        
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center p-2 bg-green-50 rounded-lg border border-green-200">
            <div className="text-2xl font-bold text-green-600">
              ₨{salesData.today.toLocaleString()}
            </div>
            <div className="text-sm text-green-700" dir="rtl">آج</div>
          </div>
          
          <div className="text-center p-2 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-2xl font-bold text-blue-600">
              ₨{salesData.yesterday.toLocaleString()}
            </div>
            <div className="text-sm text-blue-700" dir="rtl">کل</div>
          </div>
          
          <div className="text-center p-2 bg-purple-50 rounded-lg border border-purple-200">
            <div className="text-2xl font-bold text-purple-600">
              ₨{salesData.thisWeek.toLocaleString()}
            </div>
            <div className="text-sm text-purple-700" dir="rtl">اس ہفتہ</div>
          </div>
          
          <div className="text-center p-2 bg-orange-50 rounded-lg border border-orange-200">
            <div className="text-2xl font-bold text-orange-600">
              ₨{salesData.thisMonth.toLocaleString()}
            </div>
            <div className="text-sm text-orange-700" dir="rtl">اس مہینہ</div>
          </div>
        </div>
      </div>

      {/* Action Cards
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <DashboardCard
          title="سیلز رپورٹ"
          subtitle="تفصیلی فروخت کی رپورٹ دیکھیں"
          icon={<FaChartBar />}
          onClick={() => handleCardClick('Sales Report')}
        />
        <DashboardCard
          title="بلنگ"
          subtitle="نئے بل بنائیں اور پرانے دیکھیں"
          icon={<FaReceipt />}
          onClick={() => handleCardClick('Billing')}
        />
      </div> */}

      {/* Quick Stats */}
      <div className="bg-white rounded-xl shadow-lg p-3 border border-gray-200 animate-fade-in-up">
        <h3 className="text-lg font-semibold text-gray-800 mb-2" dir="rtl">
          فوری اعداد و شمار
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-xl font-bold text-gray-700">156</div>
            <div className="text-sm text-gray-600" dir="rtl">آج کے آرڈر</div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-xl font-bold text-gray-700">89</div>
            <div className="text-sm text-gray-600" dir="rtl">مکمل شدہ</div>
          </div>
          
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-xl font-bold text-gray-700">67</div>
            <div className="text-sm text-gray-600" dir="rtl">زیر التواء</div>
          </div>
        </div>
      </div>
    </div>
  );
}