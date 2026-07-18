# Tailwind CSS Reference

Quick reference for Tailwind CSS utility classes. Use this to write correct, consistent CSS.

## Layout

### Container
```
mx-auto max-w-5xl px-6    — Standard section container
mx-auto max-w-7xl px-6    — Wide container
mx-auto max-w-3xl px-6    — Narrow container (text-focused)
```

### Flexbox
```
flex                      — Block flex container
inline-flex                — Inline flex container
flex-col                   — Vertical stack
flex-row                   — Horizontal row
flex-1                     — Grow to fill
items-center               — Vertical center
justify-center             — Horizontal center
justify-between            — Space between
gap-4                      — Gap between items (1rem)
gap-8                      — Gap between items (2rem)
```

### Grid
```
grid                       — Grid container
grid-cols-2                — 2 columns
grid-cols-3                — 3 columns
grid-cols-4                — 4 columns
sm:grid-cols-12            — 12-column responsive grid
col-span-4                 — Span 4 columns
col-span-8                 — Span 8 columns
```

### Responsive
```
sm:    — 640px+
md:    — 768px+
lg:    — 1024px+
xl:    — 1280px+
```

## Spacing

### Padding
```
p-4    — 1rem all sides
p-6    — 1.5rem all sides
p-8    — 2rem all sides
px-6   — 1.5rem horizontal
py-24  — 6rem vertical
py-32  — 8rem vertical
```

### Margin
```
m-0    — No margin
mx-auto — Center horizontally
mt-4   — 1rem top
mt-8   — 2rem top
mb-6   — 1.5rem bottom
```

## Typography

### Font Size
```
text-xs     — 0.75rem (12px)
text-sm     — 0.875rem (14px)
text-base   — 1rem (16px)
text-lg     — 1.125rem (18px)
text-xl     — 1.25rem (20px)
text-2xl    — 1.5rem (24px)
text-3xl    — 1.875rem (30px)
text-4xl    — 2.25rem (36px)
text-5xl    — 3rem (48px)
text-6xl    — 3.75rem (60px)
text-7xl    — 4.5rem (72px)
```

### Font Weight
```
font-normal    — 400
font-medium    — 500
font-semibold  — 600
font-bold      — 700
```

### Text Colors
```
text-white              — White
text-black              — Black
text-gray-500           — Gray
text-platinum           — Custom: light gray
text-vermeil            — Custom: gold
text-cabinet-noir       — Custom: dark
```

### Text Alignment
```
text-left       — Left align
text-center     — Center align
text-right      — Right align
```

### Line Height
```
leading-tight      — 1.25
leading-snug       — 1.375
leading-normal     — 1.5
leading-relaxed    — 1.625
leading-7          — 1.75rem
leading-8          — 2rem
```

### Letter Spacing
```
tracking-tight     — -0.025em
tracking-normal    — 0em
tracking-wide      — 0.025em
tracking-[0.18em]  — Custom tracking
tracking-[0.32em]  — Custom tracking (eyebrows)
```

## Colors

### Background
```
bg-white            — White background
bg-black            — Black background
bg-transparent      — Transparent
bg-vermeil          — Custom gold
bg-cabinet-noir     — Custom dark
bg-atlas-slate      — Custom slate
```

### Opacity
```
opacity-0           — Transparent
opacity-50          — 50%
opacity-[0.07]      — Custom 7%
opacity-[0.10]      — Custom 10%
```

## Borders

```
border              — 1px border
border-0            — No border
border-t            — Top border only
border-b            — Bottom border only
border-platinum/10  — Custom border with opacity
rounded-full        — Pill shape
rounded-sm          — Small radius
```

## Common Patterns

### Hero Section
```tsx
<section className="relative overflow-hidden border-b border-platinum/10">
  <div className="pointer-events-none absolute inset-0 opacity-[0.07]"
    style={{ backgroundImage: "radial-gradient(...)" }} />
  <div className="relative mx-auto max-w-5xl px-6 py-28 text-center sm:py-40">
    <h1 className="font-display text-5xl sm:text-7xl">Title</h1>
  </div>
</section>
```

### Card Grid
```tsx
<div className="grid gap-8 sm:grid-cols-3">
  {items.map(item => (
    <div key={item.id} className="border border-platinum/10 bg-atlas-slate p-8">
      {item.content}
    </div>
  ))}
</div>
```

### Two Column
```tsx
<div className="grid gap-12 sm:grid-cols-12 sm:gap-8">
  <div className="sm:col-span-4">Left</div>
  <div className="sm:col-span-8">Right</div>
</div>
```

### Section with Eyebrow
```tsx
<div className="max-w-2xl">
  <span className="text-xs font-medium uppercase tracking-[0.32em] text-vermeil">
    Eyebrow
  </span>
  <h2 className="mt-5 font-display text-3xl sm:text-4xl">Heading</h2>
  <p className="mt-6 text-lg text-platinum/70">Description</p>
</div>
```
