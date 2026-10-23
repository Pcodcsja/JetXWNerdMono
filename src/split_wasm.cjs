// Use the official WASM core to avoid Windows native FFI process crashes.
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const dist = path.resolve(__dirname, '../_tools/node_modules/cn-font-split/dist');
  const { fontSplit } = await import(pathToFileURL(path.join(dist, 'wasm/index.mjs')));
  const wasm = await fs.readFile(path.join(dist, 'libffi-wasm32-wasip1.wasm'));
  const adapter = async (config) => {
    const input = typeof config.input === 'string'
      ? new Uint8Array(await fs.readFile(config.input)) : config.input;
    const files = await fontSplit(
      { ...config, input, multiThreads: false },
      (imports) => WebAssembly.instantiate(wasm, imports),
      { logger: (message) => console.log(message) }
    );
    await fs.mkdir(config.outDir, { recursive: true });
    for (const file of files) {
      if (file) await fs.writeFile(path.join(config.outDir, file.name), file.data);
    }
  };
  // Keep the package CLI's argument parsing, replacing its native backend.
  const entry = require.resolve(path.join(dist, 'node/index.js'));
  require.cache[entry] = { id: entry, filename: entry, loaded: true, exports: { fontSplit: adapter } };
  require(path.join(dist, 'cli.js'));
})().catch((error) => { console.error(error); process.exitCode = 1; });
