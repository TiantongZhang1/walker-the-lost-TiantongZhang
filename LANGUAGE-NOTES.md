# LANGUAGE-NOTES.md

Assignment 5, Step 4. Tiantong Zhang.

## Part 1 — 生成着色器的行号

文件：`godot/shaders/standard_generated.gdshader`（Godot 编辑器生成，未经编辑）

- **`shader_type` 和 `render_mode`**：第 3、4 行
- **对应 Inspector 的 Albedo 颜色和法线强度的 uniform**：第 6、20 行
- **两个采样器及其 hint**：

      // 第 7 行
      uniform sampler2D texture_albedo : source_color, filter_linear_mipmap, repeat_enable;
      // 第 19 行
      uniform sampler2D texture_normal : hint_roughness_normal, filter_linear_mipmap, repeat_enable;

- **写入三个输出的代码**：第 35、43、46 行

## Part 2 — 八道问答

### 1. `shader_type` 决定什么？

`shader_type` 决定着色器参与哪种渲染管线，以及可用的处理器、内置变量和输出。

`canvas_item` 用于 2D，提供 TEXTURE、UV、COLOR 等变量。在 `fragment()` 中，
COLOR 可以读取和写入，写它会改变输出颜色。

`spatial` 用于 3D，提供 ALBEDO、ROUGHNESS、METALLIC、NORMAL_MAP 等材质输出。
COLOR 在两边的用途不同。在 spatial 的 `fragment()` 中，它是从顶点阶段传来的
顶点颜色，只读；材质底色要写到 ALBEDO。

各着色器的第 1 行：`trap_warning.gdshader:1`（`shader_type canvas_item;`）、
`dungeon_surface.gdshader:1` 和 `hint_bands.gdshader:1`（都是 `shader_type spatial;`）。

### 2. 你写了哪些处理器函数？移进 vertex() 会怎样？

`vertex()` 是给每个顶点算一次，`fragment()` 是给每个像素算一次。陷阱精灵只有
4 个顶点，组成 2 个三角形。

把 `trap_warning.gdshader:6` 的颜色代码搬进 `vertex()` 后，会先把顶点变红，
再乘上贴图原来的颜色。贴图本来就暗，所以红色也会被压暗。

按图里的数字算，原本应该显示的红色 (214, 60, 47)，会变成大约 (35, 10, 9)，
看起来接近黑色。

所以这行要放在 `fragment()`：先拿到贴图颜色，再把它变成警告色，才能让暗色
区域也明显变红。

### 3. 三个读的内置变量、两个写的，哪些只读？

我实际只读了两个内置变量，没有凑够三个：

- `COLOR`：在 `trap_warning.gdshader` 第 6 行，读取原来的颜色，再和警告色混合。
- `UV`：在 `dungeon_surface.gdshader` 第 17、20 行，用它确定读取贴图的哪个位置。

我写入了三个：第 6 行的 `COLOR`，以及石头着色器第 23 行的 `ALBEDO`、
第 26 行的 `ROUGHNESS`。

在 `fragment()` 里，`UV` 只能读；2D 的 `COLOR` 可以读也可以写，所以第 6 行
同时读写了 `COLOR`。

我没有用内置的 `TEXTURE`，因为我用自己声明的采样器读取贴图，所以不能把
`TEXTURE` 算进去。这也意味着我目前少了题目要求的第三个读取项。

### 4. 每个 hint：只影响 Inspector，还是也影响着色器收到的值？

这三种 hint 的作用不一样：

- `hint_range`（`trap_warning.gdshader:2`）只影响 Inspector 的滑条范围，
  挡不住脚本传入越界值。
- `hint_default_black`（`dungeon_surface.gdshader:4`）会影响值，但只在没绑定
  贴图时：这时默认读到黑色。
- **`source_color` 要看它挂在哪里。** 挂在采样器上（`hint_bands.gdshader:4`），
  会影响颜色采样转换；我的对比实验出现了 64 → 137 的显示差异。挂在 vec3
  `warn_color` 上（`trap_warning.gdshader:3`），这次实验没有观察到数值转换：
  八个像素全部精确符合 H1，结果为 (214, 60, 47)，没有出现 H2 预测的
  (171, 12, 7)。

还有一个区别：vec3 上的 `source_color` 能在参数报告里看出来，`tint` 被报成
TYPE_COLOR；两个采样器的报告却一样。也就是：这次实验中，一个改变报告但没改变
值，另一个影响采样值但报告没区别。

### 5. `hint_range` 会钳制从代码设进去的值吗？

`trap_warning.gdshader` 第 2 行虽然写了 `hint_range(0.0, 1.0)`，但脚本传入的
2.0 没有被钳成 1.0。

证据是像素 B：

| 情况                     | 像素 B 的颜色 |
| ------------------------ | ------------- |
| 传入 2.0，实际测到       | (255, 0, 0)   |
| 如果被钳成 1.0，应该得到 | (214, 60, 47) |

传入 2.0 后，`mix` 会越过警告色继续计算，让 B 的绿色和蓝色通道变成负数，
最终显示为 0。因此，测到纯红说明 2.0 确实参与了计算，`hint_range` 没有限制它。

### 6. 哪一行让 albedo 按颜色采样、法线按数据采样？

生成着色器的第 7、19 行：

    // 第 7 行：albedo 按颜色采样
    uniform sampler2D texture_albedo : source_color, filter_linear_mipmap, repeat_enable;

    // 第 19 行：法线按数据采样，没有 source_color
    uniform sampler2D texture_normal : hint_roughness_normal, filter_linear_mipmap, repeat_enable;

我的 `dungeon_surface.gdshader` 第 3、4 行：

    // 第 3 行：石头底色按颜色采样
    uniform sampler2D stone_albedo : source_color, filter_linear_mipmap;

    // 第 4 行：湿度遮罩按数据采样
    uniform sampler2D wetness_mask : filter_linear_mipmap, hint_default_black;

**Godot 自动生成的代码和我手写的代码用了同样的区分：颜色带 `source_color`，
数据不带。** 法线和湿度遮罩都是数据，不能当颜色做转换。

### 7. 为什么 fragment() 读不到邻居？状态怎么进来？

很多片元会并行计算，没有谁先谁后的保证，所以一个片元不能直接读取邻居
“正在算的结果”。

游戏状态由脚本通过 uniform 传进来：

- `trap_warning.gdshader:2` 声明 `warn_amount`，作为接收状态的入口。
- `trap_warning_driver.gd:76` 写入它。
- `trap_warning.gdshader:6` 读取它，计算警告颜色。

驱动还在 `trap_warning_driver.gd:42` 把 `process_priority` 设为 100。Godot
优先执行数值较小的节点，因此优先级为 0 的陷阱状态机先更新，驱动随后传值，
再进行采样。这样着色器拿到的是这一帧刚算出的状态，不是上一帧的。

### 8. 两样 Godot 着色语言有、纯 GLSL 没有的东西

我选这两个例子：

1. `group_uniforms`，在 `dungeon_surface.gdshader:6、10、13`。它能把参数分组
   显示在 Godot Inspector 里。纯 GLSL 没有编辑器分组功能；想做这样的参数面板，
   需要在着色器之外自己实现。

2. `ALBEDO` 和 `ROUGHNESS`，在 `dungeon_surface.gdshader:23、26`。我只需要填好
   底色和粗糙度，Godot 就会接着计算光照。用纯 GLSL 时，需要自己编写或接入光照
   模型，包括计算漫反射和高光的 BRDF；给两个变量赋值不会自动得到这些效果。
