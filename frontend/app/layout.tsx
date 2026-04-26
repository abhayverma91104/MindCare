import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MindCare — Student Mental Wellness AI",
  description:
    "AI-powered stress and burnout detection system with personalized Gemini-driven support for university students.",
  keywords: ["mental health", "student wellness", "stress detection", "burnout", "AI chatbot"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
