import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_SIGNATURE = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);
const MAX_BYTES = 1048576;

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const dest = join(outDir, "entry.png");

let bytes: Buffer;
try {
  bytes = readFileSync(src);
} catch (err) {
  console.error(`error: cannot read entry.png beside main.ts: ${src}`);
  process.exit(1);
}

if (bytes.length > MAX_BYTES) {
  console.error(
    `error: entry.png is ${bytes.length} bytes, over the 1048576 byte limit`,
  );
  process.exit(1);
}

if (!bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
  console.error("error: entry.png does not start with the PNG signature");
  process.exit(1);
}

// IHDR must be the first chunk: after the 8-byte signature, a 4-byte
// length (13), "IHDR", then width/height as big-endian uint32 at
// offsets 16 and 20.
if (bytes.length < 33) {
  console.error(
    `error: entry.png is only ${bytes.length} bytes, too short for an IHDR chunk`,
  );
  process.exit(1);
}
if (bytes.readUInt32BE(8) !== 13 ||
    bytes.subarray(12, 16).toString("ascii") !== "IHDR") {
  console.error("error: entry.png has no IHDR chunk where one is expected");
  process.exit(1);
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  console.error(
    `error: entry.png is ${width}x${height}, over the 1024x1024 limit`,
  );
  process.exit(1);
}
if (width === 0 || height === 0) {
  console.error("error: entry.png has a zero width or height in IHDR");
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
writeFileSync(dest, bytes);
console.log(`wrote ${dest} (${bytes.length} bytes)`);
