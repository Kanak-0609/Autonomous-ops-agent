import type { AppProps } from "next/app";
import { Space_Grotesk, Inter } from "next/font/google";
import "@/styles/globals.css";

const display = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "700"],
});

const body = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600"],
});

export default function App({ Component, pageProps }: AppProps) {
  return (
    <main className={`${display.variable} ${body.variable}`}>
      <Component {...pageProps} />
    </main>
  );
}