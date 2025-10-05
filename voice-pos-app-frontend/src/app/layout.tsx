import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Hisaab Kitaab - ہساب کتاب",
  description: "ہساب کتاب سے کنٹرول",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ur" dir="rtl">
      <body className={`${inter.variable} font-sans antialiased`}>
        <div className="relative min-h-screen overflow-x-hidden">
          {/* Animated background */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 -z-10 bg-[linear-gradient(120deg,#eef2ff_0%,#f5f7ff_50%,#eefdf3_100%)] opacity-70"
          />

          {/* Content container */}
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
