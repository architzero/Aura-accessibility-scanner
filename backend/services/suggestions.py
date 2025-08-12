SUGGESTION_MAP = {
    # --- Critical Issues ---
    "image-alt": "AI suggestion will be generated for this issue.",
    "label": "Fix: Every form element (like `<input>`, `<select>`) must have a corresponding `<label>` to identify its purpose.",
    "link-name": "Fix: Ensure every link has discernible, descriptive text. If a link only contains an image, the image's alt text acts as the link's name.",
    "button-name": "Fix: Ensure every button has clear, discernible text that describes its function.",
    "color-contrast": "Fix: Increase the contrast between the text and background colors. Aim for a contrast ratio of at least 4.5:1 for normal text.",
    "aria-required-attr": "Fix: Elements with a specific ARIA role must have all required attributes for that role. For example, a `role='slider'` must have `aria-valuenow`.",
    "aria-valid-attr-value": "Fix: Ensure all ARIA attributes have valid values according to their specification (e.g., `aria-hidden` must be 'true' or 'false').",
    
    # --- Serious Issues ---
    "html-has-lang": "Fix: Add a `lang` attribute to the `<html>` tag to declare the default language of the page (e.g., `<html lang=\"en\">`).",
    "document-title": "Fix: Add a descriptive, non-empty `<title>` element to the HTML document's `<head>` section.",
    "meta-viewport": "Fix: Ensure the `<meta name=\"viewport\">` tag does not disable user scaling, for example by including `user-scalable=no` or `maximum-scale=1.0`.",
    
    # --- Moderate Issues ---
    "heading-order": "Fix: Heading levels should increase by only one. Ensure you don't skip levels (e.g., an `<h1>` should be followed by an `<h2>`, not an `<h3>`).",
    "list": "Fix: `<ul>` and `<ol>` list elements should only contain `<li>`, `<script>`, or `<template>` elements as direct children.",
    "region": "Fix: Wrap the main content sections of your page in landmark elements like `<main>`, `<nav>`, `<header>`, and `<footer>` to improve navigation for screen reader users.",
    "link-in-text-block": "Fix: Ensure links are visually distinct without relying only on color. A common solution is to add an underline to links within paragraphs.",
    "duplicate-id": "Fix: Ensure that every `id` attribute is unique on the page to avoid issues with screen readers and scripting.",
    
    # --- Minor/Best Practice ---
    "empty-heading": "Fix: Headings (<h1>, <h2>, etc.) must not be empty.",
    "form-field-multiple-labels": "Fix: A form element should not have more than one associated `<label>`.",
}