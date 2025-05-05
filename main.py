import json
import re

import emoji

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.provider import LLMResponse
from astrbot.api.star import Context, Star, register
from astrbot.core.utils.t2i.renderer import logger


def remove_brackets(text: str = '', value: str = ''):
    # 删除嵌套括号和括号内的内容
    pattern = re.compile(r'[\(\（].*?[\)）]', re.DOTALL)
    while re.search(pattern, text):
        text = re.sub(pattern, value, text)
    # 删除单独的中英文括号，包括空格、没有内容的括号
    text = re.sub(r'[\(\（\)\）]\s*', '', text)  # 删除后面有空格的单个括号
    text = re.sub(r'\s*[\(\（\)\）]', '', text)  # 删除前面有空格的单个括号
    text = re.sub(r'[\(\（\)\）]', '', text)  # 删除没有空格的单个括号
    return text


def remove_emojis(text: str = '', value: str = ''):
    # 修正正则表达式，确保只匹配表情符号
    return emoji.replace_emoji(text, replace=value)


def remove_urls(text: str = '', value: str = ''):
    # 改进后的正则表达式，匹配完整的 URL 包括查询参数
    url_pattern = re.compile(
        r'http[s]?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.(com|cn)',  # 匹配 http:// 或 https:// 开头的 URL
        re.IGNORECASE
    )
    # 使用空字符串替换匹配到的 URL
    return url_pattern.sub('', text)


@register("regex_filter", "yuallart", "通过正则来过滤大模型的输出", "1.0.0",
          'https://github.com/Soulter/astrbot_plugin_r1_filter')
class R1Filter(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.emoji_filter = self.config.get('emoji_filter', {
            "condition": False,
            "value": ""
        })
        self.bracket_filter = self.config.get('bracket_filter', {
            "condition": False,
            "value": ""
        })
        self.url_filter = self.config.get('url_filter', {
            "condition": True,
            "value": ""
        })
        self.debug = self.config.get('debug', True)
        self.any_filter = self.config.get('any_filter', [])
        print(self.config)

    def print_info(self, *args):
        if self.debug:
            logger.info(" ".join(map(str, args)))

    @filter.on_llm_response()
    async def resp(self, event: AstrMessageEvent, response: LLMResponse):
        completion_text: str = response.completion_text
        if response.completion_text is None:
            return
        else:
            if self.emoji_filter['condition']:
                completion_text = remove_emojis(completion_text, self.emoji_filter['value'])
                self.print_info('emoji_filter=\n', completion_text)
            if self.bracket_filter['condition']:
                completion_text = remove_brackets(completion_text, self.bracket_filter['value'])
                self.print_info('bracket_filter=\n', completion_text)
            if self.url_filter['condition']:
                completion_text = remove_urls(completion_text, self.url_filter['value'])
                self.print_info('url_filter:\n', completion_text)
            for item in self.any_filter:
                try:
                    # 将字符串转为字典
                    rule = json.loads(item)
                    condition = rule.get("condition", "false").lower() == "true"
                    pattern = rule.get("regex", "")
                    repl = rule.get("value", "")
                    if condition and pattern:
                        # 执行正则替换
                        completion_text = re.sub(pattern, repl, completion_text)
                        self.print_info('regex_filter: regex=', pattern, '\n', completion_text)
                except json.JSONDecodeError as e:
                    self.print_info(f"JSON 解析错误: {e}")
            response.completion_text = completion_text
