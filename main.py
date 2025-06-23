from cbs import *
from a_star import *
import argparse
import yaml

"""主函数"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("param", help="包含地图和障碍物的输入文件")
    parser.add_argument("output", help="输出调度文件")
    args = parser.parse_args()

    # 命令行读取输入文件
    with open(args.param, 'r') as param_file:
        try:
            param = yaml.load(param_file, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)

    # # 指定输入和输出文件路径"map/8x8/map_8by8_obst12_agents8_ex29.yaml"
    # input_file = "input.yaml"  # 指定输入文件路径
    # output_file = "output.yaml"  # 指定输出文件路径
    
    # # 读取输入文件
    # with open(input_file, 'r') as param_file:
    #     try:
    #         param = yaml.load(param_file, Loader=yaml.FullLoader)
    #     except yaml.YAMLError as exc:
    #         print(exc)
    #         return

    # 提取参数
    dimension = param["map"]["dimensions"]
    obstacles = param["map"]["obstacles"]
    agents_param = param['agents']
    agents = []
    for agent_param in agents_param:
        agents.append(Agent(agent_param['name'], agent_param['start'], agent_param['goal']))

    # 执行搜索
    solution_node = cbs_main(agents,dimension,obstacles)

    if not solution_node:
        print("未找到解决方案")
        return

    # 写入输出文件
    output = dict()
    output["schedule"] = generate_plan(solution_node.solution)
    output["cost"] = solution_node.cost
    with open(args.output, 'w') as output_yaml:
    #with open(output_file, 'w') as output_yaml:
        yaml.safe_dump(output, output_yaml)

"""生成输出格式的路径计划"""
def generate_plan(solution):
        plan = {}
        for path in solution.paths:
            # path_dict_list = []
            # path_dict_list.append({'t':0, 'x':path.agent.start[0], 'y':path.agent.start[1]})
            # for i in range(len(path.locations)):
            #     path_dict_list.append({'t':i+1, 'x':path.locations[i][0], 'y':path.locations[i][1]})
            # path_dict_list.append({'t':path.get_cost(), 'x':path.agent.goal[0], 'y':path.agent.goal[1]})
            path_dict_list = []
            for i in range(len(path.locations)):
                path_dict_list.append({'t':i, 'x':path.locations[i][0], 'y':path.locations[i][1]})
            plan[path.agent.id] = path_dict_list
        return plan

if __name__ == "__main__":
    main() 