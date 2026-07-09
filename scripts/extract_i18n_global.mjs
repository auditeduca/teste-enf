#!/usr/bin/env node
/** Extrai TRANSLATIONS de lang-selector.js para stdout JSON */
import fs from "fs";

const file = process.argv[2];
const langs = process.argv.slice(3);
const code = fs.readFileSync(file, "utf8");
const marker = "var TRANSLATIONS = ";
const m = code.indexOf(marker);
if (m < 0) process.exit(2);
const start = code.indexOf("{", m);
let depth = 0;
let i = start;
for (; i < code.length; i++) {
  if (code[i] === "{") depth++;
  else if (code[i] === "}") {
    depth--;
    if (depth === 0) break;
  }
}
const TRANSLATIONS = Function("return " + code.slice(start, i + 1))();
const out = {};
for (const lang of langs) {
  if (TRANSLATIONS[lang]) out[lang] = TRANSLATIONS[lang];
}
process.stdout.write(JSON.stringify(out));
