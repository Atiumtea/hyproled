# Changelog

## [0.4.0](https://github.com/Atiumtea/hyproled/compare/v0.3.0...v0.4.0) (2026-11-22)

### Features

* add Pixel Shift modes and orbit-2x2 default ([d48d974](https://github.com/Atiumtea/hyproled/commit/d48d97482c37caa0f0dd75c2552f35cf83e24ded), [188a95b](https://github.com/Atiumtea/hyproled/commit/188a95b222fee8d3c72aabf2f758ddafab7bd53e))
* persist preferences and add atomic active-effect stepping ([9bc7dc8](https://github.com/Atiumtea/hyproled/commit/9bc7dc8ead72f44cc67774e9a650ed28651b513c), [04a8205](https://github.com/Atiumtea/hyproled/commit/04a820569562d8bd2013273f47bfa6205662d38a))
* show Pixel Shift direction in Waybar and optimize status icons ([27461ee](https://github.com/Atiumtea/hyproled/commit/27461eed03735b89bf7ddf473ad77a61c3b460ab), [583c3fe](https://github.com/Atiumtea/hyproled/commit/583c3fefcb6ac40db215383248e781decb9e5a84))
* improve CLI and configuration validation ([e4af9a6](https://github.com/Atiumtea/hyproled/commit/e4af9a620c1e6561825b58f295779f71b9636e52))
* provide an installable Nix flake, development shell and package metadata ([ea215d2](https://github.com/Atiumtea/hyproled/commit/ea215d2654893028ba926ab307e597bdc5059bc6), [e5d35c2](https://github.com/Atiumtea/hyproled/commit/e5d35c24fd7c3b06ffe73ea092d120ed41bfb157))

### Bug Fixes

* preserve independent Mask and Pixel Shift state and balance their cycles ([a8920d2](https://github.com/Atiumtea/hyproled/commit/a8920d266dbc012dcfbf08206d888c5bd8056ffd), [917a1f2](https://github.com/Atiumtea/hyproled/commit/917a1f20694bc3d5e2e7a9b9f8f60c0d03252361))
* harden runtime state, preferences and Pixel Shift validation; constrain shader cleanup ([0a7ff38](https://github.com/Atiumtea/hyproled/commit/0a7ff380248bcf8918fc1be199f75dea7fe96f8d), [254feb8](https://github.com/Atiumtea/hyproled/commit/254feb84ddc50f526bfa4bbfd3aafdc6aac6798b), [c881cd0](https://github.com/Atiumtea/hyproled/commit/c881cd0e4a516c2e6443e670be9a9ab3e7206b8c), [cd7afa1](https://github.com/Atiumtea/hyproled/commit/cd7afa197a2ccc46df92d5ce2e28311915f8184c), [7646425](https://github.com/Atiumtea/hyproled/commit/7646425fc63ff09124d172d239ce9a27e114cc35))
* make recovery and brightness restoration crash-safe, including rollback failure handling ([1d2ad89](https://github.com/Atiumtea/hyproled/commit/1d2ad89858253aa5b639e9de1ab098495d9c0178), [2b61c45](https://github.com/Atiumtea/hyproled/commit/2b61c45292cad78567c72599ef6409d9c299d56f), [b8d908d](https://github.com/Atiumtea/hyproled/commit/b8d908d54efb703c6abc39cf5aba2a1bcba70835))
* correct CLI parsing, status handling and Hyprland API detection ([058cb55](https://github.com/Atiumtea/hyproled/commit/058cb5588192a3965204ad7c3e8f6e1e397d6a28), [f3f5a9c](https://github.com/Atiumtea/hyproled/commit/f3f5a9ca6436b12d183200e7d012099733f7579f), [2062544](https://github.com/Atiumtea/hyproled/commit/2062544b205c5b2e775bfd28c10d0fd31bb2aa6f), [f16b7f4](https://github.com/Atiumtea/hyproled/commit/f16b7f4ebd02cacff93aa255df52f47880223b34))
* fix Waybar direction reporting and icon rendering ([02ed8b3](https://github.com/Atiumtea/hyproled/commit/02ed8b3571b37e4ef36c1d8e70867fafdffa26f4), [f7f2837](https://github.com/Atiumtea/hyproled/commit/f7f28375172a489a71cbd61ab52a0681a96159d5))
* fix Lua configuration quoting, Nix test shebangs and conditional brightnessctl dependency ([bdf1bf8](https://github.com/Atiumtea/hyproled/commit/bdf1bf8501480e2d6a524bb53ae8da92f45195bf), [2ee233a](https://github.com/Atiumtea/hyproled/commit/2ee233a47d0901840a3ee410050a12cf93466594), [4e04bfb](https://github.com/Atiumtea/hyproled/commit/4e04bfbda9825982848330d163990734746b75c8), [3999c42](https://github.com/Atiumtea/hyproled/commit/3999c422539db5f3d5e5ee8906da9a59afcc4e7b))
* handle missing Git in image metrics and restore executable mode ([afe1e74](https://github.com/Atiumtea/hyproled/commit/afe1e74656e7a9ea1a35bb20ae1c84607a6e9238), [a6fc8d0](https://github.com/Atiumtea/hyproled/commit/a6fc8d06bb384f59e050ae92efe5526190fb36f9))
* preserve Pixel Shift status normalization and quote example arguments ([ae341aa](https://github.com/Atiumtea/hyproled/commit/ae341aae19f3c1ec903e52c0e12934e1f112d347), [38247ca](https://github.com/Atiumtea/hyproled/commit/38247ca0c47535cfc61d563a98dbf9b8b8b0e5cc))

### Maintenance

* add multi-architecture CI, static analysis and workflow security audits ([98af0c3](https://github.com/Atiumtea/hyproled/commit/98af0c3ad07fb365aa74c649569c76035e0a3c72), [cf53b00](https://github.com/Atiumtea/hyproled/commit/cf53b00549e7bbab1b3733b64f6a52fe7955b80c), [c413ffb](https://github.com/Atiumtea/hyproled/commit/c413ffb9143a395bb0d324842c2c36294dd9f839))
* expand regression tests for OLED exposure, configuration, state, brightness and filesystem failures ([252862c](https://github.com/Atiumtea/hyproled/commit/252862c5f8fd78cd630e4db631374b5c7eaaf969), [4097cc4](https://github.com/Atiumtea/hyproled/commit/4097cc439366b074cb598195a09e3539fd664ad2), [471e5cd](https://github.com/Atiumtea/hyproled/commit/471e5cd8cbc2b8da09c36485e9076844c73589b8), [efdf6fa](https://github.com/Atiumtea/hyproled/commit/efdf6faf5bfadee7b9ae574a1deea10c13df024d), [4bdcc5e](https://github.com/Atiumtea/hyproled/commit/4bdcc5e80b9e92187acd6d9d95f7700cecfd53de), [c63901f](https://github.com/Atiumtea/hyproled/commit/c63901ffce3c9937b8422c2fc6774e2e715f423d), [2b9006d](https://github.com/Atiumtea/hyproled/commit/2b9006d464f466fdd1ffbbb32b37e8b94b295075))
* document known issues and remove legacy runtime state formats ([bce57ee](https://github.com/Atiumtea/hyproled/commit/bce57ee389ed555ec958d8df3b1b907aeb7e9c11), [1cdf35c](https://github.com/Atiumtea/hyproled/commit/1cdf35c33fbad79067f2b044c535b07ac8b662d8), [f857138](https://github.com/Atiumtea/hyproled/commit/f8571387cddc46083f46a8dfd430d8df837a7b29))

## [0.3.0](https://github.com/Atiumtea/hyproled/compare/v0.2.0...v0.3.0) (2026-11-21)

### Features

* add OLED shader state and brightness compensation ([b315018](https://github.com/Atiumtea/hyproled/commit/b315018d2748ec519ee71cd55c90f9e7a295cd5a))
* load OLED utility settings from JSON config ([1c9de2c](https://github.com/Atiumtea/hyproled/commit/1c9de2cc0e854e348dd9004462b440a0e061183d))
* add Waybar status interface and notifications ([b5958e2](https://github.com/Atiumtea/hyproled/commit/b5958e2a575b5e375fe3d9cfc1b125aaf33cf0bd))
* add generated Waybar status icons ([662eec5](https://github.com/Atiumtea/hyproled/commit/662eec5963742dbaafdaffce874000c088b4a16d))

### Bug Fixes

* use semantic GTK palettes for status icons ([559e06b](https://github.com/Atiumtea/hyproled/commit/559e06b3617d8e83d0a1752be21d61c8544f80b3))
* parse Waybar signal registration fields ([4fdd79d](https://github.com/Atiumtea/hyproled/commit/4fdd79d41946e5de0c6f5252f2a6452b41a0674e))

### Maintenance

* ignore Python bytecode cache ([4c072fe](https://github.com/Atiumtea/hyproled/commit/4c072feac687313990cd9b17ef2f52f03d7e7564))
