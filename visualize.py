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
Colors = ['orange', 'blue', 'green']


class Animation:
    """动画类，用于可视化多智能体路径规划结果"""
    def __init__(self, map, schedule):
        """初始化动画类
        
        参数:
            map: 地图信息，包含尺寸、障碍物和智能体起始/目标位置
            schedule: 调度信息，包含每个智能体的运动路径
        """
        self.map = map
        self.schedule = schedule
        self.combined_schedule = {}
        self.combined_schedule.update(self.schedule["schedule"])

        # 计算地图宽高比
        aspect = map["map"]["dimensions"][0] / map["map"]["dimensions"][1]

        # 创建图形和坐标轴
        self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
        self.ax = self.fig.add_subplot(111, aspect='equal')
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
        self.patches.append(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='red'))
        
        # 添加障碍物
        for o in map["map"]["obstacles"]:
            x, y = o[0], o[1]
            self.patches.append(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='red', edgecolor='red'))

        # 初始化时间步
        self.T = 0
        
        # 先绘制目标位置
        for d, i in zip(map["agents"], range(0, len(map["agents"]))):
            self.patches.append(Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, facecolor=Colors[0], edgecolor='black', alpha=0.5))
        
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
                               interval=100,
                               blit=True)

    def save(self, file_name, speed):
        """保存动画到文件
        
        参数:
            file_name: 文件名
            speed: 播放速度
        """
        # 获取文件扩展名
        _, ext = os.path.splitext(file_name)
        
        # 如果文件扩展名不是.gif，则自动转换为.gif
        if ext.lower() != '.gif':
            print(f"注意: 将输出格式从{ext}更改为.gif，因为默认使用Pillow保存")
            file_name = os.path.splitext(file_name)[0] + '.gif'
            
        # 使用Pillow保存为GIF
        self.anim.save(file_name, writer='pillow', fps=10 * speed, dpi=200)
        print(f"已保存动画到 {file_name}")

    def show(self):
        """显示动画"""
        plt.show()

    def init_func(self):
        """动画初始化函数"""
        for p in self.patches:
            self.ax.add_patch(p)
        for a in self.artists:
            self.ax.add_artist(a)
        return self.patches + self.artists

    def animate_func(self, i):
        """动画更新函数
        
        参数:
            i: 当前帧索引
        """
        # 更新每个智能体的位置
        for agent_name, agent in self.combined_schedule.items():
            pos = self.getState(i / 10, agent)
            p = (pos[0], pos[1])
            self.agents[agent_name].center = p
            self.agent_names[agent_name].set_position(p)

        # 重置所有智能体的颜色
        for _,agent in self.agents.items():
            agent.set_facecolor(agent.original_face_color)

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

    def getState(self, t, d):
        """获取智能体在时间t的状态
        
        参数:
            t: 时间点
            d: 智能体的路径数据
            
        返回:
            智能体在时间t的位置
        """
        idx = 0
        while idx < len(d) and d[idx]["t"] < t:
            idx += 1
        if idx == 0:
            return np.array([float(d[0]["x"]), float(d[0]["y"])])
        elif idx < len(d):
            posLast = np.array([float(d[idx-1]["x"]), float(d[idx-1]["y"])])
            posNext = np.array([float(d[idx]["x"]), float(d[idx]["y"])])
        else:
            return np.array([float(d[-1]["x"]), float(d[-1]["y"])])
        dt = d[idx]["t"] - d[idx-1]["t"]
        t = (t - d[idx-1]["t"]) / dt
        pos = (posNext - posLast) * t + posLast
        return pos

def show_map_only(map_file):
    with open(map_file) as f:
        map_data = yaml.load(f, Loader=yaml.FullLoader)
    aspect = map_data["map"]["dimensions"][0] / map_data["map"]["dimensions"][1]
    fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
    ax = fig.add_subplot(111, aspect='equal')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=None, hspace=None)
    xmin = -0.5
    ymin = -0.5
    xmax = map_data["map"]["dimensions"][0] - 0.5
    ymax = map_data["map"]["dimensions"][1] - 0.5
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    # 边界
    ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='red'))
    # 障碍物
    for o in map_data["map"]["obstacles"]:
        x, y = o[0], o[1]
        ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='red', edgecolor='red'))
    # 目标点
    for d in map_data["agents"]:
        ax.add_patch(Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, facecolor=Colors[0], edgecolor='black', alpha=0.5))
    # 起点
    for d in map_data["agents"]:
        ax.add_patch(Circle((d["start"][0], d["start"][1]), 0.3, facecolor=Colors[0], edgecolor='black'))
        ax.text(d["start"][0], d["start"][1], d["name"].replace('agent', ''), ha='center', va='center')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map", help="包含地图的输入文件")
    parser.add_argument("schedule", nargs="?", default=None, help="智能体调度计划文件")
    parser.add_argument('--video', dest='video', default=None, help="输出视频文件（默认为GIF格式，留空则在屏幕上显示）")
    parser.add_argument("--speed", type=int, default=1, help="播放速度倍数")
    parser.add_argument("--dpi", type=int, default=200, help="输出图像的DPI（分辨率）")
    parser.add_argument("--showMap", action="store_true", help="只显示地图和障碍物")
    args = parser.parse_args()

    if args.showMap:
        show_map_only(args.map)
        exit()
    # 读取地图文件
    with open(args.map) as map_file:
        map = yaml.load(map_file, Loader=yaml.FullLoader)

    # 读取调度文件
    with open(args.schedule) as states_file:
        schedule = yaml.load(states_file, Loader=yaml.FullLoader)

    # 创建动画
    animation = Animation(map, schedule)

    # 保存或显示动画
    if args.video:
        animation.save(args.video, args.speed)
    else:
        animation.show() 