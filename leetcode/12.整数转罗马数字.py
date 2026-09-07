#
# @lc app=leetcode.cn id=12 lang=python3
#
# [12] 整数转罗马数字
#

# @lc code=start
class Solution:
    def intToRoman(self, num: int) -> str:
        # 定义映射表 整数：罗马
        int_to_roman = [
            (1000, 'M'),
            (500, 'D'), 
            (100, 'C'),
            (50, 'L'),
            (10, 'X'),
            (5, 'V'),
            (1, 'I')
        ]   

        # 定义输出
        res = ''
        # 循环输入整数
        for i in range(num):
            # 获取 key
            
            ...

        return res
# @lc code=end

