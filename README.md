# JR_CompanyWork iOS

> WebView 壳 App,打包本地 `index.html`(内嵌 iframe 加载 http://uk.frp.one:46767/)。
> 本地页秒开避免白屏,iframe 加载中由页面自身提示。通过 GitHub Actions 云端打包 IPA,无需本地 Mac。

---

## 目录结构

```
ios_project_JR_CompanyWork/
├── .github/workflows/build-ipa.yml   # 云打包 workflow(无签名模式)
├── JR_CompanyWork/                     # 工程源码
│   ├── AppDelegate.swift
│   ├── ViewController.swift           # WKWebView 加载打包内的本地 index.html
│   ├── index.html                      # 本地页面(iframe 内嵌远程站点)
│   ├── Info.plist
│   └── Assets.xcassets/
│       ├── Contents.json
│       └── AppIcon.appiconset/        # 1024×1024 企业大楼主题图标,纯 RGB 无 alpha
├── tools/generate_icon.py             # 重新生成图标脚本
├── build_ipa.sh                       # 本机打包脚本(macOS)
├── exportOptions.plist                # 导出配置(模板)
├── project.yml                        # XcodeGen 工程描述
└── README.md
```

---

## 一、用 GitHub Actions 云打包(推荐,无需 Mac)

> **当前为无签名模式**:workflow 用 `CODE_SIGNING_ALLOWED=NO` 构建,产出未签名 IPA,用来验证「构建 → 打包」流程。
> 未签名 IPA 不能直接安装;用全能签/爱思助手等工具时需自带 Apple ID 重签名。

### 1. 把代码推到 GitHub

```bash
git init && git add -A && git commit -m "init"
git remote add origin git@github.com:<你的用户名>/<仓库>.git
git push -u origin main
```

### 2. 触发打包

- **自动**:push 到 `main` 分支即触发
- **手动**:Actions 页面 → 选择 Build iOS IPA → Run workflow

### 3. 取 IPA

Workflow 跑完后,页面底部 **Artifacts** 区下载 `JR_CompanyWork-IPA`,解压得到 `JR_CompanyWork-unsigned.ipa`(未签名)。

### 4. 安装到 iPhone

未签名 IPA 需用全能签/爱思助手等工具配合 Apple ID 重签名后安装(免费账号 7 天有效)。若工具报「主可执行文件不可用」,请确认 `Info.plist` 中 `CFBundleExecutable` 已显式声明(本项目已修复)。

---

## 二、恢复签名打包(可选)

编辑 `.github/workflows/build-ipa.yml`:
1. 删掉 archive 步骤里的 `CODE_SIGNING_ALLOWED=NO` / `CODE_SIGNING_REQUIRED=NO`
2. 把文件顶部注释里的「导入签名证书与描述文件」步骤粘贴回「生成 Xcode 工程」之后
3. 把「打包 IPA(未签名)」步骤换回 `xcodebuild -exportArchive`
4. 仓库 Secrets 添加:`BUILD_CERTIFICATE_BASE64` / `P12_PASSWORD` / `BUILD_PROVISION_PROFILE_BASE64` / `KEYCHAIN_PASSWORD` / `TEAM_ID`(具体导出步骤见 StockScope 项目的 README)

---

## 三、本机 Mac 直接打包

```bash
brew install xcodegen
# 无签名(验证流程):
UNSIGNED=1 ./build_ipa.sh
# 自动签名(Xcode 已登录 Apple ID):
./build_ipa.sh
# 手动签名:
TEAM_ID=ABCDE12345 ./build_ipa.sh
```

产物:无签名模式在 `build/JR_CompanyWork-unsigned.ipa`,签名模式在 `build/JR_CompanyWork.ipa`。

---

## 注意事项

- **图标重新生成**:修改 `tools/generate_icon.py` 后执行 `python tools/generate_icon.py` 即可。图标必须是纯 RGB 无 alpha(Xcode 15+ 拒绝带透明通道的 AppIcon)。
- **Info.plist 的 `CFBundleExecutable` 必须显式声明**(全能签等工具靠它定位主可执行文件,缺失会报「主可执行文件不可用」)。
