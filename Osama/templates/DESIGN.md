# ComplianceHub — Design System
_AI-readable design reference for all ComplianceHub UI work._
_Drop this file in repo root. Cline/Qwen/Gemini reads it automatically._

---

## Brand Identity

**Organization:** TÜV Austria GCC — Certification Body
**Industry:** ISO Certification, GRC (Governance, Risk, Compliance)
**Tone:** Professional, authoritative, trustworthy, clean

---

## Colors

### Primary
- **TUV Blue:** `#003D7A` — headers, primary actions, navigation
- **TUV Red:** `#C00000` — alerts, critical items, emphasis

### Client Accents (use per client)
| Client | Primary | Secondary | Use |
|--------|---------|-----------|-----|
| MSD-MOI | `#004D26` | `#C8A96E` | Headers, accents |
| SAGCO | `#1B3A4B` | `#E07B39` | Headers, accents |
| Al-Ahsa | `#006400` | — | Headers |
| UACC | `#003D7A` | — | Headers |

### Neutral Palette
- **Background:** `#FFFFFF` (light) / `#0F172A` (dark mode)
- **Surface:** `#F8FAFC` — cards, panels
- **Border:** `#E2E8F0` — dividers, card borders
- **Text Primary:** `#0F172A` — headings, body
- **Text Secondary:** `#64748B` — labels, descriptions
- **Text Muted:** `#94A3B8` — placeholders, timestamps

### Semantic Colors
- **Success:** `#10B981` — compliant, passed, complete
- **Warning:** `#F59E0B` — partial, in-progress, attention
- **Error:** `#EF4444` — non-compliant, failed, critical
- **Info:** `#3B82F6` — informational, links

---

## Typography

### Font Stack
- **Headings:** `Inter` — clean, professional, excellent readability
- **Body:** `Inter` — consistent with headings
- **Monospace:** `JetBrains Mono` — code blocks, formulas, doc codes

### Scale
| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 2rem (32px) | 700 | 1.2 |
| H2 | 1.5rem (24px) | 600 | 1.3 |
| H3 | 1.25rem (20px) | 600 | 1.4 |
| Body | 1rem (16px) | 400 | 1.6 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Caption | 0.75rem (12px) | 400 | 1.4 |

---

## Spacing

### Base Unit: 4px
- **xs:** 4px — tight spacing (icon gaps)
- **sm:** 8px — compact spacing (table cells)
- **md:** 16px — default spacing (card padding)
- **lg:** 24px — section spacing
- **xl:** 32px — page sections
- **2xl:** 48px — major sections

---

## Layout

### Grid
- **Max width:** 1280px
- **Columns:** 12-column grid
- **Gutter:** 24px
- **Breakpoints:** sm(640px) · md(768px) · lg(1024px) · xl(1280px)

### Cards
- **Border radius:** 8px
- **Padding:** 24px
- **Shadow:** `0 1px 3px rgba(0,0,0,0.1)` (subtle)
- **Border:** 1px solid `#E2E8F0`

### Tables (ComplianceHub Core)
- **Header:** TUV Blue `#003D7A` background, white text
- **Row hover:** `#F1F5F9`
- **Zebra stripe:** `#F8FAFC`
- **Cell padding:** 12px 16px
- **Border:** 1px solid `#E2E8F0`
- **Font size:** 14px (compact for data density)

### Forms
- **Input height:** 40px
- **Border radius:** 6px
- **Border:** 1px solid `#CBD5E1`
- **Focus ring:** 2px solid `#3B82F6`
- **Label:** 14px, weight 500, color `#374151`
- **Error state:** border `#EF4444`, text `#DC2626`

---

## Components

### Buttons
- **Primary:** TUV Blue background, white text, 8px radius
- **Secondary:** white background, TUV Blue border/text
- **Danger:** `#EF4444` background, white text
- **Height:** 40px (default) / 36px (compact)
- **Padding:** 0 16px

### Status Badges
| Status | Background | Text | Icon |
|--------|-----------|------|------|
| Compliant | `#D1FAE5` | `#065F46` | ✓ |
| Partial | `#FEF3C7` | `#92400E` | ⚠ |
| Non-Compliant | `#FEE2E2` | `#991B1B` | ✗ |
| N/A | `#F1F5F9` | `#64748B` | — |

### Risk Level Badges
| Level | Background | Text |
|-------|-----------|------|
| Critical | `#DC2626` | white |
| High | `#EF4444` | white |
| Medium | `#F59E0B` | white |
| Low | `#10B981` | white |

### Dashboard Cards
- **KPI card:** white background, 8px radius, 24px padding
- **Value:** 2.5rem, weight 700, color `#0F172A`
- **Label:** 14px, weight 500, color `#64748B`
- **Trend indicator:** green up / red down arrow + percentage

---

## Principles

1. **Data density over decoration.** Tables show maximum rows. Charts show clear data. No gratuitous whitespace.
2. **Status at a glance.** Color-coded badges for compliance status, risk levels, audit findings.
3. **Client isolation.** Each client's deliverables use their brand colors. Never mix.
4. **Print-ready.** A4 format, freeze panes, repeat headers. Excel output = print-ready.
5. **Accessibility.** WCAG AA contrast. Keyboard navigable. Screen reader compatible.
6. **No AI slop.** No gradients for decoration. No animations for show. No rounded corners larger than 8px. No drop shadows heavier than subtle. Functional design only.

---

## Anti-Patterns (Never Do)

- ❌ Gradient backgrounds on cards or sections
- ❌ Rounded corners > 8px
- ❌ Heavy drop shadows or glow effects
- ❌ Animated transitions on data tables
- ❌ Decorative illustrations or stock photos
- ❌ Centered body text
- ❌ Uppercase headers (except badges)
- ❌ More than 3 font sizes in one component
- ❌ Colors not in this palette

---

## 21st.dev Components (Copy-Paste Prompts)

### Data Table (ComplianceHub Core)
```
Build a data table component with:
- Header: TUV Blue (#003D7A) background, white text, 14px font
- Rows: alternating white/#F8FAFC, hover #F1F5F9
- Cell padding: 12px 16px
- Sortable columns with arrow indicators
- Status badges: green (compliant), yellow (partial), red (non-compliant)
- Row selection with checkbox
- Pagination at bottom
- Search/filter bar above table
- Responsive: horizontal scroll on mobile
Style: Tailwind CSS, shadcn/ui conventions
```

### Dashboard KPI Card
```
Build a KPI card component with:
- White background, 8px border radius, 1px #E2E8F0 border
- Label: 14px, weight 500, color #64748B, uppercase
- Value: 2.5rem, weight 700, color #0F172A
- Trend: green arrow up (+12%) or red arrow down (-3%)
- Sparkline chart in bottom-right corner (optional)
- Subtle shadow: 0 1px 3px rgba(0,0,0,0.1)
Style: Tailwind CSS, clean minimal
```

### Risk Matrix
```
Build a risk matrix component with:
- 5x5 grid (Likelihood vs Impact)
- Color gradient: green (low) → yellow (medium) → red (high)
- Each cell shows count of risks
- Clickable cells to filter risk register
- Axis labels: 1-5 scale
- Legend showing risk levels
Style: Tailwind CSS, data visualization
```

### Audit Findings Card
```
Build an audit finding card with:
- Left border: 4px colored by severity (red=major, yellow=minor, blue=observation)
- Clause reference: monospace font, #64748B
- Finding title: 16px, weight 600
- Evidence: 14px, color #374151
- Severity badge: inline, colored background
- Status badge: open/closed/verified
- Expandable detail section
Style: Tailwind CSS, professional
```

### CAPA Timeline
```
Build a CAPA timeline component with:
- Vertical timeline with 5 steps
- Steps: Root Cause → Containment → Corrective → Preventive → Effectiveness
- Each step: icon, title, description, date, status
- Status: completed (green), in-progress (yellow), pending (gray)
- Connecting line between steps
- Current step highlighted with pulse animation
Style: Tailwind CSS, clean timeline
```

---

_Last updated: 2026-08-08 · OWL v4.0_
