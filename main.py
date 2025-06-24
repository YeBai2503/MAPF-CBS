from cbs import *
from a_star import *
from visualize import *
import yaml
import argparse

"""主函数"""
def main():
    # 默认文件路径  "map/8x8/map_8by8_obst12_agents8_ex1.yaml" "map/32x32/map_32by32_obst204_agents30_ex1.yaml"
    input_file = "map/32x32/map_32by32_obst204_agents20_ex2.yaml"  # 指定输入文件路径
    output_file = "output.yaml"  # 指定输出文件路径

    # 创建ArgumentParser对象，解析命令行参数
    parser = argparse.ArgumentParser() 
    parser.add_argument("--input", help = "输入文件（包含地图、智能体、障碍物等信息）", default = input_file)
    parser.add_argument("--output", help = "输出文件（解决方案，含规划的路径和总代价）", default = output_file)
    # 解析命令行参数
    args = parser.parse_args() 

    # 命令行读取输入文件
    with open(args.input, 'r') as param_file: # 打开输入文件(只读)
        try:
            param = yaml.load(param_file, Loader=yaml.FullLoader) # 解析yaml文件
        except yaml.YAMLError as exc:
            print(exc)

    # 提取参数
    dimension = param["map"]["dimensions"]
    obstacles = param["map"]["obstacles"]
    agents_param = param['agents']
    agents = []
    for agent_param in agents_param:
        agents.append(Agent(agent_param['name'], agent_param['start'], agent_param['goal']))

    # 执行搜索
    solution_node = cbs_main(agents,dimension,obstacles)

    if solution_node: # 有解
        # 写入输出文件
        output = dict()
        output["schedule"] = generate_plan(solution_node.solution)
        output["cost"] = solution_node.cost
        with open(args.output, 'w') as output_yaml:
            yaml.safe_dump(output, output_yaml)
        # 可视化
        animation = Animation(param, output)
        animation.show()
    else: # 无解
        print("未找到解决方案")

"""生成输出格式的路径计划"""
def generate_plan(solution):
        plan = {}
        for path in solution.paths:
            path_dict_list = []
            for i in range(len(path.locations)):
                path_dict_list.append({'t':i, 'x':path.locations[i][0], 'y':path.locations[i][1]})
            plan[path.agent.id] = path_dict_list
        return plan

if __name__ == "__main__":
    main() 