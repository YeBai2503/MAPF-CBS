'''实体类定义'''

"""智能体类"""
class Agent:
    def __init__(self, id, start, goal):
        self.id = id # 智能体ID
        self.start = start # 智能体起点
        self.goal = goal # 智能体目标点
        self.path = Path(self) # 智能体路径
    # 设置路径
    def set_path(self, path):
        self.path = path
    # 重载
    def __eq__(self, other):
        return self.id == other.id and self.start == other.start and self.goal == other.goal
    def __hash__(self):
        return hash(str(self.id) + str(self.start) + str(self.goal))

"""路径类"""
class Path:
    def __init__(self, agent):
        self.agent = agent # 路径所属智能体
        self.locations = [] # 路径点列表
    # 添加路径点
    def add_location(self, location):
        self.locations.append(location)
    # 设置路径
    def set_locations(self, locations):
        self.locations = locations
    # 获取路径长度
    def get_length(self):
        return len(self.locations)
    # 获取路径成本
    def get_cost(self):
        return len(self.locations) - 1

"""顶点冲突类"""
class VertexConflict:
    def __init__(self, agent1, agent2, location, time):
        self.agent1 = agent1 # 冲突智能体1
        self.agent2 = agent2 # 冲突智能体2
        self.location = location # 冲突位置
        self.time = time # 冲突时间

"""边冲突类"""
class EdgeConflict:
    def __init__(self, agent1, agent2, begin, end, time):
        self.agent1 = agent1 # 冲突智能体1
        self.agent2 = agent2 # 冲突智能体2
        self.begin = begin # 冲突起点（agent1所在位置）
        self.end = end # 冲突终点（agent2所在位置）
        self.time = time # 冲突时间

"""顶点约束类"""
class VertexConstraint:
    def __init__(self, agent_id, location, time):
        self.agent_id = agent_id # 约束智能体ID
        self.location = location # 约束位置
        self.time = time # 约束时间

    # 重载
    def __eq__(self, other):
        if not isinstance(other, VertexConstraint):
            return False
        return self.agent_id == other.agent_id and self.time == other.time and self.location == other.location
    # def __hash__(self):
    #     return hash(str(self.agent_id) + str(self.time) + str(self.location))

"""边约束类"""
class EdgeConstraint:
    def __init__(self, agent_id, begin, end, time):
        self.agent_id = agent_id # 约束智能体ID
        self.begin = begin # 约束起点
        self.end = end # 约束终点(time到达)
        self.time = time # 约束时间

    # 重载
    def __eq__(self, other):
        if not isinstance(other, EdgeConstraint):
            return False
        return self.agent_id == other.agent_id and self.time == other.time \
            and self.begin == other.begin and self.end == other.end
    # def __hash__(self):
    #     return hash(str(self.agent_id) + str(self.time) + str(self.begin) + str(self.end))

"""解决方案类"""
class Solution:
    def __init__(self):
        self.paths = [] # 路径列表
    # 设置路径
    def add_path(self, path):
        self.paths.append(path)

"""约束列表类"""
class Constraints:
    def __init__(self):
        self.vertex_constraints = [] # 顶点约束列表
        self.edge_constraints = [] # 边约束列表
    # 添加约束
    def add_constraint(self, constraint):
        if(isinstance(constraint, VertexConstraint)):
            self.vertex_constraints.append(constraint)
        elif(isinstance(constraint, EdgeConstraint)):
            self.edge_constraints.append(constraint)