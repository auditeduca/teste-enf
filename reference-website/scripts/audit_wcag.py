#!/usr/bin/env python3
"""WCAG Accessibility Audit — scans HTML files for WCAG 2.1 AA violations."""
import os, re, sys, argparse

def audit_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    issues = []
    
    # Images without alt
    for m in re.finditer(r'<img(?![^>]*\salt=)[^>]*>', html):
        issues.append(f"img without alt: {m.group()[:80]}")
    
    # Buttons without text or aria-label
    for m in re.finditer(r'<button([^>]*)>(.*?)</button>', html, re.DOTALL):
        attrs, inner = m.group(1), m.group(2)
        has_text = bool(re.sub(r'<[^>]+>|\s+|&[a-z]+;|×', '', inner).strip())
        if not has_text and 'aria-label' not in attrs:
            issues.append(f"button without text/aria: {m.group()[:80]}")
    
    # Inputs without label
    for m in re.finditer(r'<input[^>]*>', html):
        inp = m.group()
        if 'type="hidden"' in inp: continue
        if 'aria-label' in inp: continue
        issues.append(f"input without aria-label: {inp[:80]}")
    
    # Missing lang
    if not re.search(r'<html[^>]*lang=', html):
        issues.append("html element missing lang attribute")
    
    # Inline color styles (contrast risk)
    for m in re.finditer(r'style="[^"]*color:\s*(?:#|rgb)', html):
        issues.append(f"inline color style: {m.group()[:80]}")
    
    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict', action='store_true')
    parser.add_argument('--fail-on-error', action='store_true')
    args = parser.parse_args()
    
    all_issues = 0
    files_checked = 0
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', 'data', 'images', 'i18n', 'css', 'js', 'partials')]
        for f in files:
            if f.endswith('.html'):
                fp = os.path.join(root, f)
                issues = audit_html(fp)
                files_checked += 1
                if issues:
                    all_issues += len(issues)
                    if args.strict:
                        for i in issues:
                            print(f"  ❌ {fp}: {i}")
    
    print(f"\n{'='*50}")
    print(f"  Files checked: {files_checked}")
    print(f"  Total issues: {all_issues}")
    print(f"  Status: {'✅ PASS' if all_issues == 0 else '❌ FAIL'}")
    
    if args.fail_on_error and all_issues > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
