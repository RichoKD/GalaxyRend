"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Settings, LogOut } from "lucide-react";
import { TokenCopyButton } from "@/components/TokenCopyButton";

interface DashboardHeaderProps {
  role?: "creator" | "node" | "admin";
}

export function DashboardHeader({ role = "creator" }: DashboardHeaderProps) {
  // Get dashboard title based on role
  const dashboardTitles = {
    creator: "Creator Dashboard",
    node: "Node Dashboard",
    admin: "Admin Dashboard",
  };

  // Gradient colors based on role
  const gradientColors = {
    creator: "from-blue-400 to-cyan-400",
    node: "from-cyan-400 to-purple-400",
    admin: "from-purple-400 to-pink-400",
  };

  const title = dashboardTitles[role];
  const gradient = gradientColors[role];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-zinc-900/80 backdrop-blur-md border-b border-zinc-800">
      <nav className="w-full px-3 sm:px-4 md:px-6 lg:px-8 py-2 sm:py-2.5 md:py-3">
        <div className="flex items-center justify-between min-h-[3.5rem] sm:min-h-[3.75rem] md:min-h-[4rem]">
          {/* Logo/Brand */}
          <Link
            href="/"
            className="flex items-center gap-1 sm:gap-2 group shrink-0"
          >
            <Image
              src="/logo.png"
              alt="FluxFrame Logo"
              width={140}
              height={50}
              className="h-5 sm:h-6 md:h-7 lg:h-8 w-auto transition-all duration-300 group-hover:scale-105"
              priority
            />
          </Link>

          {/* Centered Dashboard Title */}
          <div className="hidden lg:flex flex-1 justify-center items-center px-2 md:px-3 lg:px-4">
            <h1
              className={`text-[10px] md:text-xs lg:text-sm font-medium tracking-wide bg-gradient-to-r ${gradient} bg-clip-text text-transparent opacity-80`}
            >
              {title}
            </h1>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-1 sm:gap-1.5 md:gap-2">
            <TokenCopyButton />

            <Button
              variant="outline"
              size="sm"
              className="flex border-slate-700 text-slate-300 hover:border-blue-500 hover:bg-blue-500/10 hover:text-blue-400 transition-all duration-300 px-1.5 sm:px-2 md:px-3 h-8 sm:h-9"
            >
              <Settings className="w-3.5 h-3.5 sm:w-4 sm:h-4 lg:mr-2" />
              <span className="hidden lg:inline text-xs">Settings</span>
            </Button>

            <Button
              asChild
              variant="ghost"
              size="sm"
              className="text-slate-400 hover:text-blue-400 hover:bg-blue-500/10 transition-all duration-300 px-1.5 sm:px-2 md:px-3 h-8 sm:h-9"
            >
              <Link href="/">
                <LogOut className="w-3.5 h-3.5 sm:w-4 sm:h-4 lg:mr-2" />
                <span className="hidden lg:inline text-xs">Exit</span>
              </Link>
            </Button>
          </div>
        </div>

        {/* Mobile/Tablet Title */}
        <div className="lg:hidden pb-2 sm:pb-2.5 border-t border-zinc-800 mt-1 pt-2 sm:pt-2.5 px-2 sm:px-3">
          <h1
            className={`text-[9px] sm:text-[10px] md:text-xs font-medium tracking-wide bg-gradient-to-r ${gradient} bg-clip-text text-transparent opacity-80`}
          >
            {title}
          </h1>
        </div>
      </nav>
    </header>
  );
}
