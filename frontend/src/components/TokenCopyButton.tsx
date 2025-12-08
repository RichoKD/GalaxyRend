"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Key, Copy, Check } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export function TokenCopyButton() {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const getToken = () => {
    return localStorage.getItem("access_token") || "";
  };

  const handleCopy = async () => {
    const token = getToken();
    if (token) {
      try {
        await navigator.clipboard.writeText(token);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error("Failed to copy token:", err);
      }
    }
  };

  const token = getToken();
  const tokenPreview = token
    ? `${token.slice(0, 20)}...${token.slice(-20)}`
    : "No token available";

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="flex border-slate-700 text-slate-300 hover:border-purple-500 hover:bg-purple-500/10 hover:text-purple-400 transition-all duration-300 px-1.5 sm:px-2 md:px-3 h-8 sm:h-9"
        >
          <Key className="w-3.5 h-3.5 sm:w-4 sm:h-4 lg:mr-2" />
          <span className="hidden lg:inline text-xs font-medium">
            API Token
          </span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-w-[95vw] bg-zinc-900 border-zinc-800">
        <DialogHeader>
          <DialogTitle className="text-lg sm:text-xl font-medium bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Your API Access Token
          </DialogTitle>
          <DialogDescription className="text-xs sm:text-sm text-slate-400">
            Use this token to authenticate your API requests when placing
            orders.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 sm:space-y-4 py-3 sm:py-4">
          <Alert className="bg-blue-500/10 border-blue-500/30">
            <AlertDescription className="text-xs sm:text-sm text-slate-300">
              <strong className="font-medium">Important:</strong> Keep this
              token secure. It grants access to your account.
            </AlertDescription>
          </Alert>

          <div className="space-y-2">
            <label className="text-xs sm:text-sm font-medium text-slate-300">
              Access Token
            </label>
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="flex-1 px-3 sm:px-4 py-2 sm:py-3 bg-zinc-950 border border-zinc-700 rounded-lg font-mono text-[10px] sm:text-xs text-slate-400 overflow-x-auto break-all">
                {token || "No token available"}
              </div>
              <Button
                onClick={handleCopy}
                variant="outline"
                size="sm"
                className="shrink-0 border-purple-500/50 hover:bg-purple-500/10 hover:border-purple-500 w-full sm:w-auto"
                disabled={!token}
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-2 text-green-400" />
                    <span className="text-xs sm:text-sm font-medium">
                      Copied!
                    </span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-2" />
                    <span className="text-xs sm:text-sm font-medium">Copy</span>
                  </>
                )}
              </Button>
            </div>
          </div>

          <div className="space-y-2 pt-1 sm:pt-2">
            <h4 className="text-xs sm:text-sm font-medium text-slate-300">
              How to use:
            </h4>
            <ol className="text-[10px] sm:text-xs text-slate-400 space-y-1 list-decimal list-inside">
              <li>Copy the token using the button above</li>
              <li>Include it in your API request headers</li>
              <li className="break-all">
                Header format:{" "}
                <code className="px-1.5 py-0.5 bg-zinc-950 rounded text-purple-400 font-mono">
                  Authorization: Bearer YOUR_TOKEN
                </code>
              </li>
            </ol>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
