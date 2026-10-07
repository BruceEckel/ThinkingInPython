# exercise_7.py
import plugin_list
from plugin_list import plugins

plugin_list.plugins.append("spell check")
print(plugins)
#: ['spell check']
print(plugins is plugin_list.plugins)
#: True
plugin_list.plugins = []
plugin_list.plugins.append("word count")  # [1]
print(plugins, plugin_list.plugins)
#: ['spell check'] ['word count']
print(plugins is plugin_list.plugins)
#: False
