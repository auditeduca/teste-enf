const CACHE_VERSION = "20260803-224413";
const CACHE_NAME = `calculadoras-enfermagem-cache-${CACHE_VERSION}`;

// O SCRIPT DE BUILD VAI INJETAR A LISTA DE ARQUIVOS AQUI
const urlsToCache = [
  '.chrome-perfil-pci/ActorSafetyLists/9.5220.3721/_metadata/verified_contents.json',
  '.chrome-perfil-pci/ActorSafetyLists/9.5220.3721/listdata.json',
  '.chrome-perfil-pci/ActorSafetyLists/9.5220.3721/manifest.json',
  '.chrome-perfil-pci/AmountExtractionHeuristicRegexes/4/_metadata/verified_contents.json',
  '.chrome-perfil-pci/AmountExtractionHeuristicRegexes/4/manifest.json',
  '.chrome-perfil-pci/CertificateRevocation/10686/_metadata/verified_contents.json',
  '.chrome-perfil-pci/CertificateRevocation/10686/manifest.json',
  '.chrome-perfil-pci/Crowd Deny/2026.7.30.63/_metadata/verified_contents.json',
  '.chrome-perfil-pci/Crowd Deny/2026.7.30.63/manifest.json',
  '.chrome-perfil-pci/FileTypePolicies/145.0.7584.0/_metadata/verified_contents.json',
  '.chrome-perfil-pci/FileTypePolicies/145.0.7584.0/manifest.json',
  '.chrome-perfil-pci/MEIPreload/1.1.0.3/_metadata/verified_contents.json',
  '.chrome-perfil-pci/MEIPreload/1.1.0.3/manifest.json',
  '.chrome-perfil-pci/OnDeviceHeadSuggestModel/20251024.824731831.14/_metadata/verified_contents.json',
  '.chrome-perfil-pci/OnDeviceHeadSuggestModel/20251024.824731831.14/manifest.json',
  '.chrome-perfil-pci/OptimizationHints/719/_metadata/verified_contents.json',
  '.chrome-perfil-pci/OptimizationHints/719/manifest.json',
  '.chrome-perfil-pci/PKIMetadata/1733/_metadata/verified_contents.json',
  '.chrome-perfil-pci/PKIMetadata/1733/manifest.json',
  '.chrome-perfil-pci/SODA/1.2.12/_metadata/verified_contents.json',
  '.chrome-perfil-pci/SODA/1.2.12/manifest.json',
  '.chrome-perfil-pci/SODALanguagePacks/en-US/1.5075.0/_metadata/verified_contents.json',
  '.chrome-perfil-pci/SODALanguagePacks/en-US/1.5075.0/manifest.json',
  '.chrome-perfil-pci/SODALanguagePacks/pt-BR/1.3071.0/_metadata/verified_contents.json',
  '.chrome-perfil-pci/SODALanguagePacks/pt-BR/1.3071.0/manifest.json',
  '.chrome-perfil-pci/SSLErrorAssistant/7/_metadata/verified_contents.json',
  '.chrome-perfil-pci/SSLErrorAssistant/7/manifest.json',
  '.chrome-perfil-pci/SafetyTips/3091/_metadata/verified_contents.json',
  '.chrome-perfil-pci/SafetyTips/3091/manifest.json',
  '.chrome-perfil-pci/Subresource Filter/Unindexed Rules/9.70.0/_metadata/verified_contents.json',
  '.chrome-perfil-pci/Subresource Filter/Unindexed Rules/9.70.0/manifest.json',
  '.chrome-perfil-pci/TranslateKit/models/en_es/2024.9.9.1/_metadata/verified_contents.json',
  '.chrome-perfil-pci/TranslateKit/models/en_es/2024.9.9.1/manifest.json',
  '.chrome-perfil-pci/TrustTokenKeyCommitments/2026.3.23.1/_metadata/verified_contents.json',
  '.chrome-perfil-pci/TrustTokenKeyCommitments/2026.3.23.1/keys.json',
  '.chrome-perfil-pci/TrustTokenKeyCommitments/2026.3.23.1/manifest.json',
  '.chrome-perfil-pci/WasmTtsEngine/20260723.1/_metadata/verified_contents.json',
  '.chrome-perfil-pci/WasmTtsEngine/20260723.1/background_compiled.js',
  '.chrome-perfil-pci/WasmTtsEngine/20260723.1/bindings_main.js',
  '.chrome-perfil-pci/WasmTtsEngine/20260723.1/manifest.json',
  '.chrome-perfil-pci/WasmTtsEngine/20260723.1/offscreen_compiled.js',
  '.chrome-perfil-pci/WasmTtsEngine/20260723.1/streaming_worklet_processor.js',
  '.chrome-perfil-pci/WasmTtsEngine/20260723.1/voices.json',
  '.chrome-perfil-pci/WasmTtsEngine/20260723.1/wasm_tts_manifest_v3.json',
  '.chrome-perfil-pci/ZxcvbnData/3/_metadata/verified_contents.json',
  '.chrome-perfil-pci/ZxcvbnData/3/manifest.json',
  '.chrome-perfil-pci/component_crx_cache/metadata.json',
  '.chrome-perfil-pci/extensions_crx_cache/metadata.json',
  '.chrome-perfil-pci/hyphen-data/120.0.6050.0/_metadata/verified_contents.json',
  '.chrome-perfil-pci/hyphen-data/120.0.6050.0/manifest.json',
  '.tradutor_cache/downes_ar.json',
  '.tradutor_cache/downes_de.json',
  '.tradutor_cache/downes_es.json',
  '.tradutor_cache/downes_fr.json',
  '.tradutor_cache/downes_hi.json',
  '.tradutor_cache/downes_id.json',
  '.tradutor_cache/downes_it.json',
  '.tradutor_cache/downes_ja.json',
  '.tradutor_cache/downes_ko.json',
  '.tradutor_cache/downes_nl.json',
  '.tradutor_cache/downes_pl.json',
  '.tradutor_cache/downes_ru.json',
  '.tradutor_cache/downes_sv.json',
  '.tradutor_cache/downes_tr.json',
  '.tradutor_cache/downes_uk.json',
  '.tradutor_cache/downes_vi.json',
  '.tradutor_cache/downes_zh.json',
  '.tradutor_cache/meem_id.json',
  '.tradutor_cache/meem_nl.json',
  '.tradutor_cache/meem_pl.json',
  '.tradutor_cache/meem_sv.json',
  '.tradutor_cache/meem_tr.json',
  '.tradutor_cache/meem_uk.json',
  '.tradutor_cache/meem_vi.json',
  '.tradutor_cache/moca_ar.json',
  '.tradutor_cache/moca_de.json',
  '.tradutor_cache/moca_fr.json',
  '.tradutor_cache/moca_hi.json',
  '.tradutor_cache/moca_id.json',
  '.tradutor_cache/moca_it.json',
  '.tradutor_cache/moca_ja.json',
  '.tradutor_cache/moca_ko.json',
  '.tradutor_cache/moca_nl.json',
  '.tradutor_cache/moca_pl.json',
  '.tradutor_cache/moca_ru.json',
  '.tradutor_cache/moca_sv.json',
  '.tradutor_cache/moca_tr.json',
  '.tradutor_cache/moca_uk.json',
  '.tradutor_cache/moca_vi.json',
  '.tradutor_cache/moca_zh.json',
  '.tradutor_cache/richmond_it.json',
  '.tradutor_cache/silverman_ar.json',
  '.tradutor_cache/silverman_en.json',
  '.tradutor_cache/silverman_es.json',
  '.tradutor_cache/silverman_hi.json',
  '.tradutor_cache/silverman_pl.json',
  '.tradutor_cache/silverman_tr.json',
  '.tradutor_cache/silverman_uk.json',
  '.tradutor_cache/sofa_it.json',
  '.tradutor_cache/sofa_uk.json',
  '.tradutor_cache/tinetti_uk.json',
  '.tradutor_cache/waterlow_ar.json',
  '.tradutor_cache/waterlow_de.json',
  '.tradutor_cache/waterlow_hi.json',
  '.tradutor_cache/waterlow_ja.json',
  '.tradutor_cache/waterlow_ko.json',
  '.tradutor_cache/waterlow_nl.json',
  '.tradutor_cache/waterlow_sv.json',
  '.tradutor_cache/waterlow_uk.json',
  '.vscode/extensions.json',
  '.vscode/settings.json',
  '.vscode/tasks.json',
  '/index.html',
  '/offline.html',
  'analytics-data.json',
  'atualizar-scripts.js',
  'automacoes/banco_nanda_2024_extracted.json',
  'automacoes/banco_nanda_2024_merged_suggestion.json',
  'automacoes/banco_nanda_2024_new_only.json',
  'automacoes/banco_nanda_2024_new_only_clean.json',
  'automacoes/banco_nanda_2024_new_only_clean_updated.json',
  'automacoes/catalogador/catalogador_cache.json',
  'automacoes/extrator_infograficos/cache/0056d773697805b8342670164c1bc8b5d7431218466fe94b36aea707884b5f61.json',
  'automacoes/extrator_infograficos/cache/04b00e7b0327efd81cec3c7ae2728e6318afb4b75ae224f8fac281a6353e65de.json',
  'automacoes/extrator_infograficos/cache/079b76433a0f0e2fbdace2b815bfad674e3737afaa8c0eac36fbcda06e9b213b.json',
  'automacoes/extrator_infograficos/cache/09038f61b956eef9d3efd00776a790499b2df58b48ecac20d10cb3e11cc5d903.json',
  'automacoes/extrator_infograficos/cache/09575aa2e776691d14bd91bbe58393c6bfb0563b3d5f76a8b1ca61fd59d6fed8.json',
  'automacoes/extrator_infograficos/cache/0eba1e514cdae249297b8baa816e770b66f250b3e9973e32910a1fa967376e75.json',
  'automacoes/extrator_infograficos/cache/10650f27eaeb46fb1f98e048c109d2ff04b8f8e525e6f187a7371b2e72eafcca.json',
  'automacoes/extrator_infograficos/cache/114d0f898995c2f472e6443cedfa1d2065bbc2f53b499dedac2624df0dd94346.json',
  'automacoes/extrator_infograficos/cache/118f4d410674373460de80ba8778cc2b970b311355c7ffb32e7c4b063f6ffcf5.json',
  'automacoes/extrator_infograficos/cache/14bd3f9dee8cf084dc2b235ff9009ac6effa3a8f98e853259acad367a2ebba58.json',
  'automacoes/extrator_infograficos/cache/19518a7f1adb26a5b4bc088a72571137f1e7c262c9c572904be3c80d8d4939f3.json',
  'automacoes/extrator_infograficos/cache/1bf16a6151885d997f2641674617efaca72cb3ac2d001f59237e317b9b58cb18.json',
  'automacoes/extrator_infograficos/cache/1e62c40357d7b0ab701d0bb036adc6b2d25749e2bbbdea40ad273d4a0bdf7bf4.json',
  'automacoes/extrator_infograficos/cache/1eb3970442d1b272f8d82d02b25a2b9364dde572f69750103cfb04cf179f6e19.json',
  'automacoes/extrator_infograficos/cache/1ed767ff1a207988557406f959249320e0ab2928fac423c4142b3cabff21de09.json',
  'automacoes/extrator_infograficos/cache/208e11470ade2b876bdd1a4b7c0af8c808eb5e9040870484eaf54088cb7a5fdb.json',
  'automacoes/extrator_infograficos/cache/239807332e8fc7bcaf75b719603dea04a1bb018836ace322c60754e367060bb0.json',
  'automacoes/extrator_infograficos/cache/24af573db271ce6be385c8e784362c4991fcb5597a9b3210df2652ad0e4a2416.json',
  'automacoes/extrator_infograficos/cache/27f552a7c55b89c0236159214fa6367682716389adb07983f6bff873cfa9e249.json',
  'automacoes/extrator_infograficos/cache/2a374ade8857ff94e4c9b92b440821b12dfbec8f1b7dfae963cd93d43ef4ec2f.json',
  'automacoes/extrator_infograficos/cache/2b6269687a7d8ee9ff8d5e42e3a0d6240cba7e1d839f2c50bcd903725f2d882a.json',
  'automacoes/extrator_infograficos/cache/3011bfc480834b7b85514cf62a58c4d9632588bd19c2d3e40dbeb0776ad3bc4f.json',
  'automacoes/extrator_infograficos/cache/31586f50fa4f9b33dedb4c65a4c1f58ab0f77490c6b87d1c2cf41d0be9da2e9a.json',
  'automacoes/extrator_infograficos/cache/34042e14d9fda3f1e683479fe636d95e50ad97129e5190b82b447a6ce6d35462.json',
  'automacoes/extrator_infograficos/cache/34cf2a380b92a255ca962d54a6f97d7ab96ba57f153fcc6c1591d28fc4b45eda.json',
  'automacoes/extrator_infograficos/cache/374a1e19cefadff4e059c6957440890ecb46004aa0b75c6a1e443c75ff375910.json',
  'automacoes/extrator_infograficos/cache/376152d170650bec7a3fc614a9f2e6ce871a9d44dc22ca2072c68e8c3696a1b3.json',
  'automacoes/extrator_infograficos/cache/3bb3ccc3b67e6bdade965a46cdd63b9061d4c4df4e600a1feab23ca7182ec0f0.json',
  'automacoes/extrator_infograficos/cache/3e2363b152481d58f08351ff802be9af5b8cbca3471477b58eb5d426fe66b9bf.json',
  'automacoes/extrator_infograficos/cache/46c2090f43b6a75a8cb690b4edd2a16aec6c756cd5ae8b6f5017f360c7b373cf.json',
  'automacoes/extrator_infograficos/cache/46fc1d9209b2cb10e76457d9b037fb06e0bdacedc365ce4c641a4214a2453cf4.json',
  'automacoes/extrator_infograficos/cache/48f04995709493d6a601df291d951ac5e7d2c88f6310e7656a7bb5c10e40317d.json',
  'automacoes/extrator_infograficos/cache/49e70b5ae575c13c0bc34f2df2153ea3de2c5d7814ed665fb93c17a975d6aef4.json',
  'automacoes/extrator_infograficos/cache/4a51fa24c5a3d14e3e2efb84eea4774d9a969080d56f44ca35d23a39f92d34b5.json',
  'automacoes/extrator_infograficos/cache/4d9bdf6ac2a5f38296c1b9b66eaef4260aaee165e1d3ee1a6db8a7e774b8d4cc.json',
  'automacoes/extrator_infograficos/cache/4fa3872919e6fb23a726c45ae1e21e3931a8ff85b3c5a6e12fffe473aa8b9996.json',
  'automacoes/extrator_infograficos/cache/509c6683eb200727a0eef8a2dfd681ba01fb3967ff9c04c7b0f538858029268b.json',
  'automacoes/extrator_infograficos/cache/52c1c18a81a8eb13b7c09bc023b902ee39ea180358834e7588f54910ecfc3cfa.json',
  'automacoes/extrator_infograficos/cache/555a84bf6d37acd2f007205fe388ddc89e681a549b3142d2b52c960177c96c49.json',
  'automacoes/extrator_infograficos/cache/57111d067ba205f3a19a4be09c3c4c422b71683fad55d89e3450fa998ac3801d.json',
  'automacoes/extrator_infograficos/cache/571f816dce394f0fd88f45bd612ad6ae4e338d8a029b0385022a233fcd3d9655.json',
  'automacoes/extrator_infograficos/cache/577afe52583b6b68ea364f353a190960985b9f94a14fbedaaa14ae83d9b9ed99.json',
  'automacoes/extrator_infograficos/cache/5be66831498fd679382e65f0c71342a91782a6f28d8b1098936d80bd9c13c682.json',
  'automacoes/extrator_infograficos/cache/61beae98cca2e030e5c43805f8086e106559434415b8bb79e12deb09b1d03191.json',
  'automacoes/extrator_infograficos/cache/63712548c6ebb01cc5fdde899ee9c95d7950ffa3191dea46e228c0adbaf748e8.json',
  'automacoes/extrator_infograficos/cache/67d11ee232d85a6dd718c81b3c0a1f2ba7056e188f3daf837b43508ba748f22c.json',
  'automacoes/extrator_infograficos/cache/67f4466b69b0c8f843e0b145e1af106bb2bfea4db80abc47abb16e8ea69d6072.json',
  'automacoes/extrator_infograficos/cache/6c66a3b375bba1edf07525a5d531d075d323aaa310a6a93e34484cd5774ca467.json',
  'automacoes/extrator_infograficos/cache/6caa0029ce3bb0a5d486c81298b794062d0fc8949284954e4a0ef36634c08874.json',
  'automacoes/extrator_infograficos/cache/6ee3df67f3cee71b1bb293bc310ade0bd7d6a0feef6a00f9487eac98db265661.json',
  'automacoes/extrator_infograficos/cache/78387310652549625e36cc6ef4402c3035e9c44df12b54e87bffbd7f50cce331.json',
  'automacoes/extrator_infograficos/cache/7b6e8c8dfe3b00f5b594b6997d0d100c64fc2216908a364903c503652618b78f.json',
  'automacoes/extrator_infograficos/cache/7b71882bf33e7d036cb9012bec36cbfd7df50f55e117c86f8ce39bb0e2274fd1.json',
  'automacoes/extrator_infograficos/cache/7e411dac3749931b4ce53d4bed57a37d09717d8430b78f5d00e008f79f9eca78.json',
  'automacoes/extrator_infograficos/cache/85dfa5c631b0a945e55433d9f2f8ad3c1a9b31e1ed4038623d73525d330cff3e.json',
  'automacoes/extrator_infograficos/cache/8b3264938365812cc2edac8ebf2b467848c8109ec0f60a3d5e8bbe9949c2b01e.json',
  'automacoes/extrator_infograficos/cache/8d265966910f819e9657f80fe336be15ee6d640a73a9a076f5ccbcb48caa15fe.json',
  'automacoes/extrator_infograficos/cache/8f04875fb0346ac70068307c520086282d8d824593d6c74878ade8ada5a16719.json',
  'automacoes/extrator_infograficos/cache/8f5a39c5621846edafcbde4e9e5c62fbb9b182a34fa241901e21e45133227793.json',
  'automacoes/extrator_infograficos/cache/8f73a4ba0089f466fe59dc96b31244f7f9d90d262e170b5d54bec21a069df909.json',
  'automacoes/extrator_infograficos/cache/915d81eafd21acacb751255af15ae0e58b566d8d5782cb7fb2cbd7edb2d81e98.json',
  'automacoes/extrator_infograficos/cache/9524f2ffbb1b709a44f2b4cf2050aa09be9c5fb76f1d970f6fa249edba19bd28.json',
  'automacoes/extrator_infograficos/cache/955ede8f5424b694dfa0cc7c9b694466e25c11c44ed97bd4afee2c3008eb356e.json',
  'automacoes/extrator_infograficos/cache/9739a2d8d3196f595049cacd2c73a6bc89cad63e5b68dc5946c92569e5d53442.json',
  'automacoes/extrator_infograficos/cache/9756160c397641d15a46e0a9a0fa6b8c995afc26ec77abaf045cfaaf8f8f6a02.json',
  'automacoes/extrator_infograficos/cache/99063beff80d2a049f719a5220b7fa774337ab06b6d238d27365209f64b71c17.json',
  'automacoes/extrator_infograficos/cache/a27b1ee17185caa7f8bbc6ef4cfe85fcf9a1a985712b99374f26807b6e30cbbe.json',
  'automacoes/extrator_infograficos/cache/a3226cbca9c6283d1243ec5f002934e3d8e819207312513632f83287c6c44b3d.json',
  'automacoes/extrator_infograficos/cache/a664eefed226fdd22ce443516e4c082cd381203061efcac60ed2ffc746dfc995.json',
  'automacoes/extrator_infograficos/cache/a6b2a32f6d6b8523549fc37e1de9966ceca3145795d01f5f34b1b7fe6cc62b4c.json',
  'automacoes/extrator_infograficos/cache/a6df065e5ea605e47e7af6ce5747dd045130850c28ba2f775c9293cfea129fbd.json',
  'automacoes/extrator_infograficos/cache/a71ae55309c3f3a43ccec02eea395621772e4d39b05ef3b9e84c891bcac66496.json',
  'automacoes/extrator_infograficos/cache/a9499632c043f481b01929aca57b8011c0054ea4e841d6ea90011e2205340e2e.json',
  'automacoes/extrator_infograficos/cache/a9fc73c6fbc6c70e156f4fa361ac28b09b01c30fd96527e93bcbd37be55d87e8.json',
  'automacoes/extrator_infograficos/cache/acf0804bf7374dd810c8412698ba01a5c3b70c12d921470e7642d6e265c3eeb2.json',
  'automacoes/extrator_infograficos/cache/acf60a10b825dfb00b88644ea732fdafdaf0af29dd4973dd74a5a86137f6f5ea.json',
  'automacoes/extrator_infograficos/cache/ad1562ef5bff29f0e17082a3162c8029c2bc85091e1fdb84d78c930fca380d93.json',
  'automacoes/extrator_infograficos/cache/ae7caeb03161dfa3b336567bc63c56e7717f7e54c056e1889d3ad97018a29b79.json',
  'automacoes/extrator_infograficos/cache/aebecd208d127449f0ceabbe3cbbae9bb5b520abdce0e3b51464363db25e6166.json',
  'automacoes/extrator_infograficos/cache/aede36741460097373aea15c48305bee04be1e2c66b9947727153879cdca57d4.json',
  'automacoes/extrator_infograficos/cache/b06c62c41dd923a8614a13f18aa2c06a7eee88a5d1b8738ace5340f20bbd33ee.json',
  'automacoes/extrator_infograficos/cache/b1b2f43e133cc6934f58cbf9786a6e67ee39ece5b9934f674da1db0f36f322dc.json',
  'automacoes/extrator_infograficos/cache/b47d6172c07c4151e31dcfa626a79a9deb734d2ea1c38d5c9ad8f00fd8e6009a.json',
  'automacoes/extrator_infograficos/cache/b4d1c908af10f508802e13800e188d097007914e39ce59673c58fc2f9137bae2.json',
  'automacoes/extrator_infograficos/cache/bab9560568cab56e3c103ea27f548a9c31e57e6bcbaed7a1002a91202136a0e2.json',
  'automacoes/extrator_infograficos/cache/bbd9934f5004d202414c3b84414c13199f32520d882cbbbae404e7add6e0d219.json',
  'automacoes/extrator_infograficos/cache/bc63977d01fe154cd91bcd85c12108791030a1107f0bbeb533eed2a51be50526.json',
  'automacoes/extrator_infograficos/cache/bca1b11b29cd58caf4e18b2820f6c0eafb5e61af0c0d1ecccbf5ba38468a696f.json',
  'automacoes/extrator_infograficos/cache/bed6e59492367513f7fc7d3f583b874be73419f062249a7335643afba38fc50e.json',
  'automacoes/extrator_infograficos/cache/c01916a26fe49fc57b942798f7010369ef9bc9c82fe3d14978c929e7b84911ae.json',
  'automacoes/extrator_infograficos/cache/c0ecf9afe65afd6c60a6c551ed4ac935e384709a98bbc184135db746c35b9b65.json',
  'automacoes/extrator_infograficos/cache/c3053b381ac99035f05bd95f92d83b40b5cf0666cd5ad0a7988a43dc3ff08845.json',
  'automacoes/extrator_infograficos/cache/c54324a2fe32ebf84fad3e8a20d17700252d34afe9eadca6436d0e240234e44e.json',
  'automacoes/extrator_infograficos/cache/c6ad53f59b2e15e60553e70bfc3ee631b0d413a7cd36a5c62890fb6e414a7014.json',
  'automacoes/extrator_infograficos/cache/cabc5812f39016bb3d594fe11a7e4b3b9ee174c44b12b7ace95c470509ac2904.json',
  'automacoes/extrator_infograficos/cache/d0625d7ab371f14834bbfe79196119a8b3f76d5ba298dabce01e221b046199c5.json',
  'automacoes/extrator_infograficos/cache/d508781cabf9134d87309254faa7f8a2369b87fef6e14d677934dabbfe87a904.json',
  'automacoes/extrator_infograficos/cache/d51ed06d19ca108edad01beaf0182c6dbe69d582f2d7a18292fc1d4e874af4a9.json',
  'automacoes/extrator_infograficos/cache/d75618bdda5bb43dfea9ca2cf2e927aeb2d5e18b8e6930717b94a72b3e2576e5.json',
  'automacoes/extrator_infograficos/cache/d7ebfa5f308e532e1b411a447cab8e2d8df0ec7c27d773a090cbbfc028a08a61.json',
  'automacoes/extrator_infograficos/cache/daa4a2d14b67fa3bce014eb4e57ebc4594c654932ced02a35a8c2d11158cdf94.json',
  'automacoes/extrator_infograficos/cache/dc812c7fc34d1afe0852b880cde28a3065477eb8f0995359c09fec3765835a7f.json',
  'automacoes/extrator_infograficos/cache/dd1c4a0e58e3cb0c6ae3e2df910510fadd217758a57e78c447bc9096f10c0b0b.json',
  'automacoes/extrator_infograficos/cache/ddd3d6fa5f25a7838f43d842af20154409098c1f81102edb5c310fb0c1558765.json',
  'automacoes/extrator_infograficos/cache/df05a1ae02da133e36ab7ab4d8c4971356873eed789a7b5665d79e32d15028b8.json',
  'automacoes/extrator_infograficos/cache/df4915185e8f68ed54c49b80845a302da85f5d5a8351ea10f5a0773edaf04f5d.json',
  'automacoes/extrator_infograficos/cache/e13c164d508cba4ea4d0524c9e829872378b9987310fead49b406568d67e5756.json',
  'automacoes/extrator_infograficos/cache/e222320adc0c7aaf9ccc73c018ed147c079171c622985fa14e1ea878ce6e0ac2.json',
  'automacoes/extrator_infograficos/cache/ebff153f7994d15f726eab7b59fea80a408e00dc086d8a0f01d97bcc0cfe23bc.json',
  'automacoes/extrator_infograficos/cache/ece91a24d5a2dadef9d92321d889eb9f519c9cadf3454eba232f30a334a82668.json',
  'automacoes/extrator_infograficos/cache/ee18a195a28311c7c712910a4f1fcb96ea8e59d49dd685e999585728caa8197d.json',
  'automacoes/extrator_infograficos/cache/f021def1a2e1d3d7c5930888fdcd2b90c2579c4762d0c8a8ad24a2afcd9dca6a.json',
  'automacoes/extrator_infograficos/cache/f5fca5a0a742c0c0c650ca8b68b1f45b6d3953ef4068fb82a85eae8ef54c694c.json',
  'automacoes/extrator_infograficos/cache/fa3dff6163b6cb1b5a4c5ba8233c463ccd4570ffd70869e670a2a405ef4cca81.json',
  'automacoes/extrator_infograficos/cache/fabcb79dd8308281cab951b974d1fa9ae66c32e02428264f5a12d692d6447441.json',
  'automacoes/extrator_infograficos/cache/fb5fb5b2744aeb1073d5f8166510dbb3d296e6424ba66d1b5357dcd03b5faab0.json',
  'automacoes/extrator_infograficos/cache/fba5a961f37c43abc47ee3cbcfedab0637ee25f0ed4876ecaed30b5b315c0cab.json',
  'automacoes/extrator_infograficos/cache/fbcc7354ebb1307d29bfea18377c0550ecb4809ceda17151c2305e4c00001921.json',
  'automacoes/extrator_infograficos/saida/layout.json',
  'automacoes/extrator_infograficos/saida/manifest.json',
  'automacoes/svg_cache.json',
  'automation-guard.js',
  'automatizador-em-massa.js',
  'banco_nanda.json',
  'banco_nanda.json.bak-20260704T061029.json',
  'banco_nanda_en.json',
  'banco_nanda_es.json',
  'banco_nic_completo.json',
  'banco_nic_en.json',
  'banco_strings_js.json',
  'biblioteca-automation.js',
  'biblioteca-provas.json',
  'biblioteca.json',
  'build-biblioteca.js',
  'build-downloads.js',
  'build-fale.js',
  'build-nanda.js',
  'build-pdf_provas_de_concursos.js',
  'build.js',
  'ce-calculadora-padrao.js',
  'convert-webp.js',
  'corrigir-badges.js',
  'css-duplicates-report.json',
  'de/favicon.ico',
  'docs/manifesto.json',
  'en/favicon.ico',
  'es/favicon.ico',
  'extrator-hospitais.js',
  'favicon.ico',
  'fetch-analytics.js',
  'fonts/arabic/arabic-700.woff2',
  'fonts/arabic/arabic-regular.woff2',
  'fonts/chinese/chinese-700.woff2',
  'fonts/chinese/chinese-regular.woff2',
  'fonts/devanagari/devanagari-700.woff2',
  'fonts/devanagari/devanagari-regular.woff2',
  'fonts/inter/inter-600.woff2',
  'fonts/inter/inter-700.woff2',
  'fonts/inter/inter-900.woff2',
  'fonts/inter/inter-regular.woff2',
  'fonts/japanese/japanese-700.woff2',
  'fonts/japanese/japanese-regular.woff2',
  'fonts/korean/korean-700.woff2',
  'fonts/korean/korean-regular.woff2',
  'fonts/nunito/nunito-700.woff2',
  'fonts/nunito/nunito-900.woff2',
  'fonts/nunito/nunito-regular.woff2',
  'force-clear-capas.js',
  'force-fix-lang-bar.js',
  'fr/favicon.ico',
  'ga-credentials.json',
  'generate-sitemap.js',
  'gerarCapasPDF.js',
  'gerarCapasVideo.js',
  'global-scripts.js',
  'global-styles.css',
  'glossary-search.js',
  'hi/favicon.ico',
  'hospitais.json',
  'id/favicon.ico',
  'img/education-svgrepo-com.svg',
  'it/favicon.ico',
  'ja/favicon.ico',
  'js/accessibility.js',
  'js/backToTop.js',
  'js/cookies.js',
  'js/main.js',
  'js/menu.js',
  'js/web-vitals-reporter.js',
  'ko/favicon.ico',
  'lang-selector.js',
  'lighthouserc.js',
  'locales/ar/cookies.json',
  'locales/ar/footer.json',
  'locales/bn/cookies.json',
  'locales/bn/footer.json',
  'locales/cs/cookies.json',
  'locales/cs/footer.json',
  'locales/da/cookies.json',
  'locales/da/footer.json',
  'locales/de/cookies.json',
  'locales/de/footer.json',
  'locales/el/cookies.json',
  'locales/el/footer.json',
  'locales/en/cookies.json',
  'locales/en/footer.json',
  'locales/es/cookies.json',
  'locales/es/footer.json',
  'locales/fi/cookies.json',
  'locales/fi/footer.json',
  'locales/fr/cookies.json',
  'locales/fr/footer.json',
  'locales/he/cookies.json',
  'locales/he/footer.json',
  'locales/hi/cookies.json',
  'locales/hi/footer.json',
  'locales/id/cookies.json',
  'locales/id/footer.json',
  'locales/it/cookies.json',
  'locales/it/footer.json',
  'locales/ja/cookies.json',
  'locales/ja/footer.json',
  'locales/ko/cookies.json',
  'locales/ko/footer.json',
  'locales/ms/cookies.json',
  'locales/ms/footer.json',
  'locales/nb/cookies.json',
  'locales/nb/footer.json',
  'locales/nl/cookies.json',
  'locales/nl/footer.json',
  'locales/pl/cookies.json',
  'locales/pl/footer.json',
  'locales/pt/cookies.json',
  'locales/pt/footer.json',
  'locales/ro/cookies.json',
  'locales/ro/footer.json',
  'locales/ru/cookies.json',
  'locales/ru/footer.json',
  'locales/sv/cookies.json',
  'locales/sv/footer.json',
  'locales/th/cookies.json',
  'locales/th/footer.json',
  'locales/tr/cookies.json',
  'locales/tr/footer.json',
  'locales/uk/cookies.json',
  'locales/uk/footer.json',
  'locales/ur/cookies.json',
  'locales/ur/footer.json',
  'locales/vi/cookies.json',
  'locales/vi/footer.json',
  'locales/zh/cookies.json',
  'locales/zh/footer.json',
  'log-imagens.js',
  'main.js',
  'manchester_fluxogramas.json',
  'manifest.json',
  'nl/favicon.ico',
  'otimizador-imagens.js',
  'otimizar-imagens.js',
  'padronizar-largura.js',
  'pl/favicon.ico',
  'public/output.css',
  'relatorio_auditoria_seo.json',
  'relatorio_hreflang.json',
  'relatorios/auditoria-cwv-html.json',
  'relatorios/multiplex-reserva.json',
  'remover-circulo-hero-card.js',
  'ru/favicon.ico',
  'scaffold-lang.js',
  'scan-biblioteca.js',
  'scanner-biblioteca.js',
  'scanner-footer-chain.js',
  'scripts/build-blog.js',
  'scripts/extract-docx.js',
  'scripts/find-css-duplicates.js',
  'scripts/parse-dictionary.js',
  'scripts/parse-glossario.js',
  'scripts/remove-static-glossary.js',
  'simpleRename.js',
  'src/input.css',
  'sv/favicon.ico',
  'terminologias.json',
  'termos_medicos_parsed.json',
  'tr/favicon.ico',
  'uk/favicon.ico',
  'vi/favicon.ico',
  'watch-images.js',
  'watch-pdfs.js',
  'zh/favicon.ico'
];

// 1. EVENTO DE INSTALAÇÃO (Precaching tolerante a falhas)
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then(async (cache) => {
        console.log(
          `[Service Worker] Instalando nova versão: ${CACHE_VERSION}`,
        );

        // Adiciona os ficheiros ao cache 1 a 1.
        // Se um ficheiro faltar, não impede a instalação do resto (fundamental para grandes repositórios)
        await Promise.all(
          urlsToCache
            .filter((url) => !url.startsWith("/*"))
            .map((url) => {
              return cache
                .add(new Request(url, { cache: "reload" }))
                .catch((err) => {
                  console.warn(
                    `[Service Worker] Ficheiro não encontrado para cache: ${url}`,
                  );
                });
            }),
        );
      })
      .then(() => self.skipWaiting()), // Força o SW a assumir o controlo
  );
});

// 2. EVENTO DE ATIVAÇÃO (Limpeza de caches antigos)
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log(
                `[Service Worker] Apagando cache antigo: ${cacheName}`,
              );
              return caches.delete(cacheName);
            }
          }),
        );
      })
      .then(() => self.clients.claim()),
  );
});

// 3. EVENTO DE FETCH (A Mágica da Interceção)
self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Intercepta apenas requisições HTTP/HTTPS normais de GET
  if (!url.protocol.startsWith("http") || req.method !== "GET") return;

  // ESTRATÉGIA EXCEÇÃO: Bloqueadores de Anúncios (Ad Blockers)
  // Evita o erro "Failed to convert value to 'Response'" interceptando as falhas do AdSense
  if (req.url.includes("googlesyndication.com")) {
    event.respondWith(
      fetch(req).catch((error) => {
        // Se a requisição falhar (ex: bloqueada pelo navegador), retorna uma resposta vazia inofensiva
        return new Response(null, { status: 204 });
      }),
    );
    return;
  }

  // ESTRATÉGIA 1: PÁGINAS HTML (Network First -> Cache Fallback -> Offline Fallback)
  if (
    req.mode === "navigate" ||
    req.headers.get("accept").includes("text/html")
  ) {
    // 1. Cria uma URL temporária com o Cache Buster para forçar a rede a entregar o arquivo fresco
    const bypassUrl = new URL(req.url);
    bypassUrl.searchParams.set("v", CACHE_VERSION);

    event.respondWith(
      fetch(bypassUrl)
        .then((networkResponse) => {
          // 2. Salva dinamicamente a página HTML usando a requisição ORIGINAL 'req' como chave
          const responseToCache = networkResponse.clone();
          caches
            .open(CACHE_NAME)
            .then((cache) => cache.put(req, responseToCache));
          return networkResponse;
        })
        .catch(async () => {
          // Se estiver offline, tenta carregar o HTML da versão em cache
          const cachedResponse = await caches.match(req);
          if (cachedResponse) return cachedResponse;

          // Se não tiver no cache, tenta entregar a página offline padrão
          const offlinePage = await caches.match("/offline.html");
          if (offlinePage) return offlinePage;

          // Se até o offline.html falhar (Fallback absoluto para evitar TypeError)
          return new Response(
            "<h1>Sem conexão</h1><p>Você está offline e esta página não foi salva no cache.</p>",
            {
              status: 503,
              headers: { "Content-Type": "text/html; charset=utf-8" },
            },
          );
        }),
    );
    return;
  }

  // ESTRATÉGIA 2: CSS e JS (O "Cache Buster Invisível")
  if (url.pathname.endsWith(".css") || url.pathname.endsWith(".js")) {
    event.respondWith(
      caches.match(req).then((cachedResponse) => {
        // Se estiver no cache ATUAL, entrega imediatamente!
        if (cachedResponse) return cachedResponse;

        // Se NÃO estiver no cache, vai buscar à rede e INJETA O CACHE BUSTER
        const fetchUrl = new URL(req.url);
        fetchUrl.searchParams.set("v", CACHE_VERSION);

        return fetch(fetchUrl)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              const responseToCache = networkResponse.clone();
              caches
                .open(CACHE_NAME)
                .then((cache) => cache.put(req, responseToCache));
            }
            return networkResponse;
          })
          .catch(() => {
            // Em caso de falha de rede e não ter cache (Fallback absoluto)
            return caches
              .match(req)
              .then(
                (res) =>
                  res ||
                  new Response("", { status: 404, statusText: "Not Found" }),
              );
          });
      }),
    );
    return;
  }

  // ESTRATÉGIA 3: IMAGENS E RESTANTES RECURSOS (Stale-While-Revalidate)
  event.respondWith(
    caches.match(req).then((cachedResponse) => {
      const fetchPromise = fetch(req)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches
              .open(CACHE_NAME)
              .then((cache) => cache.put(req, responseToCache));
          }
          return networkResponse;
        })
        .catch(() => {
          // Falha de rede pura (ex: bloqueio de AdBlock ou offline sem cache)
          // Precisamos retornar uma resposta válida vazia para evitar "Failed to convert value to Response"
          return new Response("", {
            status: 408,
            statusText: "Request Timeout",
          });
        });

      return cachedResponse || fetchPromise;
    }),
  );
});