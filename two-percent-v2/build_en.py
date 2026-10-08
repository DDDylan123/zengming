"""由 index.html 生成英文版 en/index.html：<html lang="en">，资源路径加 ../，页面信息换成英文。"""
import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a[:60]; s = s.replace(a, b)
rep('<html lang="zh-CN">', '<html lang="en" data-base="../">')
s = s.replace('url(fonts/', 'url(../fonts/')
s = re.sub(r'<title>.*?</title>', '<title>Two Percent — Dylan He</title>', s)
s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="A black-and-white cartoon drawn entirely in code: AI keeps getting smarter, so why is the economy still on the two-percent road? Inspired by a Sept. 23, 2026 conversation with Anthropic’s chief economist at Harvard.">', s)
s = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Two Percent — Dylan He">', s)
s = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="AI keeps getting smarter, so why is the economy still on the two-percent road? A cartoon drawn in code.">', s)
s = s.replace('https://dylanhe.cn/assets/two-percent.jpg', 'https://dylanhe.cn/assets/two-percent-en.jpg')
s = s.replace('https://dylanhe.cn/explainers/two-percent/"', 'https://dylanhe.cn/explainers/two-percent/en/"')
open('en/index.html', 'w', encoding='utf-8').write(s)
print('en/index.html written')
