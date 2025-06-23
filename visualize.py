# 可视化工具

import yaml
import matplotlib
from matplotlib.patches import Circle, Rectangle, Arrow
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import matplotlib.animation as manimation
import argparse
import math
import os

# 定义智能体的颜色
Colors = ['yellow', 'skyblue', 'green']

"""动画类，用于可视化路径规划结果"""
class Animation:
    def __init__(self, map, schedule):
        self.map = map # 地图信息，包含尺寸、障碍物和智能体起始/目标位置
        self.schedule = schedule # 调度信息，包含每个智能体的运动路径
        self.combined_schedule = {} # 合并后的调度信息，包含所有智能体的运动路径
        self.combined_schedule.update(self.schedule["schedule"]) # 合并调度信息

        # 计算地图宽高比
        aspect = map["map"]["dimensions"][0] / map["map"]["dimensions"][1]

        # 创建图形和坐标轴
        self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
        self.ax = self.fig.add_subplot(111, aspect='equal')
        self.ax.set_facecolor('ivory')  # 设置为象牙色背景
        # 边距间距
        self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1, wspace=None, hspace=None)

        # 初始化图形元素
        self.patches = []
        self.artists = []
        self.agents = dict()
        self.agent_names = dict()
        
        # 创建边界
        xmin = -0.5
        ymin = -0.5
        xmax = map["map"]["dimensions"][0] - 0.5
        ymax = map["map"]["dimensions"][1] - 0.5

        # 设置坐标轴范围
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)

        # 添加边界矩形
        self.patches.append(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='gray', linewidth=10))
        
        # 添加障碍物
        for o in map["map"]["obstacles"]:
            x, y = o[0], o[1]
            self.patches.append(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='gray', edgecolor='gray'))

        # 初始化时间步
        self.T = 0
        
        # 先绘制目标位置
        for d, i in zip(map["agents"], range(0, len(map["agents"]))):
            self.patches.append(Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, facecolor=Colors[1], edgecolor='black', alpha=0.5))
            goal_text = self.ax.text(d["goal"][0], d["goal"][1], d["name"].replace('agent', ''), 
                            alpha=0.7)  # 设置透明度使其不太突兀
            goal_text.set_horizontalalignment('center')
            goal_text.set_verticalalignment('center')
            self.artists.append(goal_text)
    
        
        # 创建智能体图形
        for d, i in zip(map["agents"], range(0, len(map["agents"]))):
            name = d["name"]
            self.agents[name] = Circle((d["start"][0], d["start"][1]), 0.3, facecolor=Colors[0], edgecolor='black')
            self.agents[name].original_face_color = Colors[0]
            self.patches.append(self.agents[name])
            self.T = max(self.T, schedule["schedule"][name][-1]["t"])
            self.agent_names[name] = self.ax.text(d["start"][0], d["start"][1], name.replace('agent', ''))
            self.agent_names[name].set_horizontalalignment('center')
            self.agent_names[name].set_verticalalignment('center')
            self.artists.append(self.agent_names[name])

        # 创建动画
        self.anim = manimation.FuncAnimation(self.fig, self.animate_func,
                               init_func=self.init_func,
                               frames=int(self.T+1) * 10, 
                               interval=100, # 帧率10
                               blit=True)

    """保存动画到文件"""
    def save(self, file_name, speed):
        # 获取文件扩展名
        _, ext = os.path.splitext(file_name)
        
        # 如果文件扩展名不是.gif，则自动转换为.gif
        if ext.lower() != '.gif':
            print(f"注意: 输出格式将从{ext}改为.gif，因为默认使用Pillow保存")
            file_name = os.path.splitext(file_name)[0] + '.gif'
            
        # 使用Pillow保存为GIF
        self.anim.save(file_name, writer='pillow', fps=10 * speed, dpi=200)
        print(f"已保存动画到 {file_name}")

    """显示动画"""
    def show(self):
        plt.show()

    """动画初始化函数"""
    def init_func(self):
        for p in self.patches:
            self.ax.add_patch(p)
        for a in self.artists:
            self.ax.add_artist(a)
        return self.patches + self.artists

    """动画更新函数"""
    def animate_func(self, i):
        current_time = i / 10
        # 更新每个智能体的位置
        for agent_name, agent in self.combined_schedule.items():
            pos = self.getState(current_time, agent)
            p = (pos[0], pos[1])
            self.agents[agent_name].center = p
            self.agent_names[agent_name].set_position(p)

            # 获取智能体路径的最后时间点
            last_time = agent[-1]["t"]
            
            # 如果当前时间已经达到或超过最后时间点，表示已到达终点
            if current_time >= last_time:
                self.agents[agent_name].set_facecolor(Colors[1])  # 蓝色(Colors[1])
            else:
                self.agents[agent_name].set_facecolor(self.agents[agent_name].original_face_color)

        # 重置所有智能体的颜色
        # for _,agent in self.agents.items():
        #     agent.set_facecolor(agent.original_face_color)

        # 检查智能体之间的碰撞
        agents_array = [agent for _,agent in self.agents.items()]
        for i in range(0, len(agents_array)):
            for j in range(i+1, len(agents_array)):
                d1 = agents_array[i]
                d2 = agents_array[j]
                pos1 = np.array(d1.center)
                pos2 = np.array(d2.center)
                if np.linalg.norm(pos1 - pos2) < 0.7:
                    d1.set_facecolor('red')
                    d2.set_facecolor('red')
                    print("碰撞! (智能体-智能体) ({}, {})".format(i, j))

        return self.patches + self.artists

    """获取智能体在时间t的状态"""
    def getState(self, t, d):
        # 找到时间t对应的索引位置
        idx = 0
        while idx < len(d) and d[idx]["t"] < t:
            idx += 1
        
        # 如果时间t小于第一个时间点，返回初始位置
        if idx == 0:
            return np.array([float(d[0]["x"]), float(d[0]["y"])])
        # 如果时间t在路径时间范围内，计算插值位置
        elif idx < len(d):
            # 获取前一个时间点的位置
            posLast = np.array([float(d[idx-1]["x"]), float(d[idx-1]["y"])])
            # 获取后一个时间点的位置
            posNext = np.array([float(d[idx]["x"]), float(d[idx]["y"])])
        # 如果时间t大于最后一个时间点，返回最终位置
        else:
            return np.array([float(d[-1]["x"]), float(d[-1]["y"])])
        
        # 计算时间插值系数(0~1之间)
        dt = d[idx]["t"] - d[idx-1]["t"]
        t = (t - d[idx-1]["t"]) / dt
        
        # 线性插值计算位置: pos = posLast + t * (posNext - posLast)
        pos = (posNext - posLast) * t + posLast
        return pos

"""仅显示静态地图，包括障碍物、起点和终点"""
def show_map_only(map_file):
    # 读取地图数据
    with open(map_file) as f:
        map_data = yaml.load(f, Loader=yaml.FullLoader)
    
    # 计算地图的宽高比例，用于设置图形窗口大小
    aspect = map_data["map"]["dimensions"][0] / map_data["map"]["dimensions"][1]
    
    # 创建图形窗口，无边框，大小根据地图比例设置
    fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
    
    # 添加子图，设置等比例坐标系
    ax = fig.add_subplot(111, aspect='equal')
    
    # 调整图形，让内容占满整个窗口(无边距)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=None, hspace=None)
    
    # 设置坐标轴范围，考虑单元格中心点坐标
    xmin = -0.5
    ymin = -0.5
    xmax = map_data["map"]["dimensions"][0] - 0.5
    ymax = map_data["map"]["dimensions"][1] - 0.5
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    
    # 绘制地图边界(红色边框)
    ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='red'))
    
    # 绘制障碍物(红色方块)
    for o in map_data["map"]["obstacles"]:
        x, y = o[0], o[1]
        ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='red', edgecolor='red'))
    
    # 绘制智能体目标点(半透明彩色方块)
    for d in map_data["agents"]:
        ax.add_patch(Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, 
                              facecolor=Colors[0], edgecolor='black', alpha=0.5))
    
    # 绘制智能体起点(彩色圆形)和标签
    for d in map_data["agents"]:
        # 绘制圆形表示起点
        ax.add_patch(Circle((d["start"][0], d["start"][1]), 0.3, 
                           facecolor=Colors[0], edgecolor='black'))
        # 添加智能体编号文本(去掉"agent"前缀)
        ax.text(d["start"][0], d["start"][1], d["name"].replace('agent', ''), 
                ha='center', va='center')
    
    # 显示图形
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # 命令行参数
    parser.add_argument("input", help = "输入文件（包含地图、智能体、障碍物等信息）")
    parser.add_argument("output", nargs="?", default=None, help = "输出文件（解决方案，含规划的路径和总代价）")
    parser.add_argument('--save', dest='video', default=None, help="输出视频文件（默认为GIF格式，留空则在屏幕上显示）")
    parser.add_argument("--speed", type=int, default=1, help="播放速度倍数")
    parser.add_argument("--dpi", type=int, default=200, help="输出图像的DPI（分辨率）")
    parser.add_argument("--showMap", action="store_true", help="只显示静态地图")
    # 解析命令行参数
    args = parser.parse_args()

    if args.showMap:
        show_map_only(args.input)
        exit()
    # 读取地图文件
    with open(args.input) as map_file:
        map = yaml.load(map_file, Loader=yaml.FullLoader)

    # 读取调度文件
    with open(args.output) as states_file:
        schedule = yaml.load(states_file, Loader=yaml.FullLoader)

    # 创建动画
    animation = Animation(map, schedule)

    # 保存动画
    if args.video:
        animation.save(args.video, args.speed)
    animation.show() # 显示动画