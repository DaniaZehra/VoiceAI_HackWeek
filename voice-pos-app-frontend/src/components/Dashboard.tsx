'use client';

import { useEffect, useMemo, useState, ReactNode } from 'react';
import { FaBoxOpen, FaChartBar, FaReceipt } from 'react-icons/fa';

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

  // Animated counter logic
  const [counter, setCounter] = useState(0);
  const target = salesData.today + salesData.yesterday;

  useEffect(() => {
    let raf: number;
    const start = performance.now();
    const duration = 1200;

    const step = (t: number) => {
      const progress = Math.min(1, (t - start) / duration);
      setCounter(Math.floor(progress * target));
      if (progress < 1) raf = requestAnimationFrame(step);
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target]);

  const summaryCards = useMemo(() => ([
    { label: 'آج', value: salesData.today, color: 'green' },
    { label: 'کل', value: salesData.yesterday, color: 'blue' },
    { label: 'اس ہفتہ', value: salesData.thisWeek, color: 'purple' },
    { label: 'اس مہینہ', value: salesData.thisMonth, color: 'orange' },
  ]), [salesData]);

  return (
    <div className="space-y-6">
      {/* Sales Summary */}
      <div className="bg-white rounded-xl shadow-soft-lg p-4 border border-gray-200 animate-fade-in-up">
        <h2 className="text-xl font-bold text-gray-800 mb-3" dir="rtl">
          آج کی فروخت کا خلاصہ
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {summaryCards.map((item) => (
            <div key={item.label} className="kpi-card text-center p-4">
              <div className="text-xs uppercase tracking-wide text-gray-500" dir="rtl">{item.label}</div>
              <div className="mt-1 text-2xl font-extrabold text-gray-900">₨{item.value.toLocaleString()}</div>
              <div className="mt-2 h-1 rounded-full accent-gradient" />
            </div>
          ))}
        </div>
        <div className="mt-4 text-sm text-gray-600" dir="rtl">
          مجموعی آمدن: <span className="font-semibold text-blue-700">₨{counter.toLocaleString()}</span>
        </div>
      </div>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <DashboardCard
          title="سیلز رپورٹ"
          subtitle="تفصیلی فروخت کی رپورٹ دیکھیں"
          icon={<FaChartBar />}
          onClick={() => handleCardClick('Sales Report')}
        />
        <DashboardCard
          title="باکسز"
          subtitle="نئے باکس بنائیں اور پرانے دیکھیں"
          icon={<FaBoxOpen />}
          onClick={() => handleCardClick('Boxes')}
        />
        <DashboardCard
          title="بلنگ"
          subtitle="نئے بل بنائیں اور پرانے دیکھیں"
          icon={<FaReceipt />}
          onClick={() => handleCardClick('Billing')}
        />
      </div>

      {/* Quick Stats */}
      <div className="bg-white rounded-xl shadow-soft-lg p-3 border border-gray-200 animate-fade-in-up">
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