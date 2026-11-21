# Changelog

## [0.3.0](https://github.com/Atiumtea/hyproled/compare/v0.2.0...v0.3.0) (2026-11-21)


### Features

* add atomic active-effect stepping ([04a8205](https://github.com/Atiumtea/hyproled/commit/04a820569562d8bd2013273f47bfa6205662d38a))
* add OLED shader state and brightness compensation ([b315018](https://github.com/Atiumtea/hyproled/commit/b315018d2748ec519ee71cd55c90f9e7a295cd5a))
* add Pixel Shift modes ([d48d974](https://github.com/Atiumtea/hyproled/commit/d48d97482c37caa0f0dd75c2552f35cf83e24ded))
* default Pixel Shift to orbit-2x2 ([188a95b](https://github.com/Atiumtea/hyproled/commit/188a95b222fee8d3c72aabf2f758ddafab7bd53e))
* improve CLI and config validation ([e4af9a6](https://github.com/Atiumtea/hyproled/commit/e4af9a620c1e6561825b58f295779f71b9636e52))
* load OLED utility settings from JSON config ([1c9de2c](https://github.com/Atiumtea/hyproled/commit/1c9de2cc0e854e348dd9004462b440a0e061183d))
* **nix:** add installable flake and development shell ([ea215d2](https://github.com/Atiumtea/hyproled/commit/ea215d2654893028ba926ab307e597bdc5059bc6))
* **nix:** add installable flake and development shell ([188efb6](https://github.com/Atiumtea/hyproled/commit/188efb64f208ae8f1562ff4e62481087e5ef72cc))
* optimize Waybar icon generation ([583c3fe](https://github.com/Atiumtea/hyproled/commit/583c3fefcb6ac40db215383248e781decb9e5a84))
* persist hyproled preferences ([9bc7dc8](https://github.com/Atiumtea/hyproled/commit/9bc7dc8ead72f44cc67774e9a650ed28651b513c))
* show Pixel Shift direction in Waybar ([27461ee](https://github.com/Atiumtea/hyproled/commit/27461eed03735b89bf7ddf473ad77a61c3b460ab))


### Bug Fixes

* balance mask and pixel shift cycles ([917a1f2](https://github.com/Atiumtea/hyproled/commit/917a1f20694bc3d5e2e7a9b9f8f60c0d03252361))
* constrain runtime shader cleanup paths ([cd7afa1](https://github.com/Atiumtea/hyproled/commit/cd7afa197a2ccc46df92d5ce2e28311915f8184c))
* correct Lua string delimiter expectations ([2ee233a](https://github.com/Atiumtea/hyproled/commit/2ee233a47d0901840a3ee410050a12cf93466594))
* correct status and full-screen CLI handling ([058cb55](https://github.com/Atiumtea/hyproled/commit/058cb5588192a3965204ad7c3e8f6e1e397d6a28))
* decouple runtime recovery from user config ([1d2ad89](https://github.com/Atiumtea/hyproled/commit/1d2ad89858253aa5b639e9de1ab098495d9c0178))
* enable online CI security audits ([c413ffb](https://github.com/Atiumtea/hyproled/commit/c413ffb9143a395bb0d324842c2c36294dd9f839))
* handle missing git in image metrics ([afe1e74](https://github.com/Atiumtea/hyproled/commit/afe1e74656e7a9ea1a35bb20ae1c84607a6e9238))
* harden Hyprland API detection ([f16b7f4](https://github.com/Atiumtea/hyproled/commit/f16b7f4ebd02cacff93aa255df52f47880223b34))
* honor option terminator in cli ([f3f5a9c](https://github.com/Atiumtea/hyproled/commit/f3f5a9ca6436b12d183200e7d012099733f7579f))
* make brightness restoration crash-safe ([b8d908d](https://github.com/Atiumtea/hyproled/commit/b8d908d54efb703c6abc39cf5aba2a1bcba70835))
* make brightnessctl dependency conditional ([3999c42](https://github.com/Atiumtea/hyproled/commit/3999c422539db5f3d5e5ee8906da9a59afcc4e7b))
* parse Waybar signal registration fields ([4fdd79d](https://github.com/Atiumtea/hyproled/commit/4fdd79d41946e5de0c6f5252f2a6452b41a0674e))
* pass explicit path to state validator ([7646425](https://github.com/Atiumtea/hyproled/commit/7646425fc63ff09124d172d239ce9a27e114cc35))
* preserve effect state flags ([a8920d2](https://github.com/Atiumtea/hyproled/commit/a8920d266dbc012dcfbf08206d888c5bd8056ffd))
* preserve Pixel Shift status normalization ([ae341aa](https://github.com/Atiumtea/hyproled/commit/ae341aae19f3c1ec903e52c0e12934e1f112d347))
* preserve recovery backups on rollback failure ([2b61c45](https://github.com/Atiumtea/hyproled/commit/2b61c45292cad78567c72599ef6409d9c299d56f))
* quote example script arguments ([38247ca](https://github.com/Atiumtea/hyproled/commit/38247ca0c47535cfc61d563a98dbf9b8b8b0e5cc))
* quote shader paths in Lua config updates ([bdf1bf8](https://github.com/Atiumtea/hyproled/commit/bdf1bf8501480e2d6a524bb53ae8da92f45195bf))
* refine Waybar icon visuals ([f7f2837](https://github.com/Atiumtea/hyproled/commit/f7f28375172a489a71cbd61ab52a0681a96159d5))
* reject duplicate scalar cli options ([2062544](https://github.com/Atiumtea/hyproled/commit/2062544b205c5b2e775bfd28c10d0fd31bb2aa6f))
* repair Waybar status direction reporting ([02ed8b3](https://github.com/Atiumtea/hyproled/commit/02ed8b3571b37e4ef36c1d8e70867fafdffa26f4))
* restore development validation tools ([3f69cb4](https://github.com/Atiumtea/hyproled/commit/3f69cb4b479805fcc3efeac603e3331c8d8df45f))
* restore hyproled executable mode ([a6fc8d0](https://github.com/Atiumtea/hyproled/commit/a6fc8d06bb384f59e050ae92efe5526190fb36f9))
* use Nix-compatible shebangs in test mocks ([4e04bfb](https://github.com/Atiumtea/hyproled/commit/4e04bfbda9825982848330d163990734746b75c8))
* use semantic GTK palettes for status icons ([559e06b](https://github.com/Atiumtea/hyproled/commit/559e06b3617d8e83d0a1752be21d61c8544f80b3))
* validate Pixel Shift configuration ([254feb8](https://github.com/Atiumtea/hyproled/commit/254feb84ddc50f526bfa4bbfd3aafdc6aac6798b))
* validate runtime mask phase ([c881cd0](https://github.com/Atiumtea/hyproled/commit/c881cd0e4a516c2e6443e670be9a9ab3e7206b8c))
* validate runtime state and preferences ([0a7ff38](https://github.com/Atiumtea/hyproled/commit/0a7ff380248bcf8918fc1be199f75dea7fe96f8d))
