import re
s1 = "blog/xiaohei/tag/python"
s2 = "blog/xiaohei/category/技术"
s3 = "blog/xiaohei/archive/2018-05"
ret1=re.match(r'blog/(\w+)/(tag|category|archive)/(.+)',s1)
print(ret1)
ret2 = re.match(r'blog/(\w+)/(tag|category|archive)/(.+)', s2)
print(ret2)
ret3 = re.match(r'blog/(\w+)/(tag|category|archive)/(.+)', s3)
print(ret3)