# 正则表达式过滤器插件

这个插件允许用户通过正则表达式过滤和修改大模型输出的内容。

## 配置项说明

### debug

是否开启调试模式，开启后会输出一些调试信息。

### emoji_filter

过滤掉所有emoji表情。

使用emoji库替换所有可能存在的emoji表情，插件会自动安装这个库，如没有，请手动安装 

```bash
pip install emoji
```
### url_filter

url过滤，会过滤掉所有url。

会替换所有以http，https，www开头，然后com，cn结尾的url

### bracket_filter

用于过滤AI的动作描写

会替换所有的中文括号（xxx），英文括号(xxx)。只有成对的括号会被替换，单个的括号则是直接删除

### any_filter

自定义正则过滤器，允许用户通过正则表达式自定义过滤规则。

## any_filter 自定义正则过滤器

`any_filter` 是一个列表配置项，允许用户添加多个自定义正则过滤规则。每个规则包含以下字段：

- `condition`: 是否启用该规则（布尔值）
- `regex`: 正则表达式，用于匹配需要过滤的内容
- `value`: 替换匹配内容的值（字符串）

## 使用示例

需要注意的是，给list输入的必须是一个json对象，且不能使用引号

以下是一个示例配置，展示了如何使用 `any_filter` 过滤特定内容：

```{"condition":"true", "regex":"xxx", "value":"replacement1"}```


这个配置会替换所有包含xxx的字符串

每个列表项都是一个json，包含三个键：`condition`、`regex`和`value`，不能多也不能少，否则会引起报错。