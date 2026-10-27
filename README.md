# 收山录 · 单路线交互原型

当前样例为武功山反穿：地球定位、真实高程山体、轨迹回放、海拔曲线、浏览器本地收藏。

运行 `python serve.py`，打开 http://127.0.0.1:8768 。所有运行资源均包含在 dist，浏览时不需要地图密钥或外部资源请求。

## 数据

- 轨迹：用户电脑已有的《武功山反穿.kml》，两步路导出，原作者微风同好。提取 2,102 个 gx:coord，按球面距离累计约 22.396 km，记录最高海拔约 1,908 m。未补造地点名称。数据未经实地核验。
- 高程：[Mapzen / AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/)，Terrarium z12 瓦片，以 257×257 网格采样，2026-10-27 获取。高度在画面中增强 1.6 倍，配色为程序地形着色，不是卫星地表影像。
- [高程数据归属和许可](https://github.com/tilezen/joerd/blob/master/docs/attribution.md)。当地高程主要来自 SRTM；应保留 Mapzen、数据生产方及 AWS Open Data 来源说明。
- 地球影像：Three.js 示例 earth_atmos_2048.jpg；Three.js 0.170.0，MIT 许可证已包含在 dist/vendor。
- 轨迹按原文件坐标直接导入，未进行坐标系转换。地表贴合只是显示处理，海拔曲线保留导入记录值；不能作为户外导航或通行依据。

本次是验证视觉与交互的单路线原型。未接全国路线库、登录、云端收藏、GPX 导入或户外导航。

## 检查

`python check_preview.py` 使用本机 Edge 检查地球/山体切换、播放、进度拖动、收藏持久化、空山册和手机宽度，并将截图写入 checks/。需先运行预览服务。
