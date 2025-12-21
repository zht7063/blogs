#!/bin/bash

TARGET_DIR="/opt/1panel/www/sites/blogs.iris763.cn/index"

echo "🚀 开始构建文档..."
uv run mkdocs build -d ./temp_site

echo "📂 部署到 1Panel 目录..."
# 使用 sudo 搬运
sudo cp -r ./temp_site/. $TARGET_DIR/

echo "🔐 修复权限为 1000:1000..."
# 关键步骤：确保 1Panel 的容器能读写这些文件
sudo chown -R 1000:1000 $TARGET_DIR

echo "🧹 清理临时文件..."
rm -rf ./temp_site

echo "✅ 部署完成并已修复权限！"

