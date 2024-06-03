# Changelog

## [1.16.1](https://github.com/bcgov/nr-forests-access-management/compare/v1.16.0...v1.16.1) (2024-06-03)


### Bug Fixes

* [#1421](https://github.com/bcgov/nr-forests-access-management/issues/1421) Disable adding forest client, and hide delegated admin features ([#1422](https://github.com/bcgov/nr-forests-access-management/issues/1422)) ([57780aa](https://github.com/bcgov/nr-forests-access-management/commit/57780aa953fa13ec677eb5da04324cbd89e8dd5b))

## [1.16.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.15.0...v1.16.0) (2024-05-03)


### Features

* [#1081](https://github.com/bcgov/nr-forests-access-management/issues/1081) grant application admin component test ([#1336](https://github.com/bcgov/nr-forests-access-management/issues/1336)) ([c4b46bc](https://github.com/bcgov/nr-forests-access-management/commit/c4b46bc23c6161b69383da47f28b8487014718c8))
* [#1184](https://github.com/bcgov/nr-forests-access-management/issues/1184) delegated admin filtering same org tests ([#1319](https://github.com/bcgov/nr-forests-access-management/issues/1319)) ([ed6ab53](https://github.com/bcgov/nr-forests-access-management/commit/ed6ab5308dd5eee99e5c9a6b06cdb5a4120c5e40))
* [#1285](https://github.com/bcgov/nr-forests-access-management/issues/1285) pass user guid from frontend, update backend schema ([#1343](https://github.com/bcgov/nr-forests-access-management/issues/1343)) ([7c79c9b](https://github.com/bcgov/nr-forests-access-management/commit/7c79c9b8c897e9f2907627af6b4123caca58165e))


### Bug Fixes

* [#1306](https://github.com/bcgov/nr-forests-access-management/issues/1306) fix description for user type code B ([#1348](https://github.com/bcgov/nr-forests-access-management/issues/1348)) ([135d529](https://github.com/bcgov/nr-forests-access-management/commit/135d529bdebd9e1b5c13c4dd10c919337c114f27))
* [#1338](https://github.com/bcgov/nr-forests-access-management/issues/1338) add log for debugging db session connection ([#1351](https://github.com/bcgov/nr-forests-access-management/issues/1351)) ([0150e48](https://github.com/bcgov/nr-forests-access-management/commit/0150e48a95723fe257d62ccbd508d0c27914e741))


### Miscellaneous

* **deps:** [Snyk] Upgrade @carbon/icons-vue from 10.79.1 to 10.88.0 ([#1339](https://github.com/bcgov/nr-forests-access-management/issues/1339)) ([9522d68](https://github.com/bcgov/nr-forests-access-management/commit/9522d6838ec345082f73e2217f7018b1b02d791d))
* **deps:** [Snyk] Upgrade vue from 3.4.6 to 3.4.21 ([#1341](https://github.com/bcgov/nr-forests-access-management/issues/1341)) ([77aecb1](https://github.com/bcgov/nr-forests-access-management/commit/77aecb19c1eb05b797bb07241c4331ae2478b9b5))

## [1.15.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.14.1...v1.15.0) (2024-04-23)


### Features

* [#1184](https://github.com/bcgov/nr-forests-access-management/issues/1184) delegated admin filtering same org ([#1310](https://github.com/bcgov/nr-forests-access-management/issues/1310)) ([5ca70f8](https://github.com/bcgov/nr-forests-access-management/commit/5ca70f86bd4db7aa471b0be0ff58630a2c08e8a4))
* [#1186](https://github.com/bcgov/nr-forests-access-management/issues/1186) add test for delegated admin granting access ([#1312](https://github.com/bcgov/nr-forests-access-management/issues/1312)) ([6cf4da8](https://github.com/bcgov/nr-forests-access-management/commit/6cf4da80c8432daf751a4fd52e3f7fe6d371fe5f))
* [#1187](https://github.com/bcgov/nr-forests-access-management/issues/1187) add security check for delegated admin remove access ([#1299](https://github.com/bcgov/nr-forests-access-management/issues/1299)) ([d3ae17f](https://github.com/bcgov/nr-forests-access-management/commit/d3ae17fad2730cfc134ad00abd525466deebc228))
* [#1187](https://github.com/bcgov/nr-forests-access-management/issues/1187) add test for security check for delegated admin removing user access ([#1305](https://github.com/bcgov/nr-forests-access-management/issues/1305)) ([3a884ee](https://github.com/bcgov/nr-forests-access-management/commit/3a884ee05cb3800cefc0f6d6d5c8680d83330ba2))
* [#1223](https://github.com/bcgov/nr-forests-access-management/issues/1223) accessibility on fam pages ([#1296](https://github.com/bcgov/nr-forests-access-management/issues/1296)) ([ff99b49](https://github.com/bcgov/nr-forests-access-management/commit/ff99b490be36c8383548f65cbdf05eee2e427bd3))
* [#1239](https://github.com/bcgov/nr-forests-access-management/issues/1239) adding business to bceid references ([#1304](https://github.com/bcgov/nr-forests-access-management/issues/1304)) ([e9a3c7f](https://github.com/bcgov/nr-forests-access-management/commit/e9a3c7f7e0d4b6b8388e2efafc83efd9c1bda272))
* [#985](https://github.com/bcgov/nr-forests-access-management/issues/985) check my own permissions ([#1276](https://github.com/bcgov/nr-forests-access-management/issues/1276)) ([8cddcd0](https://github.com/bcgov/nr-forests-access-management/commit/8cddcd014418e4ab63ddb3b59275c92512d7f96d))
* [#985](https://github.com/bcgov/nr-forests-access-management/issues/985) minor table styling tweaks ([#1308](https://github.com/bcgov/nr-forests-access-management/issues/1308)) ([135c625](https://github.com/bcgov/nr-forests-access-management/commit/135c6257f594ab1a21e54b7011d03787f7e04a37))


### Bug Fixes

* [#1206](https://github.com/bcgov/nr-forests-access-management/issues/1206) [#1207](https://github.com/bcgov/nr-forests-access-management/issues/1207) clean up and add new spar roles ([#1286](https://github.com/bcgov/nr-forests-access-management/issues/1286)) ([ae18515](https://github.com/bcgov/nr-forests-access-management/commit/ae185151fca01c6b146c8efdba6be7f8da84ca37))
* [#1293](https://github.com/bcgov/nr-forests-access-management/issues/1293) fix audit log and add test ([#1295](https://github.com/bcgov/nr-forests-access-management/issues/1295)) ([8df3969](https://github.com/bcgov/nr-forests-access-management/commit/8df39699532e692d964b4bc5bf8a52b2fdc3306e))
* [#1315](https://github.com/bcgov/nr-forests-access-management/issues/1315) fix application name error ([#1316](https://github.com/bcgov/nr-forests-access-management/issues/1316)) ([5f47c4c](https://github.com/bcgov/nr-forests-access-management/commit/5f47c4c20732ed8bf26d632870579b0f45f07401))
* [#1317](https://github.com/bcgov/nr-forests-access-management/issues/1317) fix frontend build type error caused by sidenav ([#1322](https://github.com/bcgov/nr-forests-access-management/issues/1322)) ([e3bc784](https://github.com/bcgov/nr-forests-access-management/commit/e3bc7844ae0fcbc8cf920f3b26e854a6163af2b4))
* 985 frontend pipe line fix ([#1313](https://github.com/bcgov/nr-forests-access-management/issues/1313)) ([b26166e](https://github.com/bcgov/nr-forests-access-management/commit/b26166ef7a9e465fc9759ee792cca719e4860c35))
* adjusting sidenav list for better viewing ([#1317](https://github.com/bcgov/nr-forests-access-management/issues/1317)) ([e9f7ca5](https://github.com/bcgov/nr-forests-access-management/commit/e9f7ca532744c91d6d69fc13b3a3dd6b16257135))
* **ci:** sonarcloud versions ([#1311](https://github.com/bcgov/nr-forests-access-management/issues/1311)) ([21975c4](https://github.com/bcgov/nr-forests-access-management/commit/21975c4eb47b5379db89d3ff90c8a1533b0a1bd9))


### Miscellaneous

* **deps:** [Snyk] Security upgrade vite from 4.5.2 to 4.5.3 ([#1283](https://github.com/bcgov/nr-forests-access-management/issues/1283)) ([2b9a4bc](https://github.com/bcgov/nr-forests-access-management/commit/2b9a4bcc481270c7e7f9bc9c5d3bc3cb0fe8ddbe))
* Update wiki architecture diagram ([#1318](https://github.com/bcgov/nr-forests-access-management/issues/1318)) ([73a5d76](https://github.com/bcgov/nr-forests-access-management/commit/73a5d76b34a3a636c77df1ce06c9535d8eac1d30))

## [1.14.1](https://github.com/bcgov/nr-forests-access-management/compare/v1.14.0...v1.14.1) (2024-04-09)


### Bug Fixes

* bceid login for FOM production login issue ([#1291](https://github.com/bcgov/nr-forests-access-management/issues/1291)) ([5238703](https://github.com/bcgov/nr-forests-access-management/commit/52387038011772c264aad10712e65862ddcb6288))

## [1.14.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.13.0...v1.14.0) (2024-04-08)


### Features

* [#1126](https://github.com/bcgov/nr-forests-access-management/issues/1126) Change button wording ([#1265](https://github.com/bcgov/nr-forests-access-management/issues/1265)) ([e89cfb2](https://github.com/bcgov/nr-forests-access-management/commit/e89cfb20ae7b66d8a807c7c4190fed523e6e6587))
* [#1179](https://github.com/bcgov/nr-forests-access-management/issues/1179) bceid login ([#1225](https://github.com/bcgov/nr-forests-access-management/issues/1225)) ([eb815a0](https://github.com/bcgov/nr-forests-access-management/commit/eb815a097ff011da0dafb1aca12a125f496c3725))
* [#1182](https://github.com/bcgov/nr-forests-access-management/issues/1182) bceid search bceid need check org ([#1269](https://github.com/bcgov/nr-forests-access-management/issues/1269)) ([054810d](https://github.com/bcgov/nr-forests-access-management/commit/054810d4d1ab9960a53e250a093f1989dbc83fea))
* [#1189](https://github.com/bcgov/nr-forests-access-management/issues/1189) Update successful and warning notification when adding or deleting application admin ([#1241](https://github.com/bcgov/nr-forests-access-management/issues/1241)) ([a1cad1b](https://github.com/bcgov/nr-forests-access-management/commit/a1cad1b00f2c9e2dde16fc86ee80adc8c122529f))
* [#1217](https://github.com/bcgov/nr-forests-access-management/issues/1217) backend check both token and access control table for authorization ([#1267](https://github.com/bcgov/nr-forests-access-management/issues/1267)) ([2f6ff98](https://github.com/bcgov/nr-forests-access-management/commit/2f6ff985cccd70680bc3ea7be0c1db35106f5c1e))
* [#1222](https://github.com/bcgov/nr-forests-access-management/issues/1222) store business guid ([#1230](https://github.com/bcgov/nr-forests-access-management/issues/1230)) ([aeabd35](https://github.com/bcgov/nr-forests-access-management/commit/aeabd357d2d7c902a6cbe25c28f36bfdefb653cd))
* [#1264](https://github.com/bcgov/nr-forests-access-management/issues/1264) config prod bcsc ([#1288](https://github.com/bcgov/nr-forests-access-management/issues/1288)) ([d748585](https://github.com/bcgov/nr-forests-access-management/commit/d748585e6f7e43c9c1b7ec220db6376d604b71b0))


### Bug Fixes

* [#1179](https://github.com/bcgov/nr-forests-access-management/issues/1179) bceid login bug fix ([#1255](https://github.com/bcgov/nr-forests-access-management/issues/1255)) ([f6e0dc5](https://github.com/bcgov/nr-forests-access-management/commit/f6e0dc5465beda08d5fdb0730b8c5c2850155b4f))
* [#1191](https://github.com/bcgov/nr-forests-access-management/issues/1191) Confirmation popup has too many white space ([#1268](https://github.com/bcgov/nr-forests-access-management/issues/1268)) ([c863771](https://github.com/bcgov/nr-forests-access-management/commit/c863771788699a8a2fc94fa596c06421fae4202c))
* [#1194](https://github.com/bcgov/nr-forests-access-management/issues/1194) application dropdown should list application in order ([#1252](https://github.com/bcgov/nr-forests-access-management/issues/1252)) ([6dd2266](https://github.com/bcgov/nr-forests-access-management/commit/6dd2266719978e7913de5a18e533e9541e164f33))
* [#1236](https://github.com/bcgov/nr-forests-access-management/issues/1236) update client app name ([#1271](https://github.com/bcgov/nr-forests-access-management/issues/1271)) ([e4e564e](https://github.com/bcgov/nr-forests-access-management/commit/e4e564e29b9179acd670d5504700b7c329f64fe4))
* [#1256](https://github.com/bcgov/nr-forests-access-management/issues/1256) Merge hotfix to add new client role admin ([#1261](https://github.com/bcgov/nr-forests-access-management/issues/1261)) ([dcb5002](https://github.com/bcgov/nr-forests-access-management/commit/dcb500200c638572946cac4d7d2ff2f8097161fc))
* [#1263](https://github.com/bcgov/nr-forests-access-management/issues/1263) Sort role in delegated admin table is not working ([#1278](https://github.com/bcgov/nr-forests-access-management/issues/1278)) ([0c71c89](https://github.com/bcgov/nr-forests-access-management/commit/0c71c897e4cfb10b9ecb80c4dbf09dc931312fef))
* [#1264](https://github.com/bcgov/nr-forests-access-management/issues/1264) disable bceid login button ([#1289](https://github.com/bcgov/nr-forests-access-management/issues/1289)) ([d12757f](https://github.com/bcgov/nr-forests-access-management/commit/d12757f97d291ab853a5edc92755a96dd5089660))
* [#1266](https://github.com/bcgov/nr-forests-access-management/issues/1266) update create_user and update_user length in db ([#1275](https://github.com/bcgov/nr-forests-access-management/issues/1275)) ([8ce7a02](https://github.com/bcgov/nr-forests-access-management/commit/8ce7a02a9b81a427125b2355955cfc019a28db63))
* [#1272](https://github.com/bcgov/nr-forests-access-management/issues/1272) revert read write attribute ([#1279](https://github.com/bcgov/nr-forests-access-management/issues/1279)) ([2a17a4e](https://github.com/bcgov/nr-forests-access-management/commit/2a17a4ee94efb0d79c3f51fa3d9afaea40f40ec3))
* [#1272](https://github.com/bcgov/nr-forests-access-management/issues/1272) try to add username attribute for mapping ([#1277](https://github.com/bcgov/nr-forests-access-management/issues/1277)) ([68ca9b0](https://github.com/bcgov/nr-forests-access-management/commit/68ca9b07737e0f5d2de2785dd0d1722473a58be7))
* fix the table header text for delegated admin ([#1290](https://github.com/bcgov/nr-forests-access-management/issues/1290)) ([b892597](https://github.com/bcgov/nr-forests-access-management/commit/b8925972a093cd334a15107ecf28b176ea419ab5))


### Miscellaneous

* **deps:** replace dependency npm-run-all with npm-run-all2 ^5.0.0 ([#1253](https://github.com/bcgov/nr-forests-access-management/issues/1253)) ([3725c96](https://github.com/bcgov/nr-forests-access-management/commit/3725c96a17b7de6edd2ed10e54d38c11715b1b10))
* **deps:** replace dependency npm-run-all with npm-run-all2 ^5.0.0 ([#1258](https://github.com/bcgov/nr-forests-access-management/issues/1258)) ([672d613](https://github.com/bcgov/nr-forests-access-management/commit/672d613924f3ca1ac4c289baba938854f8018814))
* **deps:** update dependency black to v24 [security] ([#1260](https://github.com/bcgov/nr-forests-access-management/issues/1260)) ([c3d8eea](https://github.com/bcgov/nr-forests-access-management/commit/c3d8eea8863085babe8c572c04669584777cec72))

## [1.13.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.12.0...v1.13.0) (2024-03-19)


### Features

* [#1144](https://github.com/bcgov/nr-forests-access-management/issues/1144) call api after login and cache results ([#1200](https://github.com/bcgov/nr-forests-access-management/issues/1200)) ([88d18e5](https://github.com/bcgov/nr-forests-access-management/commit/88d18e5911a756bf53bce48dbde841d8e7e2f7d6))
* [#1145](https://github.com/bcgov/nr-forests-access-management/issues/1145) use cached access for applications list ([#1209](https://github.com/bcgov/nr-forests-access-management/issues/1209)) ([ac55350](https://github.com/bcgov/nr-forests-access-management/commit/ac55350d17dd380bd60c48ccebe365db07bdbb91))
* [#1147](https://github.com/bcgov/nr-forests-access-management/issues/1147) get list of roles from cache ([#1229](https://github.com/bcgov/nr-forests-access-management/issues/1229)) ([8f18c47](https://github.com/bcgov/nr-forests-access-management/commit/8f18c47b5c144185bcca2c464193e166ff57366a))
* [#1149](https://github.com/bcgov/nr-forests-access-management/issues/1149) delegated admin table screen ([#1211](https://github.com/bcgov/nr-forests-access-management/issues/1211)) ([8d39e2f](https://github.com/bcgov/nr-forests-access-management/commit/8d39e2f32354ed0a3ac6ec348996a09a0468ce57))
* [#1150](https://github.com/bcgov/nr-forests-access-management/issues/1150) navigation to grant delegated admin screen ([#1228](https://github.com/bcgov/nr-forests-access-management/issues/1228)) ([44733c3](https://github.com/bcgov/nr-forests-access-management/commit/44733c36235b92476615d2a228ccfed7abac5d87))
* [#1159](https://github.com/bcgov/nr-forests-access-management/issues/1159) add delegated admin form ([#1212](https://github.com/bcgov/nr-forests-access-management/issues/1212)) ([02395db](https://github.com/bcgov/nr-forests-access-management/commit/02395dbc632afa7e1b9234830db9fb995766b84a))
* [#1160](https://github.com/bcgov/nr-forests-access-management/issues/1160) submit delegated admin form ([#1220](https://github.com/bcgov/nr-forests-access-management/issues/1220)) ([7d7e01d](https://github.com/bcgov/nr-forests-access-management/commit/7d7e01dd13d6f7ab8e289789a5e80b76d28c5f34))
* [#1163](https://github.com/bcgov/nr-forests-access-management/issues/1163) delete delegated admin function ([#1219](https://github.com/bcgov/nr-forests-access-management/issues/1219)) ([469c1e9](https://github.com/bcgov/nr-forests-access-management/commit/469c1e96ba04578840b0fd69e6c3ec839e72a83a))
* [#1180](https://github.com/bcgov/nr-forests-access-management/issues/1180) add backend api to verify bceid ([#1218](https://github.com/bcgov/nr-forests-access-management/issues/1218)) ([e1bc451](https://github.com/bcgov/nr-forests-access-management/commit/e1bc451fb8afa4f6831be6024e0eaa93cc461d4e))


### Bug Fixes

* [#1224](https://github.com/bcgov/nr-forests-access-management/issues/1224) - Delegated Admin Table Disappears On Sign Out ([#1248](https://github.com/bcgov/nr-forests-access-management/issues/1248)) ([ac24c9c](https://github.com/bcgov/nr-forests-access-management/commit/ac24c9c760705de6eb7bbe668779456542126257))
* [#1232](https://github.com/bcgov/nr-forests-access-management/issues/1232) Merge hotfix branch for adding new forest client role ([#1244](https://github.com/bcgov/nr-forests-access-management/issues/1244)) ([57be90f](https://github.com/bcgov/nr-forests-access-management/commit/57be90f3806d654976f3c7e3bbe97449615814ed))
* [#1247](https://github.com/bcgov/nr-forests-access-management/issues/1247) [#1233](https://github.com/bcgov/nr-forests-access-management/issues/1233) Merge hotfix to add new client role, update client redirect urls  ([#1251](https://github.com/bcgov/nr-forests-access-management/issues/1251)) ([9c220ab](https://github.com/bcgov/nr-forests-access-management/commit/9c220abbfbf350efb24e3e1bece9d4592492e379))


### Miscellaneous

* **deps:** update dependency cryptography to v42.0.4 [security] ([#1208](https://github.com/bcgov/nr-forests-access-management/issues/1208)) ([5668013](https://github.com/bcgov/nr-forests-access-management/commit/5668013bb8112802dc146a67d27b700f9e1eb24b))

## [1.12.3](https://github.com/bcgov/nr-forests-access-management/compare/v1.12.2...v1.12.3) (2024-03-20)

### Bug Fixes

* [#1256](https://github.com/bcgov/nr-forests-access-management/issues/1256) add client role admin ([#1257](https://github.com/bcgov/nr-forests-access-management/issues/1257)) ([865ea90](https://github.com/bcgov/nr-forests-access-management/commit/865ea90f3b56ea03865ef339378d16bec9ecffdf))

## [1.12.2](https://github.com/bcgov/nr-forests-access-management/compare/v1.12.1...v1.12.2) (2024-03-18)


### Bug Fixes

* [#1247](https://github.com/bcgov/nr-forests-access-management/issues/1247) [#1233](https://github.com/bcgov/nr-forests-access-management/issues/1233) add new client role, update client redirect urls ([#1249](https://github.com/bcgov/nr-forests-access-management/issues/1249)) ([2a79595](https://github.com/bcgov/nr-forests-access-management/commit/2a79595189e3bf3ccce56fc73218d25c6ec52ec0))

## [1.12.1](https://github.com/bcgov/nr-forests-access-management/compare/v1.12.0...v1.12.1) (2024-03-14)


### Bug Fixes

* [#1232](https://github.com/bcgov/nr-forests-access-management/issues/1232) add flyway script to add a new client role ([#1237](https://github.com/bcgov/nr-forests-access-management/issues/1237)) ([e744380](https://github.com/bcgov/nr-forests-access-management/commit/e744380fe2da4f1282cc82a9ccc4d8c04968965e))

## [1.12.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.11.0...v1.12.0) (2024-02-16)


### Features

* [#1090](https://github.com/bcgov/nr-forests-access-management/issues/1090) delete delegated admin ([#1196](https://github.com/bcgov/nr-forests-access-management/issues/1196)) ([c5dbbee](https://github.com/bcgov/nr-forests-access-management/commit/c5dbbee8e4d57659399053f9e23fa7202499711f))
* [#1174](https://github.com/bcgov/nr-forests-access-management/issues/1174) add tests for get my fam access api ([#1195](https://github.com/bcgov/nr-forests-access-management/issues/1195)) ([914ae89](https://github.com/bcgov/nr-forests-access-management/commit/914ae896ed86c6263bd4ce10c23cbb74b36abc04))


### Bug Fixes

* [#1066](https://github.com/bcgov/nr-forests-access-management/issues/1066) admin segregation cleanup ([#1203](https://github.com/bcgov/nr-forests-access-management/issues/1203)) ([ee9f3e4](https://github.com/bcgov/nr-forests-access-management/commit/ee9f3e4d94e2c32fd93bfde436428d7d51e8e16f))
* [#1197](https://github.com/bcgov/nr-forests-access-management/issues/1197) update terraform IDP config to manual enter endpoints ([#1202](https://github.com/bcgov/nr-forests-access-management/issues/1202)) ([a2ea756](https://github.com/bcgov/nr-forests-access-management/commit/a2ea756e759bfb10a73f748f3f01eee051df483c))


### Miscellaneous

* **deps:** [Snyk] Security upgrade cryptography from 42.0.0 to 42.0.2 ([#1171](https://github.com/bcgov/nr-forests-access-management/issues/1171)) ([9af8e16](https://github.com/bcgov/nr-forests-access-management/commit/9af8e16efe9bf66f36da4a670c82d2a25cd0b1ee))
* **deps:** update dependency fastapi to v0.109.1 [security] ([#1177](https://github.com/bcgov/nr-forests-access-management/issues/1177)) ([02ac2bd](https://github.com/bcgov/nr-forests-access-management/commit/02ac2bd96eb47603ee62e6ee9b62169eaa5044ed))

## [1.11.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.10.0...v1.11.0) (2024-02-09)


### Features

* [#1052](https://github.com/bcgov/nr-forests-access-management/issues/1052) incorporate axios with admin api ([#1067](https://github.com/bcgov/nr-forests-access-management/issues/1067)) ([0b0cc70](https://github.com/bcgov/nr-forests-access-management/commit/0b0cc70760b8ccea948fd66a5f612aa362821251))
* [#1059](https://github.com/bcgov/nr-forests-access-management/issues/1059) application admin management UI ([#1162](https://github.com/bcgov/nr-forests-access-management/issues/1162)) ([05a1124](https://github.com/bcgov/nr-forests-access-management/commit/05a1124baabeb950a141b4632a0f05989fa2e83e))
* [#1082](https://github.com/bcgov/nr-forests-access-management/issues/1082) test for userDomainSelect component ([#1101](https://github.com/bcgov/nr-forests-access-management/issues/1101)) ([a6f830c](https://github.com/bcgov/nr-forests-access-management/commit/a6f830cc1dede36a11327e4787f320b18ca1a1a4))
* [#1083](https://github.com/bcgov/nr-forests-access-management/issues/1083) component testing for usernameInput component  ([#1152](https://github.com/bcgov/nr-forests-access-management/issues/1152)) ([ccca81d](https://github.com/bcgov/nr-forests-access-management/commit/ccca81d278a99c1d6e67e306d2a723a2094636f4))
* [#1085](https://github.com/bcgov/nr-forests-access-management/issues/1085) new access control privilege table ([#1120](https://github.com/bcgov/nr-forests-access-management/issues/1120)) ([15c513d](https://github.com/bcgov/nr-forests-access-management/commit/15c513dc7c2587a848d16a0c629538a9eee387c6))
* [#1086](https://github.com/bcgov/nr-forests-access-management/issues/1086) get delegated admin endpoint ([#1167](https://github.com/bcgov/nr-forests-access-management/issues/1167)) ([5430a54](https://github.com/bcgov/nr-forests-access-management/commit/5430a54f21bcfedc6cebd5c32b204c9636ace0d7))
* [#1089](https://github.com/bcgov/nr-forests-access-management/issues/1089) add post delegated admin endpoint ([#1138](https://github.com/bcgov/nr-forests-access-management/issues/1138)) ([3d34d47](https://github.com/bcgov/nr-forests-access-management/commit/3d34d47474bf469f34ea8338ebe85db57d094cee))
* [#1122](https://github.com/bcgov/nr-forests-access-management/issues/1122) support spar to add dev redirect urls to test ([#1123](https://github.com/bcgov/nr-forests-access-management/issues/1123)) ([7a3968a](https://github.com/bcgov/nr-forests-access-management/commit/7a3968a7e3e7bbc3eabf41654e89484ad5bd5d5a))
* [#1131](https://github.com/bcgov/nr-forests-access-management/issues/1131) add tests ([#1141](https://github.com/bcgov/nr-forests-access-management/issues/1141)) ([7e35a01](https://github.com/bcgov/nr-forests-access-management/commit/7e35a01325cb5654134b84c54e7ae5c73a7e6eee))
* [#1131](https://github.com/bcgov/nr-forests-access-management/issues/1131) additional get admin management endpoints ([#1136](https://github.com/bcgov/nr-forests-access-management/issues/1136)) ([b5694a2](https://github.com/bcgov/nr-forests-access-management/commit/b5694a259c486472893f63deb8adc7586c11227f))
* [#1139](https://github.com/bcgov/nr-forests-access-management/issues/1139) add forest client validator ([#1176](https://github.com/bcgov/nr-forests-access-management/issues/1176)) ([2f02a51](https://github.com/bcgov/nr-forests-access-management/commit/2f02a517aa1ecf52f03d26f55abf7eab9780a26c))
* [#1143](https://github.com/bcgov/nr-forests-access-management/issues/1143) my fam access api ([#1170](https://github.com/bcgov/nr-forests-access-management/issues/1170)) ([9a18497](https://github.com/bcgov/nr-forests-access-management/commit/9a1849779b153952f18be85f7bedcc911ab5c038))
* [#1175](https://github.com/bcgov/nr-forests-access-management/issues/1175) create application admin endpoint to only allow IDIR user ([#1188](https://github.com/bcgov/nr-forests-access-management/issues/1188)) ([dee5998](https://github.com/bcgov/nr-forests-access-management/commit/dee5998e52a2bea4f07fa48ea74c7726a85ff3e4))
* [#850](https://github.com/bcgov/nr-forests-access-management/issues/850) primevue component tab ([#1096](https://github.com/bcgov/nr-forests-access-management/issues/1096)) ([319bf5a](https://github.com/bcgov/nr-forests-access-management/commit/319bf5ac0fb4cba4250337b093ee5625a7d26d0e))
* [#887](https://github.com/bcgov/nr-forests-access-management/issues/887) Implement application admin management UI - manage permission UI ([#1118](https://github.com/bcgov/nr-forests-access-management/issues/1118)) ([7e2a5a6](https://github.com/bcgov/nr-forests-access-management/commit/7e2a5a67e52ccc1a2fe3f9b38cae3267508491a9))
* [#888](https://github.com/bcgov/nr-forests-access-management/issues/888) transfer to admin table ([#1068](https://github.com/bcgov/nr-forests-access-management/issues/1068)) ([fac94f1](https://github.com/bcgov/nr-forests-access-management/commit/fac94f178f202951946449bd7cd2b76812baf1b9))
* [#921](https://github.com/bcgov/nr-forests-access-management/issues/921) add first and last name to user verification identity card ([#1112](https://github.com/bcgov/nr-forests-access-management/issues/1112)) ([4ab1af3](https://github.com/bcgov/nr-forests-access-management/commit/4ab1af35cbaae77091375785d211b761d9b70650))
* [#970](https://github.com/bcgov/nr-forests-access-management/issues/970) add tests for adding forest client number ([#1102](https://github.com/bcgov/nr-forests-access-management/issues/1102)) ([4a2bca0](https://github.com/bcgov/nr-forests-access-management/commit/4a2bca0bc4515583e7b54137ac593d032593c056))


### Bug Fixes

* (frontend) update primevue and custom stylesheet version ([#1107](https://github.com/bcgov/nr-forests-access-management/issues/1107)) ([7c89757](https://github.com/bcgov/nr-forests-access-management/commit/7c89757f065e368a321909e0b32255d4aed02c78))
* [#1069](https://github.com/bcgov/nr-forests-access-management/issues/1069) fix a type error ([#1094](https://github.com/bcgov/nr-forests-access-management/issues/1094)) ([2efac08](https://github.com/bcgov/nr-forests-access-management/commit/2efac081987c22d72fbceda67b222d75138ef3c8))
* [#1076](https://github.com/bcgov/nr-forests-access-management/issues/1076) fetch before navigation ([#1077](https://github.com/bcgov/nr-forests-access-management/issues/1077)) ([b8c0cd8](https://github.com/bcgov/nr-forests-access-management/commit/b8c0cd8575ab2317d48b878899261dd7a05c9ed1))
* [#1087](https://github.com/bcgov/nr-forests-access-management/issues/1087) update return of get app admin api to include user and application information  ([#1099](https://github.com/bcgov/nr-forests-access-management/issues/1099)) ([bfab3da](https://github.com/bcgov/nr-forests-access-management/commit/bfab3da3ef24665b075a9677484dec7e2dcf797b))
* [#1097](https://github.com/bcgov/nr-forests-access-management/issues/1097) add route security ([#1104](https://github.com/bcgov/nr-forests-access-management/issues/1104)) ([c66149a](https://github.com/bcgov/nr-forests-access-management/commit/c66149a7b6f6cfeabd7615acb5980c01f47d4487))
* [#1097](https://github.com/bcgov/nr-forests-access-management/issues/1097) fix import error due to refactoring. ([#1105](https://github.com/bcgov/nr-forests-access-management/issues/1105)) ([cdef600](https://github.com/bcgov/nr-forests-access-management/commit/cdef60072d5f6d9c4067559ceaa56ab3ad97fff0))
* [#1106](https://github.com/bcgov/nr-forests-access-management/issues/1106) bc logo redirect ([#1168](https://github.com/bcgov/nr-forests-access-management/issues/1168)) ([f84bb4f](https://github.com/bcgov/nr-forests-access-management/commit/f84bb4f7f36d5af99d9cd679f4f5a26a6028b585))
* [#1121](https://github.com/bcgov/nr-forests-access-management/issues/1121) breadcrumb component not routing ([#1169](https://github.com/bcgov/nr-forests-access-management/issues/1169)) ([f14c878](https://github.com/bcgov/nr-forests-access-management/commit/f14c8780c7080365299c4f0e21c0deb5d34a448e))
* [#1134](https://github.com/bcgov/nr-forests-access-management/issues/1134) add test logout url for forest client test ([#1156](https://github.com/bcgov/nr-forests-access-management/issues/1156)) ([278c663](https://github.com/bcgov/nr-forests-access-management/commit/278c66325f5d9669c51df0bbf94717ba6dd353d6))
* [#1139](https://github.com/bcgov/nr-forests-access-management/issues/1139) add missing package ([#1193](https://github.com/bcgov/nr-forests-access-management/issues/1193)) ([0ca1e3a](https://github.com/bcgov/nr-forests-access-management/commit/0ca1e3a3270b90958198f90c89c33aeeea802e8a))
* [#888](https://github.com/bcgov/nr-forests-access-management/issues/888) add missing access for auth lambda db user ([#1074](https://github.com/bcgov/nr-forests-access-management/issues/1074)) ([cc8460b](https://github.com/bcgov/nr-forests-access-management/commit/cc8460b8691caf07cd6ffa4ed87d6e08341b1d1f))
* [#888](https://github.com/bcgov/nr-forests-access-management/issues/888) fix auth function when read application admins ([#1075](https://github.com/bcgov/nr-forests-access-management/issues/1075)) ([efbba1c](https://github.com/bcgov/nr-forests-access-management/commit/efbba1c6d398aeb7e4a2a9b893ab4f377b3bb7e2))
* [#921](https://github.com/bcgov/nr-forests-access-management/issues/921) fix user identity card style on mobile ([#1119](https://github.com/bcgov/nr-forests-access-management/issues/1119)) ([c60f28b](https://github.com/bcgov/nr-forests-access-management/commit/c60f28b17953f5b187d3c0e1761d6aec92dbf003))
* [#972](https://github.com/bcgov/nr-forests-access-management/issues/972) axios version upgrade ([#1125](https://github.com/bcgov/nr-forests-access-management/issues/1125)) ([986718b](https://github.com/bcgov/nr-forests-access-management/commit/986718bb5e35b4fd791bf90ee36d2f5f4dd63e9a))
* admin management api minor refactoring ([#1157](https://github.com/bcgov/nr-forests-access-management/issues/1157)) ([7a5d9dd](https://github.com/bcgov/nr-forests-access-management/commit/7a5d9ddcd063641ccebc476f8c0e57fc91a172e4))
* fixing bugs from previous 1059 task ([#1192](https://github.com/bcgov/nr-forests-access-management/issues/1192)) ([bef0ca3](https://github.com/bcgov/nr-forests-access-management/commit/bef0ca3effaf2675cce93b4fe221a38d7f6a34ae))
* fixing wrong import for Session ([#1142](https://github.com/bcgov/nr-forests-access-management/issues/1142)) ([da6a35b](https://github.com/bcgov/nr-forests-access-management/commit/da6a35bfa71efb244eedae506b630727fe407cdf))


### Miscellaneous

* [#1069](https://github.com/bcgov/nr-forests-access-management/issues/1069) refactor the grant access form ([#1080](https://github.com/bcgov/nr-forests-access-management/issues/1080)) ([b7724b5](https://github.com/bcgov/nr-forests-access-management/commit/b7724b5934c3c1e6e38ec2aa5a5c94fb6bac0a02))
* [#1135](https://github.com/bcgov/nr-forests-access-management/issues/1135) update FAM readme for Windows OS workspace setup ([#1137](https://github.com/bcgov/nr-forests-access-management/issues/1137)) ([7e4a962](https://github.com/bcgov/nr-forests-access-management/commit/7e4a962395555fc018ca361106167794d5a3c7e4))
* **deps:** [Snyk] Security upgrade cryptography from 41.0.7 to 42.0.0 ([#1161](https://github.com/bcgov/nr-forests-access-management/issues/1161)) ([a7edaf9](https://github.com/bcgov/nr-forests-access-management/commit/a7edaf9bc9121f92c68bfd7bc578a06494cc26d9))
* **deps:** update all non-major dependencies ([#1064](https://github.com/bcgov/nr-forests-access-management/issues/1064)) ([d12913f](https://github.com/bcgov/nr-forests-access-management/commit/d12913fead9148797ac6165fb9c3cefcf9843bd9))
* **deps:** update dependency cryptography to v41.0.6 [security] ([#1061](https://github.com/bcgov/nr-forests-access-management/issues/1061)) ([d22c289](https://github.com/bcgov/nr-forests-access-management/commit/d22c2893dd950d328e747d9d2ed4fdab050c238e))
* **deps:** update dependency pycryptodome to v3.19.1 [security] ([#1109](https://github.com/bcgov/nr-forests-access-management/issues/1109)) ([8d510c0](https://github.com/bcgov/nr-forests-access-management/commit/8d510c0005620c8bb492e39f67f41a87ff139783))
* Update issue templates ([#1166](https://github.com/bcgov/nr-forests-access-management/issues/1166)) ([d444f32](https://github.com/bcgov/nr-forests-access-management/commit/d444f32a1044702ba8ab37f1647c63eb871c50fa))

## [1.10.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.9.0...v1.10.0) (2023-12-05)


### Features

* [#1007](https://github.com/bcgov/nr-forests-access-management/issues/1007) new fam app admin model ([#1029](https://github.com/bcgov/nr-forests-access-management/issues/1029)) ([f7f341f](https://github.com/bcgov/nr-forests-access-management/commit/f7f341f414b804c50c0413e2ccd2bdbe14bab8cc))
* [#1010](https://github.com/bcgov/nr-forests-access-management/issues/1010) admin api gateway ([#1050](https://github.com/bcgov/nr-forests-access-management/issues/1050)) ([b61aeba](https://github.com/bcgov/nr-forests-access-management/commit/b61aeba18814f967c3986a64deb56cc1e39977b3))
* [#1018](https://github.com/bcgov/nr-forests-access-management/issues/1018) add auth test for bceid and bcsc login ([#1065](https://github.com/bcgov/nr-forests-access-management/issues/1065)) ([8c2a40d](https://github.com/bcgov/nr-forests-access-management/commit/8c2a40daaea098934d6cb24290a8db3df7223903))
* [#1042](https://github.com/bcgov/nr-forests-access-management/issues/1042) new admin api gen ([#1054](https://github.com/bcgov/nr-forests-access-management/issues/1054)) ([477277f](https://github.com/bcgov/nr-forests-access-management/commit/477277f09f82d9242e6ff9a0cc0aa508161e0af9))
* [#1046](https://github.com/bcgov/nr-forests-access-management/issues/1046) add test for admin management endpoints ([#1055](https://github.com/bcgov/nr-forests-access-management/issues/1055)) ([7e39737](https://github.com/bcgov/nr-forests-access-management/commit/7e397373e1165e658414d1ca2646c943e9c1105a))
* [#884](https://github.com/bcgov/nr-forests-access-management/issues/884) add admin management lambda ([#1035](https://github.com/bcgov/nr-forests-access-management/issues/1035)) ([bdc5423](https://github.com/bcgov/nr-forests-access-management/commit/bdc54236ee072be524bbf92876540d6af51bde77))
* [#885](https://github.com/bcgov/nr-forests-access-management/issues/885) add admin management endpoint ([#1049](https://github.com/bcgov/nr-forests-access-management/issues/1049)) ([5b69940](https://github.com/bcgov/nr-forests-access-management/commit/5b699403484e9b627ce692b4411cc6019e065238))


### Bug Fixes

* [#1014](https://github.com/bcgov/nr-forests-access-management/issues/1014) client id input field error validation issues ([#1032](https://github.com/bcgov/nr-forests-access-management/issues/1032)) ([a23acbd](https://github.com/bcgov/nr-forests-access-management/commit/a23acbd28dde91b7c20abfddb842636ae85a4884))
* [#1015](https://github.com/bcgov/nr-forests-access-management/issues/1015) Notification issues when the text is too long ([#1034](https://github.com/bcgov/nr-forests-access-management/issues/1034)) ([a8fbad8](https://github.com/bcgov/nr-forests-access-management/commit/a8fbad8c61c6daa724e0e0f6fe52337874ab37a5))
* [#1044](https://github.com/bcgov/nr-forests-access-management/issues/1044) Better Error Message for Self Granting User Error ([#1053](https://github.com/bcgov/nr-forests-access-management/issues/1053)) ([4c958a7](https://github.com/bcgov/nr-forests-access-management/commit/4c958a78f49a081722912ee531c80654087c37fe))
* [#885](https://github.com/bcgov/nr-forests-access-management/issues/885) fix admin management db username in flyway ([#1051](https://github.com/bcgov/nr-forests-access-management/issues/1051)) ([bb5352c](https://github.com/bcgov/nr-forests-access-management/commit/bb5352c3adf393537e1db0fa7446d8dc0df4219f))
* [#993](https://github.com/bcgov/nr-forests-access-management/issues/993) user name field consistency ([#1043](https://github.com/bcgov/nr-forests-access-management/issues/1043)) ([f0f573d](https://github.com/bcgov/nr-forests-access-management/commit/f0f573db302c4185df16464ca5e9683c48a38c73))
* typing breaking build ([#1058](https://github.com/bcgov/nr-forests-access-management/issues/1058)) ([6f8d3ea](https://github.com/bcgov/nr-forests-access-management/commit/6f8d3ea55d82d61c499682442b6770c81a074205))


### Miscellaneous

* [#1022](https://github.com/bcgov/nr-forests-access-management/issues/1022) refactor frontend code to be consistent ([#1060](https://github.com/bcgov/nr-forests-access-management/issues/1060)) ([88c6796](https://github.com/bcgov/nr-forests-access-management/commit/88c6796921035f601da6ed2fb3b388418b085b4a))
* renovate extends bcgov/renovate-config ([#1045](https://github.com/bcgov/nr-forests-access-management/issues/1045)) ([45ea082](https://github.com/bcgov/nr-forests-access-management/commit/45ea082deffdf2c6adc1884528bcf0fe9ed4dc46))

## [1.9.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.8.2...v1.9.0) (2023-11-07)


### Features

* [#844](https://github.com/bcgov/nr-forests-access-management/issues/844) adjust grant access user page ([#1011](https://github.com/bcgov/nr-forests-access-management/issues/1011)) ([789bbab](https://github.com/bcgov/nr-forests-access-management/commit/789bbab44f8cbbf205e227e91450aadf754ed319))


### Bug Fixes

* [#1020](https://github.com/bcgov/nr-forests-access-management/issues/1020) fix forest client number add error ([#1025](https://github.com/bcgov/nr-forests-access-management/issues/1025)) ([1a8eb3b](https://github.com/bcgov/nr-forests-access-management/commit/1a8eb3b2f90a74c535ee9a303a51738415312480))
* [#1020](https://github.com/bcgov/nr-forests-access-management/issues/1020) fix grant access page role change issue ([#1023](https://github.com/bcgov/nr-forests-access-management/issues/1023)) ([84dbc4b](https://github.com/bcgov/nr-forests-access-management/commit/84dbc4b2cc2d27a151f1a2709121477da154b49a))
* [#984](https://github.com/bcgov/nr-forests-access-management/issues/984) added to return login user email for SPAR ([#1024](https://github.com/bcgov/nr-forests-access-management/issues/1024)) ([b550415](https://github.com/bcgov/nr-forests-access-management/commit/b550415f5761b8de2684f3fd22cf2847aed8a44a))

## [1.8.2](https://github.com/bcgov/nr-forests-access-management/compare/v1.8.1...v1.8.2) (2023-11-06)


### Bug Fixes

* [#1017](https://github.com/bcgov/nr-forests-access-management/issues/1017) audit bcsc ([#1019](https://github.com/bcgov/nr-forests-access-management/issues/1019)) ([35de359](https://github.com/bcgov/nr-forests-access-management/commit/35de359d06c3d60e83df2cb9748321502fd7ae3d))
* [#953](https://github.com/bcgov/nr-forests-access-management/issues/953) paginator default page ([#1009](https://github.com/bcgov/nr-forests-access-management/issues/1009)) ([2a3b4a1](https://github.com/bcgov/nr-forests-access-management/commit/2a3b4a18a63302c30b1b901628936ca14f7b6cec))
* [#995](https://github.com/bcgov/nr-forests-access-management/issues/995) current route on breadcrumb ([#1013](https://github.com/bcgov/nr-forests-access-management/issues/1013)) ([5d616c6](https://github.com/bcgov/nr-forests-access-management/commit/5d616c6d5729a58a1bcae6b29987e40dfb0b8613))
* [#997](https://github.com/bcgov/nr-forests-access-management/issues/997) frontend small fixes ([#1016](https://github.com/bcgov/nr-forests-access-management/issues/1016)) ([70ec2d8](https://github.com/bcgov/nr-forests-access-management/commit/70ec2d8e6d80adcedcbb1000dfe102980582a57a))
* [Snyk] Security upgrade cryptography from 41.0.4 to 41.0.5 ([#998](https://github.com/bcgov/nr-forests-access-management/issues/998)) ([fa6086c](https://github.com/bcgov/nr-forests-access-management/commit/fa6086ca1bc9f32bebfeb0c85280fe6a5ab0b86d))

## [1.8.1](https://github.com/bcgov/nr-forests-access-management/compare/v1.8.0...v1.8.1) (2023-10-26)


### Bug Fixes

* [#999](https://github.com/bcgov/nr-forests-access-management/issues/999) fix the role not render problem on the grant access page ([#1000](https://github.com/bcgov/nr-forests-access-management/issues/1000)) ([28ee71e](https://github.com/bcgov/nr-forests-access-management/commit/28ee71e94728a91a480680e35efe2eec2591b7c5))

## [1.8.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.7.1...v1.8.0) (2023-10-25)


### Features

* [#802](https://github.com/bcgov/nr-forests-access-management/issues/802) aws bastion host terraform ([#892](https://github.com/bcgov/nr-forests-access-management/issues/892)) ([643549e](https://github.com/bcgov/nr-forests-access-management/commit/643549e8f9519a17e0b4bb024a898a994c34ef4f))
* [#842](https://github.com/bcgov/nr-forests-access-management/issues/842) breadcrumb component ([#980](https://github.com/bcgov/nr-forests-access-management/issues/980)) ([8a721cf](https://github.com/bcgov/nr-forests-access-management/commit/8a721cffa9b1441d25ad06d642f059e13dd12d8a))
* [#853](https://github.com/bcgov/nr-forests-access-management/issues/853) forest client number multiple values ([#956](https://github.com/bcgov/nr-forests-access-management/issues/956)) ([cf3cf26](https://github.com/bcgov/nr-forests-access-management/commit/cf3cf26caa9864ef4e11d8937e2cd76027205f27))
* [#896](https://github.com/bcgov/nr-forests-access-management/issues/896) sidenav collapseble for mobile ([#943](https://github.com/bcgov/nr-forests-access-management/issues/943)) ([3678cdf](https://github.com/bcgov/nr-forests-access-management/commit/3678cdf58a90b1f7337bce5ddbcf76a722860a5b))
* [#990](https://github.com/bcgov/nr-forests-access-management/issues/990) added 50 dev urls for each cognito client ([#996](https://github.com/bcgov/nr-forests-access-management/issues/996)) ([1286162](https://github.com/bcgov/nr-forests-access-management/commit/128616290a08e3761ecdaf3f6c18e596ab36dc8b))


### Bug Fixes

* [#365](https://github.com/bcgov/nr-forests-access-management/issues/365) Remove Unused Endponts. ([#968](https://github.com/bcgov/nr-forests-access-management/issues/968)) ([2976dfc](https://github.com/bcgov/nr-forests-access-management/commit/2976dfcf4efad92a20c8a6cb1b2ceebb8d1b2dfb))
* [#952](https://github.com/bcgov/nr-forests-access-management/issues/952) eliminate summary page ([#991](https://github.com/bcgov/nr-forests-access-management/issues/991)) ([c565197](https://github.com/bcgov/nr-forests-access-management/commit/c56519777f0b68ea79620ba6d61b32e2a21f26d4))
* [#987](https://github.com/bcgov/nr-forests-access-management/issues/987) add missing type check router guards ([#992](https://github.com/bcgov/nr-forests-access-management/issues/992)) ([c9c7189](https://github.com/bcgov/nr-forests-access-management/commit/c9c7189a2c6a26e0c4d56cc2a1a92f104a4ff9a2))
* broken frontend build from previous merge ([#989](https://github.com/bcgov/nr-forests-access-management/issues/989)) ([d6d1b1f](https://github.com/bcgov/nr-forests-access-management/commit/d6d1b1f5a0969aba9befbe5a5d7ce4370d98abbf))
* update redirect url for spar as requested ([#977](https://github.com/bcgov/nr-forests-access-management/issues/977)) ([ea0ad6e](https://github.com/bcgov/nr-forests-access-management/commit/ea0ad6e08e78c2dff955ae24a6dbbc46aa733164))


### Miscellaneous

* [#978](https://github.com/bcgov/nr-forests-access-management/issues/978) pydantic sqlalchemy upgrade ([#982](https://github.com/bcgov/nr-forests-access-management/issues/982)) ([d5410db](https://github.com/bcgov/nr-forests-access-management/commit/d5410db0ef00a5032382a1ae1e2018def4fe3ca3))
* **deps:** Bump @babel/traverse from 7.22.1 to 7.23.2 in /frontend ([#979](https://github.com/bcgov/nr-forests-access-management/issues/979)) ([b21477a](https://github.com/bcgov/nr-forests-access-management/commit/b21477a40f883a8b255c99439d0d273ebee98fc8))
* **deps:** update dependency cryptography to v41.0.4 [security] ([#923](https://github.com/bcgov/nr-forests-access-management/issues/923)) ([b0cb28a](https://github.com/bcgov/nr-forests-access-management/commit/b0cb28a9eab8c652c06ae81421db880a9b7cd57c))

## [1.7.1](https://github.com/bcgov/nr-forests-access-management/compare/v1.7.0...v1.7.1) (2023-10-16)


### Bug Fixes

* [#938](https://github.com/bcgov/nr-forests-access-management/issues/938) Remove unnecessary flows from nsgs based on security reviews. ([#960](https://github.com/bcgov/nr-forests-access-management/issues/960)) ([6614d74](https://github.com/bcgov/nr-forests-access-management/commit/6614d74e3e0f3c351df0ec78b162bd9d20d8a1d3))
* incorrect swapped action ([#965](https://github.com/bcgov/nr-forests-access-management/issues/965)) ([1976022](https://github.com/bcgov/nr-forests-access-management/commit/19760228422e2f260651b6cc50583e48476ebfa5))


### Miscellaneous

* swap out unmaintained action ([#961](https://github.com/bcgov/nr-forests-access-management/issues/961)) ([b30fdf9](https://github.com/bcgov/nr-forests-access-management/commit/b30fdf9ad73842bf42cf22082931c8d485d6a456))
* Update actions/upload-artifact action to v3 ([#967](https://github.com/bcgov/nr-forests-access-management/issues/967)) ([9b70fe0](https://github.com/bcgov/nr-forests-access-management/commit/9b70fe091912a66c01f508f71d0a9a7f249a8ac6))
* update checkout action for node 12 deprecation ([#962](https://github.com/bcgov/nr-forests-access-management/issues/962)) ([75894bc](https://github.com/bcgov/nr-forests-access-management/commit/75894bc8d261991ed3739e6c8ae91b8a0198328c))

## [1.7.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.6.0...v1.7.0) (2023-10-10)


### Features

* [#934](https://github.com/bcgov/nr-forests-access-management/issues/934) profile sidebar for mobile ([#946](https://github.com/bcgov/nr-forests-access-management/issues/946)) ([68479fd](https://github.com/bcgov/nr-forests-access-management/commit/68479fd913966b730d569ad12ecfed50da980c88))


### Bug Fixes

* [#722](https://github.com/bcgov/nr-forests-access-management/issues/722) Update terraform CloudFront to use the new certificate ([#947](https://github.com/bcgov/nr-forests-access-management/issues/947)) ([6d60d93](https://github.com/bcgov/nr-forests-access-management/commit/6d60d9385bf545b1effe24e910b04bc7ca3a1288))

## [1.6.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.5.0...v1.6.0) (2023-10-05)


### Features

* [#915](https://github.com/bcgov/nr-forests-access-management/issues/915) tfc s3 migration deployment ([#948](https://github.com/bcgov/nr-forests-access-management/issues/948)) ([e325af6](https://github.com/bcgov/nr-forests-access-management/commit/e325af6c5eabb2cdc32b0fbb412ab7e0cd47cc8d))

## [1.5.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.4.0...v1.5.0) (2023-10-03)


### Features

* [#846](https://github.com/bcgov/nr-forests-access-management/issues/846) user information card new design style ([#913](https://github.com/bcgov/nr-forests-access-management/issues/913)) ([5986c57](https://github.com/bcgov/nr-forests-access-management/commit/5986c57a2b01567ee31c0f08b80689523160a699))
* [#847](https://github.com/bcgov/nr-forests-access-management/issues/847) adjust forest client information card ([#932](https://github.com/bcgov/nr-forests-access-management/issues/932)) ([43d5a56](https://github.com/bcgov/nr-forests-access-management/commit/43d5a5668cb54c07a9d62802fdf0f7192fe764ae))
* [#849](https://github.com/bcgov/nr-forests-access-management/issues/849) adjust styling manage permissions ([#890](https://github.com/bcgov/nr-forests-access-management/issues/890)) ([4adfb59](https://github.com/bcgov/nr-forests-access-management/commit/4adfb59347318229d4d8908a3683614ff69a7ccb))
* 851 search bar in the manage permissions page ([#895](https://github.com/bcgov/nr-forests-access-management/issues/895)) ([55927e9](https://github.com/bcgov/nr-forests-access-management/commit/55927e921ede4f3aad669a18dc8fc6d802d04421))
* drawio adjust ([#910](https://github.com/bcgov/nr-forests-access-management/issues/910)) ([ab7c5ab](https://github.com/bcgov/nr-forests-access-management/commit/ab7c5abc5cf47b41a0eec00e32451c63391cf56b))


### Bug Fixes

* [#720](https://github.com/bcgov/nr-forests-access-management/issues/720) make user attribute displayname and email writable  ([#912](https://github.com/bcgov/nr-forests-access-management/issues/912)) ([32029f5](https://github.com/bcgov/nr-forests-access-management/commit/32029f530dc7c0c45f2431c2bc47caf4cf2b838b))
* [#897](https://github.com/bcgov/nr-forests-access-management/issues/897) frontend minor style changes ([#914](https://github.com/bcgov/nr-forests-access-management/issues/914)) ([2a2a291](https://github.com/bcgov/nr-forests-access-management/commit/2a2a291f9a0270c84b703d0e3b23097fa29acaf4))
* [#933](https://github.com/bcgov/nr-forests-access-management/issues/933) added redirect urls for silva client as required ([#944](https://github.com/bcgov/nr-forests-access-management/issues/944)) ([9fd0afa](https://github.com/bcgov/nr-forests-access-management/commit/9fd0afa038414e4f799d775ebc629b0932235131))

## [1.4.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.3.0...v1.4.0) (2023-09-14)


### Features

* [#715](https://github.com/bcgov/nr-forests-access-management/issues/715) component integration test for landing page ([#861](https://github.com/bcgov/nr-forests-access-management/issues/861)) ([f441fcc](https://github.com/bcgov/nr-forests-access-management/commit/f441fcc8cc0829ebef7df475fd3f0cf6d2c549de))
* [#720](https://github.com/bcgov/nr-forests-access-management/issues/720) Add user display name and email to the profile section ([#891](https://github.com/bcgov/nr-forests-access-management/issues/891)) ([aeb8be9](https://github.com/bcgov/nr-forests-access-management/commit/aeb8be9853a4837206d49f5c6280a0a8815d209d))
* [#751](https://github.com/bcgov/nr-forests-access-management/issues/751) further restrict api lambda user ([#870](https://github.com/bcgov/nr-forests-access-management/issues/870)) ([cbe5f13](https://github.com/bcgov/nr-forests-access-management/commit/cbe5f13f578b6a8720b80592eb1133194706becf))
* Custom network security groups to segregate lambdas [#773](https://github.com/bcgov/nr-forests-access-management/issues/773) ([#841](https://github.com/bcgov/nr-forests-access-management/issues/841)) ([8ee4ae1](https://github.com/bcgov/nr-forests-access-management/commit/8ee4ae1c275de3fe7df2528ae28b27d9609a2362))


### Bug Fixes

* [#719](https://github.com/bcgov/nr-forests-access-management/issues/719) use same button component ([#864](https://github.com/bcgov/nr-forests-access-management/issues/864)) ([9d42f90](https://github.com/bcgov/nr-forests-access-management/commit/9d42f909026a36dc727c4d6de6777bf6ffaf012e))
* [#831](https://github.com/bcgov/nr-forests-access-management/issues/831) remove user role confirm dialog bug ([#871](https://github.com/bcgov/nr-forests-access-management/issues/871)) ([5a3cfe6](https://github.com/bcgov/nr-forests-access-management/commit/5a3cfe6c7e7605bfa46331ee31f99c2d4a2d91aa))
* [#839](https://github.com/bcgov/nr-forests-access-management/issues/839) fix browser console error for labels ([#866](https://github.com/bcgov/nr-forests-access-management/issues/866)) ([ab15111](https://github.com/bcgov/nr-forests-access-management/commit/ab1511150a15a67169b65fee9e28a8977b35d210))
* [#848](https://github.com/bcgov/nr-forests-access-management/issues/848) profile signout incorrect ([#869](https://github.com/bcgov/nr-forests-access-management/issues/869)) ([f7fe57a](https://github.com/bcgov/nr-forests-access-management/commit/f7fe57a0b22ec18ed8a9d656a1f45dfe7b5b6846))
* [#848](https://github.com/bcgov/nr-forests-access-management/issues/848) user name disappearing when log out ([#865](https://github.com/bcgov/nr-forests-access-management/issues/865)) ([b879047](https://github.com/bcgov/nr-forests-access-management/commit/b87904797e1399f067a14783f9ddc26a0f015b9a))
* [#858](https://github.com/bcgov/nr-forests-access-management/issues/858) upgrade fastapi version to solve pipeline issue ([#862](https://github.com/bcgov/nr-forests-access-management/issues/862)) ([0a98744](https://github.com/bcgov/nr-forests-access-management/commit/0a98744a87d298f5f92786b9cf630647eb476cdf))
* [#867](https://github.com/bcgov/nr-forests-access-management/issues/867) add user email return to silva application ([#872](https://github.com/bcgov/nr-forests-access-management/issues/872)) ([4d2725a](https://github.com/bcgov/nr-forests-access-management/commit/4d2725aebe0dc400a0f2e9b2066d17152eaae258))
* [#867](https://github.com/bcgov/nr-forests-access-management/issues/867) fix url of oidc debugger tool  ([#873](https://github.com/bcgov/nr-forests-access-management/issues/873)) ([b093196](https://github.com/bcgov/nr-forests-access-management/commit/b09319622a66edb6ba1094937f130259450d6bc2))
* [#874](https://github.com/bcgov/nr-forests-access-management/issues/874) frontend improvement no try catch ([#875](https://github.com/bcgov/nr-forests-access-management/issues/875)) ([fb4128c](https://github.com/bcgov/nr-forests-access-management/commit/fb4128c57fce37633fb9544b3a215a079b0e2ad4))
* Freeze important pydantic and SQLAlchemy dependencies version. ([#881](https://github.com/bcgov/nr-forests-access-management/issues/881)) ([feeec18](https://github.com/bcgov/nr-forests-access-management/commit/feeec1821ed4bbca9416e192717fb45532ee7caa))
* minor backend improvement part2 ([#860](https://github.com/bcgov/nr-forests-access-management/issues/860)) ([c049bab](https://github.com/bcgov/nr-forests-access-management/commit/c049bab490ea7ac9ccf326fa603e945cc5c3e663))


### Miscellaneous

* **deps:** update dependency mock to v5 ([#832](https://github.com/bcgov/nr-forests-access-management/issues/832)) ([d32ffb1](https://github.com/bcgov/nr-forests-access-management/commit/d32ffb1e685e5bbaaca7ef69006e69500fc7dad4))
* **deps:** update dependency mypy to v1 ([#833](https://github.com/bcgov/nr-forests-access-management/issues/833)) ([4026caf](https://github.com/bcgov/nr-forests-access-management/commit/4026cafac47405bc7e7ebe7877e908042eccb5e3))

## [1.3.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.2.2...v1.3.0) (2023-08-30)


### Features

* [#478](https://github.com/bcgov/nr-forests-access-management/issues/478) add gc notify email endpoint ([#789](https://github.com/bcgov/nr-forests-access-management/issues/789)) ([93ee292](https://github.com/bcgov/nr-forests-access-management/commit/93ee292e9f7ae30abec736eba14f8d41e58f23e7))
* [#561](https://github.com/bcgov/nr-forests-access-management/issues/561) API audit logs ([#772](https://github.com/bcgov/nr-forests-access-management/issues/772)) ([f027191](https://github.com/bcgov/nr-forests-access-management/commit/f02719122e34b4f22cbc07cb64a9adfeb11ecd2f))
* [#561](https://github.com/bcgov/nr-forests-access-management/issues/561) audit for auth login  ([#766](https://github.com/bcgov/nr-forests-access-management/issues/766)) ([e15d94b](https://github.com/bcgov/nr-forests-access-management/commit/e15d94b7af89ae3d47dc6d8ddae3f3f62cc972da))
* [#679](https://github.com/bcgov/nr-forests-access-management/issues/679) integrate idim lookup proxy ([#728](https://github.com/bcgov/nr-forests-access-management/issues/728)) ([1e71989](https://github.com/bcgov/nr-forests-access-management/commit/1e71989f57196fd3f5d56f2f5e6c4c97948b1a9f))
* [#688](https://github.com/bcgov/nr-forests-access-management/issues/688) Restrict admins from self-modification ([#705](https://github.com/bcgov/nr-forests-access-management/issues/705)) ([197e505](https://github.com/bcgov/nr-forests-access-management/commit/197e50576c44953952b9403ebb8cade49d38b582))
* [#700](https://github.com/bcgov/nr-forests-access-management/issues/700) input sanitization ([#837](https://github.com/bcgov/nr-forests-access-management/issues/837)) ([d2703d1](https://github.com/bcgov/nr-forests-access-management/commit/d2703d1f72870b83f618d5e2706c8b7e29386694))
* [#704](https://github.com/bcgov/nr-forests-access-management/issues/704) switch to carbon icons ([#754](https://github.com/bcgov/nr-forests-access-management/issues/754)) ([846a579](https://github.com/bcgov/nr-forests-access-management/commit/846a57950b858dd652cf4d7e3e89a008e1033c5a))
* [#718](https://github.com/bcgov/nr-forests-access-management/issues/718) Reduce access of API DB user ([#745](https://github.com/bcgov/nr-forests-access-management/issues/745)) ([ac18807](https://github.com/bcgov/nr-forests-access-management/commit/ac18807d1d2b056f5c75e084a984014d51bf3452))
* [#718](https://github.com/bcgov/nr-forests-access-management/issues/718) Use seperate auth lambda database user ([#731](https://github.com/bcgov/nr-forests-access-management/issues/731)) ([a012ab0](https://github.com/bcgov/nr-forests-access-management/commit/a012ab0d820ff1366d2aa01666bbba545238d9e6))
* [#725](https://github.com/bcgov/nr-forests-access-management/issues/725) add waf terraform ([#797](https://github.com/bcgov/nr-forests-access-management/issues/797)) ([d2a79ff](https://github.com/bcgov/nr-forests-access-management/commit/d2a79ffa43db56e63da7bdc22f5b19c67100b28c))
* [#726](https://github.com/bcgov/nr-forests-access-management/issues/726) Added redirect urls for forest client test and prod in terraform ([#741](https://github.com/bcgov/nr-forests-access-management/issues/741)) ([56cc3e4](https://github.com/bcgov/nr-forests-access-management/commit/56cc3e41de4c6476cedc21d61037069b2c1272e5))
* [#818](https://github.com/bcgov/nr-forests-access-management/issues/818) onboard support for Silva ([#821](https://github.com/bcgov/nr-forests-access-management/issues/821)) ([84c7fdd](https://github.com/bcgov/nr-forests-access-management/commit/84c7fdd9fea43094f9445466123d86694002646c))
* 575 implement bcgovpubcode ([#723](https://github.com/bcgov/nr-forests-access-management/issues/723)) ([10234fa](https://github.com/bcgov/nr-forests-access-management/commit/10234fa788ddb54160ad01a4ecb8a29ef04820a7))
* 616 frontend main page ([#699](https://github.com/bcgov/nr-forests-access-management/issues/699)) ([55d8f4a](https://github.com/bcgov/nr-forests-access-management/commit/55d8f4a43cb7f2327bcf3d87ba5e07efdae699b5))


### Bug Fixes

* [#561](https://github.com/bcgov/nr-forests-access-management/issues/561) update audit log ([#807](https://github.com/bcgov/nr-forests-access-management/issues/807)) ([6577df7](https://github.com/bcgov/nr-forests-access-management/commit/6577df7d7c781f5cd5fe0807133452d7255b44a1))
* [#704](https://github.com/bcgov/nr-forests-access-management/issues/704) fix frontend pipeline build error caused by type ([#811](https://github.com/bcgov/nr-forests-access-management/issues/811)) ([bcf7d23](https://github.com/bcgov/nr-forests-access-management/commit/bcf7d23a8908ad21c655e6ccfedeba37b9843e59))
* [#714](https://github.com/bcgov/nr-forests-access-management/issues/714) cleanup frontend code ([#756](https://github.com/bcgov/nr-forests-access-management/issues/756)) ([1806a35](https://github.com/bcgov/nr-forests-access-management/commit/1806a35f28e421dff3026645b551fe85ce3ac25d))
* [#721](https://github.com/bcgov/nr-forests-access-management/issues/721) style unit px to rem ([#806](https://github.com/bcgov/nr-forests-access-management/issues/806)) ([69113fe](https://github.com/bcgov/nr-forests-access-management/commit/69113fe78746e41d6bbb1bcd44b79d70b69e60ef))
* [#733](https://github.com/bcgov/nr-forests-access-management/issues/733) Disable grant access button when there is no application selected ([#749](https://github.com/bcgov/nr-forests-access-management/issues/749)) ([9bf2f3d](https://github.com/bcgov/nr-forests-access-management/commit/9bf2f3dc1cafddfec67ec2a83675503390ac0325))
* [#735](https://github.com/bcgov/nr-forests-access-management/issues/735) error handling fix ([#746](https://github.com/bcgov/nr-forests-access-management/issues/746)) ([5d2a709](https://github.com/bcgov/nr-forests-access-management/commit/5d2a70915c66aa1cae226abf09e92bf437c9c9a0))
* [#748](https://github.com/bcgov/nr-forests-access-management/issues/748) - Fixing the Forest Client Number at Summary Page ([#803](https://github.com/bcgov/nr-forests-access-management/issues/803)) ([a431623](https://github.com/bcgov/nr-forests-access-management/commit/a4316236c618c61bfef2b263ce5f0e60eec103bf))
* [#750](https://github.com/bcgov/nr-forests-access-management/issues/750) frontend minor fixes ([#819](https://github.com/bcgov/nr-forests-access-management/issues/819)) ([496a302](https://github.com/bcgov/nr-forests-access-management/commit/496a302a7156e5931b3c4682e57d703d941af0c1))
* [#755](https://github.com/bcgov/nr-forests-access-management/issues/755) cleaning up stylesheet, and updating classes ([#822](https://github.com/bcgov/nr-forests-access-management/issues/822)) ([855e711](https://github.com/bcgov/nr-forests-access-management/commit/855e71178ff9c2a1e1892303a6dd59dc9fc1ce23))
* [#759](https://github.com/bcgov/nr-forests-access-management/issues/759) Show Next button in the grant access page, but disabled it until meet requirement. ([#768](https://github.com/bcgov/nr-forests-access-management/issues/768)) ([438f5a8](https://github.com/bcgov/nr-forests-access-management/commit/438f5a819ad694a92848e56b457302ae39e1b58d))
* [#800](https://github.com/bcgov/nr-forests-access-management/issues/800) Frontend test breaks the pipeline build ([#801](https://github.com/bcgov/nr-forests-access-management/issues/801)) ([a679747](https://github.com/bcgov/nr-forests-access-management/commit/a6797475b4cb77ce76364dcb6404c93a0aa2070d))
* [#814](https://github.com/bcgov/nr-forests-access-management/issues/814) update dynamic icon import to fix pipeline slow issue ([#816](https://github.com/bcgov/nr-forests-access-management/issues/816)) ([241d124](https://github.com/bcgov/nr-forests-access-management/commit/241d1246358746b4f8d8a71ba20ba6d1cea50d38))
* [#815](https://github.com/bcgov/nr-forests-access-management/issues/815) large filesize image ([#823](https://github.com/bcgov/nr-forests-access-management/issues/823)) ([51dd608](https://github.com/bcgov/nr-forests-access-management/commit/51dd6086cbcee15e8c4cb745de843cec9eda5dc0))
* [#825](https://github.com/bcgov/nr-forests-access-management/issues/825) 403 error interceptor ([#829](https://github.com/bcgov/nr-forests-access-management/issues/829)) ([0258ccc](https://github.com/bcgov/nr-forests-access-management/commit/0258cccc4c6a4ef1c2fbcdb1a5246fb2c967b9eb))
* [#826](https://github.com/bcgov/nr-forests-access-management/issues/826) clear previous success message on dashboard ([#830](https://github.com/bcgov/nr-forests-access-management/issues/830)) ([f432d0c](https://github.com/bcgov/nr-forests-access-management/commit/f432d0cee6dba88a16e77ec2a5b4202d2b7e8772))
* [#827](https://github.com/bcgov/nr-forests-access-management/issues/827)  logout causing type error ([#828](https://github.com/bcgov/nr-forests-access-management/issues/828)) ([6a86b0c](https://github.com/bcgov/nr-forests-access-management/commit/6a86b0c5b320fd83f62abdfffdbc956b651c55b8))
* minor backend adjustment ([#812](https://github.com/bcgov/nr-forests-access-management/issues/812)) ([5ba837d](https://github.com/bcgov/nr-forests-access-management/commit/5ba837d3f25bc738639382649ced664ae882e319))
* server/backend/requirements.txt upgrade cryptography from 41.0.1 to 41.0.2 ([#702](https://github.com/bcgov/nr-forests-access-management/issues/702)) ([b5220e3](https://github.com/bcgov/nr-forests-access-management/commit/b5220e37a7b9bf8b403cc78c4f1347630cde3b52))


### Miscellaneous

* [#684](https://github.com/bcgov/nr-forests-access-management/issues/684) update fam architecture diagram ([#706](https://github.com/bcgov/nr-forests-access-management/issues/706)) ([eec32c7](https://github.com/bcgov/nr-forests-access-management/commit/eec32c768415708d749c1c578051257d5922527c))
* bump bcgov-nr/action-test-and-analyst to v0.0.2 ([#783](https://github.com/bcgov/nr-forests-access-management/issues/783)) ([bc7fab9](https://github.com/bcgov/nr-forests-access-management/commit/bc7fab9ddabf0c066195167ebbd0a8a05d3f2b6e))
* **deps-dev:** Bump @antfu/utils from 0.7.2 to 0.7.5 in /frontend ([#771](https://github.com/bcgov/nr-forests-access-management/issues/771)) ([3869c3d](https://github.com/bcgov/nr-forests-access-management/commit/3869c3d0da84199706f719686469e5e3eed25bde))
* **deps-dev:** bump tough-cookie from 4.1.2 to 4.1.3 in /frontend ([#770](https://github.com/bcgov/nr-forests-access-management/issues/770)) ([47a46c5](https://github.com/bcgov/nr-forests-access-management/commit/47a46c57b9fb293037747edba1d24bd784c7d2b8))
* **deps-dev:** bump vite from 4.3.7 to 4.3.9 in /frontend ([#757](https://github.com/bcgov/nr-forests-access-management/issues/757)) ([dda1b66](https://github.com/bcgov/nr-forests-access-management/commit/dda1b66000ce7f37c0620d0585ddadaca1c5794c))
* **deps:** bump @nestjs/core and @openapitools/openapi-generator-cli in /client-code-gen ([#769](https://github.com/bcgov/nr-forests-access-management/issues/769)) ([fd8977f](https://github.com/bcgov/nr-forests-access-management/commit/fd8977f8e1aa34f5d016a78b31d92f6181f59919))
* **deps:** bump fast-xml-parser and aws-amplify in /frontend ([#752](https://github.com/bcgov/nr-forests-access-management/issues/752)) ([35ef36f](https://github.com/bcgov/nr-forests-access-management/commit/35ef36f2d55d0b6571b55d6a2584f7b99748cce6))
* **deps:** update boto ([#784](https://github.com/bcgov/nr-forests-access-management/issues/784)) ([d295b33](https://github.com/bcgov/nr-forests-access-management/commit/d295b3337073d956bed82a69dbe977cebacaaf0d))
* **deps:** update dependency @types/node to v18 ([#817](https://github.com/bcgov/nr-forests-access-management/issues/817)) ([f82bfa7](https://github.com/bcgov/nr-forests-access-management/commit/f82bfa7c703311cf5b0c10b5fc759c46cd2d3826))
* **deps:** update dependency authlib to v1.2.1 ([#675](https://github.com/bcgov/nr-forests-access-management/issues/675)) ([b201161](https://github.com/bcgov/nr-forests-access-management/commit/b201161a65d10e96f4c60ad72434a97c4f8b9fe3))
* **deps:** update dependency botocore to v1.31.23 and boto3 to v1.28.23 ([#761](https://github.com/bcgov/nr-forests-access-management/issues/761)) ([068440a](https://github.com/bcgov/nr-forests-access-management/commit/068440a305d99bc812715bee706a5092468b7af9))
* **deps:** update dependency cryptography to v41.0.3 [security] ([#732](https://github.com/bcgov/nr-forests-access-management/issues/732)) ([d8274de](https://github.com/bcgov/nr-forests-access-management/commit/d8274dea48618799eb20ac095905e701b0a2aaaa))
* **deps:** update dependency flake8 to v6 ([#809](https://github.com/bcgov/nr-forests-access-management/issues/809)) ([ed72388](https://github.com/bcgov/nr-forests-access-management/commit/ed72388f5b2842df2ac661f5b36e015280d08f87))
* **deps:** update dependency psycopg2-binary to v2.9.7 ([#776](https://github.com/bcgov/nr-forests-access-management/issues/776)) ([6b84476](https://github.com/bcgov/nr-forests-access-management/commit/6b844765345303958d47fde5c3a327a264fa6e1e))
* **deps:** update dependency uvicorn to v0.23.2 ([#777](https://github.com/bcgov/nr-forests-access-management/issues/777)) ([907c477](https://github.com/bcgov/nr-forests-access-management/commit/907c477af346629c26b0e4c89e941314c25a1cb0))
* **deps:** update vitest monorepo to ^0.34.0 ([#785](https://github.com/bcgov/nr-forests-access-management/issues/785)) ([69d461f](https://github.com/bcgov/nr-forests-access-management/commit/69d461ff2e8122bcc0853a597067e8191672abbf))
* Enable dev deployment for push on main. ([#767](https://github.com/bcgov/nr-forests-access-management/issues/767)) ([16431d3](https://github.com/bcgov/nr-forests-access-management/commit/16431d39b9a416b89473909fd33056f3c843efa7))
* increase renovate PR limit ([#774](https://github.com/bcgov/nr-forests-access-management/issues/774)) ([1160f7c](https://github.com/bcgov/nr-forests-access-management/commit/1160f7cf3d5b065afe9a6b7b03cdeb298beea82e))
* update and triggers for frontend tests ([#788](https://github.com/bcgov/nr-forests-access-management/issues/788)) ([b8334b5](https://github.com/bcgov/nr-forests-access-management/commit/b8334b50925967946c1a5e63498f0ce053e92400))

## [1.2.2](https://github.com/bcgov/nr-forests-access-management/compare/v1.2.1...v1.2.2) (2023-07-13)


### Bug Fixes

* [#592](https://github.com/bcgov/nr-forests-access-management/issues/592) renovate dashboard backend ([#612](https://github.com/bcgov/nr-forests-access-management/issues/612)) ([838babf](https://github.com/bcgov/nr-forests-access-management/commit/838babfc66db9de8436f27ee0723a392ddc01fd9))
* **config:** [#578](https://github.com/bcgov/nr-forests-access-management/issues/578) Onboard Silva to FAM ([#641](https://github.com/bcgov/nr-forests-access-management/issues/641)) ([92b0b94](https://github.com/bcgov/nr-forests-access-management/commit/92b0b94f351409d80f36be0cc19ae05ec6caf7f4))
* **deps:** update dependency aws-amplify to v5 ([#600](https://github.com/bcgov/nr-forests-access-management/issues/600)) ([10f487e](https://github.com/bcgov/nr-forests-access-management/commit/10f487e9c43966e916ac916b1591b5b119e9a7ed))
* **deps:** update dependency boto3 to v1.26.147 ([#629](https://github.com/bcgov/nr-forests-access-management/issues/629)) ([e55ab75](https://github.com/bcgov/nr-forests-access-management/commit/e55ab7580ed9731d342813798b53bf71bea9d1f9))
* **deps:** update dependency cryptography to v41 [security] ([#625](https://github.com/bcgov/nr-forests-access-management/issues/625)) ([f3e65cc](https://github.com/bcgov/nr-forests-access-management/commit/f3e65cc4e24de02f56714af4fd5097526c0364f3))
* **deps:** update dependency mangum to v0.17.0 ([#630](https://github.com/bcgov/nr-forests-access-management/issues/630)) ([cefa173](https://github.com/bcgov/nr-forests-access-management/commit/cefa17328695c3fa8a6c1272a28814dcbe1c524b))
* **deps:** update dependency uvicorn to v0.22.0 ([#634](https://github.com/bcgov/nr-forests-access-management/issues/634)) ([3ee9e82](https://github.com/bcgov/nr-forests-access-management/commit/3ee9e829521b224d50e833a8f74f855cfb6d1e2e))


### Miscellaneous

* [#194](https://github.com/bcgov/nr-forests-access-management/issues/194) add deployment smoke test ([#609](https://github.com/bcgov/nr-forests-access-management/issues/609)) ([b040435](https://github.com/bcgov/nr-forests-access-management/commit/b0404355cdce2c1433b3c8bd1d3055b0942bac07))
* [#475](https://github.com/bcgov/nr-forests-access-management/issues/475) enable tools environment ([#680](https://github.com/bcgov/nr-forests-access-management/issues/680)) ([e338e38](https://github.com/bcgov/nr-forests-access-management/commit/e338e3897b93cb598aca26a5a7579cf27128670d))
* [#475](https://github.com/bcgov/nr-forests-access-management/issues/475) repair tools ci ([#682](https://github.com/bcgov/nr-forests-access-management/issues/682)) ([3853660](https://github.com/bcgov/nr-forests-access-management/commit/38536607cc6651c6a7da539b6877d469771bf8f9))
* [#475](https://github.com/bcgov/nr-forests-access-management/issues/475) tune tools deployment scripts ([#681](https://github.com/bcgov/nr-forests-access-management/issues/681)) ([cfd5ffe](https://github.com/bcgov/nr-forests-access-management/commit/cfd5ffea425cc7357923386e0450f411af48d950))
* [#594](https://github.com/bcgov/nr-forests-access-management/issues/594) backend cleanup alembic remnants ([#614](https://github.com/bcgov/nr-forests-access-management/issues/614)) ([333c566](https://github.com/bcgov/nr-forests-access-management/commit/333c5663505d1fbc4e138bcb382b9f80547567cf))
* [#87](https://github.com/bcgov/nr-forests-access-management/issues/87) backend and auth sonar adjustments and fixes ([#669](https://github.com/bcgov/nr-forests-access-management/issues/669)) ([22bce51](https://github.com/bcgov/nr-forests-access-management/commit/22bce512b98a5e46070009a9cd893cc0c98c5bf7))
* [#87](https://github.com/bcgov/nr-forests-access-management/issues/87) code coverage debugging ([#674](https://github.com/bcgov/nr-forests-access-management/issues/674)) ([ce9752d](https://github.com/bcgov/nr-forests-access-management/commit/ce9752dcbcbc6b759d7cf4fce85952938c287c31))
* [#87](https://github.com/bcgov/nr-forests-access-management/issues/87) coverage for PRs ([#666](https://github.com/bcgov/nr-forests-access-management/issues/666)) ([5f68a9e](https://github.com/bcgov/nr-forests-access-management/commit/5f68a9ebbd258bef995983d56efe1cd19e06ebcf))
* [#87](https://github.com/bcgov/nr-forests-access-management/issues/87) sonar cloud with coverage ([#668](https://github.com/bcgov/nr-forests-access-management/issues/668)) ([f3ff8b1](https://github.com/bcgov/nr-forests-access-management/commit/f3ff8b11a66d54b799f56c086de68413367abd26))
* 475 eliminate pet names ([#683](https://github.com/bcgov/nr-forests-access-management/issues/683)) ([f12537d](https://github.com/bcgov/nr-forests-access-management/commit/f12537d2e4c5d4d83797b44ac8517e55eb10e996))
* **api-tests:** [#649](https://github.com/bcgov/nr-forests-access-management/issues/649) refactor tests api ([#652](https://github.com/bcgov/nr-forests-access-management/issues/652)) ([4c34a91](https://github.com/bcgov/nr-forests-access-management/commit/4c34a913ea4279e7a3c19ac6f04eb45ff8053152))
* **auth_function:** [#649](https://github.com/bcgov/nr-forests-access-management/issues/649) refactor tests ([#650](https://github.com/bcgov/nr-forests-access-management/issues/650)) ([8742f4b](https://github.com/bcgov/nr-forests-access-management/commit/8742f4b7358e06184efe9b74fc756ed16d940ff3))
* coverage for main merge ([#664](https://github.com/bcgov/nr-forests-access-management/issues/664)) ([0fa6c46](https://github.com/bcgov/nr-forests-access-management/commit/0fa6c46d2e5ef0681aa2e0afc61db48ac9e2f128))
* **deps:** [#87](https://github.com/bcgov/nr-forests-access-management/issues/87) update dependency fastapi to v0.98.0 ([#671](https://github.com/bcgov/nr-forests-access-management/issues/671)) ([c8eacbf](https://github.com/bcgov/nr-forests-access-management/commit/c8eacbfbf13a4a6f803e0c8bd8d2c97986082ca4))
* **deps:** update dependency @types/node to v18 ([#585](https://github.com/bcgov/nr-forests-access-management/issues/585)) ([3475d32](https://github.com/bcgov/nr-forests-access-management/commit/3475d32c0b4ac44b297a3fae890d6a1c27ce2787))
* **deps:** update dependency boto3 to v1.26.162 ([#647](https://github.com/bcgov/nr-forests-access-management/issues/647)) ([43e5312](https://github.com/bcgov/nr-forests-access-management/commit/43e5312aea588607cfb9c469a117215a072d8a8e))
* **deps:** update dependency botocore to v1.29.160 ([#667](https://github.com/bcgov/nr-forests-access-management/issues/667)) ([7b11409](https://github.com/bcgov/nr-forests-access-management/commit/7b11409b626229389167f601eb21d79052e6e752))
* **deps:** update dependency fastapi to v0.98.0 ([#633](https://github.com/bcgov/nr-forests-access-management/issues/633)) ([fc54a7a](https://github.com/bcgov/nr-forests-access-management/commit/fc54a7a3d931d37d3662b7050871aa1c455eab3c))
* **deps:** update dependency jsdom to v22 ([#589](https://github.com/bcgov/nr-forests-access-management/issues/589)) ([ecd6903](https://github.com/bcgov/nr-forests-access-management/commit/ecd690370dffa5029133c0a5a3257e8f48acf084))
* **deps:** update dependency vue-tsc to v1 ([#597](https://github.com/bcgov/nr-forests-access-management/issues/597)) ([a182bab](https://github.com/bcgov/nr-forests-access-management/commit/a182bab1caae0750a6b9562157453536b2587eea))
* **deps:** update dependency yup to v1 ([#598](https://github.com/bcgov/nr-forests-access-management/issues/598)) ([069f250](https://github.com/bcgov/nr-forests-access-management/commit/069f250c5b4880d540ffd9727bdd371187b25cf8))
* **deps:** update vite to v4 (major) ([#590](https://github.com/bcgov/nr-forests-access-management/issues/590)) ([786f76b](https://github.com/bcgov/nr-forests-access-management/commit/786f76b476f802cad4b5362af56aceebddd21ec1))
* **deps:** update vitest monorepo to ^0.32.0 ([#643](https://github.com/bcgov/nr-forests-access-management/issues/643)) ([48f8140](https://github.com/bcgov/nr-forests-access-management/commit/48f81408a69329a145bda67350e8e571430879bd))
* Remove unnecessary "@types/node": "^18.0.0" from frontend. ([#611](https://github.com/bcgov/nr-forests-access-management/issues/611)) ([758088d](https://github.com/bcgov/nr-forests-access-management/commit/758088d62097bd3e213474ffba2800b9ccc5dff6))
* renovate prConcurrentLimit=3 ([#677](https://github.com/bcgov/nr-forests-access-management/issues/677)) ([474fb49](https://github.com/bcgov/nr-forests-access-management/commit/474fb49af7f94b7a456fe0f1508367154a71619b))

## [1.2.1](https://github.com/bcgov/nr-forests-access-management/compare/v1.2.0...v1.2.1) (2023-05-25)


### Bug Fixes

* [#450](https://github.com/bcgov/nr-forests-access-management/issues/450) BCSC post-merge bugfix and local dev repair ([#604](https://github.com/bcgov/nr-forests-access-management/issues/604)) ([fa3f700](https://github.com/bcgov/nr-forests-access-management/commit/fa3f700a14512ad2433025a262b930965c4891d5))

## [1.2.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.1.1...v1.2.0) (2023-05-25)


### Features

* [#179](https://github.com/bcgov/nr-forests-access-management/issues/179) Front end integration with Forest Client API ([#565](https://github.com/bcgov/nr-forests-access-management/issues/565)) ([697bb45](https://github.com/bcgov/nr-forests-access-management/commit/697bb45d5e12dee3cef27f5f27d9c1725ea83d51))
* [#305](https://github.com/bcgov/nr-forests-access-management/issues/305) forest client api backend integration ([#532](https://github.com/bcgov/nr-forests-access-management/issues/532)) ([93c2868](https://github.com/bcgov/nr-forests-access-management/commit/93c286887c6d4024fb8eeb12daca6eb75fbcca7a))
* [#450](https://github.com/bcgov/nr-forests-access-management/issues/450) bcsc integration ([#534](https://github.com/bcgov/nr-forests-access-management/issues/534)) ([a583bda](https://github.com/bcgov/nr-forests-access-management/commit/a583bda69ac2f4462bbf0a018ca3263c9004d5b3))
* [#462](https://github.com/bcgov/nr-forests-access-management/issues/462) Write script to transfer user from csv file into FAM ([#555](https://github.com/bcgov/nr-forests-access-management/issues/555)) ([ebd08b9](https://github.com/bcgov/nr-forests-access-management/commit/ebd08b9e6bcfd22816aa155d495eeb0403e9e85e))
* [#551](https://github.com/bcgov/nr-forests-access-management/issues/551) landing page ([#572](https://github.com/bcgov/nr-forests-access-management/issues/572)) ([834840f](https://github.com/bcgov/nr-forests-access-management/commit/834840f8daab193b2bb2788750083989d4883835))
* add renovate support ([#581](https://github.com/bcgov/nr-forests-access-management/issues/581)) ([35bd050](https://github.com/bcgov/nr-forests-access-management/commit/35bd05019739ed28d24ad5e1ba82d3a225705cce))


### Bug Fixes

* [#522](https://github.com/bcgov/nr-forests-access-management/issues/522) Merge hotfix branch for fixing duplicate user records ([#559](https://github.com/bcgov/nr-forests-access-management/issues/559)) ([bf2ef44](https://github.com/bcgov/nr-forests-access-management/commit/bf2ef443dc28a3a4ab7e26fe56536c2622248b19))
* [#544](https://github.com/bcgov/nr-forests-access-management/issues/544) Add FOM demo callback and logout url to FOM-TEST client in terraform ([#550](https://github.com/bcgov/nr-forests-access-management/issues/550)) ([ff6f416](https://github.com/bcgov/nr-forests-access-management/commit/ff6f416e4ecd1d218c386ee8d438313d0ae329fe))
* [#560](https://github.com/bcgov/nr-forests-access-management/issues/560) Fix application error when refresh manage access page, and when only has access to one app ([#573](https://github.com/bcgov/nr-forests-access-management/issues/573)) ([c6779b4](https://github.com/bcgov/nr-forests-access-management/commit/c6779b499d3cf6532f0b30cfee31ec71c2e52bcc))
* 392 - Refactoring folder structure ([#583](https://github.com/bcgov/nr-forests-access-management/issues/583)) ([568aae1](https://github.com/bcgov/nr-forests-access-management/commit/568aae1fee7dd02834aab2ff67fb24277e2fd386))


### Miscellaneous

* [#469](https://github.com/bcgov/nr-forests-access-management/issues/469) add postgres tests ([#535](https://github.com/bcgov/nr-forests-access-management/issues/535)) ([d995104](https://github.com/bcgov/nr-forests-access-management/commit/d9951049bd09e1fbb92da4dd2908a6c4b97adc41))
* [#481](https://github.com/bcgov/nr-forests-access-management/issues/481) Improve documentation for getting users from Keycloak for fom ([#524](https://github.com/bcgov/nr-forests-access-management/issues/524)) ([e08e29a](https://github.com/bcgov/nr-forests-access-management/commit/e08e29aa63f27d65bbe60a9df921b23209b11c1c))
* Pinned aurora_postgresql_v2 version to prevent deploy issues ([#545](https://github.com/bcgov/nr-forests-access-management/issues/545)) ([e76ab9d](https://github.com/bcgov/nr-forests-access-management/commit/e76ab9d39c5809feeedc5a1259e8d3ec8161037e))
* temp disable autodeploy to DEV ([d155888](https://github.com/bcgov/nr-forests-access-management/commit/d155888347f290ac83251f3da058bca1c34ad4e8))
* Update Cognito fam client_id and user pool id for locally to work. ([#540](https://github.com/bcgov/nr-forests-access-management/issues/540)) ([d535bc0](https://github.com/bcgov/nr-forests-access-management/commit/d535bc0e12f89791fc12218f87b6ad9d63489c59))

## [1.1.2](https://github.com/bcgov/nr-forests-access-management/compare/v1.1.1...v1.1.2) (2023-04-20)


### Bug Fixes

* [#522](https://github.com/bcgov/nr-forests-access-management/issues/522) Fix user role duplicate records, fix target default branch in hotfix release please ([#557](https://github.com/bcgov/nr-forests-access-management/issues/557)) ([e98ec72](https://github.com/bcgov/nr-forests-access-management/commit/e98ec72cc67dadc8332b909b7ba64ff6166a662a))

## [1.1.1](https://github.com/bcgov/nr-forests-access-management/compare/v1.1.0...v1.1.1) (2023-03-25)


### Bug Fixes

* [#506](https://github.com/bcgov/nr-forests-access-management/issues/506) move SPAR role deletions to new migration ([#525](https://github.com/bcgov/nr-forests-access-management/issues/525)) ([0ca70a9](https://github.com/bcgov/nr-forests-access-management/commit/0ca70a9ef65b73e6351eefe282467bde5bcfc53f))

## [1.1.0](https://github.com/bcgov/nr-forests-access-management/compare/v1.0.0...v1.1.0) (2023-03-25)


### Features

* [#336](https://github.com/bcgov/nr-forests-access-management/issues/336) filter fam front-end by environment ([#488](https://github.com/bcgov/nr-forests-access-management/issues/488)) ([202c107](https://github.com/bcgov/nr-forests-access-management/commit/202c1072bac221b1e882169d5d99aa52457bbff2))


### Bug Fixes

* [#506](https://github.com/bcgov/nr-forests-access-management/issues/506) Insert SPAR roles in FAM ([#522](https://github.com/bcgov/nr-forests-access-management/issues/522)) ([af36b48](https://github.com/bcgov/nr-forests-access-management/commit/af36b48d85c6a972fba91e7719e68460270f4b73))
* [#516](https://github.com/bcgov/nr-forests-access-management/issues/516) Duplicate and Environment Conflict when Creating Role Assignment in PROD for FOM TEST for Client ([#520](https://github.com/bcgov/nr-forests-access-management/issues/520)) ([bc71656](https://github.com/bcgov/nr-forests-access-management/commit/bc716565d51591a4e1fed2962202bd010ce323dd))
* [#517](https://github.com/bcgov/nr-forests-access-management/issues/517) Spike aurora-postgresql version auto upgraded by AWS ([#518](https://github.com/bcgov/nr-forests-access-management/issues/518)) ([7da0298](https://github.com/bcgov/nr-forests-access-management/commit/7da029844a75c3cb3981a0ce04d21e25298ff38d))
* [#519](https://github.com/bcgov/nr-forests-access-management/issues/519) fam cognito logout for fom TEST not working ([#521](https://github.com/bcgov/nr-forests-access-management/issues/521)) ([695b70b](https://github.com/bcgov/nr-forests-access-management/commit/695b70b6c99f3d231bf6c8ad3af6383b54ebba3e))
* 506 delete mistakenly entered SPAR roles ([#523](https://github.com/bcgov/nr-forests-access-management/issues/523)) ([8ac6921](https://github.com/bcgov/nr-forests-access-management/commit/8ac6921f7b883881b9fd5d3c3f0ab235753aa675))


### Miscellaneous

* [#438](https://github.com/bcgov/nr-forests-access-management/issues/438) deleted old messy changelog content ([#511](https://github.com/bcgov/nr-forests-access-management/issues/511)) ([67ea069](https://github.com/bcgov/nr-forests-access-management/commit/67ea06924b9ff89281c2a684ed2f4674d8b1410e))

## [1.0.0](https://github.com/bcgov/nr-forests-access-management/compare/v0.1.0...v1.0.0) (2023-03-18)

First production version of FAM was released in February 2023. A production "hotfix" was done in March 2023 to onboard SPAR. Detailed changelog starts from here.
