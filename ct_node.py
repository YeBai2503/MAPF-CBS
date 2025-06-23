from entity import *

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
            self.cost = self.__calculate_cost(self.solution) # 计算成本

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
    # 重写__eq__和__hash__方法
    def __eq__(self, other):
        return self.get_all_constraints() == other.get_all_constraints()
    def __hash__(self):
        return hash(str(self.get_all_constraints()))