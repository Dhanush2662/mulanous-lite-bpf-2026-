import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { AppFrame } from "@/components/app-frame";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Mulanous Lite",
  description: "Operational decisions for what needs attention today.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <AppFrame>{children}</AppFrame>
      </body>
    </html>
  );
}
