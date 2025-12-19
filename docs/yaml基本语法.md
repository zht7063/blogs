---
title: yaml-intro
data: 25-12-18
author: iris
tags:
  - basic
  - yaml
---



# Markdown 元数据格式









# YAML 基本语法

## 基本规则

yaml 可以单独作为一个文件，也可以嵌入到 markdown 文件的元数据区。yaml 采用键值对形式标记数据，对空格和缩进十分敏感，要注意以下规则：

1.   使用空格进行缩进：通过空格缩进表示数据的层级关系和嵌套；
2.   严禁使用 tab：只能用空格，绝对不可以存在任何 tab 制表位；
3.   缩进保持一致：同一层级元素必须保持左对齐（保持相同缩进量），通常采用 2-4 个空格作为一级缩进；
4.   冒号和短横线后的空格：
     -   键值对的冒号后面必须跟一个空格；
     -   列表项的短横线后面必须跟一个空格。

*下面是一个简单案例：*

```yaml
views:
  - type: table
    name: 表格
    order:
      - file.name
      - fille.fullname
      - file.tags
      - file.folder
```

## 基本数据结构

YAML 主要由三种基本数据结构组成：纯量（Scalars）、序列（Sequences / List）、和映射（Mappings / Dictionaries）。

### 纯量

纯量是单个的、不可分割的值，是 YAML 中最基本的数据单元。

-   字符串 String：
    -   默认无需引号：`my_str: hello yaml`；
    -   单引号：不会转移特殊字符，所有内容视为字面量；
    -   双引号：会转义特殊字符，如 \n 会被解析为换行符；
-   数字 Number：包含整数或者浮点数；
-   布尔值 Boolean：true 或者 false；
-   空值 Null：使用 null 或者 ~ 表示。

### 序列





### 映射





# YAML 文件和编辑器



# 格式化工具

