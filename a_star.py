"""A*搜索算法，用于CBS的底层搜索"""
from entity import *
import heapq

"""Step类（存储路径节点的信息）"""
class Step():
    def __init__(self, x, y, parent, time):
        self.x = x # x坐标
        self.y = y # y坐标
        self.parent = parent  # 父节点
        self.time = time # 当前时间

    # 设置优先级
    def set_priority(self, g, h):
        self.g = g # g(n)起点到当前点的代价（也等同于时间）
        self.h = h # h(n)当前点到目标点的曼哈顿距离
        self.priority = g + h # 优先级f(n) = g(n) + h(n)

    # 重载
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.time == other.time
    def __hash__(self):
        return hash(str(self.x) + str(self.y) + str(self.time))
    def __lt__(self, other):
        return self.priority < other.priority

"""A*搜索算法类"""
class A_Star():
    begin = [-1,-1] # 起点
    end = [-1,-1] # 终点
    step_cost = 1 # 每一步的代价
    vertex_constraints = [] # 顶点约束集
    edge_constraints = [] # 边约束集
    agent_id = None # 智能体ID

    # 初始化
    def __init__(self, size, obstacles):
        self.size = size # 地图大小
        self.obstacles = obstacles # 障碍物
        # 初始化地图
        self.map = [[ 0 for j in range(self.size[1])] for i in range(self.size[0])]
        for obstacle in self.obstacles:
            self.map[obstacle[0]][obstacle[1]] = 1 # 障碍物
    
    # h(n)启发函数：曼哈顿距离
    def h(self, step):
        return abs(self.end[0] - step.x) + abs(self.end[1] - step.y)
    
    # 检查当前约束
    def check_constraints(self, current, target, time):
        # 顶点约束
        for constraint in self.vertex_constraints:
            if(constraint.time == time):
                if(list(constraint.location) == list(target)):
                    return False

        # 边约束
        for constraint in self.edge_constraints:
            if(constraint.time == time):
                if(list(constraint.begin) == list(current) and list(constraint.end) == list(target)):
                    return False
        return True

    # 检查当前时刻是否存在约束
    def check_current_having_constraints(self, time):
        for constraint in self.vertex_constraints:
            if(constraint.time == time):
                return True
        for constraint in self.edge_constraints:
            if(constraint.time == time):
                return True
        return False

    # 构建完整路径
    def build_complete_path(self, current_step):
        path = [] # 路径数组
        while current_step:
            path.append([current_step.x, current_step.y])
            current_step = current_step.parent
        return path[::-1] # 反转
    
    # 获取邻居
    def get_neighbors(self, current_step):
        neighbors = []
        x = current_step.x
        y = current_step.y
        time = current_step.time+1

        # 左
        if(x-1 >= 0 and self.map[x-1][y] == 0 and self.check_constraints([x,y],[x-1, y],time)):
            neighbors.append(Step(x-1, y, current_step, time))
        # 右
        if(x+1 < self.size[0] and self.map[x+1][y] == 0 and self.check_constraints([x,y],[x+1, y],time)):
            neighbors.append(Step(x+1, y, current_step, time))
        # 上
        if(y-1 >= 0 and self.map[x][y-1] == 0 and self.check_constraints([x,y],[x, y-1],time)):
            neighbors.append(Step(x, y-1, current_step, time))
        # 下
        if(y+1 < self.size[1] and self.map[x][y+1] == 0 and self.check_constraints([x,y],[x, y+1],time)):
            neighbors.append(Step(x, y+1, current_step, time))

        # 等待（待思考：该时刻无约束是否应该等待？）
        if(self.check_constraints([x,y],[x,y],time)):
            neighbors.append(Step(x, y, current_step, time))

        return neighbors

    # A*搜索
    def search(self, agent, constraints):
        self.agent_id = agent.id
        self.begin = agent.start
        self.end = agent.goal
        open_list = [] # 待遍历节点
        close_list = set() # 已遍历节点
        self.vertex_constraints = [] # 清空顶点约束集
        self.edge_constraints = [] # 清空边约束集
        max_t = 0 # 最大时间(用于到达终点后仍被碰撞)

        # 初始化约束
        for constraint in constraints:
            if(isinstance(constraint, VertexConstraint)): # 顶点约束
                max_t = max(max_t, constraint.time)
                self.vertex_constraints.append(constraint)
            elif(isinstance(constraint, EdgeConstraint)): # 边约束
                self.edge_constraints.append(constraint)
                
        # 初始化起点
        start = Step(self.begin[0],self.begin[1], None, 0)
        start.set_priority(0, 0) # 设置优先级为最高0
        heapq.heappush(open_list, start)

        # 开始搜索
        count = 0
        while open_list:
            count += 1
            if(count > 999999999):
                print("A*搜索超时,结束")
                return None
            
            current_step = heapq.heappop(open_list) # 最高优先级节点
            # 到达终点
            if current_step.x == self.end[0] and current_step.y == self.end[1] and current_step.time >= max_t:
                # 构建路径
                path = Path(agent) 
                path.set_locations(self.build_complete_path(current_step))
                return path 

            # 未到达终点
            else:
                close_list.add(current_step)
                neighbors = self.get_neighbors(current_step) # 获取可用邻居节点
                for neighbor in neighbors:
                    # 遍历过
                    if neighbor in close_list:
                        continue
                    # 未遍历
                    if neighbor not in open_list:
                        neighbor.set_priority(current_step.g + 1, self.h(neighbor))
                        heapq.heappush(open_list, neighbor)
        return None
