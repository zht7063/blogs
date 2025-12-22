---
title: py-schedule
tags:
  - packages
---

schedule 是一个 python 的定时/计划包，可以用于实现定时自动化功能，比如定时启动指定的程序代码。下面简单介绍 schedule 包的使用方法。

# Schedule 包

我们首先需要安装并导入 schedule 包到项目中，下面顺手定义一个获取当前时间的函数：

```python
# uv add schedule
import schedule
import time
from loguru import logger


def get_time() -> str:
    """
    Gets time current time and return it as a string:

    Returns:
        str: The current time in the format of "HH:MM:SS"

    Examples:
        09:09:30 (22/12/25)
    """
    return time.strftime("%H:%M:%S (%d/%m/%y)")


def task():
    print("Doing task ...", get_time())

```

接下来我们就可以以 task 作为需要计划执行的任务，对其进行 schedule。

## 间隔运行

首先，最简单的方法是设置间隔运行，schedule 通过 every 函数定义间隔时间，通过 seconds 函数定义间隔单位（seconds、minutes、hours、days、weeks），最后通过 do 函数定义需要 schedule 的函数，比如：

```python
schedule.every(5).seconds.do(task)
```

此外，定义了计划之后，需要用 run_pending 函数让 schedule，由于 schedule 本身没有自己让自己执行 run 的能力，所以需要在外面嵌套一个死循环，比如：

```python
while True:
		schedule.run_pending()
		time.sleep(1)
```

这样就可以启动一个每隔 5 秒钟自动执行一次的任务。下面是（除了 task 以及前面的定义以外的）完整代码：

```python
schedule.every(5).seconds.do(task)


if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)

```

## 指定执行时间

我们还可以指定 schedule 的精确运行时间，比如每分钟第 15 秒的时候执行任务。此时，`every()` 将不需要传入内容，通过 `minute.ai(":15").do(task)` 实现定时执行命令的功能。

```python
schedule.every().minute(":15").do(task) # 每分钟第 15 秒的时候执行一次
schedule.every().hour(":15").do(task) # 每小时 15 分的时候执行一次
```

或者，如果觉得每个小时还是有点频繁，则可以在 `every` 中添加限定，如每 10 小时的 15 分执行任务：

```python
schedule.every(10).hour(":15").do(task)
```

此外，这个方法还有一个特殊用法，比如每周一（早上六点）执行任务：

```python
schedule.every().monday.do(task)
schedule.every().monday.at("6:00").do(task)
```

## 装饰器

`schedule` 还提供了装饰器功能，两个常见的装饰器如：

```python
from schedule import repeat, every
```

对于需要计划执行的函数，使用 `@repeat()` 并传入 `every` 指定间隔，如：

```python
@repeat(every(5).seconds)
def task():
    print("Doing task ...", time.strftime("%H:%M:%S (%d/%m/%y)"))

while True:
  schedule.run_pending()
  time.sleep(1)
```

> 注意，一个 repeat 装饰器相当于一行 schedule 定义，所以可以为同一个函数同时添加多个装饰器，以进行不同频率、不同参数的函数定期执行。

## 传参

对于这样重复执行的 task，同样也可以为其传入参数。我们从函数调用和装饰器两个角度说明传参的方法。

对于手动安排的 schedule，可以直接在 `do` 中跟随参数列表，实现参数传递，比如：

```python
def task(args1, args2):
    print(args1, args2)
    print("Doing task ...", time.strftime("%H:%M:%S (%d/%m/%y)"))

schedule.every(5).seconds.do(task, "Hello", "World")
```

对于使用装饰器的任务，可以通过在装饰器中额外添加参数的方式实现：

```python
@repeat(every(10).seconds, "Python", "is fun")
def task2(args1, args2):
    print(args1, args2)
    print("Doing task 2 ...", time.strftime("%H:%M:%S (%d/%m/%y)"))
```

此外，死循环不能缺省：

```python
while True:
    schedule.run_pending()
    time.sleep(1)
```

## 取消 schedule

在定义任务后，我们可以获取其实例：

```python
job = schedule.every(5).seconds.do(task)
```

此外，也可以通过 `schedule.get_jobs()` 获取所有 job 实例：

```python
jobs = schedule.get_jobs()
```

于是，获取到 job 实例之后，我们就可以取消他：

```python
schedule.cancle_job(job)
```

## 一次性 job

如果我们的 task 只需要执行一次，要怎么做？

需要让函数返回一个特殊值 `schedule.CancelJob`。

```python
def task():
    print("Doing task ...", time.strftime("%H:%M:%S (%d/%m/%y)"))

    return schedule.CancelJob


schedule.every(5).seconds.do(task)
```

这样，当 task 执行结束后，将会自动取消 schedule 功能。

---

此外，通过 `schedule.clear` 函数，可以批量取消任务。

运行任务的时候，通过 `.tag` 可以为为不同的任务设置不同的标签，

```python
schedule.every(5).seconds.do(task).tag("t1")
schedule.every(5).seconds.do(task).tag("t1", "p1")
schedule.every(5).seconds.do(task).tag("t2", "p1", "k1")

print(f"t1 tasks: {len(schedule.get_jobs('t1'))}")
print(f"p1 tasks: {len(schedule.get_jobs('p1'))}")
print(f"k1 tasks: {len(schedule.get_jobs('k1'))}")
```

## 其他内容

### 设置间隔范围

通过 `.to()` 可以为定时任务设置间隔范围：

```python
schedule.every(1).to(10).seconds.do(task)
```

### 立刻执行全部内容

通过 `schedule.run_all([delay_seconds=10])` 可以立刻执行所有任务，然后再进行间隔计划之行。

```python
schedule.run_all()
# or add delay_seconds.
schedule.run_all(delay_seconds=10)
```

### 并发执行

为了避免程序阻塞，我们可以加入线程进行处理。

```python
import schedule
from schedule import repeat, every
import time
import threading

def task():
    print("Task: ", time.strftime("%H:%M:%S (%d/%m/%y)"))
    time.sleep(5)


def start_thread(func):
    job_one = threading.Thread(target=func)
    job_one.start()


schedule.every(1).seconds.do(start_thread, task)

```

