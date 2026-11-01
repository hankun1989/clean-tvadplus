# 最终成功版本的验证记录

2026-11-01，2018 年 MiTV4A / Android 6.0.1 / armeabi-v7a / PatchWall 3.50.1621。最终组合为官方 CMFA 2.11.36.Meta、完整 14 条规则、本仓库启动助手 0.1.0，以及用户批准的云视听旧缓存处理。

| 验证对象 | 实际结果 |
|---|---|
| 小米桌面《大梦归离》 | 原约 110–127 秒片头，处理后用户确认直接进入正片 |
| 独立芒果 TV `com.hunantv.license` | 用户确认直接进入正片；完整重启后再次确认 |
| 独立云视听 `com.ktcp.video` 20.2.0.2004 | 《小马宝莉》长片头消失；获准单应用重置后，约 15 秒化妆品开屏消失 |
| 独立银河奇异果 `com.gitvdemo.video` 16.10.0.221990 | 通过电视官方商店安装，用户确认直接进入正片；该次片名未提供 |
| 最终配置完整重启 | 未手动打开工具/助手；约 30 秒时只读观察到助手和过滤服务自动运行，用户随后确认“这几个地方都没有广告了” |

启动助手组合另完成一轮完整重启：约 39 秒观察到两项服务自动运行，用户从“我的应用 → 芒果 TV”播放并确认直接进入正片。未把配置保存或服务存在单独当作播放验收。

## 去标识的最终运行摘录

```text
CMFA: Sniffer is loaded and working
CMFA: ... t7z.cupid.ptqy.gitv.tv:443
      match DomainSuffix(cupid.ptqy.gitv.tv) using REJECT
CMFA: ... data6.video.ptqy.gitv.tv:443 match Match using DIRECT
CMFA: ... ott.da.mgtv.com:443 match DomainSuffix(da.mgtv.com) using REJECT
CMFA: ... lives.l.aiseet.atianqi.com:80
      match DomainSuffix(lives.l.aiseet.atianqi.com) using REJECT
TVFilterStarter: Requested filter start (service-connected)
```

省略连接地址、设备标识、跟踪参数和账号。原始日志、家庭截图、第三方 APK、运行口令及私有签名材料不发布；仓库只包含最终流程、最终规则、通用脚本及自有助手源码/实测 APK。

测试范围限上述实际样本和固件，不代表所有片源、全部平台或未来版本永久有效。其他固件和平台版本重新核对兼容性与实际播放。机制参考：[官方 CMFA](https://github.com/MetaCubeX/ClashMetaForAndroid)、[域名识别配置](https://wiki.metacubex.one/en/config/sniff/)。
