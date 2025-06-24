"""基于冲突的搜索（Conflict-Based Search）算法"""
from a_star import A_Star
from entity import *
from ct_node import CTNode

from copy import deepcopy
import heapq
import sys

"""CBS类"""
class CBS:
    def __init__(self, agents, size, obstacles):
        self.agents = agents # 智能体列表
        self.size = size # 地图大小
        self.obstacles = obstacles # 障碍物
        self.a_star = A_Star(size, obstacles) # 初始化底层规划器（A*算法）
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
            return 404 # 无解的解决方案

        paths = solution.paths
        # 检查顶点冲突
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                max_t = max(len(paths[i].locations),len(paths[j].locations))
                for t in range(max_t):
                    # 注：到达终点后仍可能被碰撞
                    if t>=len(paths[j].locations):
                        if paths[i].locations[t] == paths[j].locations[len(paths[j].locations)-1]:
                            return VertexConflict(self.agents[i], self.agents[j], paths[i].locations[t], t)                        
                    elif t>=len(paths[i].locations):
                        if paths[j].locations[t] == paths[i].locations[len(paths[i].locations)-1]:
                            return VertexConflict(self.agents[i], self.agents[j], paths[j].locations[t], t)  
                    else: # 智能体i和j在t时刻到达同一位置
                        if paths[i].locations[t] == paths[j].locations[t]:
                            return VertexConflict(self.agents[i], self.agents[j], paths[i].locations[t], t)
        # 检查边冲突
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                # 智能体i和j在t时刻交换位置
                for t in range(len(paths[i].locations)-1):
                    if t>=len(paths[j].locations)-1:
                        break
                    if(paths[i].locations[t] == paths[j].locations[t+1] and paths[i].locations[t+1] == paths[j].locations[t]):
                        return EdgeConflict(self.agents[i], self.agents[j], paths[i].locations[t], paths[j].locations[t], t+1)
        return None

    """冲突解决"""
    def resolve_conflict(self, best_node, conflict):
        # 顶点冲突
        if(isinstance(conflict, VertexConflict)):
            # 生成约束
            constraint1 = VertexConstraint(conflict.agent1.id, conflict.location, conflict.time)
            constraint2 = VertexConstraint(conflict.agent2.id, conflict.location, conflict.time)
            
            # 生成CT子节点,并求解决方案（含计算总成本）
            best_node.set_left_child([constraint1]) 
            best_node.set_right_child([constraint2])
            best_node.left_child.set_solution(self.get_solution(best_node.left_child))
            best_node.right_child.set_solution(self.get_solution(best_node.right_child))
            
            # 添加子节点进open_list
            heapq.heappush(self.open_list, best_node.left_child)
            heapq.heappush(self.open_list, best_node.right_child)

        # 边冲突
        elif(isinstance(conflict, EdgeConflict)):
            # 生成约束
            constraint1 = EdgeConstraint(conflict.agent1.id, conflict.begin, conflict.end, conflict.time)
            #### 注意：agent2的begin和end是相反的
            constraint2 = EdgeConstraint(conflict.agent2.id, conflict.end, conflict.begin, conflict.time)
            
            # 生成CT子节点,并求解决方案（含计算总成本）
            best_node.set_left_child([constraint1]) 
            best_node.set_right_child([constraint2])
            best_node.left_child.set_solution(self.get_solution(best_node.left_child))
            best_node.right_child.set_solution(self.get_solution(best_node.right_child))
            
            # 添加子节点进open_list
            heapq.heappush(self.open_list, best_node.left_child)
            heapq.heappush(self.open_list, best_node.right_child)
        return None

    """获取解决方案"""
    def get_solution(self, ctNode): 
        all_constraints = ctNode.get_all_constraints() # 获取完整约束（从根节点到当前节点）
        solution = Solution() # 初始化解决方案

        # 根节点: 初始化所有解决方案
        if(ctNode.parent is None): 
            for agent in self.agents:
                # 获取待求解智能体的全部约束
                agent_constraints = ctNode.get_agent_constraints(agent, all_constraints)
                # 调用底层规划求解
                path = self.a_star.search(agent, agent_constraints)
                
                if path is None: # 无解
                    print(str(agent.id)+"在当前节点约束下无解决方案")
                    return None
                solution.add_path(path)

        # 非根节点: 更新新增约束的智能体的解决方案，继承父节点其他解决方案
        else:
            solution = deepcopy(ctNode.parent.solution)
            for constraint in ctNode.constraints:
                # 获取待求解智能体的信息
                current_agent_id = constraint.agent_id
                current_agent = None
                current_agent_index = -1
                for i in range(len(self.agents)):
                    if(self.agents[i].id == current_agent_id):
                        current_agent = self.agents[i]
                        current_agent_index = i

                # 智能体不存在
                if(current_agent is None):
                    print("agent"+str(current_agent_id)+"不存在")
                    return None
                # 求解    
                else:
                    # 获取待求解智能体的全部约束
                    current_agent_constraints = ctNode.get_agent_constraints(current_agent, all_constraints)
                    # 调用底层规划求解
                    path = self.a_star.search(current_agent, current_agent_constraints)
                    
                    if path is None: # 无解
                        print(str(current_agent_id)+"在当前节点约束下无解决方案")
                        return None
                    else:
                        solution.paths[current_agent_index] = path # 更新该智能体的路径解决方案
        return solution

"""CBS主函数"""
def cbs_main(agents, size, obstacles):
    cbs = CBS(agents, size, obstacles) # 初始化环境
    if(not cbs.check_problem()): # 检查问题合理性
        return None
    root = CTNode([], None) # 根节点
    heapq.heappush(cbs.open_list, root) # 添加根节点
    root.set_solution(cbs.get_solution(root))

    # 主循环
    count = 0 # 计数
    while(cbs.open_list):
        count+=1
        if(count>999999999):
            print("扩展节点数超过999999999，退出")
            return None
        sys.stdout.write(f"\r————————————进度: 第{count}个节点————————————")
        sys.stdout.flush()

        best_node = heapq.heappop(cbs.open_list) # 最小成本节点(最佳优先搜索)
        cbs.closed_list.append(best_node) # 添加到已扩展节点列表

        # 冲突检测
        conflict = cbs.search_first_conflict(best_node.solution) 

        # 无解节点
        if conflict == 404: # 无解节点
            # cbs.open_list.remove(best_node) # 从待扩展节点列表中移除
            # cbs.closed_list.append(best_node) # 添加到已扩展节点列表
            continue
        # 有冲突，解决冲突
        elif(conflict):
            cbs.resolve_conflict(best_node, conflict) # 冲突解决
        # 无冲突，结束
        else:
            print()
            print("成功找到解决方案，共扩展了 "+str(count)+" 个节点")
            return best_node
    return None
