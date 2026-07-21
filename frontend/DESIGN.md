---
name: Kinetic Utility
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#414754'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#727786'
  outline-variant: '#c1c6d7'
  surface-tint: '#0059c5'
  primary: '#0058c3'
  on-primary: '#ffffff'
  primary-container: '#0070f3'
  on-primary-container: '#ffffff'
  inverse-primary: '#aec6ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#4e5e74'
  on-tertiary: '#ffffff'
  tertiary-container: '#67778e'
  on-tertiary-container: '#fffeff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#aec6ff'
  on-primary-fixed: '#001a43'
  on-primary-fixed-variant: '#004397'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#d3e4fe'
  tertiary-fixed-dim: '#b7c8e1'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485d'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
  container-max: 1200px
  gutter: 24px
  margin-mobile: 16px
---

## Brand & Style
The design system is rooted in the "Precision Minimalist" movement, drawing inspiration from high-performance developer tools and productivity platforms. It prioritizes speed, clarity, and utility to serve a dual audience of ambitious students and modern recruiters. 

The aesthetic is characterized by a "High-Definition" clarity: ample white space, razor-sharp typography, and a restrained use of color that ensures primary actions are unmistakable. The interface should feel "lightweight" yet structurally sound, utilizing subtle borders and soft shadows to create a sense of organized depth without the clutter of traditional enterprise software.

## Colors
The palette is dominated by a clean "Studio White" background to maximize readability. 
- **Primary:** A vibrant, high-energy blue used exclusively for primary calls to action, active states, and critical progress indicators.
- **Secondary:** A deep slate used for primary headings and icons to provide strong visual anchoring.
- **Tertiary:** A muted slate-gray for secondary text and metadata.
- **Neutral/Surface:** Systematic grays are used for layout containment and subtle background differentiation. 
- **Borders:** A consistent #E5E7EB is used for all structural divisions, maintaining a "blueprint" feel.

## Typography
This design system utilizes **Inter** across all roles to maintain a systematic, utilitarian aesthetic. 
- **Headlines:** Use tight letter-spacing (-0.01em to -0.02em) for larger sizes to create a "dense," professional look.
- **Hierarchy:** Rely on weight shifts (600 for headers, 400 for body) rather than dramatic color changes.
- **Labels:** Small labels and buttons use Medium (500) weights to ensure legibility against the vibrant primary blue or neutral backgrounds.

## Layout & Spacing
The layout follows a strict **8px grid system**. 
- **Desktop:** A 12-column fluid grid with a 1200px max-width container. Content is centered with generous 48px to 64px vertical section padding.
- **Mobile:** Transition to a single-column layout with 16px side margins. Horizontal scrolling "carousels" are preferred for job categories or featured companies to save vertical space.
- **Rhythm:** Use "md" (16px) for internal component spacing and "lg" (24px) for spacing between distinct UI blocks.

## Elevation & Depth
Depth is created through a combination of **Tonal Layers** and **Ambient Shadows**.
- **Level 0 (Background):** Pure #FFFFFF.
- **Level 1 (Cards/Inputs):** White surface with a 1px #E5E7EB border.
- **Level 2 (Hover/Active):** A soft, highly diffused shadow (0px 4px 12px rgba(0, 0, 0, 0.05)) is applied to cards when hovered to indicate interactivity.
- **Level 3 (Modals/Popovers):** A more pronounced shadow (0px 12px 24px rgba(0, 0, 0, 0.1)) to separate critical overlays from the main content.
- **Backdrop:** Use a subtle blur (8px) on navigation bars or modal backdrops to maintain context.

## Shapes
The shape language is modern and approachable, utilizing "Rounded" (8px to 12px) corners.
- **Default (md):** 8px for small buttons and input fields.
- **Large (lg):** 12px for standard cards and containers.
- **Extra Large (xl):** 16px for prominent feature sections or modal containers.
- Avoid 100% pill-shapes except for specific "Status" badges or tags.

## Components
- **Buttons:** Primary buttons use the Vibrant Blue background with White text. Secondary buttons use a white background with the #E5E7EB border and Slate-Dark text. Height should be a consistent 40px or 48px.
- **Inputs:** Fields use a 1px #E5E7EB border that transitions to 1px Primary Blue + a 2px soft blue focus ring (low opacity) when active.
- **Cards:** Job cards should have a 12px radius, a 1px border, and no shadow in their default state, gaining a shadow only on hover.
- **Chips/Badges:** Use a subtle background (e.g., 10% opacity of the primary blue) with 12px text for category tags or "New" labels.
- **Lists:** Use horizontal dividers (1px #F3F4F6) with 16px vertical padding for job listings to create a clean, scannable feed.
- **Job Feed Filter:** A persistent "sticky" sidebar on desktop, transitioning to a "Filter" button with a bottom-sheet on mobile.