# GalaxyRend Frontend Architecture

## Recommended Tech Stack

### Core

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Shadcn/ui
- **State Management**: Zustand + React Query

### Web3 Integration

- **StarkNet SDK**: starknet.js
- **Wallet Connection**: get-starknet
- **React Hooks**: starknet-react
- **IPFS**: ipfs-http-client

### Additional Tools

- **File Upload**: react-dropzone
- **Forms**: React Hook Form + Zod validation
- **Charts**: Recharts
- **Animations**: Framer Motion
- **Icons**: Lucide React

## Project Structure

```
frontend/
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── layout.tsx              # Root layout with wallet provider
│   │   ├── page.tsx                # Homepage
│   │   ├── jobs/
│   │   │   ├── page.tsx            # Job list
│   │   │   ├── create/
│   │   │   │   └── page.tsx        # Create new job
│   │   │   └── [id]/
│   │   │       ├── page.tsx        # Job details
│   │   │       └── results/
│   │   │           └── page.tsx    # View results
│   │   ├── dashboard/
│   │   │   └── page.tsx            # User dashboard
│   │   └── api/
│   │       ├── ipfs/
│   │       │   ├── upload/route.ts # Upload to IPFS
│   │       │   └── fetch/route.ts  # Fetch from IPFS
│   │       └── jobs/
│   │           └── route.ts        # Job metadata API
│   │
│   ├── components/
│   │   ├── ui/                     # Shadcn/ui components
│   │   ├── web3/
│   │   │   ├── ConnectWallet.tsx
│   │   │   ├── NetworkSelector.tsx
│   │   │   └── TransactionStatus.tsx
│   │   ├── jobs/
│   │   │   ├── JobCard.tsx
│   │   │   ├── JobForm.tsx
│   │   │   ├── JobDetails.tsx
│   │   │   └── JobResults.tsx
│   │   ├── upload/
│   │   │   ├── BlendFileUpload.tsx
│   │   │   └── IPFSUploader.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── Sidebar.tsx
│   │
│   ├── hooks/
│   │   ├── useStarknetContract.ts  # Contract interaction
│   │   ├── useJobRegistry.ts       # Job CRUD operations
│   │   ├── useIPFS.ts              # IPFS operations
│   │   └── useWallet.ts            # Wallet state management
│   │
│   ├── lib/
│   │   ├── starknet.ts             # StarkNet client setup
│   │   ├── ipfs.ts                 # IPFS client setup
│   │   ├── contracts.ts            # Contract ABIs and addresses
│   │   ├── utils.ts                # Helper functions
│   │   └── validations.ts          # Zod schemas
│   │
│   ├── stores/
│   │   ├── jobStore.ts             # Job state management
│   │   ├── walletStore.ts          # Wallet state
│   │   └── settingsStore.ts        # App settings
│   │
│   └── types/
│       ├── contracts.ts            # Contract type definitions
│       ├── jobs.ts                 # Job-related types
│       └── ipfs.ts                 # IPFS types
│
├── public/
│   ├── icons/
│   └── examples/                   # Example .blend files
│
├── next.config.js
├── tailwind.config.js
├── package.json
└── README.md
```

## Key Features to Implement

### 1. Job Creation Flow

```typescript
// components/jobs/JobForm.tsx
1. Upload .blend file → IPFS
2. Set reward amount
3. Set deadline
4. Call contract create_job()
5. Show transaction status
```

### 2. Job Discovery & Tracking

```typescript
// hooks/useJobRegistry.ts
- Real-time job updates via contract events
- Filter jobs by status, reward, deadline
- Track user's submitted jobs
- Monitor job progress
```

### 3. Result Viewing

```typescript
// components/jobs/JobResults.tsx
- Display rendered images from IPFS
- Compare multiple worker results
- Download high-resolution outputs
- Rate/review worker quality
```

### 4. Wallet Integration

```typescript
// components/web3/ConnectWallet.tsx
- Connect ArgentX/Braavos wallets
- Display account balance
- Network switching (mainnet/testnet)
- Transaction history
```

## Implementation Steps

### Phase 1: Core Setup

```bash
npx create-next-app@latest galaxyrend-frontend --typescript --tailwind --app
cd galaxyrend-frontend
npm install starknet get-starknet @starknet-react/core @starknet-react/chains
npm install zustand @tanstack/react-query
npm install react-hook-form @hookform/resolvers zod
npm install react-dropzone ipfs-http-client
npx shadcn-ui@latest init
```

###GalaxyRend Web3 Integration

```typescript
// lib/starknet.ts
export const provider = new RpcProvider({
  nodeUrl: process.env.NEXT_PUBLIC_STARKNET_RPC,
});

export const jobRegistryContract = new Contract(
  jobRegistryAbi,
  process.env.NEXT_PUBLIC_CONTRACT_ADDRESS,
  provider
);
```

### Phase 3: Key Components

```typescript
// components/jobs/JobForm.tsx
- File upload with validation
- Form with reward/deadline inputs
- IPFS upload progress
- Contract transaction handling

// components/jobs/JobCard.tsx
- Job status indicators
- Reward amount display
- Deadline countdown
- Action buttons (claim/view)
```

### Phase 4: Advanced Features

```typescript
// Real-time updates
- WebSocket connection for job status
- Push notifications for completed jobs
- Worker performance metrics
- Cost estimation tools
```

## Sample Component Implementation

```typescript
// components/jobs/JobForm.tsx
"use client";

import { useState } from "react";
import { useContract } from "@starknet-react/core";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

const jobSchema = z.object({
  blendFile: z.instanceof(File),
  reward: z.number().min(0.001),
  deadline: z.date().min(new Date()),
  description: z.string().min(10).max(500),
});

export function JobForm() {
  const [uploading, setUploading] = useState(false);
  const { contract } = useContract({
    abi: jobRegistryAbi,
    address: process.env.NEXT_PUBLIC_CONTRACT_ADDRESS,
  });

  const form = useForm<z.infer<typeof jobSchema>>({
    resolver: zodResolver(jobSchema),
  });

  const onSubmit = async (data: z.infer<typeof jobSchema>) => {
    try {
      setUploading(true);

      // 1. Upload to IPFS
      const ipfsHash = await uploadToIPFS(data.blendFile);

      // 2. Create job on contract
      const result = await contract.create_job(
        ipfsHash,
        parseUnits(data.reward.toString(), 18),
        Math.floor(data.deadline.getTime() / 1000)
      );

      // 3. Wait for confirmation
      await provider.waitForTransaction(result.transaction_hash);

      toast.success("Job created successfully!");
    } catch (error) {
      toast.error("Failed to create job");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <BlendFileUpload {...form.register("blendFile")} />
        <RewardInput {...form.register("reward")} />
        <DeadlineSelector {...form.register("deadline")} />
        <Button type="submit" disabled={uploading}>
          {uploading ? "Creating Job..." : "Create Job"}
        </Button>
      </form>
    </Form>
  );
}
```

## Why This Approach?

### ✅ **Advantages**

- **User-Friendly**: Familiar Web2 UX with Web3 integration
- **Performance**: SSR + optimized bundles
- **Developer Experience**: TypeScript + modern tooling
- **Scalable**: Component-based architecture
- **Web3 Native**: Built for StarkNet ecosystem

### 🎯 **Perfect for GalaxyRend**

- Handles file uploads seamlessly
- Real-time job tracking
- Wallet integration out of the box
- IPFS integration for decentralized storage
- Transaction status monitoring
- Mobile-responsive design

This architecture will give you a production-ready frontend that scales with your platform growth!
