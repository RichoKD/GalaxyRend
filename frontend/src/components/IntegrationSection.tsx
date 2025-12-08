"use client";

import React from "react";

import { cn } from "@/lib/utils";

import { Marquee } from "@/components/magicui/marquee";

const IntegrationSection = () => {
  const platforms = [
    {
      image:
        "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/logos/slack-icon.svg",
      name: "StarkNet",
      className: "invert dark:invert-0",
    },
    {
      image:
        "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/logos/notion-icon.svg",
      name: "Ethereum",
      className: "invert dark:invert-0",
    },
    {
      image:
        "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/logos/github-icon.svg",
      name: "ArgentX",
      className: "invert dark:invert-0",
    },
    {
      image:
        "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/logos/google-icon.svg",
      name: "Braavos",
      className: "invert dark:invert-0",
    },
    {
      image:
        "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/logos/figma-icon.svg",
      name: "MetaMask",
      className: "invert dark:invert-0",
    },
  ];

  return (
    <section className="relative py-24 lg:py-32 overflow-hidden">
      {/* Enhanced cosmic background with Starknet-inspired gradients */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-500/10 to-transparent"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-gradient-to-r from-cyan-500/20 via-blue-600/15 to-purple-600/20 blur-3xl rounded-full opacity-40"></div>

      {/* Additional cosmic elements */}
      <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-gradient-to-r from-blue-400/10 to-cyan-400/10 blur-2xl rounded-full opacity-30 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[200px] bg-gradient-to-l from-purple-500/10 to-blue-500/10 blur-2xl rounded-full opacity-25"></div>

      <div className="container mx-auto px-6 relative z-10">
        {/* Header Section */}
        <div className="text-center flex flex-col max-w-4xl mx-auto mb-16 space-y-6">
          <div className="inline-flex w-fit mx-auto items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-400/30 text-blue-300 text-sm font-medium backdrop-blur-sm">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-lg shadow-cyan-400/50"></div>
            Blockchain Integrations
          </div>

          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
            <span className="bg-gradient-to-br from-foreground via-foreground/90 to-foreground/70 bg-clip-text text-transparent">
              Connect with trusted
            </span>
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Web3 platforms
            </span>
          </h2>

          <p className="text-lg md:text-xl text-muted-foreground/80 leading-relaxed max-w-2xl mx-auto">
            Power up your workflow with FluxFrame's decentralized ecosystem.
            <br className="hidden md:block" />
            Connect wallets and blockchain services securely in clicks.
          </p>
        </div>

        {/* Enhanced Marquee Section with cosmic styling */}
        <div className="relative">
          {/* Enhanced gradient overlays with blue/cyan theme */}
          <div className="absolute inset-0 bg-gradient-to-r from-background via-transparent to-background z-10 pointer-events-none"></div>

          {/* First row */}
          <div className="mb-8">
            <Marquee pauseOnHover className="[--duration:25s]">
              {platforms.map((platform, index) => (
                <div
                  key={`row1-${index}`}
                  className="group mx-4 flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-br from-slate-800/50 via-slate-900/50 to-slate-800/50 backdrop-blur-sm border border-blue-500/20 px-6 py-4 hover:bg-gradient-to-br hover:from-blue-900/30 hover:via-slate-900/60 hover:to-cyan-900/30 hover:border-cyan-400/40 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-blue-500/20"
                >
                  <div className="relative">
                    <img
                      src={platform.image}
                      alt={platform.name}
                      className={cn(
                        "size-6 transition-all duration-300 group-hover:scale-110",
                        platform?.className
                      )}
                    />
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-md"></div>
                  </div>
                  <p className="text-base font-medium text-foreground/90 group-hover:text-cyan-300 transition-colors duration-300">
                    {platform.name}
                  </p>
                </div>
              ))}
            </Marquee>
          </div>

          {/* Second row (reverse) */}
          <div className="mb-8">
            <Marquee pauseOnHover reverse className="[--duration:30s]">
              {[...platforms].reverse().map((platform, index) => (
                <div
                  key={`row2-${index}`}
                  className="group mx-4 flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-br from-slate-800/50 via-slate-900/50 to-slate-800/50 backdrop-blur-sm border border-blue-500/20 px-6 py-4 hover:bg-gradient-to-br hover:from-blue-900/30 hover:via-slate-900/60 hover:to-cyan-900/30 hover:border-cyan-400/40 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-blue-500/20"
                >
                  <div className="relative">
                    <img
                      src={platform.image}
                      alt={platform.name}
                      className={cn(
                        "size-6 transition-all duration-300 group-hover:scale-110",
                        platform?.className
                      )}
                    />
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-md"></div>
                  </div>
                  <p className="text-base font-medium text-foreground/90 group-hover:text-cyan-300 transition-colors duration-300">
                    {platform.name}
                  </p>
                </div>
              ))}
            </Marquee>
          </div>

          {/* Third row */}
          <div>
            <Marquee pauseOnHover className="[--duration:35s]">
              {platforms
                .slice(0, 4)
                .concat(platforms.slice(0, 3))
                .map((platform, index) => (
                  <div
                    key={`row3-${index}`}
                    className="group mx-4 flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-br from-slate-800/50 via-slate-900/50 to-slate-800/50 backdrop-blur-sm border border-blue-500/20 px-6 py-4 hover:bg-gradient-to-br hover:from-blue-900/30 hover:via-slate-900/60 hover:to-cyan-900/30 hover:border-cyan-400/40 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-blue-500/20"
                  >
                    <div className="relative">
                      <img
                        src={platform.image}
                        alt={platform.name}
                        className={cn(
                          "size-6 transition-all duration-300 group-hover:scale-110",
                          platform?.className
                        )}
                      />
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-cyan-400/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-md"></div>
                    </div>
                    <p className="text-base font-medium text-foreground/90 group-hover:text-cyan-300 transition-colors duration-300">
                      {platform.name}
                    </p>
                  </div>
                ))}
            </Marquee>
          </div>

          <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background z-10 pointer-events-none"></div>
        </div>

        <div className="text-center mt-20">
          <div className="inline-flex items-center gap-6 px-10 py-6 rounded-3xl bg-gradient-to-r from-blue-500/20 via-cyan-500/15 to-purple-500/20 backdrop-blur-2xl border border-blue-400/30 shadow-2xl shadow-blue-500/10 hover:shadow-cyan-400/20 transition-all duration-500">
            <span className="text-base font-semibold bg-gradient-to-r from-foreground to-cyan-300 bg-clip-text text-transparent">
              Join teams already using FluxFrame
            </span>
            <div className="flex -space-x-3">
              {["Alice", "Bob", "Carol", "David"].map((seed, i) => (
                <div
                  key={i}
                  className="w-10 h-10 rounded-full border-3 border-background shadow-xl shadow-blue-500/30 hover:scale-110 transition-transform duration-300 overflow-hidden"
                  style={{ animationDelay: `${i * 0.1}s` }}
                >
                  <img
                    src={`https://api.dicebear.com/9.x/notionists/svg?seed=${seed}`}
                    alt={`User ${seed}`}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-600/80 to-cyan-600/80 border-3 border-background flex items-center justify-center shadow-xl shadow-cyan-500/30 hover:scale-110 transition-transform duration-300">
                <span className="text-sm font-bold bg-gradient-to-r from-white to-cyan-200 bg-clip-text text-transparent">
                  +
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export { IntegrationSection };
