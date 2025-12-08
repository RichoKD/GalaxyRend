"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useWallet } from "@/hooks/useWallet";
import { Button } from "@/components/ui/button";
import { Wallet, Loader2, AlertCircle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface WalletConnectButtonProps {
  redirectTo?: string;
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
  className?: string;
  showIcon?: boolean;
}

export function WalletConnectButton({
  redirectTo = "/dashboard",
  variant = "default",
  size = "default",
  className = "",
  showIcon = true,
}: WalletConnectButtonProps) {
  const router = useRouter();
  const { isAuthenticated, user } = useAuth();
  const { connect, isConnecting, error, isWalletInstalled } = useWallet();
  const [showDialog, setShowDialog] = useState(false);

  const handleConnect = async () => {
    if (!isWalletInstalled) {
      setShowDialog(true);
      return;
    }

    try {
      console.log("Starting wallet connection...");
      await connect();
      console.log("Wallet connected successfully");
      // Redirect after successful connection
      router.push(redirectTo);
    } catch (err) {
      console.error("Connection failed:", err);

      // More specific error handling
      if (err instanceof Error) {
        if (err.message.includes("Authentication failed")) {
          console.error("Authentication error details:", err);
          // You might want to show a more specific error message to the user
        } else if (err.message.includes("User rejected")) {
          console.log("User rejected the connection request");
        } else {
          console.error("Unknown connection error:", err.message);
        }
      }
    }
  };

  // If already authenticated, show connected state
  if (isAuthenticated && user) {
    return (
      <Button
        variant="outline"
        size={size}
        className={className}
        onClick={() => router.push(redirectTo)}
      >
        {showIcon && <Wallet className="w-4 h-4 mr-2" />}
        {user.address.slice(0, 6)}...{user.address.slice(-4)}
      </Button>
    );
  }

  return (
    <>
      <Button
        variant={variant}
        size={size}
        className={className}
        onClick={handleConnect}
        disabled={isConnecting}
      >
        {isConnecting ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            <span className="text-base font-medium">Connecting...</span>
          </>
        ) : (
          <>
            {showIcon && <Wallet className="w-4 h-4 mr-2" />}
            <span className="text-base font-medium">Connect Wallet</span>
          </>
        )}
      </Button>

      {/* Error display */}
      {error && (
        <Alert variant="destructive" className="mt-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Wallet not installed dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Starknet Wallet Required</DialogTitle>
            <DialogDescription>
              To use FluxFrame, you need a Starknet wallet installed in your
              browser.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-slate-400">
              We recommend one of these wallets:
            </p>
            <div className="space-y-3">
              <a
                href="https://www.argent.xyz/argent-x/"
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 border border-zinc-800 rounded-lg hover:border-zinc-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-200">ArgentX</h3>
                    <p className="text-sm text-slate-400">
                      Most popular Starknet wallet
                    </p>
                  </div>
                  <Button size="sm" variant="outline">
                    Install
                  </Button>
                </div>
              </a>
              <a
                href="https://braavos.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 border border-zinc-800 rounded-lg hover:border-zinc-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-200">Braavos</h3>
                    <p className="text-sm text-slate-400">
                      Advanced Starknet wallet
                    </p>
                  </div>
                  <Button size="sm" variant="outline">
                    Install
                  </Button>
                </div>
              </a>
            </div>
            <p className="text-xs text-slate-500">
              After installing, refresh this page and try connecting again.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
