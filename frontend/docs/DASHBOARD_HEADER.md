# DashboardHeader Component

A reusable, responsive header component for all dashboard pages with mobile menu support.

## Features

✅ **Fixed positioning** with backdrop blur and semi-transparent background  
✅ **Responsive navigation** - Horizontal menu on desktop, hamburger menu on mobile  
✅ **Role-based navigation** - Automatic menu items based on user role (creator/node/admin)  
✅ **Active link highlighting** - Current page is highlighted in blue  
✅ **Mobile-first design** - Optimized for all screen sizes  
✅ **Accessible** - ARIA labels and semantic HTML  
✅ **Smooth transitions** - Hover effects and color changes

## Usage

### Basic Implementation

Update your dashboard page to use the new header:

```tsx
import BaseLayout from "@/components/BaseLayout";

export default function CreatorDashboard() {
  return (
    <BaseLayout
      gradientVariant="blue"
      showFooter={true}
      useDashboardHeader={true}
      dashboardRole="creator"
    >
      {/* Your dashboard content */}
    </BaseLayout>
  );
}
```

### Props

#### BaseLayout Props

| Prop                 | Type                                      | Default     | Description                     |
| -------------------- | ----------------------------------------- | ----------- | ------------------------------- |
| `useDashboardHeader` | `boolean`                                 | `false`     | Enable the new dashboard header |
| `dashboardRole`      | `"creator" \| "node" \| "admin"`          | `"creator"` | User role for navigation items  |
| `gradientVariant`    | `"blue" \| "cyan" \| "purple" \| "green"` | `"blue"`    | Background gradient color       |
| `showFooter`         | `boolean`                                 | `true`      | Show/hide footer                |
| `showBackground`     | `boolean`                                 | `true`      | Show/hide background effects    |

### Role-Based Navigation

The header automatically displays appropriate navigation items based on role:

#### Creator Dashboard

- Dashboard
- My Jobs
- Create Job

#### Node Dashboard

- Dashboard
- Available Jobs
- My Assignments

#### Admin Dashboard

- Dashboard
- Users
- All Jobs

## Examples

### Creator Dashboard

```tsx
<BaseLayout
  useDashboardHeader={true}
  dashboardRole="creator"
  gradientVariant="blue"
  showFooter={true}
>
  <div className="py-12">{/* Creator dashboard content */}</div>
</BaseLayout>
```

### Node Dashboard

```tsx
<BaseLayout
  useDashboardHeader={true}
  dashboardRole="node"
  gradientVariant="cyan"
  showFooter={true}
>
  <div className="py-12">{/* Node dashboard content */}</div>
</BaseLayout>
```

### Admin Dashboard

```tsx
<BaseLayout
  useDashboardHeader={true}
  dashboardRole="admin"
  gradientVariant="purple"
  showFooter={true}
>
  <div className="py-12">{/* Admin dashboard content */}</div>
</BaseLayout>
```

## Responsive Design

### Desktop (≥ 768px)

- Full horizontal navigation with all menu items
- Settings and Exit buttons visible
- Logo on the left
- Navigation items in center
- Action buttons on right

### Mobile (< 768px)

- Hamburger menu button
- Logo on left
- Exit button and menu toggle on right
- Collapsible vertical menu panel
- Menu closes automatically after navigation

## Styling

### Header Structure

```
Fixed Header (z-50)
├── Semi-transparent background (bg-zinc-900/80)
├── Backdrop blur effect
└── Bottom border (border-zinc-800)
```

### Navigation Container

```
Responsive container
├── Desktop: Horizontal flex layout
├── Mobile: Collapsible vertical menu
└── Progressive spacing (4 → 6 → 8)
```

### Interactive Elements

- **Links**: Slate 300 → Blue 400 on hover
- **Active Links**: Blue 400 color
- **Buttons**: Smooth transitions with hover effects
- **Menu Toggle**: X icon when open, hamburger when closed

## Accessibility

✅ Semantic HTML (`<header>`, `<nav>`)  
✅ ARIA labels for screen readers  
✅ Keyboard navigation support  
✅ Focus states for interactive elements  
✅ Proper link elements with href attributes

## Customization

To add custom navigation items, edit the `navigationItems` object in `DashboardHeader.tsx`:

```tsx
const navigationItems = {
  creator: [
    { href: "/dashboard/creators", label: "Dashboard", icon: LayoutDashboard },
    { href: "/dashboard/creators/new-page", label: "New Page", icon: SomeIcon },
  ],
  // ... other roles
};
```

## Migration Guide

### Before (Old Header)

```tsx
<BaseLayout
  title="Creator Dashboard"
  subtitle="Manage your projects"
  gradientVariant="blue"
  showFooter={true}
>
```

### After (New Header)

```tsx
<BaseLayout
  useDashboardHeader={true}
  dashboardRole="creator"
  gradientVariant="blue"
  showFooter={true}
>
```

## Benefits

1. **Cleaner UI** - No more large title/subtitle taking up space
2. **Better Navigation** - Easy access to all dashboard sections
3. **Consistent Design** - Same header across all dashboard pages
4. **Mobile Optimized** - Collapsible menu for small screens
5. **Reusable** - One component for all dashboards
6. **Maintainable** - Update navigation in one place

## Notes

- The header is fixed at the top with `z-index: 50`
- BaseLayout automatically adds proper spacing below the header
- Active link detection uses Next.js `usePathname()` hook
- Mobile menu uses React state for toggle functionality
- All transitions are smooth (300ms duration)
