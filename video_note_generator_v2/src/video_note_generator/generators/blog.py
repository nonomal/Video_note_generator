"""
博客文章生成器

将视频转录内容转化为深度博客文章
"""
from typing import Optional, Tuple
import logging


class BlogGenerator:
    """博客文章生成器"""

    def __init__(self, ai_processor, logger: Optional[logging.Logger] = None):
        """
        初始化博客生成器

        Args:
            ai_processor: AI处理器实例
            logger: 日志记录器
        """
        self.ai_processor = ai_processor
        self.logger = logger or logging.getLogger(__name__)

        # 博客生成提示词
        self.blog_prompt = """YouTube视频转博客提示词

你是一位顶级的深度内容创作者与思想转述者，拥有将任何复杂信息转化为一篇结构精巧、文笔优美、思想深刻的中文博客文章的卓越能力。你的写作风格不是信息的罗列，而是思想的启迪；你的文章不仅让人读懂，更让人思考。

你的任务是：将我发送的视频内容，完全内化和吸收后，以你自己的口吻和叙事风格，创作一篇全新的、独立的深度文章。

核心创作原则：

- 思想的重塑，而非文字的搬运： 你的目标不是"转写"视频，而是"启迪"读者。你要深入理解视频的内核，然后用最具洞察力和启发性的方式将其重新组织和呈现。
- 标题是文章的灵魂： 你需要为整篇文章、以及文章内部的每一个逻辑章节，都创作出高度概括且充满吸引力的标题。绝不使用"引言"、"正文"、"总结"这类模板化标题。
- 叙事驱动一切： 用流畅的散文体贯穿全文。即使是解释步骤或框架，也要用叙事性的段落来呈现，通过优雅的过渡词（例如"这一切的起点在于……"、"要理解这背后的逻辑，我们首先需要……"、"然而，真正的关键在于……"）来串联逻辑，而不是依赖项目符号。
- 完整性至上： 必须忠实地涵盖视频中的所有重要内容、观点和细节。不要遗漏任何关键信息，不要因为追求简洁而牺牲完整性。文章长度应该与视频内容的丰富程度相匹配，宁可详尽也不要简略。

**极其重要：**

【关于项目符号的绝对禁令】
绝对禁止使用任何形式的项目符号、编号列表或bullet points，包括但不限于：
- 星号（*）开头的列表
- 数字编号（1.、2.、3.）的列表
- 破折号（-）开头的列表
- 圆点（•）开头的列表
- 任何其他形式的列表标记

即使在列举多个要点时，也必须使用连贯的段落形式。例如：

❌ 错误示例（使用了列表）：
这个框架包括：
1. 第一个要点
2. 第二个要点
3. 第三个要点

✅ 正确示例（使用段落）：
这个框架包括三个核心要素。首先是第一个要点的内容，它描述了……其次是第二个要点，这一点强调……最后是第三个要点，它关注……

【关于内容完整性】
必须完整呈现视频的所有重要内容，不得省略或简化任何关键观点、案例或论述。文章篇幅没有上限，要充分展开每一个主题。

文章生成流程与要求：

第一步：基础信息与总标题

- 文章总标题： 在理解视频全部内容后，构思一个能够精准概括核心思想，并能瞬间抓住读者眼球的博客主标题（可包含副标题）。
- 文章元信息： 在文章末尾或开头附上以下信息：
  - 思想来源 (Source of Inspiration): [视频创作者名称]
  - 原始视频 (Original Video): [原始视频链接]

第二步：创作第一章节（开篇）

- 章节标题： 创作一个能激发读者强烈好奇心，或点明核心矛盾的标题。
- 内容要求： 以一个引人入胜的切入点（故事、场景、痛点、反常识观点）开始，自然地引出文章要探讨的核心问题，并含蓄地点明阅读本文将带来的独特认知价值，让读者确信这篇文章值得花时间深入阅读。

第三步：创作主体章节（核心论述）

- 章节标题： 根据视频的核心内容，将其拆解为2-4个逻辑连贯、层层递进的主题。为每一个主题创作一个精准、凝练、能体现其观点的小标题。
- 内容要求：
  - 这是文章的主体。你需要用充满洞察力的语言，将每个主题详细、生动地展开。多使用比喻、案例和追问来深化论述。
  - 当遇到方法论或操作流程时，请将其逻辑和步骤融入到连贯的段落描述中。通过分析每一步的"为什么"，让读者不仅知其然，更知其所以然。
  - 确保章节之间的过渡平滑且富有逻辑性，引导读者自然地从一个论点走向下一个更深的论点。

第四步：创作升华章节（抽象与提炼）

- 章节标题： 这个章节的标题应该直接点出你提炼出的核心框架、思维模型或底层逻辑的名称，例如"'机会密度'框架：如何发现隐藏的价值"或"成长的关键：建立你的'反馈飞轮'"。
- 内容要求：
  - 从前面的具体论述中，精准地抽象出最具普适性和启发性的框架或心智模型。
  - 用清晰、优雅的语言，深入阐释这个模型的构成要素、运转原理及其背后的哲学。
  - 重点不在于罗列定义，而在于生动地描绘出读者如何在自己的生活和工作中应用这个模型，从而获得思维上的跃迁。

第五步：创作结尾章节（回响与余味）

- 章节标题： 创作一个富有哲理或前瞻性的标题，为全文画上一个有力的句号。
- 内容要求：
  - 用精炼的语言，重新点亮文章的核心主旨，让读者产生一种"原来如此"的顿悟感。
  - 将文章的观点延伸至更广阔的领域，或留给读者一个开放性的、值得长期思考的问题。
  - 目标是让读者在合上文章后，脑海中仍有余音，心中仍有回响。

全局风格与限制：

- 文体流畅： 优先使用完整的段落进行叙述。**原则上不使用项目符号 (bullet points)**，除非在极少数情况下，用于并列呈现几个无法用段落替代的关键词或短语，且能极大增强表达清晰度时，方可破例。
- 口吻自信： 以一位独立的创作者和思想家的口吻进行写作，而不是作为视频的"介绍者"。完全隐去"视频中提到"、"作者认为"等中介性表述。
- 忠于思想，不限于形式： 可以在不增加新事实的前提下，对原视频的论述顺序进行优化重组，以达到最佳的阅读和逻辑体验。
- 专有名词处理： 保留原文专有名词，并在首次出现时于括号内提供中文翻译。
- 纯粹输出： 最终交付的内容应只有纯粹的文章本身，不包含任何关于指令（如字数要求）或创作过程的元语言。

请基于以下视频内容创作博客文章：

{content}"""

    def generate(
        self,
        content: str,
        video_info: dict,
        max_tokens: int = 4000
    ) -> Optional[str]:
        """
        生成博客文章

        Args:
            content: 整理后的视频内容
            video_info: 视频信息（标题、作者、链接等）
            max_tokens: 最大生成token数

        Returns:
            博客文章内容，失败返回None
        """
        try:
            self.logger.info("开始生成博客文章...")

            # 构建包含视频信息的内容
            full_content = f"""
视频标题：{video_info.get('title', '未知')}
视频作者：{video_info.get('uploader', '未知')}
视频链接：{video_info.get('url', '')}
视频平台：{video_info.get('platform', '未知')}

视频内容：
{content}
"""

            # 使用AI生成博客
            system_prompt = "你是一位顶级的深度内容创作者与思想转述者。"
            user_prompt = self.blog_prompt.format(content=full_content)

            blog_content = self.ai_processor.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=0.8  # 稍高温度以增加创意
            )

            if blog_content:
                self.logger.info(f"✅ 博客文章生成成功（{len(blog_content)}字符）")
                return blog_content
            else:
                self.logger.error("博客文章生成失败：AI返回空内容")
                return None

        except Exception as e:
            self.logger.error(f"生成博客文章失败: {e}", exc_info=True)
            return None

    def format_blog(
        self,
        content: str,
        video_info: dict
    ) -> str:
        """
        格式化博客文章，添加元信息

        Args:
            content: 博客内容
            video_info: 视频信息

        Returns:
            格式化后的博客文章
        """
        import re

        # 移除AI生成内容中已有的元信息部分（避免重复）

        # 首先移除文章开头的元信息（带英文翻译的格式）
        content_cleaned = re.sub(
            r'^[\n\s]*思想来源\s*\([^)]*\):[^\n]*\n原始视频\s*\([^)]*\):[^\n]*\n',
            '',
            content,
            flags=re.MULTILINE
        ).strip()

        # 也移除不带括号的简单格式
        content_cleaned = re.sub(
            r'^[\n\s]*思想来源:[^\n]*\n原始视频:[^\n]*\n',
            '',
            content_cleaned,
            flags=re.MULTILINE
        ).strip()

        # 查找并移除 "思想来源" 到文章结尾的部分
        content_cleaned = re.sub(
            r'\n*---\n*\*\*文章元信息\*\*.*$',
            '',
            content_cleaned,
            flags=re.DOTALL
        ).strip()

        # 移除可能单独出现的元信息行
        content_cleaned = re.sub(
            r'\n*- 思想来源.*?\n- 原始视频.*?\n.*$',
            '',
            content_cleaned,
            flags=re.DOTALL
        ).strip()

        # 移除末尾的AI创作声明
        content_cleaned = re.sub(
            r'\n*---\n*\*本文由 AI 辅助创作.*$',
            '',
            content_cleaned,
            flags=re.DOTALL
        ).strip()

        # 在文章末尾添加元信息
        footer = f"""

---

**文章元信息**

- 思想来源 (Source of Inspiration): {video_info.get('uploader', '未知创作者')}
- 原始视频 (Original Video): {video_info.get('url', '')}
- 视频平台 (Platform): {video_info.get('platform', '未知')}
- 文章生成时间: {video_info.get('timestamp', '')}

---

*本文由 AI 辅助创作，基于视频内容深度重构而成。*
"""

        return content_cleaned + footer
