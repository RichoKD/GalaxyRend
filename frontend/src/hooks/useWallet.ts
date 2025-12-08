"use client";

import { useState, useCallback } from "react";
import { authAPI, type ChallengeResponse } from "@/lib/api-client";
import { useAuth } from "@/contexts/AuthContext";

export interface WalletState {
  isConnecting: boolean;
  isConnected: boolean;
  address: string | null;
  error: string | null;
}

/**
 * Hook for Starknet wallet integration
 * Supports: ArgentX, Braavos, and other Starknet wallets
 */
export function useWallet() {
  const { login } = useAuth();
  const [state, setState] = useState<WalletState>({
    isConnecting: false,
    isConnected: false,
    address: null,
    error: null,
  });

  /**
   * Check if Starknet wallet is installed
   */
  const isWalletInstalled = useCallback((): boolean => {
    if (typeof window === "undefined") return false;
    return (
      !!(window as any).starknet ||
      !!(window as any).starknet_argentX ||
      !!(window as any).starknet_braavos
    );
  }, []);

  /**
   * Get the Starknet wallet provider
   */
  const getWalletProvider = useCallback(() => {
    if (typeof window === "undefined") return null;

    // Try different wallet providers
    const win = window as any;
    return win.starknet || win.starknet_argentX || win.starknet_braavos || null;
  }, []);

  /**
   * Connect to Starknet wallet and authenticate with backend
   */
  const connect = useCallback(async () => {
    setState((prev) => ({ ...prev, isConnecting: true, error: null }));

    try {
      // Check if wallet is installed
      if (!isWalletInstalled()) {
        throw new Error(
          "Starknet wallet not found. Please install ArgentX or Braavos extension."
        );
      }

      const provider = getWalletProvider();
      if (!provider) {
        throw new Error("Failed to get wallet provider");
      }

      // Enable wallet connection (will prompt user)
      let accounts: string[];
      try {
        accounts = await provider.enable({ starknetVersion: "v5" });
      } catch (err) {
        throw new Error("User rejected wallet connection");
      }

      if (!accounts || accounts.length === 0) {
        throw new Error("No accounts found in wallet");
      }

      const address = accounts[0];
      console.log("Wallet connected:", address);

      // Step 1: Get authentication challenge from backend
      let challenge: ChallengeResponse;
      try {
        challenge = await authAPI.getChallenge(address);
        console.log("Challenge received:", challenge);
      } catch (err) {
        throw new Error("Failed to get authentication challenge from server");
      }

      // Step 2: Sign the challenge with wallet
      let signature: string[];
      let signedMessage: string;

      try {
        // Use the exact message from backend for consistency
        signedMessage = challenge.message;

        console.log("Message to sign:", signedMessage);

        let signatureResult;

        // Try Method 1: Typed Data (preferred, more secure)
        try {
          const typedData = {
            types: {
              StarkNetDomain: [
                { name: "name", type: "string" },
                { name: "chainId", type: "felt" },
              ],
              Message: [{ name: "message", type: "string" }],
            },
            primaryType: "Message",
            domain: {
              name: "FluxFrame",
              chainId: await provider.provider.getChainId(),
            },
            message: {
              message: signedMessage,
            },
          };

          console.log("Attempting typed data signature...");
          signatureResult = await provider.account.signMessage(typedData);
        } catch (typedDataErr: any) {
          console.warn(
            "Typed data signing failed:",
            typedDataErr?.message || typedDataErr
          );

          // Method 2: Try with shortString if message is too long
          if (signedMessage.length > 31) {
            console.log(
              "Message too long for typed data, using hash approach..."
            );
            // For long messages, we'll just sign a short version and send full message to backend
            const shortMsg = `Auth:${challenge.nonce.slice(0, 20)}`;
            try {
              const shortTypedData = {
                types: {
                  StarkNetDomain: [{ name: "name", type: "shortstring" }],
                  Message: [{ name: "msg", type: "shortstring" }],
                },
                primaryType: "Message",
                domain: {
                  name: "FluxFrame",
                },
                message: {
                  msg: shortMsg,
                },
              };
              signatureResult = await provider.account.signMessage(
                shortTypedData
              );
            } catch (shortErr) {
              throw new Error(
                "Message is too long for wallet to sign. Please contact support."
              );
            }
          } else {
            throw typedDataErr;
          }
        }

        // Handle different signature formats
        if (Array.isArray(signatureResult)) {
          signature = signatureResult.map(String);
        } else if (
          typeof signatureResult === "object" &&
          "signature" in signatureResult
        ) {
          signature = (signatureResult as any).signature.map(String);
        } else {
          signature = [String(signatureResult)];
        }

        console.log("Message signed successfully:", signature);
      } catch (err) {
        console.error("Signature error:", err);
        throw new Error(
          "Failed to sign message. User may have rejected the signature."
        );
      }

      // Step 3: Authenticate with backend
      try {
        await login(address, signature, {
          message: signedMessage,
          timestamp: parseInt(challenge.timestamp),
        });

        setState({
          isConnecting: false,
          isConnected: true,
          address,
          error: null,
        });

        console.log("Authentication successful!");
      } catch (err) {
        throw new Error("Authentication failed. Please try again.");
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to connect wallet";
      console.error("Wallet connection error:", err);

      setState({
        isConnecting: false,
        isConnected: false,
        address: null,
        error: errorMessage,
      });

      throw err;
    }
  }, [isWalletInstalled, getWalletProvider, login]);

  /**
   * Disconnect wallet
   */
  const disconnect = useCallback(async () => {
    const provider = getWalletProvider();

    try {
      // Some wallets support programmatic disconnect
      if (provider && typeof provider.disable === "function") {
        await provider.disable();
      }
    } catch (err) {
      console.error("Error disconnecting wallet:", err);
    }

    setState({
      isConnecting: false,
      isConnected: false,
      address: null,
      error: null,
    });
  }, [getWalletProvider]);

  /**
   * Get current connected address from wallet
   */
  const getAddress = useCallback(async (): Promise<string | null> => {
    const provider = getWalletProvider();
    if (!provider || !provider.isConnected) return null;

    try {
      const accounts = await provider.enable({ starknetVersion: "v5" });
      return accounts?.[0] || null;
    } catch {
      return null;
    }
  }, [getWalletProvider]);

  return {
    ...state,
    connect,
    disconnect,
    getAddress,
    isWalletInstalled: isWalletInstalled(),
  };
}

// Type augmentation for window.starknet
declare global {
  interface Window {
    starknet?: any;
    starknet_argentX?: any;
    starknet_braavos?: any;
  }
}
