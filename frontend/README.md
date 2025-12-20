# GalaxyRend Frontend

This is the frontend for [GalaxyRend](https://galaxyrend.xyz) - a decentralized work platform built on Starknet where Creators post jobs, Nodes deliver excellence, and AI ensures quality.

## About GalaxyRend

GalaxyRend is a revolutionary platform that connects creators with skilled nodes in a decentralized ecosystem. Built on Starknet, it provides:

- **For Creators**: Post jobs, manage submissions, and release rewards with confidence
- **For Nodes**: Find jobs, submit quality work, and earn rewards in crypto
- **For Admins**: Oversee the ecosystem, resolve disputes, and ensure fairness## Project Overview

GalaxyRend Frontend is a Next.js 15 application with React 19 that provides a modern, responsive user interface for the decentralized work platform. The application features a cosmic dark theme design and seamless integration with Starknet blockchain technology.

### Tech Stack

- **Framework**: Next.js 15.4.5 with App Router
- **Runtime**: React 19.1.1
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4 with custom design system
- **UI Components**: Radix UI primitives + Custom GalaxyRend components
- **Icons**: Tabler Icons React, Lucide React
- **Animation**: Framer Motion for smooth interactions
- **Forms**: React Hook Form with Zod validation
- **Package Manager**: Bun (with npm fallback)

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Architecture

The application follows a standard Next.js App Router architecture:

```text
src/
├── app/                    # App Router pages and layouts
│   ├── globals.css        # Global styles and Tailwind configuration
│   ├── layout.tsx         # Root layout component
│   ├── page.tsx           # Home page component
│   └── favicon.ico        # Application favicon
├── components/            # Reusable UI components
│   ├── ui/               # Base UI components (Radix + custom)
│   ├── magicui/          # Specialized UI components
│   └── [Feature Components] # GalaxyRend page-specific components
└── lib/                  # Utility functions and configurations
    └── utils.ts          # Common utility functions
```

## Key Components

### Root Layout (`src/app/layout.tsx`)

The root layout component that wraps all pages and provides:

- **Font Configuration**: Geist Sans and Geist Mono fonts with CSS variables
- **Global Styling**: Dark theme applied by default with cosmic design system
- **Metadata**: GalaxyRend branding ("GalaxyRend - Decentralized Work Platform")
- **Error Handling**: ErrorReporter component for graceful error handling
- **External Scripts**: Route messaging script for iframe communication

### GalaxyRend Components

#### HeroSection (`src/components/HeroSection.tsx`)

- Main landing area with GalaxyRend branding and navigation
- Hero content: "Decentralized Work, Verified Results"
- Connect Wallet and Learn More CTAs
- Role-based cards for Creators, Nodes, and Admins
- Cosmic gradient background with Starknet imagery

#### BentoGrid (`src/components/BentoGrid.tsx`)

- Grid layout system for GalaxyRend feature showcase
- Responsive design for different screen sizes

#### IntegrationSection (`src/components/IntegrationSection.tsx`)

- Highlights GalaxyRend's blockchain integrations
- Focus on Starknet technology and smart contracts

#### TestimonialSection (`src/components/TestimonialSection.tsx`)

- User testimonials and social proof for the platform
- Community feedback and success stories

#### FooterSection (`src/components/Footer.tsx`)

- GalaxyRend branding and platform navigation
- Newsletter subscription
- Links for Nodes, Creators, Admins, Browse Jobs
- Social media integration and legal links

### Error Handling (`src/components/ErrorReporter.tsx`)

A comprehensive error reporting system that:

- **Captures Runtime Errors**: Handles window.onerror and unhandled promise rejections
- **Dev Overlay Integration**: Monitors Next.js development overlay for errors
- **Iframe Communication**: Posts error information to parent windows when embedded
- **User-Friendly UI**: Provides a clean error interface for production errors
- **Development Details**: Shows detailed error information in development mode

### UI Component System

GalaxyRend uses a comprehensive UI component library:

#### Base Components (`src/components/ui/`)

Radix UI primitives with custom GalaxyRend styling including:

- `accordion`, `alert`, `aspect-ratio`, `avatar`, `badge`
- `breadcrumb`, `button`, `card`, `carousel`, `checkbox`
- `collapsible`, `context-menu`, `dialog`, `drawer`, `dropdown-menu`
- `hover-card`, `input` and many more

#### Magic UI Components (`src/components/magicui/`)

- **Marquee**: Animated scrolling text component for testimonials

#### GalaxyRend Feature Components

- **HeroSection**: Main landing area with platform messaging
- **BentoGrid**: Grid layout for feature showcase
- **IntegrationSection**: Blockchain integration highlights
- **TestimonialSection**: User testimonials and social proof
- **FooterSection**: Platform navigation and branding

## GalaxyRend Application Flow

### Current Page Structure

The GalaxyRend homepage (`src/app/page.tsx`) renders components in this order:

```typescript
export default function Home() {
  return (
    <div>
      <HeroSection /> // Navigation + Hero content
      <BentoGrid /> // Feature showcase grid
      <IntegrationSection /> // Blockchain integrations
      <TestimonialSection /> // User testimonials
      <FooterSection /> // Footer with platform links
    </div>
  );
}
```

### User Journey Flow

1. **Landing**: Users see hero section with GalaxyRend branding
2. **Value Proposition**: "Decentralized Work, Verified Results" messaging
3. **Role Selection**: Cards for Creators, Nodes, and Admins
4. **Feature Discovery**: BentoGrid showcases platform capabilities
5. **Trust Building**: Integration highlights and testimonials
6. **Action**: Connect Wallet CTAs throughout the experience

## GalaxyRend Styling System

The application uses a sophisticated Tailwind CSS setup with GalaxyRend branding:

### Design System

- **Theme**: Dark mode applied by default for cosmic feel
- **Colors**: Blue and cyan gradients for GalaxyRend branding
- **Typography**: Geist Sans and Mono fonts with CSS variables
- **Components**: Consistent design patterns across all UI elements

### Custom Design Features

- **CSS Variables**: Defined in `globals.css` for consistent dark theming
- **Cosmic Gradients**: Blue/cyan color schemes throughout
- **Background Images**: Starknet-themed background in hero section
- **Border Radius**: Standardized border radius values for modern look
- **Shadow System**: Layered shadow system with cosmic glows

### Tailwind Configuration

- **Custom Colors**: GalaxyRend brand-specific color palette
- **Dark Mode**: Default dark theme with cosmic design elements
- **Responsive Design**: Mobile-first responsive utilities
- **Component Variants**: Using `class-variance-authority` for component variants

## Build and Deployment

### Development Commands

```bash
# Install dependencies
npm install
# or
bun install

# Start development server with Turbopack
npm run dev
# or
bun dev

# Build for production
npm run build

# Start production server
npm run start

# Run linting
npm run lint
```

### Production Build Features

- **Next.js Optimization**: Automatic code splitting and optimization
- **TypeScript**: Full type checking enabled for reliability
- **Turbopack**: Development mode optimization for faster builds
- **Static Generation**: Pages pre-rendered where possible
- **Image Optimization**: Next.js Image component with remote patterns
- **Font Optimization**: Automatic font loading optimization

## Technology Stack

- **Frontend**: Next.js 15 with React 19
- **Styling**: Tailwind CSS with custom components
- **UI Components**: Radix UI primitives
- **Blockchain**: Starknet integration
- **Deployment**: Vercel

## Learn More

To learn more about the technologies used:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API
- [Starknet Documentation](https://docs.starknet.io/) - learn about Starknet blockchain
- [Tailwind CSS](https://tailwindcss.com/docs) - utility-first CSS framework

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## Development Guidelines

### Component Development

```typescript
// Example GalaxyRend component pattern
import { ComponentProps } from "./types";
import { cn } from "@/lib/utils";

export function MyComponent({ className, ...props }: ComponentProps) {
  return (
    <div className={cn("base-styles", className)} {...props}>
      {/* Component content */}
    </div>
  );
}
```

### Best Practices

1. **Use Existing Components**: Check `src/components/ui/` first
2. **Follow Design System**: Maintain GalaxyRend branding consistency
3. **Responsive Design**: Use Tailwind responsive prefixes
4. **Accessibility**: Leverage Radix UI components for a11y
5. **Performance**: Optimize images and use Next.js features

## Project Status

- ✅ **GalaxyRend Branding**: Custom platform design and messaging
- ✅ **Dark Theme**: Cosmic design system implemented
- ✅ **Component Library**: Comprehensive UI components available
- ✅ **Responsive Design**: Mobile-first approach
- ✅ **Type Safety**: Full TypeScript implementation
- ✅ **Build Pipeline**: Optimized development and production builds
- 🚧 **Starknet Integration**: Ready for wallet connection features
- 🚧 **API Integration**: Prepared for backend connectivity

This GalaxyRend frontend provides a solid foundation for the decentralized work platform with modern development practices and an engaging user experience.
