# The site's design system

The shared system is `assets/tokens.css`. `assets/style.css` supplies publication and article patterns;
`assets/explorer.css` composes the evidence desk from the same roles. Both pages load tokens first.
Component styles do not introduce their own font sizes, weights, line heights or spacing values.

## Type roles

Newsreader carries reading text and editorial headings. Instrument Sans carries navigation, labels and notes
(including label headings inside source inspectors).
JetBrains Mono identifies exact strings and source records. Weights are regular 400, medium 500 and
strong 600; emphasis uses the relevant family's italic. There are no shrinking phone captions.

| Role | Size / line height in px | Use |
| --- | --- | --- |
| Display | 72/72 wide, 64/64 tablet, 40/48 phone | Opening research question |
| Page title | 48/48, 36/40 phone | Evidence desk entrance |
| Chapter title | 36/40, 32/40 phone | Article chapters and overview |
| Subheading | 24/32 | Subsections and the active desk comparison |
| Intro | 24/32 | Opening standfirst |
| Body | 18/28 | Narrative, case explanations and inference text |
| Interface | 14/20, medium or strong | Navigation, controls, record categories |
| Note | 14/24 | Captions, provenance, cautions, metadata |
| Record | 14/24, monospace | Literal page content, prompts, event paths |
| Token specimen | 18/28, monospace | A short token being examined |
| Metric | 36/40 | Counts and hypothetical result comparisons |

The desk has a page title followed by a 24px comparison heading, 18px question and 14px record labels.
It does not repeat the article's chapter-title scale inside every evidence group. Literal source text
stays 14px even when two cases remain adjacent on a narrow phone.

## Spacing and layout

Spacing is an 8px unit: 8, 16, 24, 32, 40, 48, 64, 80 and 96px. A 4px half-step serves compact label
relationships. Borders, focus outlines, vector geometry and font optical alignment are exceptions,
not additional spacing scales. Dimensions are relative units so browser text settings remain useful.

| Relationship | Rule |
| --- | --- |
| Paragraph gap | 24px |
| Heading to narrative | 32px after a chapter header; 16px after a subhead |
| Major evidence block | 32px outside the block |
| Panel inset | 24px desktop, 16px phone |
| Record/list row | 16px vertical spacing |
| Label to associated text | 8px when stacked |
| Chapter spacing | 80px wide, 64px tablet, 48px phone |
| Main gutter | 48px tablet/desktop, 24px phone, 16px below 360px |
| Prose measure | 656px maximum |
| Publication frame | 1280px including gutters |
| Desktop contents rail | 176px; 48–64px gap to article |
| Main control target | 48px; contents links use a 40px row |

Responsive changes alter composition rather than inventing smaller component type. Below 1024px the
cover stacks and the contents become a native disclosure. Below 768px the masthead uses T/P/A and the
overview stacks. Below 640px article comparison panels stack; desk source landmarks remain adjacent.
The compact 360px boundary changes gutters only. Role sizes change centrally at 640px and 1280px.

## Component rules

- The opening exhibit and case files share an inset, rule colour, source label and caption role.
  The opening record takes its natural content height; a hidden extra record does not reserve an empty area.
- Case narrative stays in the body role. Its exact strings use the record role. The inference rows use
  a fixed label column and body text, then stack on phones.
- Comparative metrics share one size. Their denominator and assumed population remain adjacent in notes
  or body text; magnitude is not used as decorative promotion.
- Technical disclosures use the same ruled summary, control target and spacing. They open at a deep link.
- Navigation and actions use text and underlines. Font size, weight, spacing and rules establish hierarchy;
  there is no decorative animation, gradient or 3D layer.
- Colour roles distinguish text priority, source identity and evidence state. Text labels also carry the
  distinction. Light, dark and print palettes are in the same token file.

## Maintaining the system

Choose an existing role before adding component styling. Change the token when a role is wrong across
the site; change the composition when the relationship is wrong in one view. Keep responsive type in
the token file, and use the page styles for grid changes. Generated paper figures retain their source
geometry. The colour contrast test reads the token palettes directly.

Review the opening, a case, a technical disclosure and a full desk comparison at 320, 375, 768 and
1440px. Check reading rhythm and alignment as well as overflow. A list of valid tokens alone cannot
establish visual quality; the rendered compositions must still be reviewed.
