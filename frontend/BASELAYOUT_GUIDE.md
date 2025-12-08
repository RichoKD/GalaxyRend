# BaseLayout Usage Guide

## Overview

BaseLayout is a reusable component that provides consistent background, header, and footer across all dashboard pages in FluxFrame.

## Component Location

`/frontend/src/components/BaseLayout.tsx`

## Features

- ✅ Background image from HeroSection
- ✅ Cosmic gradient overlays
- ✅ Consistent header with logo and navigation
- ✅ Optional footer
- ✅ Customizable gradient variants
- ✅ Responsive design
- ✅ Optional custom header actions

---

## Basic Usage

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";

export default function YourPage() {
  return (
    <BaseLayout
      title="Page Title"
      subtitle="Page subtitle or description"
      gradientVariant="blue"
      showFooter={true}
    >
      {/* Your page content goes here */}
      <div className="container mx-auto px-6 py-8">
        <h2>Your Content</h2>
      </div>
    </BaseLayout>
  );
}
```

---

## Props

| Prop              | Type                                            | Default  | Description                    |
| ----------------- | ----------------------------------------------- | -------- | ------------------------------ |
| `children`        | `ReactNode`                                     | Required | Your page content              |
| `title`           | `string`                                        | Optional | Page title displayed in header |
| `subtitle`        | `string`                                        | Optional | Subtitle displayed below title |
| `gradientVariant` | `"blue"` \| `"cyan"` \| `"purple"` \| `"green"` | `"blue"` | Color scheme for gradients     |
| `showBackground`  | `boolean`                                       | `true`   | Show/hide background image     |
| `showFooter`      | `boolean`                                       | `true`   | Show/hide footer section       |
| `headerActions`   | `ReactNode`                                     | Optional | Custom header action buttons   |

---

## Gradient Variants

### Blue (Creator/Default)

```tsx
<BaseLayout gradientVariant="blue">
```

- Title gradient: blue-400 to cyan-400
- Background gradients: blue and cyan tones

### Cyan (Node)

```tsx
<BaseLayout gradientVariant="cyan">
```

- Title gradient: cyan-400 to purple-400
- Background gradients: cyan and purple tones

### Purple (Admin)

```tsx
<BaseLayout gradientVariant="purple">
```

- Title gradient: purple-400 to blue-400
- Background gradients: purple and blue tones

### Green (Custom)

```tsx
<BaseLayout gradientVariant="green">
```

- Title gradient: green-400 to cyan-400
- Background gradients: green and cyan tones

---

## Examples

### 1. Simple Page (Minimum Configuration)

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";

export default function SimplePage() {
  return (
    <BaseLayout>
      <div className="container mx-auto px-6 py-8">
        <p className="text-slate-200">Simple content</p>
      </div>
    </BaseLayout>
  );
}
```

### 2. Page with Title & Subtitle

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";

export default function DashboardPage() {
  return (
    <BaseLayout
      title="Creator Dashboard"
      subtitle="Manage your projects and collaborate with nodes"
      gradientVariant="blue"
    >
      <div className="container mx-auto px-6 py-8">{/* Your content */}</div>
    </BaseLayout>
  );
}
```

### 3. Page with Custom Header Actions

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";
import { Button } from "@/components/ui/button";
import { Bell, User } from "lucide-react";

export default function CustomHeaderPage() {
  const customActions = (
    <>
      <Button variant="ghost" size="sm">
        <Bell className="w-4 h-4" />
      </Button>
      <Button variant="outline" size="sm">
        <User className="w-4 h-4 mr-2" />
        Profile
      </Button>
    </>
  );

  return (
    <BaseLayout
      title="Custom Page"
      headerActions={customActions}
      gradientVariant="cyan"
    >
      <div className="container mx-auto px-6 py-8">{/* Your content */}</div>
    </BaseLayout>
  );
}
```

### 4. Page Without Background

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";

export default function CleanPage() {
  return (
    <BaseLayout
      title="Clean Page"
      showBackground={false}
      gradientVariant="purple"
    >
      <div className="container mx-auto px-6 py-8">
        {/* Content without background image */}
      </div>
    </BaseLayout>
  );
}
```

### 5. Page Without Footer

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";

export default function NoFooterPage() {
  return (
    <BaseLayout
      title="Modal-like Page"
      showFooter={false}
      gradientVariant="blue"
    >
      <div className="container mx-auto px-6 py-8">
        {/* Content without footer */}
      </div>
    </BaseLayout>
  );
}
```

---

## Replication Flow

To create a new page using BaseLayout:

### Step 1: Create the Page File

```bash
# Create new page in desired location
touch frontend/src/app/dashboard/your-page/page.tsx
```

### Step 2: Add Base Structure

```tsx
"use client";

import BaseLayout from "@/components/BaseLayout";

export default function YourPage() {
  return (
    <BaseLayout
      title="Your Page Title"
      subtitle="Your page description"
      gradientVariant="blue" // or cyan, purple, green
      showFooter={true}
    >
      <div className="container mx-auto px-6 py-8">
        {/* Your content here */}
      </div>
    </BaseLayout>
  );
}
```

### Step 3: Add Your Content

Fill in the container with your specific page content (forms, cards, tables, etc.)

### Step 4: Customize (Optional)

- Change `gradientVariant` based on page type
- Add custom `headerActions` if needed
- Toggle `showBackground` or `showFooter` as needed

---

## Best Practices

### 1. Consistent Spacing

Always use the container pattern for consistent spacing:

```tsx
<BaseLayout>
  <div className="container mx-auto px-6 py-8">{/* Content */}</div>
</BaseLayout>
```

### 2. Gradient Variants by Role

- **Creators**: Use `gradientVariant="blue"`
- **Nodes**: Use `gradientVariant="cyan"`
- **Admins**: Use `gradientVariant="purple"`
- **Other**: Use `gradientVariant="green"`

### 3. Content Cards

Use backdrop-blur for cards that need to stand out against the background:

```tsx
<Card className="bg-zinc-900/80 border-zinc-800 backdrop-blur-sm">
  {/* Card content */}
</Card>
```

### 4. Responsive Design

The BaseLayout is fully responsive. Ensure your content is also responsive:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Responsive grid */}
</div>
```

### 5. Loading States

Show loading states within the BaseLayout:

```tsx
<BaseLayout title="Dashboard">
  <div className="container mx-auto px-6 py-8">
    {isLoading ? (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
      </div>
    ) : (
      <YourContent />
    )}
  </div>
</BaseLayout>
```

---

## Complete Example: Node Dashboard

```tsx
"use client";

import { useState, useEffect } from "react";
import BaseLayout from "@/components/BaseLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function NodeDashboard() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch your data here
    fetchData();
  }, []);

  const fetchData = async () => {
    // Your data fetching logic
    setIsLoading(false);
  };

  return (
    <BaseLayout
      title="Node Dashboard"
      subtitle="Browse jobs and earn rewards"
      gradientVariant="cyan"
      showFooter={true}
    >
      <div className="container mx-auto px-6 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center min-h-[60vh]">
            <p className="text-slate-400">Loading...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Your dashboard content */}
            <Card className="bg-zinc-900/80 border-zinc-800 backdrop-blur-sm p-6">
              <h3 className="text-xl font-semibold text-slate-200 mb-4">
                Available Jobs
              </h3>
              {/* Job listings */}
            </Card>
          </div>
        )}
      </div>
    </BaseLayout>
  );
}
```

---

## Troubleshooting

### Issue: Background not showing

**Solution**: Ensure `showBackground={true}` and the image exists at `/public/background-image.png`

### Issue: Header actions not visible

**Solution**: Check that `headerActions` prop contains valid React components

### Issue: Footer overlapping content

**Solution**: Add sufficient bottom padding to your content container

### Issue: Gradient colors not matching

**Solution**: Verify you're using the correct `gradientVariant` prop value

---

## File Structure

```text
frontend/
├── src/
│   ├── components/
│   │   ├── BaseLayout.tsx          # Main layout component
│   │   ├── Footer.tsx              # Footer component
│   │   └── ui/                     # UI components
│   └── app/
│       └── dashboard/
│           ├── creators/
│           │   └── page.tsx        # Example: Creator dashboard
│           ├── nodes/
│           │   └── page.tsx        # Example: Node dashboard
│           └── admin/
│               └── page.tsx        # Example: Admin dashboard
```

---

## Quick Reference Card

```tsx
// Minimal
<BaseLayout>
  <div className="container mx-auto px-6 py-8">
    {/* Content */}
  </div>
</BaseLayout>

// Full Options
<BaseLayout
  title="Page Title"
  subtitle="Description"
  gradientVariant="blue|cyan|purple|green"
  showBackground={true|false}
  showFooter={true|false}
  headerActions={<YourCustomActions />}
>
  <div className="container mx-auto px-6 py-8">
    {/* Content */}
  </div>
</BaseLayout>
```

---

## Need Help?

- Check the BaseLayout component source for implementation details
- Refer to existing dashboard pages for working examples
- Ensure all required dependencies are imported

Happy building! 🚀
