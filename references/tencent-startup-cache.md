# 云视听旧开屏缓存的最终处理

读取时机：独立云视听 `com.ktcp.video` 已应用本仓库完整规则，视频可正常播放，但进入应用仍播放旧开屏广告。实测版本 `20.2.0.2004` / versionCode `1276008`。

## 已验证的完整方法

1. 保持最终配置生效，包含开屏取单 `news-l.play.aiseet.atianqi.com` 与视频广告订单 `lives.l.aiseet.atianqi.com`，正常共享内容域放行。
2. 确认进入云视听仍有开屏广告，核对需要保留的账号、本机设置、本地记录及离线视频。
3. 若需重置，说明会退出登录并清除目标应用本机数据，取得**仅重置云视听**的明确同意。没有完整备份的私有账号数据不能承诺恢复。
4. 仅在获准后执行单应用重置：

```sh
adb -s "$SERIAL" shell pm clear com.ktcp.video
```

5. 核对成功，重新打开该应用。验证开屏、同一免费剧集的片头和正常播放；由用户自行重新登录，按需要恢复应用偏好。最后按整体流程完整重启验收。

本例在完整规则生效、用户同意重置后，化妆品开屏消失；最终整机重启后用户确认所测几个入口均无广告。其他应用不默认重置。

## 为什么需要区分私有订单

该版本开屏订单保存于 Context.getFilesDir() 下：

```text
files/tad_cache/splash_cache/tadSplashData
files/tad_cache/splash/DATAOCD
```

SDK 可从本地订单播放旧广告。普通 cacheDir 与这些私有文件范围不同，不能把“清缓存”替代成本节已验证的数据重置，也不能把品牌轮换当成新取单成功。普通 shell 无权访问私有文件时，不宣称已定向删除。

本仓库不提供清空整个 files/shared_prefs/数据库目录的命令，不修改原 APK 或系统权限。

## 保持内容正常

最终规则精确匹配实际广告域。`vmat.gtimg.com`、`tv.aiseet.atianqi.com`、`vv.play.aiseet.atianqi.com` 等共享内容/功能域保持放行。不要扩大成整个腾讯、atianqi 或 gtimg 域的封禁。平台更新后按新的实际连接验证。
