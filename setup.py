#!/usr/bin/env python3
"""
自动部署脚本：构建 MkDocs 文档并部署到 1Panel 目录
支持定时任务执行
"""

import subprocess
import shutil
import time
from pathlib import Path
from loguru import logger
import schedule


# 配置路径
TARGET_DIR = Path("/opt/1panel/www/sites/blogs.iris763.cn/index")
TEMP_SITE_DIR = Path("./temp_site")
PROJECT_ROOT = Path(__file__).parent


def build_docs() -> bool:
    """
    构建 MkDocs 文档
    
    Returns:
        bool: 构建是否成功
    """
    logger.info("🚀 开始构建文档...")
    try:
        # 使用 uv run 执行 mkdocs build
        result = subprocess.run(
            ["uv", "run", "mkdocs", "build", "-d", str(TEMP_SITE_DIR)],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True
        )
        logger.success("✅ 文档构建成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 文档构建失败: {e}")
        logger.error(f"错误输出: {e.stderr}")
        return False


def deploy_to_target() -> bool:
    """
    部署构建好的文档到目标目录
    
    Returns:
        bool: 部署是否成功
    """
    logger.info("📂 部署到 1Panel 目录...")
    
    if not TEMP_SITE_DIR.exists():
        logger.error(f"❌ 临时构建目录不存在: {TEMP_SITE_DIR}")
        return False
    
    try:
        # 确保目标目录存在
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        
        # 使用 sudo 复制文件
        logger.info(f"正在复制文件到 {TARGET_DIR}...")
        subprocess.run(
            ["sudo", "cp", "-r", f"{TEMP_SITE_DIR}/.", str(TARGET_DIR)],
            check=True
        )
        
        # 修复权限为 1000:1000
        logger.info("🔐 修复权限为 1000:1000...")
        subprocess.run(
            ["sudo", "chown", "-R", "1000:1000", str(TARGET_DIR)],
            check=True
        )
        
        logger.success("✅ 部署成功并已修复权限")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 部署失败: {e}")
        return False


def cleanup_temp_files() -> None:
    """
    清理临时文件
    """
    logger.info("🧹 清理临时文件...")
    try:
        if TEMP_SITE_DIR.exists():
            shutil.rmtree(TEMP_SITE_DIR)
            logger.success("✅ 临时文件清理完成")
        else:
            logger.info("临时目录不存在，跳过清理")
    except Exception as e:
        logger.warning(f"⚠️ 清理临时文件时出现警告: {e}")


def deploy_task() -> None:
    """
    完整的部署任务：构建 -> 部署 -> 清理
    """
    logger.info("=" * 50)
    logger.info("开始执行部署任务")
    logger.info("=" * 50)
    
    # 构建文档
    if not build_docs():
        cleanup_temp_files()
        return
    
    # 部署到目标目录
    if not deploy_to_target():
        cleanup_temp_files()
        return
    
    # 清理临时文件
    cleanup_temp_files()
    
    logger.info("=" * 50)
    logger.success("🎉 部署任务完成！")
    logger.info("=" * 50)


def main():
    """
    主函数：设置定时任务并运行
    """
    # 处理日志文件权限问题：如果文件存在但无法写入，直接删除重建
    log_file = PROJECT_ROOT / "deploy.log"
    if log_file.exists():
        try:
            # 尝试检查文件是否可写
            with open(log_file, "a"):
                pass
        except PermissionError:
            # 权限不足，直接删除文件
            try:
                log_file.unlink()
            except PermissionError:
                # 如果无法删除（需要 sudo），尝试使用 sudo 删除
                subprocess.run(
                    ["sudo", "rm", "-f", str(log_file)],
                    check=False,
                    capture_output=True
                )
    
    # 配置 loguru
    logger.add(
        str(log_file),
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        encoding="utf-8"
    )
    
    logger.info("部署脚本启动")
    logger.info(f"项目根目录: {PROJECT_ROOT}")
    logger.info(f"目标目录: {TARGET_DIR}")
    logger.info(f"临时目录: {TEMP_SITE_DIR}")
    
    # 设置定时任务（示例：每天凌晨 2 点执行）
    # 可以根据需要修改时间
    # schedule.every().day.at("02:00").do(deploy_task)
    
    # 也可以设置其他时间间隔，例如：
    # schedule.every(6).hours.do(deploy_task)  # 每 6 小时执行一次
    schedule.every().hour.at(":00").do(deploy_task)    # 每小时第0分钟执行（整点执行）
    
    logger.info("定时任务已设置：每小时整点执行任务")
    logger.info("按 Ctrl+C 退出")
    
    # 立即执行一次（可选）
    deploy_task()
    
    # 运行定时任务循环
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出...")
    except Exception as e:
        logger.error(f"发生错误: {e}")
        raise


if __name__ == "__main__":
    main()

