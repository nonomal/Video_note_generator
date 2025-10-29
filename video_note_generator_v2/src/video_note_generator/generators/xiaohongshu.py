"""
小红书笔记生成器
"""
import re
from typing import Optional, List, Tuple
import logging

from ..ai_processor import AIProcessor


class XiaohongshuGenerator:
    """小红书笔记生成器"""

    def __init__(
        self,
        ai_processor: AIProcessor,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化生成器

        Args:
            ai_processor: AI 处理器
            logger: 日志记录器
        """
        self.ai_processor = ai_processor
        self.logger = logger or logging.getLogger(__name__)

    def generate(
        self,
        content: str,
        max_tokens: int = 2000
    ) -> Tuple[str, List[str], List[str]]:
        """
        生成小红书笔记（分两步：先生成标题，再生成正文）

        Args:
            content: 输入内容
            max_tokens: 最大 token 数

        Returns:
            (笔记内容, 标题列表, 标签列表) 元组
        """
        # 第一步：生成5个标题
        self.logger.info("第一步：生成小红书标题...")
        titles = self._generate_titles(content)

        if not titles:
            self.logger.warning("标题生成失败，使用默认流程")
            titles = ["小红书笔记"]

        # 选择第一个标题作为主标题
        main_title = titles[0] if titles else "小红书笔记"
        self.logger.info(f"已生成 {len(titles)} 个标题，主标题: {main_title[:30]}...")

        # 第二步：生成正文内容
        self.logger.info("第二步：生成小红书正文...")
        xiaohongshu_content = self._generate_content(content, main_title, max_tokens)

        if not xiaohongshu_content:
            return content, titles, []

        # 提取标签
        tags = self._extract_tags(xiaohongshu_content)

        return xiaohongshu_content, titles, tags

    def _generate_titles(self, content: str) -> List[str]:
        """
        第一步：生成5个不同风格的标题

        Args:
            content: 输入内容

        Returns:
            标题列表
        """
        system_prompt = self._build_title_system_prompt()
        user_prompt = self._build_title_user_prompt(content)

        result = self.ai_processor.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8,  # 稍高温度增加创意
            max_tokens=500  # 标题不需要太多token
        )

        if not result:
            return []

        # 解析标题
        titles = []
        for line in result.split('\n'):
            line = line.strip()
            # 移除序号和标记
            line = re.sub(r'^\d+[.、)\]]\s*', '', line)
            line = re.sub(r'^\[?标题\d*\]?\s*', '', line, flags=re.IGNORECASE)
            line = re.sub(r'^[-*]\s*', '', line)

            if line and len(line) > 5 and len(line) < 50:
                titles.append(line)

        return titles[:5]  # 最多返回5个

    def _generate_content(self, content: str, title: str, max_tokens: int) -> str:
        """
        第二步：根据选定的标题生成正文

        Args:
            content: 输入内容
            title: 选定的标题
            max_tokens: 最大token数

        Returns:
            正文内容
        """
        system_prompt = self._build_content_system_prompt()
        user_prompt = self._build_content_user_prompt(content, title)

        result = self.ai_processor.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=max_tokens
        )

        return result if result else ""

    def _extract_tags(self, content: str) -> List[str]:
        """
        从生成的内容中提取标签

        Args:
            content: 生成的内容

        Returns:
            标签列表
        """
        tag_matches = re.findall(r'#([^\s#]+)', content)
        return tag_matches if tag_matches else []

    def _build_title_system_prompt(self) -> str:
        """构建标题生成的系统提示词"""
        return """## 小红书爆款标题生成专家

### 角色设定
你是一名资深的小红书标题大师。
你精通各种爆款标题创作技巧。
你擅长用标题瞬间抓住用户注意力。

### 标题创作技能

你掌握以下5种标题创作方法：
1. **数字法则**：用具体数字增加可信度（如"7天"、"3个方法"）
2. **二极管标题**：制造强烈反差和对比效果
3. **疑问句式**：激发好奇心（如"为什么..."、"怎么..."）
4. **情绪共鸣**：使用高唤起情绪词，瞬间唤醒用户共鸣
5. **利益驱动**：直击痛点或利益点

【7大爆款标题风格】
- 数字悬念型：【3个懒人收纳法，房间一周不乱！】
- 情感共鸣型：【谁懂啊！这碗面直接治愈了我的周一！】
- 结果导向型：【跟着博主做，7天搞定Python基础！】
- 反差对比型：【从烂脸到水光肌，我只做了这两件事】
- 稀缺信息型：【这10个上海小众秘境，90%的人没去过】
- 对话互动型：【你的枕头选对了吗？快来对照这份指南！】
- 价值宣言型：【2025年投资自己，这3项技能最值钱】

### 平台禁忌词（严禁使用）
【诱导类】速来、必看、必收、千万不要、马上、抓紧、最后一波
【夸大类】全网第一、最全、最强、史上、终极、完美、天花板、封神
【营销类】免费送、0元购、薅羊毛、福利、红包、点击领取、价格感人
【负面类】丑哭、踩雷、血亏、别买、避坑、垃圾、后悔、翻车

### 标题创作要求
1. 每个标题使用不同的爆款标题风格
2. 严禁使用平台禁忌词
3. emoji优先用✨🔥✅💡❗️😭🤔💪，每个标题最多2个
4. 避免"XX分享""XX笔记"等无效词
5. 使用"亲测""试过""我发现"等真实感表述
6. 每个标题字数控制在20字以内
7. 标题要有吸引力，让人忍不住点进来看"""

    def _build_title_user_prompt(self, content: str) -> str:
        """构建标题生成的用户提示词"""
        return f"""请根据以下内容，生成5个不同风格的小红书爆款标题。

内容概要：
{content[:500]}...

要求：
1. 生成5个标题，每个使用不同的爆款标题风格
2. 直接输出5个标题，每行一个，不要添加序号和说明
3. 严格遵守平台禁忌词规则
4. 每个标题字数控制在20字以内
5. 必须包含emoji，每个标题最多2个

示例格式：
数字迷雾大揭秘✨3个方法让你秒懂数字陷阱！
谁懂啊🤔这些数字问题把我绕晕了！
从被骗到透视💡7天学会识破数字套路
你真的懂数字吗❗️90%人都答错的题！
2025必学技能🔥数字思维让你更聪明

请开始生成："""

    def _build_content_system_prompt(self) -> str:
        """构建正文生成的系统提示词"""
        return """## 小红书爆款正文生成专家

### 角色设定
你是一名资深的小红书爆款文案写手。
你精通小红书平台的内容创作规则。
你擅长创作高互动、高转化的种草文案。

### 正文创作技能

#### 1. 写作风格
- **语言风格**：像朋友聊天，真诚、直接、有温度
- **句式结构**：简单明了，主谓宾清晰，一句话一个意思
- **词汇选择**：大白话优先，专业术语必须解释
- **段落节奏**：每段2-3句，保持呼吸感

#### 2. 写作开篇方法
- **金句开场**：用一句话抓住注意力
- **痛点切入**：直接说出用户困扰
- **反转开场**：先说常见误区，再给出正确方法
- **故事引入**：用个人经历引发共鸣

#### 3. 文本结构
- **开头**：emoji+金句/痛点（1-2句话）
- **主体**：分点叙述，每点前加emoji，3-5个要点
- **每个要点包含**：具体方法+个人体验+效果说明
- **结尾**：总结+互动引导

#### 4. 互动引导方法
- **提问式**："你们有遇到这种情况吗？"
- **征集式**："评论区说说你的方法～"
- **行动式**："赶紧收藏起来！"
- **共鸣式**："姐妹们懂我的扣1！"

#### 5. 小技巧
- 使用"姐妹们"、"宝子们"等亲昵称呼
- 适当使用网络流行语和梗
- 多用"你、我、他"，少用"其、该、此、彼"
- 多用"真的"、"绝了"、"爱了"等语气词
- 用"第一、第二、第三"而不是"首先、其次、最后"

#### 6. 爆炸词库
**情绪类**：绝了、爱了、yyds、无敌、炸裂、疯狂、上头、氛围感
**效果类**：秒杀、碾压、吊打、封神、神仙、手残党必备
**程度类**：超级、巨、狂、暴、极致
**共鸣类**：懂的都懂、破防了、DNA动了、真实、太真实了

### 写作约束（严格执行）

**禁止使用以下内容**：
1. 不使用破折号（——）
2. 禁用"A而且B"的对仗结构
3. 不使用冒号（：），除非是对话或列表
4. 开头不用设问句
5. 一句话只表达一个完整意思
6. 每段不超过3句话
7. 避免嵌套从句和复合句
8. 多用"你、我、他"，少用"其、该、此、彼"

**改写策略**：
1. **长句拆短**：把复合句拆成多个简单句
2. **术语翻译**：把专业词汇翻译成大白话
3. **增加温度**：适当加入个人感受和真实体验
4. **逻辑清晰**：用"第一、第二、第三"标注顺序

### 创作要求
1. 内容真诚可信，把"真诚"摆在第一位
2. 避免假大空，花里胡哨的内容
3. 保持小红书社区调性，注重用户体验
4. 正文控制在600-800字之间
5. 在文末添加5-10个相关标签（用#号开头）"""

    def _build_content_user_prompt(self, content: str, title: str) -> str:
        """构建正文生成的用户提示词"""
        return f"""请根据以下标题和内容，创作一篇爆款小红书正文。

标题：
{title}

内容：
{content}

---

【极其重要：关于列表的绝对禁令】
绝对禁止使用任何形式的项目符号、编号列表或bullet points，包括但不限于：
- 星号（*）开头的列表
- 横杠（-）开头的列表
- 数字编号（1.、2.、3.）的列表
- 任何形式的条目化表述

所有内容必须使用连贯的段落形式，用"第一"、"第二"、"第三"等词语自然串联。

❌ 错误示例（使用了列表）：
这些问题包括：
* 问题1
* 问题2
* 问题3

✅ 正确示例（使用段落）：
这些问题包括三个方面。第一是问题1的内容。第二是问题2的描述。第三则是问题3的解释。

---

创作要求：
开篇方法：选择金句开场/痛点切入/反转开场/故事引入之一
文本结构：开头（emoji+金句1-2句）→ 主体（3-5个要点用段落展开，每段前加emoji）→ 结尾（总结+互动引导）
写作风格：像朋友聊天，真诚、直接、有温度
句式要求：简单明了，一句话一个意思，每段2-3句话
称呼使用："姐妹们"、"宝子们"等亲昵称呼
语气词：多用"真的"、"绝了"、"爱了"等
人称使用：多用"你、我、他"，少用"其、该、此、彼"
互动引导：2-3处自然的互动问句
正文控制在600-800字之间
文末添加5-10个相关标签（用#号开头，每个标签另起一行）

写作约束（严格禁止）：
- 绝对不使用任何形式的项目符号或编号列表
- 不使用破折号（——）
- 禁用"A而且B"的对仗结构
- 尽量避免使用冒号（：），用句号代替
- 开头不用设问句
- 避免嵌套从句和复合句
- 所有内容都用自然段落呈现

请直接输出正文内容，不要包含标题。"""

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """## 小红书爆款文案生成专家

### 角色设定
你是一名资深的小红书爆款文案写手。
你精通小红书平台的内容创作规则。
你擅长创作高互动、高转化的种草文案。

---

### 一、标题创作技能

你掌握以下5种标题创作方法：
1. **数字法则**：用具体数字增加可信度（如"7天"、"3个方法"）
2. **二极管标题**：制造强烈反差和对比效果
3. **疑问句式**：激发好奇心（如"为什么..."、"怎么..."）
4. **情绪共鸣**：使用高唤起情绪词，瞬间唤醒用户共鸣
5. **利益驱动**：直击痛点或利益点

【7大爆款标题风格】
- 数字悬念型：【3个懒人收纳法，房间一周不乱！】
- 情感共鸣型：【谁懂啊！这碗面直接治愈了我的周一！】
- 结果导向型：【跟着博主做，7天搞定Python基础！】
- 反差对比型：【从烂脸到水光肌，我只做了这两件事】
- 稀缺信息型：【这10个上海小众秘境，90%的人没去过】
- 对话互动型：【你的枕头选对了吗？快来对照这份指南！】
- 价值宣言型：【2025年投资自己，这3项技能最值钱】

---

### 二、小红书正文创作技能

#### 1. 写作风格
- **语言风格**：像朋友聊天，真诚、直接、有温度
- **句式结构**：简单明了，主谓宾清晰，一句话一个意思
- **词汇选择**：大白话优先，专业术语必须解释
- **段落节奏**：每段2-3句，保持呼吸感

#### 2. 写作开篇方法
- **金句开场**：用一句话抓住注意力
- **痛点切入**：直接说出用户困扰
- **反转开场**：先说常见误区，再给出正确方法
- **故事引入**：用个人经历引发共鸣

#### 3. 文本结构
- **开头**：emoji+金句/痛点（1-2句话）
- **主体**：分点叙述，每点前加emoji，3-5个要点
- **每个要点包含**：具体方法+个人体验+效果说明
- **结尾**：总结+互动引导

#### 4. 互动引导方法
- **提问式**："你们有遇到这种情况吗？"
- **征集式**："评论区说说你的方法～"
- **行动式**："赶紧收藏起来！"
- **共鸣式**："姐妹们懂我的扣1！"

#### 5. 小技巧
- 使用"姐妹们"、"宝子们"等亲昵称呼
- 适当使用网络流行语和梗
- 多用"你、我、他"，少用"其、该、此、彼"
- 多用"真的"、"绝了"、"爱了"等语气词
- 用"第一、第二、第三"而不是"首先、其次、最后"

#### 6. 爆炸词库
**情绪类**：绝了、爱了、yyds、无敌、炸裂、疯狂、上头、氛围感
**效果类**：秒杀、碾压、吊打、封神、神仙、手残党必备
**程度类**：超级、巨、狂、暴、极致
**共鸣类**：懂的都懂、破防了、DNA动了、真实、太真实了

#### 7. SEO标签规则
从生成的稿子中，抽取3-6个核心关键词。
生成#标签并放在文章最后。

#### 8. 口语化要求
文章的每句话都尽量口语化、简短。
避免长句和书面语。
一句话只表达一个完整意思。

#### 9. Emoji使用规则
在每段话的中间关键词处插入表情符号。
emoji优先用「✨/🔥/✅/💡/❗️/😭/🤔/💪」。

---

### 三、写作约束（严格执行）

**禁止使用以下内容**：
1. 不使用破折号（——）
2. 禁用"A而且B"的对仗结构
3. 不使用冒号（：），除非是对话或列表
4. 开头不用设问句
5. 一句话只表达一个完整意思
6. 每段不超过3句话
7. 避免嵌套从句和复合句
8. 多用"你、我、他"，少用"其、该、此、彼"

**平台禁忌词（严禁使用）**：
【诱导类】速来、必看、必收、千万不要、马上、抓紧、最后一波
【夸大类】全网第一、最全、最强、史上、终极、完美、天花板、封神
【营销类】免费送、0元购、薅羊毛、福利、红包、点击领取、价格感人
【负面类】丑哭、踩雷、血亏、别买、避坑、垃圾、后悔、翻车

**改写策略**：
1. **长句拆短**：把复合句拆成多个简单句
2. **术语翻译**：把专业词汇翻译成大白话
3. **增加温度**：适当加入个人感受和真实体验
4. **逻辑清晰**：用"第一、第二、第三"标注顺序

---

### 四、创作要求
1. 内容真诚可信，把"真诚"摆在第一位
2. 避免假大空，花里胡哨的内容
3. 避免使用广告法违禁词和平台敏感词
4. 保持小红书社区调性，注重用户体验
5. 每个标题和正文都要有独特视角
6. 正文控制在600-800字之间"""

    def _build_user_prompt(self, content: str) -> str:
        """构建用户提示词"""
        return f"""请将以下内容转换为爆款小红书笔记。

内容如下：
{content}

---

请严格按照以下格式输出内容。
只输出格式描述的部分。
不要解释创作过程。
不要添加任何提示词相关说明。

**输出格式**：

一. 标题
[标题1]
[标题2]
[标题3]
[标题4]
[标题5]

二. 正文
[正文内容]

标签：[#标签1 #标签2 #标签3 #标签4 #标签5]

---

**标题创作要求**：
1. 生成5个不同风格的标题，每个标题使用不同的爆款标题风格
2. 严禁使用平台禁忌词（速来、必看、最全、最强、免费送、薅羊毛、丑哭、踩雷等）
3. emoji优先用✨🔥✅💡❗️😭🤔💪，每个标题最多2个
4. 避免"XX分享""XX笔记"等无效词
5. 使用"亲测""试过""我发现"等真实感表述
6. 每个标题字数控制在20字以内

**正文创作要求（严格执行）**：
1. 开篇方法：金句开场/痛点切入/反转开场/故事引入（选择1种）
2. 文本结构：开头（emoji+金句1-2句）→ 主体（3-5个要点，每点前加emoji）→ 结尾（总结+互动引导）
3. 写作风格：像朋友聊天，真诚、直接、有温度
4. 句式要求：简单明了，一句话一个意思，每段2-3句话
5. 词汇选择：大白话优先，专业术语必须解释
6. 称呼使用："姐妹们"、"宝子们"等亲昵称呼
7. 语气词：多用"真的"、"绝了"、"爱了"等
8. 人称使用：多用"你、我、他"，少用"其、该、此、彼"
9. 顺序表达：用"第一、第二、第三"而不是"首先、其次、最后"
10. 互动引导：2-3处自然的互动问句（提问式/征集式/行动式/共鸣式）
11. 正文控制在600-800字之间

**写作约束（禁止）**：
1. 不使用破折号（——）
2. 禁用"A而且B"的对仗结构
3. 不使用冒号（：），除非是对话或列表
4. 开头不用设问句
5. 避免嵌套从句和复合句
6. 避免长句和书面语

**标签要求**：
提取5-10个标签，包含核心关键词、关联关键词、高转化词、热搜词
"""

    def _parse_result(self, result: str) -> Tuple[List[str], List[str]]:
        """
        解析生成结果

        Args:
            result: AI 生成的结果

        Returns:
            (标题列表, 标签列表) 元组
        """
        titles = []
        tags = []

        self.logger.debug(f"正在解析生成结果:\n{result}")

        # 提取标题（在"一. 标题"和"二. 正文"之间的内容）
        title_section_match = re.search(r'一[.、]\s*标题(.*?)二[.、]\s*正文', result, re.DOTALL)
        if title_section_match:
            title_section = title_section_match.group(1).strip()
            # 提取每一行非空内容作为标题
            for line in title_section.split('\n'):
                line = line.strip()
                # 移除可能的序号和标记
                line = re.sub(r'^\d+[.、)\]]\s*', '', line)
                line = re.sub(r'^\[标题\d+\]\s*', '', line)
                if line and not line.startswith('#'):
                    titles.append(line)

        # 如果上述方法未找到，尝试提取前几行作为标题
        if not titles:
            content_lines = result.split('\n')
            for line in content_lines[:10]:  # 只检查前10行
                line = line.strip()
                # 跳过明显的标记行
                if line and not line.startswith('#') and '正文' not in line and '标题' not in line and len(line) > 5:
                    # 移除可能的序号
                    line = re.sub(r'^\d+[.、)\]]\s*', '', line)
                    if line:
                        titles.append(line)
                        if len(titles) >= 5:  # 最多提取5个
                            break

        if titles:
            self.logger.info(f"提取到 {len(titles)} 个标题")
            for i, title in enumerate(titles[:3], 1):  # 只显示前3个
                self.logger.info(f"  标题{i}: {title[:50]}...")
        else:
            self.logger.warning("未能提取到标题")

        # 提取标签（在"标签："后面的内容）
        tag_matches = re.findall(r'#([^\s#]+)', result)
        if tag_matches:
            tags = tag_matches
            self.logger.info(f"提取到 {len(tags)} 个标签")
        else:
            self.logger.warning("未找到标签")

        return titles, tags

    def format_note(
        self,
        content: str,
        title: str,
        tags: List[str],
        images: List[str],
        all_titles: List[str] = None
    ) -> str:
        """
        格式化笔记内容

        Args:
            content: 笔记内容
            title: 主标题（用于文件名，通常是第一个标题）
            tags: 标签列表
            images: 图片URL列表
            all_titles: 所有标题列表（可选）

        Returns:
            格式化后的Markdown内容
        """
        output = []

        # 清理content中可能已有的标题（避免重复）
        # 移除开头的markdown标题
        content_cleaned = re.sub(r'^#\s+.*?\n', '', content, count=1).strip()

        # 移除content末尾已有的标签（避免重复）
        # 查找并移除末尾的标签部分（以 --- 分隔或连续的 #标签）
        content_cleaned = re.sub(r'\n\n---\n\n#.*$', '', content_cleaned, flags=re.DOTALL)
        content_cleaned = re.sub(r'\n\n(#[^\s#]+\s*)+$', '', content_cleaned).strip()

        # 如果有多个标题，先展示所有标题供选择
        if all_titles and len(all_titles) > 1:
            output.append("# 备选标题\n")
            for i, t in enumerate(all_titles, 1):
                output.append(f"{i}. {t}")
            output.append("\n---\n")

        # 主标题
        output.append(f"# {title}\n")

        # 如果有图片，添加封面
        if images:
            output.append(f"![封面图]({images[0]})\n")

        # 正文内容（插入图片）
        content_parts = content_cleaned.split('\n\n')
        mid_point = len(content_parts) // 2

        # 前半部分
        output.append('\n\n'.join(content_parts[:mid_point]))
        output.append('\n')

        # 中间图片
        if len(images) > 1:
            output.append(f"\n![配图]({images[1]})\n")

        # 后半部分
        output.append('\n\n'.join(content_parts[mid_point:]))

        # 末尾图片
        if len(images) > 2:
            output.append(f"\n\n![配图]({images[2]})")

        # 标签（只添加一次）
        if tags:
            output.append("\n\n---\n")
            output.append('\n'.join([f"#{tag}" for tag in tags]))

        return '\n'.join(output)
