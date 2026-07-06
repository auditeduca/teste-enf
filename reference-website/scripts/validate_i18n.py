#!/usr/bin/env python3
"""Validate i18n dictionaries — checks all languages have required keys."""
import os, json, sys, argparse

REQUIRED_KEYS_MIN = 345
LANGUAGES = ["en","es","fr","de","it","nl","pl","ru","tr","ar","he","hi","bn",
             "zh-CN","zh-TW","ja","ko","vi","th","id","ms","tl","sw","am","el","ro","hu","cs","sv"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--languages', type=int, default=28)
    parser.add_argument('--fail-on-missing', action='store_true')
    args = parser.parse_args()
    
    i18n_dir = 'i18n'
    if not os.path.isdir(i18n_dir):
        print(f"❌ i18n directory not found")
        sys.exit(1)
    
    total_ok = 0
    total_fail = 0
    
    for lang in LANGUAGES[:args.languages]:
        fp = os.path.join(i18n_dir, f'{lang}.json')
        if not os.path.exists(fp):
            print(f"  ❌ {lang}: file missing")
            total_fail += 1
            continue
        
        with open(fp, 'r', encoding='utf-8') as f:
            try:
                d = json.load(f)
            except json.JSONDecodeError as e:
                print(f"  ❌ {lang}: invalid JSON — {e}")
                total_fail += 1
                continue
        
        key_count = len(d)
        if key_count >= REQUIRED_KEYS_MIN:
            print(f"  ✅ {lang}: {key_count} keys")
            total_ok += 1
        else:
            missing = REQUIRED_KEYS_MIN - key_count
            print(f"  ⚡ {lang}: {key_count} keys ({missing} missing)")
            total_fail += 1
    
    print(f"\n{'='*50}")
    print(f"  Languages OK: {total_ok}/{args.languages}")
    print(f"  Languages FAIL: {total_fail}")
    print(f"  Status: {'✅ PASS' if total_fail == 0 else '❌ FAIL'}")
    
    if args.fail_on_missing and total_fail > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
