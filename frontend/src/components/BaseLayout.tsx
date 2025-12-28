"use client";

import { ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Settings, LogOut } from "lucide-react";
import { FooterSection } from "@/components/Footer";
import { DashboardHeader } from "@/components/DashboardHeader";

interface BaseLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  headerActions?: ReactNode;
  showBackground?: boolean;
  showFooter?: boolean;
  gradientVariant?: "blue" | "cyan" | "purple" | "green";
  useDashboardHeader?: boolean;
  dashboardRole?: "creator" | "node" | "admin";
}

export default function BaseLayout({
  children,
  title,
  subtitle,
  headerActions,
  showBackground = true,
  showFooter = true,
  gradientVariant = "blue",
  useDashboardHeader = false,
  dashboardRole = "creator",
}: BaseLayoutProps) {
  // Gradient color configurations based on role/page type
  const gradientColors = {
    blue: {
      title: "from-blue-400 to-cyan-400",
      bg1: "bg-blue-500/30",
      bg2: "bg-cyan-500/20",
    },
    cyan: {
      title: "from-cyan-400 to-purple-400",
      bg1: "bg-cyan-500/30",
      bg2: "bg-purple-500/20",
    },
    purple: {
      title: "from-purple-400 to-blue-400",
      bg1: "bg-purple-500/30",
      bg2: "bg-blue-500/20",
    },
    green: {
      title: "from-green-400 to-cyan-400",
      bg1: "bg-green-500/30",
      bg2: "bg-cyan-500/20",
    },
  };

  const colors = gradientColors[gradientVariant];

  return (
    <div className="min-h-screen bg-zinc-950 flex flex-col">
      {/* Background Layer */}
      {showBackground && (
        <>
          {/* Background Image with Overlay */}
          <div className="fixed inset-0 z-0">
            <Image
              src="/background-image.png"
              alt="Background"
              fill
              className="object-cover opacity-60"
              priority
            />
            <div className="absolute inset-0 bg-zinc-950/70" />
          </div>

          {/* Cosmic Gradient Overlays */}
          <div aria-hidden className="fixed inset-0 z-0 opacity-40">
            <div
              className={`w-96 h-96 absolute top-0 right-1/4 rounded-full blur-3xl ${colors.bg1}`}
            />
            <div
              className={`w-96 h-96 absolute bottom-1/4 left-1/4 rounded-full blur-3xl ${colors.bg2}`}
            />
          </div>
        </>
      )}

      {/* Header */}
      {useDashboardHeader ? (
        <DashboardHeader role={dashboardRole} />
      ) : (
        <header className="fixed top-0 left-0 right-0 z-50 bg-zinc-900/80 backdrop-blur-md border-b border-zinc-800">
          <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16 sm:h-20">
              {/* Logo/Brand */}
              <Link href="/" className="flex items-center gap-2 group shrink-0">
                <Image
                  src="/logo.png"
                  alt="GalaxyRend Logo"
                  width={140}
                  height={50}
                  className="h-8 sm:h-10 w-auto transition-all duration-300 group-hover:scale-105"
                />
              </Link>

              {/* Center Title Section (Desktop) */}
              {title && (
                <div className="hidden lg:flex flex-col items-center flex-1 px-8 max-w-xl">
                  <h1
                    className={`text-md font-bold bg-gradient-to-r ${colors.title} bg-clip-text text-transparent text-center`}
                  >
                    {title}
                  </h1>
                  {subtitle && (
                    <p className="text-md text-slate-400 mt-1 text-center line-clamp-1">
                      {subtitle}
                    </p>
                  )}
                </div>
              )}

              {/* Header Actions */}
              <div className="flex items-center gap-2 sm:gap-3">
                {headerActions ? (
                  headerActions
                ) : (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      className="hidden sm:flex border-slate-700 text-slate-300 hover:border-blue-500 hover:bg-blue-500/10 hover:text-blue-400 transition-all duration-300"
                    >
                      <Settings className="w-4 h-4 sm:mr-2" />
                      <span className="hidden sm:inline">Settings</span>
                    </Button>
                    <Button
                      asChild
                      variant="ghost"
                      size="sm"
                      className="text-slate-400 hover:text-blue-400 hover:bg-blue-500/10 transition-all duration-300"
                    >
                      <Link href="/">
                        <LogOut className="w-4 h-4 sm:mr-2" />
                        <span className="hidden sm:inline">Exit</span>
                      </Link>
                    </Button>
                  </>
                )}
              </div>
            </div>

            {/* Mobile Title */}
            {title && (
              <div className="lg:hidden pb-2 border-t border-zinc-800 mt-2 pt-2">
                <h1
                  className={`text-base sm:text-lg font-bold bg-gradient-to-r ${colors.title} bg-clip-text text-transparent`}
                >
                  {title}
                </h1>
                {subtitle && (
                  <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
                )}
              </div>
            )}
          </nav>
        </header>
      )}

      {/* Spacer for fixed header */}
      <div className="h-30" />

      {/* Main Content */}
      <main className="relative z-10 flex-1">{children}</main>

      {/* Footer */}
      {showFooter && (
        <footer className="relative z-10 mt-auto">
          <FooterSection />
        </footer>
      )}
    </div>
  );
}
