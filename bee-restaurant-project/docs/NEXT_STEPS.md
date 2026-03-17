# Next Steps

## Demo-Ready (v0.1.0 → presentable)

- [ ] **Swap placeholder models** — source 5 food GLBs from Sketchfab (CC-licensed), optimize with `npx @gltf-transform/cli optimize` (target <2MB, 512px textures, <50K triangles), place in `public/models/`
- [ ] **Convert GLB → USDZ** — use Apple's Reality Converter (macOS) for iOS "View in AR" (Layer 2). Place alongside GLBs in `public/models/`
- [ ] **Deploy to Vercel** — `npx vercel --prod`. HTTPS required for camera access
- [ ] **Test on real devices** — Android mid-range (Samsung A / Redmi Note), iPhone (iOS 17+). Verify: swipe carousel, model loading, native AR buttons, in-app browser gate

## Demo-Pitchable (v0.2.0)

- [ ] **Design a demo menu** — printable PDF with high-contrast, feature-rich graphics. Must double as a MindAR image target (asymmetric patterns, no large blank areas, 300+ DPI)
- [ ] **Compile .mind file** — run menu design through [MindAR Image Target Compiler](https://hiukim.github.io/mind-ar-js-doc/tools/compile), save to `public/targets/menu.mind`
- [ ] **Generate QR code** — pointing to deployed Vercel URL. Error correction level H, min 2cm physical size
- [ ] **Record demo video** — screen capture of full flow on a real phone (QR scan → loading → 3D viewer → swipe → native AR)
- [ ] **Test MindAR on Android** — verify image tracking with the compiled .mind file and real menu printout

## Production (v1.0.0)

- [ ] **Real food models** — AI pipeline: video capture → Luma AI / Meshy → Blender scale calibration → GLB export → glTF-Transform optimize → USDZ convert
- [ ] **Multi-restaurant support** — route by slug (`/demo-pizza`, `/restaurant-b`), config JSON per restaurant
- [ ] **CDN migration** — move models from `public/` to Cloudflare R2, update menu.json paths with CDN base URL
- [ ] **Analytics** — scan counts, popular items, session duration, device breakdown
- [ ] **Admin dashboard** — restaurant owners manage menu items, upload models, set prices (Vue/React frontend)
- [ ] **Dynamic QR codes** — redirect-based so URLs can change without reprinting menus
- [ ] **MindAR iOS fix** — monitor issue #478, enable Layer 3 on iOS when resolved
