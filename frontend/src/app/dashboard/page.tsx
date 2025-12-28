"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Briefcase,
  Server,
  Shield,
  ArrowRight,
  Sparkles,
  Check,
  Loader2,
} from "lucide-react";
import { useAuth, type UserRole } from "@/contexts/AuthContext";
import { WalletConnectButton } from "@/components/WalletConnectButton";

export default function DashboardPage() {
  const router = useRouter();
  const {
    user,
    role,
    setRole,
    isAuthenticated,
    isLoading: authLoading,
  } = useAuth();
  const [selectedRole, setSelectedRole] = useState<UserRole>(role);
  const [isLoading, setIsLoading] = useState(false);

  // Redirect if already has a role
  useEffect(() => {
    if (isAuthenticated && role) {
      switch (role) {
        case "creator":
          router.push("/dashboard/creators");
          break;
        case "node":
          router.push("/dashboard/nodes");
          break;
        case "admin":
          router.push("/dashboard/admin");
          break;
      }
    }
  }, [isAuthenticated, role, router]);

  const handleRoleSelection = async (newRole: UserRole) => {
    setSelectedRole(newRole);
  };

  const handleContinue = async () => {
    if (!selectedRole) return;

    setIsLoading(true);

    // Save role to auth context
    setRole(selectedRole);

    // Navigate to role-specific dashboard
    switch (selectedRole) {
      case "creator":
        router.push("/dashboard/creators");
        break;
      case "node":
        router.push("/dashboard/nodes");
        break;
      case "admin":
        router.push("/dashboard/admin");
        break;
    }
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-slate-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Show connect wallet if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 flex items-center justify-center p-6">
        <Card className="max-w-md w-full bg-zinc-900/80 border-zinc-800 p-8 text-center backdrop-blur-sm">
          <Shield className="w-16 h-16 mx-auto mb-4 text-blue-500" />
          <h2 className="text-2xl font-bold text-slate-200 mb-4">
            Connect Your Wallet
          </h2>
          <p className="text-slate-400 mb-6">
            To access the dashboard, please connect your Starknet wallet first.
          </p>
          <WalletConnectButton
            size="lg"
            className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
            redirectTo="/dashboard"
          />
        </Card>
      </div>
    );
  }

  const roles = [
    {
      id: "creator" as UserRole,
      title: "Creator",
      icon: Briefcase,
      description: "Post jobs and manage projects",
      features: [
        "Create and manage rendering jobs",
        "Review submissions from nodes",
        "Release payments securely",
        "Track project progress",
      ],
      gradient: "from-blue-500 to-cyan-400",
      hoverGradient: "hover:from-blue-600 hover:to-cyan-500",
      borderColor: "border-blue-500/50",
      iconBg: "bg-gradient-to-r from-blue-500 to-cyan-400",
    },
    {
      id: "node" as UserRole,
      title: "Node",
      icon: Server,
      description: "Deliver quality work and earn rewards",
      features: [
        "Browse available rendering jobs",
        "Submit high-quality work",
        "Earn crypto rewards",
        "Build your reputation",
      ],
      gradient: "from-cyan-500 to-purple-500",
      hoverGradient: "hover:from-cyan-600 hover:to-purple-600",
      borderColor: "border-cyan-500/50",
      iconBg: "bg-gradient-to-r from-cyan-500 to-purple-500",
    },
  ];

  // Check if user is admin (controlled access)
  const isAdmin = user?.is_admin || false;

  // Add admin role only for authorized users
  if (isAdmin) {
    roles.push({
      id: "admin" as UserRole,
      title: "Admin",
      icon: Shield,
      description: "Oversee and manage the ecosystem",
      features: [
        "Monitor platform activity",
        "Resolve disputes fairly",
        "Ensure quality standards",
        "Manage system settings",
      ],
      gradient: "from-purple-500 to-blue-500",
      hoverGradient: "hover:from-purple-600 hover:to-blue-600",
      borderColor: "border-purple-500/50",
      iconBg: "bg-gradient-to-r from-purple-500 to-blue-500",
    });
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 relative overflow-hidden">
      {/* Cosmic Background Effects */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-6 py-16 md:py-24">
        {/* Header */}
        <div className="text-center mb-16 space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-4">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300 font-medium">
              Welcome to GalaxyRend
            </span>
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-slate-200 via-blue-300 to-cyan-300 bg-clip-text text-transparent">
            Choose Your Role
          </h1>

          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto">
            Select how you want to participate in the GalaxyRend ecosystem. You
            can always change this later.
          </p>
        </div>

        {/* Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-7xl mx-auto mb-12">
          {roles.map((role) => {
            const Icon = role.icon;
            const isSelected = selectedRole === role.id;

            return (
              <Card
                key={role.id}
                onClick={() => handleRoleSelection(role.id)}
                className={`
                  relative cursor-pointer transition-all duration-300 
                  bg-zinc-900/80 backdrop-blur-sm border-2 
                  ${
                    isSelected
                      ? `${role.borderColor} shadow-lg shadow-${role.gradient}/20 scale-105`
                      : "border-zinc-800 hover:border-zinc-700"
                  }
                  ${role.hoverGradient}
                  p-8 rounded-2xl group
                `}
              >
                {/* Selected Indicator */}
                {isSelected && (
                  <div className="absolute top-4 right-4 w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full flex items-center justify-center">
                    <Check className="w-5 h-5 text-white" />
                  </div>
                )}

                {/* Icon */}
                <div className="mb-6">
                  <div
                    className={`w-16 h-16 ${role.iconBg} rounded-xl flex items-center justify-center shadow-lg transform transition-transform group-hover:scale-110`}
                  >
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                </div>

                {/* Content */}
                <div className="space-y-4">
                  <div>
                    <h3 className="text-2xl font-bold text-slate-200 mb-2">
                      {role.title}
                    </h3>
                    <p className="text-slate-400">{role.description}</p>
                  </div>

                  {/* Features */}
                  <ul className="space-y-3 pt-4">
                    {role.features.map((feature, index) => (
                      <li
                        key={index}
                        className="flex items-start gap-3 text-sm text-slate-300"
                      >
                        <div className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <div className="w-2 h-2 rounded-full bg-blue-400" />
                        </div>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Hover Effect */}
                <div
                  className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${role.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
                />
              </Card>
            );
          })}
        </div>

        {/* Continue Button */}
        <div className="flex justify-center">
          <Button
            onClick={handleContinue}
            disabled={!selectedRole || isLoading}
            size="lg"
            className={`
              px-8 py-6 text-lg font-semibold rounded-xl transition-all duration-300
              ${
                selectedRole
                  ? "bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white shadow-lg hover:shadow-blue-500/50"
                  : "bg-zinc-800 text-zinc-500 cursor-not-allowed"
              }
            `}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Loading...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Continue to Dashboard
                <ArrowRight className="w-5 h-5" />
              </span>
            )}
          </Button>
        </div>

        {/* Help Text */}
        <p className="text-center text-sm text-slate-500 mt-8">
          Not sure which role to choose?{" "}
          <button className="text-blue-400 hover:text-blue-300 underline">
            Learn more about each role
          </button>
        </p>
      </div>
    </div>
  );
}
