"use client";

import NumberFlow from "@number-flow/react";
import { motion } from "framer-motion";
import { Users, Briefcase, Shield } from "lucide-react";
import React from "react";

import { cn } from "@/lib/utils";

const css = `
.galaxyrend-bg {
    background: radial-gradient(circle at 50% 0%, rgba(74, 144, 226, 0.15) 0%, transparent 50%),
                linear-gradient(135deg, rgba(46, 210, 201, 0.02) 25%, transparent 25.5%, transparent 50%, rgba(46, 210, 201, 0.02) 50.5%, rgba(46, 210, 201, 0.02) 75%, transparent 75.5%, transparent);
    background-size: 800px 400px, 12px 12px;
    border: 1px solid rgba(46, 210, 201, 0.08);
    backdrop-filter: blur(8px);
  }

  .stark-gradient-blur {
    background: radial-gradient(600px circle at 50% 0%, rgba(74, 144, 226, 0.18) 0%, transparent 70%);
  }`;

const StatsSection = () => {
  return (
    <section className="relative -mt-8 py-32 overflow-hidden bg-gradient-to-b from-slate-900 to-slate-800">
      <style>{css}</style>

      {/* Background blur gradient */}
      <div className="absolute inset-0 stark-gradient-blur" />

      <div className="container mx-auto relative z-10">
        <div className="mx-auto max-w-3xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="w-full font-calSans text-5xl font-medium tracking-tight lg:text-7xl bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent">
              Decentralized work. Verified results.
            </h1>
            <p className="mt-6 text-lg tracking-tight text-slate-400 lg:text-xl max-w-2xl mx-auto leading-relaxed">
              Connect. Create. Complete. The future of freelance.
            </p>
          </motion.div>
        </div>

        <div className="relative mx-auto mt-24 flex h-112 max-w-5xl items-center justify-center gap-6">
          {[
            { value: 1250, label: "Active Nodes", delay: 0.2, icon: Users },
            { value: 89, label: "Success Rate", delay: 0.4, icon: Shield },
            {
              value: 3400,
              label: "Jobs Completed",
              className: "bg-gradient-to-tr from-blue-400 to-cyan-400",
              showToolTip: true,
              delay: 0.6,
              icon: Briefcase,
            },
            { value: 850, label: "Active Creators", delay: 0.8, icon: Users },
          ].map((props, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.6,
                delay: index * 0.15,
                type: "spring",
                damping: 12,
              }}
              className="h-full w-full"
            >
              <BarChart {...props} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export { StatsSection };

const BarChart = ({
  value,
  label,
  className = "",
  showToolTip = false,
  delay = 0,
  icon: Icon = Users,
}: {
  value: number;
  label: string;
  className?: string;
  showToolTip?: boolean;
  delay?: number;
  icon?: React.ElementType;
}) => {
  const percentage = Math.min((value / 4000) * 100, 97); // Scale values to percentage for height

  return (
    <div className="group relative h-full w-full">
      <div className="galaxyrend-bg relative h-full w-full overflow-hidden rounded-3xl hover:border-cyan-400/20 transition-all duration-300">
        <motion.div
          initial={{ opacity: 0, y: 100, height: 0 }}
          animate={{ opacity: 1, y: 0, height: `${percentage}%` }}
          transition={{ duration: 0.8, type: "spring", damping: 20, delay }}
          className={cn(
            "absolute bottom-0 mt-auto w-full rounded-3xl bg-gradient-to-t from-slate-600 to-slate-500 p-4 text-white shadow-2xl",
            className
          )}
        >
          <div className="relative flex h-16 w-full items-center justify-center gap-2 rounded-2xl bg-black/20 tracking-tight backdrop-blur-sm">
            <div className="absolute top-1 left-1 hidden h-14 w-14 items-center justify-center rounded-2xl bg-white/10 md:flex backdrop-blur-sm">
              <Icon className="size-7" />
            </div>
            <NumberFlow
              value={value}
              suffix={label.includes("Rate") ? "%" : ""}
              className="text-2xl font-semibold"
            />
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 100, height: 0 }}
        animate={{ opacity: 1, y: 0, height: `${percentage}%` }}
        transition={{ duration: 0.8, type: "spring", damping: 15, delay }}
        className="absolute bottom-0 w-full"
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: showToolTip ? 1 : 0, y: showToolTip ? 0 : 20 }}
          transition={{
            duration: 0.6,
            type: "spring",
            damping: 15,
            delay: delay + 0.3,
          }}
          className={cn(
            "absolute -top-12 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-xl bg-black/80 backdrop-blur-md px-4 py-2 text-white border border-white/20 shadow-xl",
            className
          )}
        >
          <div
            className={cn(
              "absolute -bottom-12 left-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white bg-black/80 transition-all duration-300 ease-in-out backdrop-blur-md",
              className.includes("bg-gradient") && "bg-cyan-400 border-cyan-300"
            )}
          />
          <svg
            className={cn(
              "absolute -bottom-2 left-1/2 -translate-x-1/2",
              className.includes("bg-gradient")
                ? "text-cyan-400"
                : "text-black/80"
            )}
            width="12"
            height="8"
            viewBox="0 0 12 8"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M4.5 7.5C5.33 8.5 6.67 8.5 7.5 7.5L11 2C11.83 1 11.17 0 10 0H2C0.83 0 0.17 1 1 2L4.5 7.5Z"
              fill="currentColor"
            />
          </svg>
          <span className="text-sm font-medium">Platform Leader</span>
        </motion.div>
      </motion.div>
      <p className="mx-auto mt-4 w-fit text-sm tracking-tight text-slate-500 font-medium">
        {label}
      </p>
    </div>
  );
};
