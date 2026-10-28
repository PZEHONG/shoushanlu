# 收山录 · 中国经典徒步档案

当前包含 11 个档案：武功山反穿，加上《新民周刊》2025-11-17 的十条经典路线。支持地球定位、真实高程地形、搜索、筛选和逐条本地收藏。

新增十条为墨脱、冈仁波齐、虎跳峡、雨崩、南太行、长穿毕、贡嘎、喀拉峻、乌孙古道、腾格里。它们目前均为 `pending`：只有真实区域地形，没有可核实完整轨迹，不显示猜测路线、里程、海拔曲线或回放。武功山保留真实导入轨迹和回放。

名单出处：https://paper.xinmin.cn/html/xmzk/2025-11-17/56/42043.html 。不是官方排名；地区代表位置不是起点，区域地形不等于完整线路覆盖。每条档案保存其地理背景来源。

运行 `python serve.py`，打开 http://127.0.0.1:8768 。所有运行资源均包含在 dist，浏览时不需要地图密钥或外部资源请求。

## 数据

- 轨迹：用户电脑已有的《武功山反穿.kml》，两步路导出，原作者微风同好。提取 2,102 个 gx:coord，按球面距离累计约 22.396 km，记录最高海拔约 1,908 m。未补造地点名称。数据未经实地核验。
- 高程：[Mapzen / AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/)，Terrarium z12 瓦片，以 257×257 网格采样，2026-10-27 获取。高度在画面中增强 1.6 倍，配色为程序地形着色，不是卫星地表影像。
- [高程数据归属和许可](https://github.com/tilezen/joerd/blob/master/docs/attribution.md)。当地高程主要来自 SRTM；应保留 Mapzen、数据生产方及 AWS Open Data 来源说明。
- 地球影像：Three.js 示例 earth_atmos_2048.jpg；Three.js 0.170.0，MIT 许可证已包含在 dist/vendor。
- 轨迹按原文件坐标直接导入，未进行坐标系转换。地表贴合只是显示处理，海拔曲线保留导入记录值；不能作为户外导航或通行依据。

新增地形采用 Terrarium z11、193×193 网格，真实高程数据已打包；不依赖运行时外网地图接口。目录位于 `dist/catalog.json`，地形位于 `dist/terrains/`。切换时按需加载、缓存数据并释放旧网格。

收藏存储于 `shoushanlu:collection`，自动兼容旧的 `shoushanlu:wugong` 收藏。尚无登录、云端收藏、GPX 上传或户外导航。

## 检查

`python test_catalog.py` 验证所有目录数据、真实高程范围和轨迹数据边界。

`python check_catalog_ui.py` 使用本机 Edge 检查全部 11 个档案、搜索和筛选、缺轨迹状态、回放、收藏迁移与持久化、快速切换及手机布局。需先运行预览服务，截图输出到 `checks/`。
