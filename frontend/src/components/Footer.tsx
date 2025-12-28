"use client";

import {
  ArrowRight,
  Facebook,
  Instagram,
  Linkedin,
  Twitter,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { WalletConnectButton } from "@/components/WalletConnectButton";

const navigation = [
  {
    title: "Platform",
    links: [
      { name: "Nodes", href: "/dashboard/nodes" },
      { name: "Creators", href: "/dashboard/creators" },
      { name: "Admins", href: "/dashboard/admin" },
      { name: "Browse Jobs", href: "/dashboard" },
    ],
  },
  {
    title: "Company",
    links: [
      { name: "About", href: "#" },
      { name: "Pricing", href: "#" },
    ],
  },
  {
    title: "Support",
    links: [
      { name: "FAQ", href: "#" },
      { name: "Contact", href: "#" },
    ],
  },
  {
    title: "Legal",
    links: [
      { name: "Terms of service", href: "#" },
      { name: "Privacy policy", href: "#" },
    ],
  },
];

const socialLinks = [
  { icon: Facebook, href: "https://facebook.com", label: "Facebook" },
  { icon: Twitter, href: "https://twitter.com", label: "Twitter" },
  { icon: Linkedin, href: "https://linkedin.com", label: "LinkedIn" },
  { icon: Instagram, href: "https://instagram.com", label: "Instagram" },
];

const FooterSection = () => {
  return (
    <section className="relative py-12 md:py-16 text-white overflow-hidden">
      {/* Background image with overlay */}
      <div className="absolute inset-0 z-0">
        <img
          src="/background-image.png"
          alt="Footer background"
          className="w-full h-full object-cover opacity-40"
        />
      </div>

      {/* Glassy dark overlay */}
      <div className="absolute inset-0 bg-zinc-950/85 backdrop-blur-md"></div>

      <div className="container max-w-7xl mx-auto px-6 relative z-10">
        <footer>
          {/* Navigation Section */}
          <nav className="grid grid-cols-2 gap-8 md:gap-10 mb-10 sm:grid-cols-4">
            {navigation.map((section) => (
              <div key={section.title}>
                <h3 className="mb-4 text-base font-semibold text-cyan-400">
                  {section.title}
                </h3>
                <ul className="space-y-3">
                  {section.links.map((link) => (
                    <li key={link.name}>
                      <a
                        href={link.href}
                        className="inline-block text-slate-200 text-sm transition-colors duration-200 hover:text-cyan-400"
                      >
                        {link.name}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>

          {/* Bottom Section */}
          <div className="border-slate-600/30 border-t pt-6">
            <div className="flex flex-col w-full items-center justify-between gap-4 sm:flex-row">
              <p className="text-slate-200 text-sm">
                © {new Date().getFullYear()} -{" "}
                <a
                  href="/"
                  className="underline transition-colors hover:text-cyan-400"
                  target="_blank"
                >
                  GalaxyRend
                </a>
              </p>
              <div className="flex items-center gap-5">
                {socialLinks.map((link) => (
                  <a
                    aria-label={link.label}
                    key={link.href}
                    href={link.href}
                    className="text-slate-200 transition-colors hover:text-cyan-400"
                  >
                    <link.icon
                      size={18}
                      className="transition-transform hover:scale-110"
                    />
                  </a>
                ))}
              </div>
            </div>
          </div>
        </footer>
      </div>
    </section>
  );
};

export { FooterSection };
