// 测试入口：编译并运行认证及学生、教师客户端功能测试。
// Reuse Vite's installed esbuild and Vue compiler. No dependency installation,
// server, database, browser storage or generated test bundle is required.
import { createRequire } from 'node:module'
import Module from 'node:module'
import { readFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const testDir = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(testDir, '..')
const require = createRequire(path.join(root, 'package.json'))
const { build } = createRequire(require.resolve('vite'))('esbuild')
const { parse, compileScript } = require('vue/compiler-sfc')
const fixture = path.join(testDir, 'auth-fixtures.mjs')
const result = await build({
  entryPoints: [path.join(testDir, 'auth.test.mjs')],
  bundle: true,
  write: false,
  platform: 'node',
  format: 'cjs',
  packages: 'external',
  loader: { '.webp': 'dataurl' },
  plugins: [
    {
      name: 'auth-test-boundaries',
      setup(builder) {
        builder.onResolve(
          { filter: /^(?:@\/utils|@\/store|@\/router|@\/router\/routes|vue-i18n)$/ },
          () => ({
            path: fixture,
          })
        )
        builder.onResolve({ filter: /^@\// }, (args) => {
          const full = path.join(root, 'src', args.path.slice(2))
          return {
            path: existsSync(full + '.js')
              ? full + '.js'
              : path.extname(full)
              ? full
              : path.join(full, 'index.js'),
          }
        })
        builder.onLoad({ filter: /\.vue$/ }, async (args) => {
          if (
            !/[\\/]views[\\/](login|register|profile|student[\\/](classroom|history)|teacher[\\/](classroom|classroom-detail))[\\/]index.vue$/.test(
              args.path
            )
          ) {
            return { contents: 'export default {}', loader: 'js' }
          }
          const { descriptor } = parse(await readFile(args.path, 'utf8'))
          return {
            contents:
              "import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue';\n" +
              "import { useRouter, useRoute } from '" +
              fixture.replaceAll('\\', '/') +
              "';\n" +
              compileScript(descriptor, { id: args.path }).content,
            loader: 'js',
          }
        })
      },
    },
  ],
})
const compiled = new Module(path.join(testDir, 'auth-tests.cjs'))
compiled.filename = path.join(testDir, 'auth-tests.cjs')
compiled.paths = Module._nodeModulePaths(testDir)
compiled._compile(result.outputFiles[0].text, compiled.filename)
