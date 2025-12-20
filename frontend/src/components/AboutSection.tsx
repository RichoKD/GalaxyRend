"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Award, Globe, Lock, TrendingUp } from "lucide-react";

export function AboutSection() {
  const features = [
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Affordable Rendering",
      description: "Pay significantly less than centralized render farms",
      color: "from-cyan-500 to-blue-500",
    },
    {
      icon: <Award className="w-6 h-6" />,
      title: "Quality Guaranteed",
      description: "Only verified render nodes with proven track records",
      color: "from-blue-500 to-purple-500",
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Global Network",
      description: "Access rendering power from render nodes worldwide",
      color: "from-purple-500 to-pink-500",
    },
    {
      icon: <Lock className="w-6 h-6" />,
      title: "Full Privacy",
      description: "Your scenes stay on IPFS, not on centralized servers",
      color: "from-pink-500 to-cyan-500",
    },
  ];

  const creatorBenefits = [
    "Render faster than ever before",
    "Scale to thousands of frames simultaneously",
    "Only pay for completed, quality renders",
    "Transparent rendering history on blockchain",
    "Direct control over quality requirements",
  ];

  const nodeBenefits = [
    "Monetize your idle GPU/CPU resources",
    "Get paid directly in cryptocurrency",
    "No platform fees or middlemen",
    "Build your rendering reputation",
    "Work on your own schedule",
  ];

  return (
    <section
      id="about"
      className="relative py-20 md:py-32 bg-zinc-950 overflow-hidden scroll-mt-20"
    >
      {/* Background gradient effect */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-600/5 via-transparent to-purple-600/5 pointer-events-none" />

      <div className="relative container mx-auto px-6 max-w-6xl">
        {/* Header - Centered */}
        <div className="mb-20 space-y-6 text-center flex flex-col items-center">
          <Badge className="mx-auto bg-blue-500/10 border-blue-500/30 text-xl md:text-2xl lg:text-3xl hover:bg-blue-500/20 py-3 px-6 rounded-full">
            <span className="bg-gradient-to-r from-slate-200 via-blue-300 to-cyan-300 bg-clip-text text-transparent">
              About VeriFrame - Decentralized Rendering for Everyone
            </span>
          </Badge>

          <p className="lead-text text-slate-300 max-w-2xl text-base md:text-lg">
            VeriFrame connects creators with distributed rendering nodes in a
            trustless marketplace. Get faster renders at better prices while
            node operators earn fair rewards.
          </p>
        </div>

        {/* Mission Statement */}
        <div className="grid md:grid-cols-3 gap-6 mb-20">
          <Card className="bg-gradient-to-br from-blue-600/10 to-cyan-600/10 border-blue-500/20 p-8 space-y-4">
            <h3 className="text-xl font-semibold text-blue-300">Our Mission</h3>
            <p className="text-slate-300">
              Democratize access to high-quality 3D rendering through a
              transparent, secure, and efficient decentralized marketplace.
            </p>
          </Card>

          <Card className="bg-gradient-to-br from-cyan-600/10 to-purple-600/10 border-cyan-500/20 p-8 space-y-4">
            <h3 className="text-xl font-semibold text-cyan-300">
              Why Decentralized?
            </h3>
            <p className="text-slate-300">
              Eliminate expensive middlemen, ensure transparency, provide
              permissionless access, and guarantee fair compensation for all
              participants.
            </p>
          </Card>

          <Card className="bg-gradient-to-br from-purple-600/10 to-pink-600/10 border-purple-500/20 p-8 space-y-4">
            <h3 className="text-xl font-semibold text-purple-300">
              Built on Trust
            </h3>
            <p className="text-slate-300">
              Reputation-based verification, immutable blockchain records, and
              quality tracking ensure accountability and fair partnerships.
            </p>
          </Card>
        </div>

        {/* Three Roles */}
        <div className="mb-20">
          <h3 className="heading-2 text-3xl md:text-4xl font-bold text-center mb-12 text-slate-200">
            How VeriFrame Works
          </h3>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Creators */}
            <div className="space-y-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-lg blur opacity-40" />
                <Card className="relative bg-zinc-900/80 border-blue-500/30 p-8 space-y-4">
                  <h4 className="text-2xl font-bold text-blue-300">Creators</h4>
                  <p className="text-sm text-slate-300">
                    VFX artists, animators, studios needing rendering power
                  </p>
                  <ul className="space-y-2">
                    {creatorBenefits.map((benefit, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-3 text-sm text-slate-300"
                      >
                        <Check className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                        <span>{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </Card>
              </div>
            </div>

            {/* Render Nodes */}
            <div className="space-y-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-lg blur opacity-40" />
                <Card className="relative bg-zinc-900/80 border-cyan-500/30 p-8 space-y-4">
                  <h4 className="text-2xl font-bold text-cyan-300">
                    Render Nodes
                  </h4>
                  <p className="text-sm text-slate-300">
                    GPU/CPU operators contributing rendering power
                  </p>
                  <ul className="space-y-2">
                    {nodeBenefits.map((benefit, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-3 text-sm text-slate-300"
                      >
                        <Check className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                        <span>{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </Card>
              </div>
            </div>

            {/* Admins */}
            <div className="space-y-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg blur opacity-40" />
                <Card className="relative bg-zinc-900/80 border-purple-500/30 p-8 space-y-4">
                  <h4 className="text-2xl font-bold text-purple-300">Admins</h4>
                  <p className="text-sm text-slate-300">
                    Platform maintainers ensuring system integrity
                  </p>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-3 text-sm text-slate-300">
                      <Check className="w-4 h-4 text-pink-400 mt-0.5 flex-shrink-0" />
                      Verify legitimate render nodes
                    </li>
                    <li className="flex items-start gap-3 text-sm text-slate-300">
                      <Check className="w-4 h-4 text-pink-400 mt-0.5 flex-shrink-0" />
                      Monitor rendering quality
                    </li>
                    <li className="flex items-start gap-3 text-sm text-slate-300">
                      <Check className="w-4 h-4 text-pink-400 mt-0.5 flex-shrink-0" />
                      Resolve disputes fairly
                    </li>
                    <li className="flex items-start gap-3 text-sm text-slate-300">
                      <Check className="w-4 h-4 text-pink-400 mt-0.5 flex-shrink-0" />
                      Maintain security
                    </li>
                    <li className="flex items-start gap-3 text-sm text-slate-300">
                      <Check className="w-4 h-4 text-pink-400 mt-0.5 flex-shrink-0" />
                      Support users
                    </li>
                  </ul>
                </Card>
              </div>
            </div>
          </div>
        </div>

        {/* Core Features */}
        <div className="mb-20">
          <h3 className="heading-2 text-3xl md:text-4xl font-bold text-center mb-12 text-slate-200">
            Why Choose VeriFrame?
          </h3>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <Card
                key={i}
                className="bg-zinc-900/50 border-zinc-800 hover:border-blue-500/50 transition-colors p-6 space-y-4 group"
              >
                <div
                  className={`bg-gradient-to-br ${feature.color} p-3 rounded-lg w-fit group-hover:scale-110 transition-transform`}
                >
                  <div className="text-white">{feature.icon}</div>
                </div>
                <h4 className="font-semibold text-slate-200">
                  {feature.title}
                </h4>
                <p className="text-sm text-slate-400">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
