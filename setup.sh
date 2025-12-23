#!/bin/bash

# ==========================================
# MkDocs 自动化构建部署脚本
# 适用环境：Root Crontab 调用 + Homebrew 安装的 uv
# ==========================================

# 遇到错误立即退出
set -e

# --- 1. 变量配置 ---
USER="iris"

# 使用 which uv 获取 uv 的完整路径
# ⚠️⚠️⚠️ 请确认这里是你截图中的完整路径 ⚠️⚠️⚠️
# Homebrew on Linux 的标准路径通常是下面这个
UV_PATH="/home/linuxbrew/.linuxbrew/bin/uv"

# 项目所在目录
PROJECT_DIR="/home/${USER}/blogs"
# 1Panel 网站根目录
TARGET_DIR="/opt/1panel/www/sites/blogs.iris763.cn/index"
# 临时构建目录
TEMP_SITE_DIR="${PROJECT_DIR}/temp_site"

# --- 2. 环境检查 ---
# 检查 uv 路径是否正确
if [ ! -f "$UV_PATH" ]; then
    echo "❌ [$(date)] 错误: 找不到 uv 命令，请检查脚本中的 UV_PATH 变量: $UV_PATH"
    exit 1
fi

# 确保目标目录存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "⚠️ [$(date)] 警告: 目标目录不存在，正在创建..."
    mkdir -p "$TARGET_DIR"
fi

# 切换到项目目录
cd "$PROJECT_DIR"

echo "========================================"
echo "🕒 [$(date)] 开始执行自动化部署..."
echo "========================================"

# --- 3. 拉取最新代码 (以 iris 身份) ---
echo "📥 正在拉取 Git 仓库更新..."
# 使用 sudo -u iris 确保使用 iris 的 SSH Key
sudo -u "$USER" git pull origin main

# --- 4. 构建静态站点 (以 iris 身份) ---
echo "🧹 清理旧构建缓存..."
rm -rf "$TEMP_SITE_DIR"

echo "🚀 开始构建 MkDocs..."
# 即使是 Homebrew 安装的 uv，也建议用 iris 身份运行
# 这样生成的 site 目录权限才是 iris 的
sudo -u "$USER" "$UV_PATH" run mkdocs build -d "$TEMP_SITE_DIR"

# --- 5. 部署到生产环境 (以 Root 身份) ---
echo "📂 正在部署到 1Panel 目录: $TARGET_DIR"
# 清空目标目录内容 (保留目录本身)
rm -rf "$TARGET_DIR"/*
# 将构建产物复制过去
cp -r "$TEMP_SITE_DIR"/. "$TARGET_DIR"/

# --- 6. 权限修复 (以 Root 身份) ---
# 1Panel 默认运行用户
echo "🔐 修复目录权限为 1000:1000..."
chown -R 1000:1000 "$TARGET_DIR"

# --- 7. 收尾清理 ---
echo "🧹 清理临时文件..."
rm -rf "$TEMP_SITE_DIR"

echo "✅ [$(date)] 部署成功完成！"
echo "----------------------------------------"