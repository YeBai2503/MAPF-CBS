"""基于冲突的搜索（Conflict-Based Search）算法"""
from a_star import A_Star
from copy import deepcopy
from entity import Agent,Path,VertexConstraint,EdgeConstraint,VertexConflict,EdgeConflict

"""解决方案类"""
class Solution:
    def __init__(self):
        self.paths = [] # 路径列表
    # 设置路径
    def add_path(self, path):
        self.paths.append(path)
    # # 获取指定智能体某时刻位置
    # def get_location(self, i, time):  
    #     if(time > 0 and time <= len(self.paths[i])):
    #         return self.paths[i].locations[time];
    #     elif(time > len(self.paths[i])):
    #         return env.agents[i].goal
    #     elif(time == 0):
    #         return env.agents[i].start
    #     else:
    #         return None
        

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

"""CT节点"""
class CTNode:
    def __init__(self, constraints, parent):
        self.parent = parent # 父节点
        self.constraints = constraints # 约束列表
        self.left_child = None # 左子节点
        self.right_child = None # 右子节点
        
    # 设置解决方案
    def set_solution(self, solution):
        self.solution = solution # 路径列表
        if(solution is None):
            self.cost = float('inf') # 设置成本为无穷大
        else:
            self.cost = self.__calculate_cost(self.solution) # 成本

    # 重写__eq__和__hash__方法
    def __eq__(self, other):
        return self.get_all_constraints() == other.get_all_constraints()
    def __hash__(self):
        return hash(str(self.get_all_constraints()))

    # 获取父节点
    def get_parent(self):
        return self.parent
    # 生成左子节点
    def set_left_child(self, constraints):
        self.left_child = CTNode(constraints, self)
        return self.left_child
    # 生成右子节点
    def set_right_child(self, constraints):
        self.right_child = CTNode(constraints, self)
        return self.right_child
    # 获取左子节点
    def get_left_child(self):
        return self.left_child
    # 获取右子节点
    def get_right_child(self):
        return self.right_child
    # 小于
    def __lt__(self, other):
        return self.cost < other.cost
    # 获取完整约束（从根节点到当前节点）
    def get_all_constraints(self):
        constraints = []
        node = self
        while(node is not None):
            constraints.extend(node.constraints)
            node = node.parent
        return constraints

    # 获取指定智能体的全部约束
    def get_agent_constraints(self, agent, constraints):
        agent_constraints = []
        for constraint in constraints:
            if(constraint.agent_id == agent.id):
                agent_constraints.append(constraint)
        return agent_constraints

    # 计算成本
    def __calculate_cost(self, solution):
        sum = 0
        for path in solution.paths:
            sum += path.get_cost()
        return sum
   
    
"""环境类"""
class Environment:
    def __init__(self, agents, size, obstacles):
        self.agents = agents # 智能体列表
        self.size = size # 地图大小
        self.obstacles = obstacles # 障碍物
        self.a_star = A_Star(size, obstacles)
        self.open_list = [] # 待扩展（检查）节点列表
        self.closed_list = [] # 已扩展（检查）节点列表

    # 检查问题合理性（是否有起点重复、终点重复、起点终点与障碍物冲突）
    def check_problem(self):
        start_positions = [] # 起点列表
        goal_positions = [] # 终点列表
        for agent in self.agents:
            # 检查起点重复
            if agent.start in start_positions:
                print("!!起点重复!!")
                return False
            start_positions.append(agent.start)
            # 检查终点重复
            if agent.goal in goal_positions:
                print("!!终点重复!!")
                return False
            goal_positions.append(agent.goal)
            # 检查起点终点与障碍物冲突
            if agent.start in self.obstacles or agent.goal in self.obstacles:
                print("!!起点终点与障碍物冲突!!")
                return False
            if(agent.start[0] < 0 or agent.start[0] >= self.size[0] or agent.start[1] < 0 or agent.start[1] >= self.size[1]):
                print("!!起点超出地图范围!!")
                return False
            if(agent.goal[0] < 0 or agent.goal[0] >= self.size[0] or agent.goal[1] < 0 or agent.goal[1] >= self.size[1]):
                print("!!终点超出地图范围!!")
                return False
        return True

    """冲突检测(第一个冲突)"""
    def search_first_conflict(self,solution):
        if solution is None:
            return 404
        paths = solution.paths

        print("冲突检测：：：：：")
        print("paths[0]",paths[0].locations)
        print("paths[1]",paths[1].locations)
        # 检查顶点冲突
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                # 智能体i和j在t时刻到达同一位置
                for t in range(len(paths[i].locations)):
                    if t>=len(paths[j].locations):
                        break
                    if paths[i].locations[t] == paths[j].locations[t]:
                        print("顶点冲突："+str(paths[i].locations[t])+" "+str(t+1))
                        return VertexConflict(self.agents[i], self.agents[j], paths[i].locations[t], t)
        # 检查边冲突
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                # 智能体i和j在t时刻交换位置
                for t in range(len(paths[i].locations)-1):
                    if t>=len(paths[j].locations)-1:
                        break
                    if(paths[i].locations[t] == paths[j].locations[t+1] and paths[i].locations[t+1] == paths[j].locations[t]):
                        print("/////////边冲突："+str(paths[i].locations[t])+" "+str(t+1))
                        return EdgeConflict(self.agents[i], self.agents[j], paths[i].locations[t], paths[j].locations[t], t+1)
        return None

    """冲突解决"""
    def resolve_conflict(self, best_node, conflict):
        # 顶点冲突
        if(isinstance(conflict, VertexConflict)):
            # 添加约束
            constraint1 = VertexConstraint(conflict.agent1.id, conflict.location, conflict.time)
            constraint2 = VertexConstraint(conflict.agent2.id, conflict.location, conflict.time)
            
            print("1constraint1"+constraint1.agent_id + " " + str(constraint1.location) + " " + str(constraint1.time))
            print("2constraint2"+constraint2.agent_id + " " + str(constraint2.location) + " " + str(constraint2.time))
            
            best_node.set_left_child([constraint1]) 
            best_node.set_right_child([constraint2])
            best_node.left_child.set_solution(self.get_solution(best_node.left_child))
            best_node.right_child.set_solution(self.get_solution(best_node.right_child))

            if(best_node.left_child.solution is not None):
                print("best_node.left_child.solution",best_node.left_child.solution.paths[0].locations,best_node.left_child.solution.paths[1].locations)
            if(best_node.right_child.solution is not None):
                print("best_node.right_child.solution",best_node.right_child.solution.paths[0].locations,best_node.right_child.solution.paths[1].locations)
            
            # 添加子节点
            self.open_list.append(best_node.left_child)
            self.open_list.append(best_node.right_child)
        # 边冲突
        elif(isinstance(conflict, EdgeConflict)):
            # 添加约束
            constraint1 = EdgeConstraint(conflict.agent1.id, conflict.begin, conflict.end, conflict.time)
            #### 注意：agent2的begin和end是相反的
            constraint2 = EdgeConstraint(conflict.agent2.id, conflict.end, conflict.begin, conflict.time)
            
            print("3constraint1" + constraint1.agent_id + " " + str(constraint1.begin) + " " + str(constraint1.end) + " " + str(constraint1.time))
            print("4constraint2" + constraint2.agent_id + " " + str(constraint2.begin) + " " + str(constraint2.end) + " " + str(constraint2.time))
            
            
            best_node.set_left_child([constraint1]) 
            best_node.set_right_child([constraint2])
            best_node.left_child.set_solution(self.get_solution(best_node.left_child))
            best_node.right_child.set_solution(self.get_solution(best_node.right_child))
            # 添加子节点
            self.open_list.append(best_node.left_child)
            self.open_list.append(best_node.right_child)
        return None

    # 获取解决方案
    def get_solution(self, ctNode): 
        all_constraints = ctNode.get_all_constraints()
        solution = Solution()
        # 根节点: 初始化所有解决方案
        if(ctNode.parent is None): 
            for agent in self.agents:
                agent_constraints = ctNode.get_agent_constraints(agent, all_constraints)
                path = self.a_star.search(agent, agent_constraints)
                if path is None:
                    print("agent"+str(agent.id)+"无解决方案")
                    return None
                solution.add_path(path)
        # 非根节点: 更新新增约束的智能体的解决方案，继承父节点其他解决方案
        else:
            solution = deepcopy(ctNode.parent.solution)
            for constraint in ctNode.constraints:
                current_agent_id = constraint.agent_id
                current_agent = None
                current_agent_index = -1
                for i in range(len(self.agents)):
                    if(self.agents[i].id == current_agent_id):
                        current_agent = self.agents[i]
                        current_agent_index = i
                if(current_agent is None):
                    print("agent"+str(current_agent_id)+"不存在")
                    return None
                else:
                    current_agent_constraints = ctNode.get_agent_constraints(current_agent, all_constraints)
                    path = self.a_star.search(current_agent, current_agent_constraints)
                    if path is None:
                        print("agent"+str(current_agent_id)+"无解决方案")
                        return None
                    else:
                        solution.paths[current_agent_index] = path
        return solution

    # 更新一个智能体的解决方案路径?
    def update_solution(self, ctNode, agent_id):
        return None


"""CBS主函数"""
def cbs_main(agents, size, obstacles):
    env = Environment(agents, size, obstacles) # 初始化环境
    if(not env.check_problem()): # 检查问题合理性
        return None
    root = CTNode([], None) # 根节点
    env.open_list.append(root) # 添加根节点
    root.set_solution(env.get_solution(root))


    i =1
    # 主循环
    while(env.open_list):
        i+=1
        print(len(env.closed_list))
        if(i>500000000):
            return None

        best_node = min(env.open_list) # 最小成本节点(最佳优先搜索)
        env.open_list.remove(best_node) # 从待扩展节点列表中移除
        env.closed_list.append(best_node) # 添加到已扩展节点列表

        print("—————————————第"+str(i)+"个节点———————————————————————")

        # 冲突检测
        conflict = env.search_first_conflict(best_node.solution) 
        if conflict == 404: # 无解节点
            env.open_list.remove(best_node) # 从待扩展节点列表中移除
            env.closed_list.append(best_node) # 添加到已扩展节点列表
            continue
        elif(conflict):
            # 冲突解决
            env.resolve_conflict(best_node, conflict) 
        else:
            print("成功！！！！")
            return best_node
    return None
