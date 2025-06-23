# CBS

## 一、基本概念

* **基本元素**：
  
  * **路径path**：智能体 $a_i$ 的一个 $\{move,wait\}$ 动作的序列。智能体 $a_i$ 从 $start_i$ 开始执行这个动作序列，可以最终到达 $goal_i$ 。
  
  * **解决方案solution**：给定的 $k$ 个智能体的 $k$ 个路径的集合。
  
  * **冲突conflict**：用一个元组表示，包含顶点冲突、边冲突、跟随冲突、循环冲突、交换冲突等类型，例如顶点冲突 $(a_i,a_j,v,t)$ 表示智能体 $a_i$ 和 $a_j$ 在时间步 $t$ 占据顶点 $v$ 。
  
  * **约束constrain**t：用一个元组表示，例如 $(a_i,v,t)$ 表示智能体 $a_i$ 禁止在时间步 $t$ 占据顶点 $v$ ；$(a_i,v_1,v_2,t)$ 表示智能体 $a_i$ 被禁止在 $t$ 时刻从 $v_1$ 开始沿边移动到 $v_2$（ $t+1$ 时刻到达）。
  
  * **成本cost**：所有智能体到达目标并不再次离开所需的时间步数的总和。

* **约束树CT(the constraint tree)**：二叉树，节点按成本排序。每个节点包括：
  
  * 一组约束
  
  * 一个满足约束的解决方案：一组所有智能体的路径
  
  * 解决方案的总成本

* **两层算法**：
  
  * **底层**：为智能体 $a_i$ 找到一个满足所有约束的最佳路径，同时完全忽略其他智能体。搜索空间有时间和空间两个维度。可使用任何单智能体路径规划算法来实现，如 $A*$ 算法。
  
  * **顶层**：在**约束树CT**上执行最佳优先搜索。对每个节点遍历底层的规划路径，检查路径间是否有冲突，如果有则施加约束并分裂出新节点，重新进行底层规划，直到所有底层路径无冲突为止。
    *当最佳优先搜索出现平局时，可参考的方案是：优先选择关联解决方案中冲突较少的 CT 节点。进一步的平局则按 FIFO 方式解决。*

## 二、基本过程（顶层规划）

1. **CT节点构建**：调用底层算法，为每个智能体生成一条符合约束的最短路径（通常使用 $A*$ 或 $Dijkstra$ 算法）得出该节点的解决方案，然后计算总成本。（注：根节点约束集为空）
2. **冲突检测**：在CT上执行最佳优先搜索，检查最佳CT节点的解决方案是否存在冲突。若不存在，则完成任务。
3. **冲突解决**：若存在冲突，增加有效的约束来解决冲突，并构建子CT节点。之后重复以上步骤，直至所有找到无冲突的解决方案。

```伪代码
输入: MAPF实例
输出：解决方案Solution
1 Root.constraints = ∅ // 根节点约束集为空
2 Root.solution = find individual paths by the low level() // 调用底层算法生成解决方案
3 Root.cost = SIC(Root.solution) //计算总成本
4 insert Root to CT // 插入约束树
5 while CT not empty do // 循环检查CT
6     P ← best node from CT // 找出最佳CT节点(最低解决成本)
7     Validate the paths in P until a conflict occurs. // 检测冲突
8     if P has no conflict then // 若无冲突
9         return P.solution // 找到解决方案，返回
10    C ← first conflict (aᵢ, aⱼ, v, t) in P // 保存第一个冲突
11    foreach agent aᵢ in C do // 遍历冲突中的每个智能体
12        A ← new node
13        A.constraints ← P.constraints + (aᵢ, v, t) // 增加约束
14        A.solution ← P.solution // 继承解决方案
15        Update A.solution by invoking the low level(aᵢ) // 调用底层算法更新新增约束的智能体aᵢ的解决方案路径
16        A.cost = SIC(A.solution) //计算总成本
17        if A.cost < ∞ // 若该节点有效
18            Insert A to CT // 插入约束树
```

## 三、A*算法（底层规划）

* 优先级算法 $f(n) = g(n) + h(n)$
  
  * $f(n)$：节点 $n$ 的综合优先级。
  
  * $g(n)$：节点 $n$ 距离起点的代价。
  
  * $h(n)$：节点 $n$ 距离终点的预计代价，$A*$ 算法的启发函数。对于网格类型地图，可以用以下启发函数：
    
    * 如果图中只允许朝上下左右四个方向移动，可使用**曼哈顿距离**。
    
    * 如果图中允许朝八个方向（上下左右 + 对角）移动，则可使用**对角距离**。
    
    * 如果图中允许朝任何方向移动，则可使用**欧几里得距离**。

* 两个集合：
  
  * **open_list**：存放待遍历的节点
  
  * **close_list**：存放已遍历的节点

* 每次从优先队列（**open_list**） 中选取 $f(n)$ 值最小（优先级最高）的节点作为下一个待遍历的节点。

```伪代码
1 初始化open_list和close_list;
2 将起点加入open_list中，并设置优先级为0（优先级最高）;
3 while(open_list不为空) do
4     从open_list中选取优先级最高的节点n;
5     if 节点n为终点:
6         从终点开始逐步追踪parent节点，一直到达起点;
7         return 找到的结果路径;
8     if 节点n不是终点:
9         将节点n从open_list中删除，并加入close_list;
10        for each 节点n的邻近节点;
11            if 邻近节点m在close_list中:
12                continue;
13            if 邻近节点m也不在open_list中:
14                设置节点m的parent为节点n;
15                计算节点m的优先级;
16                将节点m加入open_list中;
```
