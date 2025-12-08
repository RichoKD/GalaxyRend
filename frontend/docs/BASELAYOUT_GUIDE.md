# BaseLayout Implementation Guide

## Overview

The `BaseLayout` component provides a reusable layout structure for all dashboard pages in FluxFrame. It includes:

- Background image from HeroSection
- Cosmic gradient overlays
- Consistent header with logo and navigation
- Customizable title and actions
- Responsive design

## File Structure

```text
frontend/src/
├── components/
│   └── BaseLayout.tsx          # Reusable layout component
└── app/
    └── dashboard/
        ├── creators/
        │   └── page.tsx        # Creator dashboard (uses BaseLayout)
        ├── nodes/
        │   └── page.tsx        # Node dashboard (uses BaseLayout)
        └── admin/
            └── page.tsx        # Admin dashboard (uses BaseLayout)
```

---

## BaseLayout API

### Props

| Prop              | Type                                      | Default         | Description                              |
| ----------------- | ----------------------------------------- | --------------- | ---------------------------------------- |
| `children`        | `ReactNode`                               | Required        | Page content to render inside the layout |
| `title`           | `string`                                  | `undefined`     | Page title shown in header               |
| `subtitle`        | `string`                                  | `undefined`     | Subtitle/description below title         |
| `headerActions`   | `ReactNode`                               | Default actions | Custom buttons/actions in header         |
| `showBackground`  | `boolean`                                 | `true`          | Show/hide background image and gradients |
| `gradientVariant` | `"blue" \| "cyan" \| "purple" \| "green"` | `"blue"`        | Color theme for page                     |

### Gradient Variants

Each variant affects the title gradient and background overlays:

- **`blue`**: Blue-to-cyan gradient (for Creators)

  - Title: `from-blue-400 to-cyan-400`
  - Backgrounds: Blue and cyan overlays

- **`cyan`**: Cyan-to-purple gradient (for Nodes)

  - Title: `from-cyan-400 to-purple-400`
  - Backgrounds: Cyan and purple overlays

- **`purple`**: Purple-to-blue gradient (for Admins)

  - Title: `from-purple-400 to-blue-400`
  - Backgrounds: Purple and blue overlays

- **`green`**: Green-to-cyan gradient (for Success/Special pages)
  - Title: `from-green-400 to-cyan-400`
  - Backgrounds: Green and cyan overlays

---

## Usage Flow - Step by Step

### Step 1: Basic Implementation

Create a new page and wrap your content with `BaseLayout`:

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";
import { Card } from "@/components/ui/card";

export default function YourPage() {
  return (
    <BaseLayout
      title="Your Page Title"
      subtitle="Brief description of what this page does"
      gradientVariant="blue"
    >
      <div className="container mx-auto px-6 py-8">
        {/* Your page content here */}
        <Card className="bg-zinc-900/80 border-zinc-800 backdrop-blur-sm">
          <p className="text-slate-200 p-6">Your content</p>
        </Card>
      </div>
    </BaseLayout>
  );
}
```

### Step 2: Add Custom Header Actions (Optional)

Replace default Settings/Exit buttons with custom actions:

```tsx
import { Button } from "@/components/ui/button";
import { Bell, User, Plus } from "lucide-react";

export default function YourPage() {
  return (
    <BaseLayout
      title="Your Page"
      subtitle="Description"
      gradientVariant="cyan"
      headerActions={
        <>
          <Button variant="ghost" size="sm" className="text-slate-300">
            <Bell className="w-4 h-4 mr-2" />
            Notifications
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="border-zinc-700 text-slate-300"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Action
          </Button>
          <Button size="sm" className="bg-cyan-600 hover:bg-cyan-700">
            <User className="w-4 h-4 mr-2" />
            Profile
          </Button>
        </>
      }
    >
      {/* Content */}
    </BaseLayout>
  );
}
```

### Step 3: Choose Appropriate Gradient Variant

Match the gradient to the page purpose:

```tsx
// For Creator pages
<BaseLayout gradientVariant="blue" title="Creator Dashboard">

// For Node pages
<BaseLayout gradientVariant="cyan" title="Node Dashboard">

// For Admin pages
<BaseLayout gradientVariant="purple" title="Admin Dashboard">

// For Success/Special pages
<BaseLayout gradientVariant="green" title="Achievements">
```

### Step 4: Disable Background (Optional)

For pages that need a clean background:

```tsx
<BaseLayout
  title="Settings"
  subtitle="Manage your preferences"
  showBackground={false}
>
  {/* Clean background without image/gradients */}
</BaseLayout>
```

---

## Complete Examples

### Example 1: Creator Dashboard

```tsx
"use client";

import { useState } from "react";
import BaseLayout from "@/components/BaseLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Plus, Briefcase } from "lucide-react";

export default function CreatorDashboard() {
  const [activeTab, setActiveTab] = useState("active");

  return (
    <BaseLayout
      title="Creator Dashboard"
      subtitle="Manage your projects and collaborate with nodes"
      gradientVariant="blue"
    >
      <div className="container mx-auto px-6 py-8">
        {/* Stats, Jobs, etc. */}
        <Card className="bg-zinc-900/80 border-zinc-800 backdrop-blur-sm p-6">
          <h3 className="text-slate-200 text-lg font-semibold mb-4">
            Your Active Jobs
          </h3>
          {/* Job list content */}
        </Card>
      </div>
    </BaseLayout>
  );
}
```

### Example 2: Node Dashboard with Custom Actions

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";
import { Button } from "@/components/ui/button";
import { Activity, Settings } from "lucide-react";

export default function NodeDashboard() {
  return (
    <BaseLayout
      title="Node Dashboard"
      subtitle="Browse jobs and earn rewards"
      gradientVariant="cyan"
      headerActions={
        <>
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-500/10 border border-green-500/20">
            <Activity className="w-4 h-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">Online</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="border-zinc-700 text-slate-300"
          >
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
        </>
      }
    >
      <div className="container mx-auto px-6 py-8">
        {/* Node dashboard content */}
      </div>
    </BaseLayout>
  );
}
```

### Example 3: Admin Dashboard

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";
import { Card } from "@/components/ui/card";
import { Shield } from "lucide-react";

export default function AdminDashboard() {
  return (
    <BaseLayout
      title="Admin Dashboard"
      subtitle="Monitor platform health and manage disputes"
      gradientVariant="purple"
      headerActions={
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500/10 border border-purple-500/20">
          <Shield className="w-4 h-4 text-purple-400" />
          <span className="text-sm text-purple-400 font-medium">
            Admin Access
          </span>
        </div>
      }
    >
      <div className="container mx-auto px-6 py-8">{/* Admin content */}</div>
    </BaseLayout>
  );
}
```

---

## Best Practices

### 1. Consistent Styling

Always use these classes for cards to maintain consistency:

```tsx

<Card className="bg-zinc-900/80 border-zinc-800 backdrop-blur-sm">
```

### 2. Container Padding

Wrap your content in a container with consistent padding:

```tsx
<div className="container mx-auto px-6 py-8">{/* Content */}</div>
```

### 3. Responsive Design

The BaseLayout is mobile-responsive:

- Title shows in header on desktop
- Title moves below logo on mobile
- Header actions stack appropriately

### 4. Gradient Selection

Choose gradients that match the user role:

- Creators → Blue
- Nodes → Cyan
- Admins → Purple
- Special pages → Green

### 5. Custom Actions

When adding custom `headerActions`, ensure they:

- Use appropriate icon sizes (`w-4 h-4`)
- Have proper spacing (`gap-4`)
- Match the zinc color scheme
- Include tooltips/labels for clarity

---

## Replication Checklist

To create a new page using BaseLayout:

- [ ] Import `BaseLayout` from `@/components/BaseLayout`
- [ ] Add `"use client"` directive at the top
- [ ] Choose appropriate `gradientVariant`

- [ ] Set descriptive `title` and `subtitle`
- [ ] Wrap content in `<div className="container mx-auto px-6 py-8">`
- [ ] Use backdrop blur on cards: `backdrop-blur-sm`
- [ ] Use consistent card styling: `bg-zinc-900/80 border-zinc-800`
- [ ] Test mobile responsiveness

- [ ] Add custom `headerActions` if needed
- [ ] Ensure all text uses appropriate slate colors

---

## Troubleshooting

### Background not showing

- Ensure `/public/background-image.png` exists
- Check `showBackground={true}` is set
- Verify no conflicting z-index issues

### Header actions not appearing

- Make sure you're passing `ReactNode` to `headerActions`
- Check for proper JSX fragment wrapping: `<>...</>`

### Title colors not working

- Verify `gradientVariant` is one of: `"blue" | "cyan" | "purple" | "green"`
- Check Tailwind config includes gradient utilities

### Mobile layout issues

- Test at different breakpoints (sm, md, lg)

- Ensure container has proper responsive padding
- Check that header actions don't overflow

---

## Migration from Old Pages

If you have existing dashboard pages without BaseLayout:

1. **Backup your page content** (everything inside the return statement)
2. **Remove old header/background code**
3. **Import BaseLayout**
4. **Wrap content with BaseLayout**
5. **Add title, subtitle, gradientVariant props**
6. **Test and adjust spacing as needed**

Example migration:

```tsx
// BEFORE
export default function OldPage() {
  return (
    <div className="min-h-screen bg-zinc-950">
      <header>{/* header code */}</header>
      <main>{/* content */}</main>
    </div>
  );
}

// AFTER
import BaseLayout from "@/components/BaseLayout";

export default function NewPage() {
  return (
    <BaseLayout title="Page Title" gradientVariant="blue">
      {/* content only */}
    </BaseLayout>
  );
}
```

---

## Summary

The BaseLayout component provides:
✅ Consistent background and styling across pages
✅ Reusable header with logo and navigation
✅ Customizable titles, subtitles, and actions
✅ Multiple color themes via gradients
✅ Mobile-responsive design
✅ Easy to implement and maintain

Use it for **all dashboard pages** to maintain design consistency!
